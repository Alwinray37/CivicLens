import os
from utils.json_helper import JsonHelper
from pipeline.stage import PipelineStage

REQUIRED_CHUNK_KEYS = {"StartTime", "Title", "Summary"}

class ChunkGen(PipelineStage):
    def validate(self, input_data):
        if not isinstance(input_data, str):
            self.logger.error(f"input_data must be a file path string, got {type(input_data)}")
            return False

        if not input_data.endswith('.json'):
            self.logger.error(f"input_data must be a .json file, got: {input_data}")
            return False

        if not os.path.isfile(input_data):
            self.logger.error(f"File does not exist: {input_data}")
            return False

        data = JsonHelper.load_json_data(input_data)
        if data is None:
            self.logger.error(f"Failed to load JSON from: {input_data}")
            return False

        if not isinstance(data, list):
            self.logger.error(f"JSON root must be a list, got {type(data)}")
            return False

        if len(data) == 0:
            self.logger.error("JSON chunk list is empty")
            return False

        for i, item in enumerate(data):
            if not isinstance(item, dict):
                self.logger.error(f"Item [{i}] must be a dict, got {type(item)}")
                return False

            missing = REQUIRED_CHUNK_KEYS - item.keys()
            if missing:
                self.logger.error(f"Item [{i}] is missing required keys: {missing}")
                return False

            for key in REQUIRED_CHUNK_KEYS:
                if not isinstance(item[key], str):
                    self.logger.error(f"Item [{i}]['{key}'] must be a string, got {type(item[key])}")
                    return False

        return True
    
    def execute(self, intput_data):
        data = JsonHelper.load_json_data(intput_data)

        raise NotImplementedError()
    
    def cleanup(self):
        pass