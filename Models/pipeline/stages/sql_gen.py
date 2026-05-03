import json
from pathlib import Path
from pipeline.stage import PipelineStage
from utils.json_helper import JsonHelper


def _sql_escape(value):
    """Escape a value for safe inclusion in a SQL literal."""
    if value is None:
        return "NULL"
    if isinstance(value, bool):
        return "TRUE" if value else "FALSE"
    if isinstance(value, (int, float)):
        return str(value)
    s = str(value).replace("'", "''")
    return f"'{s}'"


def _sql_vector(embedding):
    """Format a list of floats as a pgvector literal."""
    csv = ",".join(str(f) for f in embedding)
    return f"'[{csv}]'::vector"


class SqlGen(PipelineStage):
    def validate(self, input_data):
        if not Path(input_data).exists():
            return False

        meeting_data = JsonHelper.load_json_data(input_data)

        required_keys = ["date", "video_url", "agenda_items", "summaries", "chunk_data"]
        if not all(key in meeting_data for key in required_keys):
            return False

        if not isinstance(meeting_data["agenda_items"], dict) or "items" not in meeting_data["agenda_items"]:
            return False
        if not isinstance(meeting_data["agenda_items"]["items"], list):
            return False

        if not isinstance(meeting_data["summaries"], list):
            return False

        if not isinstance(meeting_data["chunk_data"], list):
            return False

        if not isinstance(meeting_data["date"], str) or len(meeting_data["date"]) == 0:
            return False
        if not isinstance(meeting_data["video_url"], str) or len(meeting_data["video_url"]) == 0:
            return False

        return True

    def execute(self, input_data):
        meeting_data = JsonHelper.load_json_data(input_data)

        date = meeting_data["date"]
        video_url = meeting_data["video_url"]
        agenda_items = meeting_data["agenda_items"]["items"]
        summaries = meeting_data["summaries"]
        chunk_data = meeting_data["chunk_data"]

        lines = ["BEGIN;", ""]

        # Insert meeting
        lines.append("-- Insert meeting")
        lines.append(
            f"INSERT INTO public.\"Meetings\" (\"Date\", \"VideoURL\", \"Title\") VALUES "
            f"({_sql_escape(date)}, {_sql_escape(video_url)}, {_sql_escape('City Council Meeting')});"
        )
        lines.append("")

        # Insert agenda items
        if agenda_items:
            lines.append("-- Insert agenda items")
            lines.append("WITH m AS (")
            lines.append(f"    SELECT \"MeetingID\" AS mid FROM public.\"Meetings\" WHERE \"Date\" = {_sql_escape(date)}")
            lines.append(")")
            for i, item in enumerate(agenda_items):
                title = _sql_escape(item.get("title", ""))
                description = _sql_escape(item.get("description", ""))
                item_number = int(item.get("item_number", i + 1))
                file_number = _sql_escape(item.get("file_number"))
                order_number = i + 1

                values = (
                    f"m.mid, {_sql_escape(title).replace(chr(39), '', 2) if False else title}, "
                    f"{description}, {item_number}, {order_number}, {file_number}"
                )

                if i == 0:
                    lines.append(
                        f"INSERT INTO public.\"AgendaItems\" "
                        f"(\"MeetingID\", \"Title\", \"Description\", \"ItemNumber\", \"OrderNumber\", \"FileNumber\")"
                    )
                    lines.append(f"SELECT m.mid, {title}, {description}, {item_number}, {order_number}, {file_number}")
                    lines.append("FROM m")
                else:
                    lines.append("UNION ALL")
                    lines.append(f"SELECT m.mid, {title}, {description}, {item_number}, {order_number}, {file_number}")
                    lines.append("FROM m")

            lines.append(";")
            lines.append("")

        # Insert summaries
        if summaries:
            lines.append("-- Insert summaries")
            lines.append("WITH m AS (")
            lines.append(f"    SELECT \"MeetingID\" AS mid FROM public.\"Meetings\" WHERE \"Date\" = {_sql_escape(date)}")
            lines.append(")")

            for i, summary in enumerate(summaries):
                start_time = _sql_escape(str(summary.get("StartTime", "")))
                title = _sql_escape(summary.get("Title", ""))
                summary_text = _sql_escape(summary.get("Summary", ""))

                if i == 0:
                    lines.append(
                        f"INSERT INTO public.\"Summaries\" "
                        f"(\"MeetingID\", \"StartTime\", \"Title\", \"Summary\")"
                    )
                    lines.append(f"SELECT m.mid, {start_time}, {title}, {summary_text}")
                    lines.append("FROM m")
                else:
                    lines.append("UNION ALL")
                    lines.append(f"SELECT m.mid, {start_time}, {title}, {summary_text}")
                    lines.append("FROM m")

            lines.append(";")
            lines.append("")

        # Insert chunks with embeddings
        if chunk_data:
            lines.append("-- Insert chunks")
            lines.append("WITH m AS (")
            lines.append(f"    SELECT \"MeetingID\" AS mid FROM public.\"Meetings\" WHERE \"Date\" = {_sql_escape(date)}")
            lines.append(")")

            for i, chunk in enumerate(chunk_data):
                chunk_num = int(chunk.get("chunknum", i + 1))
                start_time = float(chunk.get("starttime", 0))
                end_time = float(chunk.get("endtime", 0))
                content = _sql_escape(chunk.get("chunk", ""))
                embedding = _sql_vector(chunk.get("embedding", []))

                if i == 0:
                    lines.append(
                        f"INSERT INTO public.\"MeetingChunks\" "
                        f"(\"meeting_id\", \"ChunkNum\", \"StartTime\", \"EndTime\", \"Content\", \"Embedding\")"
                    )
                    lines.append(f"SELECT m.mid, {chunk_num}, {start_time}, {end_time}, {content}, {embedding}")
                    lines.append("FROM m")
                else:
                    lines.append("UNION ALL")
                    lines.append(f"SELECT m.mid, {chunk_num}, {start_time}, {end_time}, {content}, {embedding}")
                    lines.append("FROM m")

            lines.append(";")
            lines.append("")

        lines.append("COMMIT;")

        sql_text = "\n".join(lines)
        output_path = str(Path(self.config.output_dir / f"Meeting_{date}.sql"))

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(sql_text)

        return output_path

    def cleanup(self):
        pass
