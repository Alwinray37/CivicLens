import logging
from typing import Any
from abc import ABC, abstractmethod
from pipeline.config import PipelineConfig

class PipelineStage(ABC):
    def __init__(self, config: PipelineConfig):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    def validate(self, input_data: Any) -> bool:
        """Validate input before execution."""
        pass

    @abstractmethod
    def execute(self, input_data: Any) -> Any:
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
            if self.config.enable_cleanup:
                self.cleanup()