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

            m4a_audio_file = VideoDownloader(self.config).run(meeting)
            mp3_audio_file = AudioConverter(self.config).run(m4a_audio_file)

            agenda_pdf_file = PdfDownloader(self.config).run(meeting)
            agenda_json_file = PdfParser(self.config).run(agenda_pdf_file)

            #TODO add audio file processing

        except PipelineError as e:
            self.logger.critical(f"Pipeline failed: {e}")
    
from abc import ABC, abstractmethod
import logging
from typing import Any
class PipelineStage(ABC):
    def __init__(self, config: PipelineConfig):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    def validate(self, input_data: Any) -> bool:
        """Validate input before execution."""
        pass

    @abstractmethod
    def execute(self, intput_data: Any) -> Any:
        """Execute this stage. Return output for next stage."""
        pass

    def cleanup(self):
        """Optional: clean up resources after execution."""
        pass

    def run(self, input_data: Any) -> Any:
        try:
            self.logger.info(f"Starting {self.__class__.__name__}...")
            
            if not self.validate(input_data):
                raise ValueError(f"Invalid input for {self.__class__.__name__}")
            
            result = self.execute(input_data)
            self.logger.info(f"{self.__class__.__name__} completed successfully")
            
            return result
        except Exception as e:
            self.logger.error(f"{self.__class__.__name__} failed: {e}")
            raise
        finally:
            self.cleanup()