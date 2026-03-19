import logging

from pipeline.config import PipelineConfig
from pipeline.exceptions import PipelineError

from pipeline.stages.meeting_fetcher import MeetingFetcher
from pipeline.stages.video_downloader import VideoDownloader
from pipeline.stages.audio_converter import AudioConverter
from pipeline.stages.pdf_downloader import PdfDownloader
from pipeline.stages.pdf_parser import PdfParser

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

            #m4a_audio_file = VideoDownloader(self.config).run(meeting)

            #TEMP            
            #m4a_audio_file = str(self.config.temp_dir / "RegularCityCouncil-31326.m4a")
            mp3_audio_file = str(self.config.temp_dir / "RegularCityCouncil-31326.mp3")
            #TEMP

            #mp3_audio_file = AudioConverter(self.config).run(m4a_audio_file)

            agenda_pdf_file = PdfDownloader(self.config).run(meeting)
            agenda_json_file = PdfParser(self.config).run(agenda_pdf_file)

            #TODO add audio file processing

        except PipelineError as e:
            self.logger.critical(f"Pipeline failed: {e}")