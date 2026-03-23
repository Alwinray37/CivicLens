import logging

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

class PipelineOrchestrator:
    def __init__(self, config: PipelineConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)

    def execute(self):
        try:
            meetings = MeetingFetcher(self.config).run(None)

            if not meetings:
                raise PipelineError("No meetings found")
            
            #get latest meeting
            meeting = meetings[-1]

            #TEMP   
            #agenda_pdf_file = PdfDownloader(self.config).run(meeting)
            #agenda_json_file = PdfParser(self.config).run(agenda_pdf_file)

            agenda_json_file = str(self.config.temp_dir / "agenda_17962_parsed.json")

            #m4a_audio_file = VideoDownloader(self.config).run(meeting)

               
            #m4a_audio_file = str(self.config.temp_dir / "RegularCityCouncil-31326.m4a")
            mp3_audio_file = str(self.config.temp_dir / "RegularCityCouncil-31326.mp3")
            
            #mp3_audio_file = AudioConverter(self.config).run(m4a_audio_file)

            #transcript = TranscriptGen(self.config).run(mp3_audio_file)
            #TEMP

            transcript_json_file = str(self.config.temp_dir / "RegularCityCouncil-31326.json")

            summary_dict = {
                "files": [transcript_json_file, agenda_json_file],
                "options": {
                    "lines_per_chunk": 50,
                    "overlap": 5,
                    "max_query": 5,
                    },
            }

            chunk_input = {
                "transcript_file": transcript_json_file,
                "options": summary_dict["options"],
                "chunk_artifact_file" : None
            }

            chunk_file = ChunkGen(self.config).run(chunk_input)

            #TEMP
            #chunk_file = str(self.config.temp_dir / "RegularCityCouncil-31326_chunks_embeddings.json")
            #TEMP
            
            summary_dict["chunk_artifact_file"] = chunk_file
            summary_json_file = SummaryGen(self.config).run(summary_dict)

            #TODO add audio file processing

        except PipelineError as e:
            self.logger.critical(f"Pipeline failed: {e}")