import logging

from utils.json_helper import JsonHelper

from pipeline.config import PipelineConfig
from pipeline.exceptions import PipelineError

from pipeline.stages.meeting_fetcher import MeetingFetcher
from pipeline.stages.video_downloader import VideoDownloader
from pipeline.stages.audio_converter import AudioConverter
from pipeline.stages.pdf_downloader import PdfDownloader
from pipeline.stages.pdf_parser import PdfParser
from pipeline.stages.transcript_gen import TranscriptGen
from pipeline.stages.summary_gen import SummaryGen
from pipeline.stages.chunk_gen import ChunkGen
from pipeline.stages.combine_meeting_data import CombineMeetingData
from pipeline.stages.sql_gen import SqlGen
from pipeline.stages.db_insert import DbInsert

class PipelineOrchestrator:
    def __init__(self, config: PipelineConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)

    def execute(self):
        try:
            meetings = MeetingFetcher(self.config).run(None)

            if not meetings:
                raise PipelineError("No meetings found")

            if self.config.target_date:
                matched = [m for m in meetings if m["dateTime"][:10] == self.config.target_date]
                if not matched:
                    raise PipelineError(
                        f"No meeting found for date {self.config.target_date}. "
                        f"Available dates: {[m['dateTime'][:10] for m in meetings]}"
                    )
                meeting = matched[0]
            else:
                meeting = meetings[-1]

            agenda_pdf_file = PdfDownloader(self.config).run(meeting)
            agenda_json_file = PdfParser(self.config).run(agenda_pdf_file)

            m4a_audio_file = VideoDownloader(self.config).run(meeting)

            mp3_audio_file = AudioConverter(self.config).run(m4a_audio_file)

            transcript_json_file = TranscriptGen(self.config).run(mp3_audio_file)

            summary_dict = {
                "files": [transcript_json_file, agenda_json_file],
                "chunk_artifact_file": None,
                "options": {
                    "lines_per_chunk": 50,
                    "overlap": 5,
                    "max_query": 5,
                    },
            }

            chunk_input = {
                "transcript_file": transcript_json_file,
                "options": summary_dict["options"],
            }

            chunk_file = ChunkGen(self.config).run(chunk_input)

            summary_dict["chunk_artifact_file"] = chunk_file
            summary_json_file = SummaryGen(self.config).run(summary_dict)

            meeting_info = {
                "summary_file": summary_json_file,
                "agenda_file": agenda_json_file,
                "chunk_file": chunk_file,
                "meeting": meeting
            }

            meeting_data_file = CombineMeetingData(self.config).run(meeting_info)

            # Always generate the SQL backup file
            sql_file = SqlGen(self.config).run(meeting_data_file)
            self.logger.info(f"SQL backup written to {sql_file}")

            # Insert into DB if configured and not skipped
            if self.config.db_url and not self.config.no_db:
                meeting_id = DbInsert(self.config).run(meeting_data_file)
                self.logger.info(f"Inserted into database as MeetingID={meeting_id}")
            elif not self.config.db_url:
                self.logger.info("No db_url configured, skipping database insertion")
            else:
                self.logger.info("--no-db flag set, skipping database insertion")

        except PipelineError as e:
            self.logger.critical(f"Pipeline failed: {e}")
            raise
