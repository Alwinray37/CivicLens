from pathlib import Path

from sqlalchemy import create_engine, text

from pipeline.stage import PipelineStage
from pipeline.exceptions import PipelineError
from utils.json_helper import JsonHelper


class DbInsert(PipelineStage):
    def validate(self, input_data):
        if not self.config.db_url:
            self.logger.error("db_url is not configured")
            return False

        if not isinstance(input_data, (str, Path)):
            self.logger.error(f"Input must be a file path, got {type(input_data)}")
            return False

        if not Path(input_data).exists():
            self.logger.error(f"File does not exist: {input_data}")
            return False

        return True

    def execute(self, input_data):
        meeting_data = JsonHelper.load_json_data(input_data)

        date = meeting_data["date"]
        video_url = meeting_data["video_url"]
        agenda_items = meeting_data["agenda_items"]["items"]
        summaries = meeting_data["summaries"]
        chunk_data = meeting_data["chunk_data"]

        engine = create_engine(self.config.db_url)

        try:
            with engine.begin() as conn:
                # Insert meeting and get its ID
                result = conn.execute(
                    text(
                        'INSERT INTO public."Meetings" ("Date", "VideoURL", "Title") '
                        "VALUES (:date, :video_url, :title) "
                        'RETURNING "MeetingID"'
                    ),
                    {"date": date, "video_url": video_url, "title": "City Council Meeting"},
                )
                meeting_id = result.scalar_one()
                self.logger.info(f"Inserted meeting {meeting_id} for {date}")

                # Insert agenda items
                if agenda_items:
                    agenda_rows = []
                    for i, item in enumerate(agenda_items):
                        agenda_rows.append({
                            "meeting_id": meeting_id,
                            "title": item.get("title", ""),
                            "description": item.get("description", ""),
                            "item_number": int(item.get("item_number", i + 1)),
                            "order_number": i + 1,
                            "file_number": item.get("file_number"),
                        })

                    conn.execute(
                        text(
                            'INSERT INTO public."AgendaItems" '
                            '("MeetingID", "Title", "Description", "ItemNumber", "OrderNumber", "FileNumber") '
                            "VALUES (:meeting_id, :title, :description, :item_number, :order_number, :file_number)"
                        ),
                        agenda_rows,
                    )
                    self.logger.info(f"Inserted {len(agenda_rows)} agenda items")

                # Insert summaries
                if summaries:
                    summary_rows = []
                    for s in summaries:
                        summary_rows.append({
                            "meeting_id": meeting_id,
                            "title": s.get("Title", ""),
                            "summary": s.get("Summary", ""),
                            "start_time": str(s.get("StartTime", "")),
                        })

                    conn.execute(
                        text(
                            'INSERT INTO public."Summaries" '
                            '("MeetingID", "Title", "Summary", "StartTime") '
                            "VALUES (:meeting_id, :title, :summary, :start_time)"
                        ),
                        summary_rows,
                    )
                    self.logger.info(f"Inserted {len(summary_rows)} summaries")

                # Insert chunks with embeddings
                if chunk_data:
                    for chunk in chunk_data:
                        embedding_list = chunk.get("embedding", [])
                        vector_str = "[" + ",".join(str(f) for f in embedding_list) + "]"

                        conn.execute(
                            text(
                                'INSERT INTO public."MeetingChunks" '
                                '("meeting_id", "ChunkNum", "StartTime", "EndTime", "Content", "Embedding") '
                                "VALUES (:meeting_id, :chunk_num, :start_time, :end_time, :content, :embedding::vector)"
                            ),
                            {
                                "meeting_id": meeting_id,
                                "chunk_num": int(chunk.get("chunknum", 0)),
                                "start_time": float(chunk.get("starttime", 0)),
                                "end_time": float(chunk.get("endtime", 0)),
                                "content": chunk.get("chunk", ""),
                                "embedding": vector_str,
                            },
                        )
                    self.logger.info(f"Inserted {len(chunk_data)} chunks")

            self.logger.info(f"All data committed for meeting {meeting_id}")
            return meeting_id

        except Exception as e:
            raise PipelineError(f"Database insertion failed: {e}")
        finally:
            engine.dispose()

    def cleanup(self):
        pass
