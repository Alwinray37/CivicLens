
import os
import json
from pathlib import Path
from pipeline.stage import PipelineStage
from pipeline.exceptions import PipelineError
from utils.meeting_summary import MeetingSummary
from utils.json_helper import JsonHelper

class SummaryGen(PipelineStage):
    def validate(self, input_data):
        """Validate that input_data is a dictionary with the required structure."""
        if not isinstance(input_data, dict):
            self.logger.error(f"input_data must be a dictionary, got {type(input_data)}")
            return False
        
        if "files" not in input_data:
            self.logger.error("input_data must contain 'files' key")
            return False
        
        if not isinstance(input_data["files"], list):
            self.logger.error(f"'files' must be a list, got {type(input_data['files'])}")
            return False
        
        if len(input_data["files"]) != 2:
            self.logger.error(f"'files' list must contain exactly 2 items, got {len(input_data['files'])}")
            return False
        
        # Validate each file in the files list
        for i, file_path in enumerate(input_data["files"]):
            if not isinstance(file_path, str):
                self.logger.error(f"files[{i}] must be a string, got {type(file_path)}")
                return False
            
            if not file_path.endswith('.json'):
                self.logger.error(f"files[{i}] must have .json extension, got {file_path}")
                return False
            
            if not os.path.isfile(file_path):
                self.logger.error(f"File does not exist: {file_path}")
                return False
            
            # Try to parse the JSON file to ensure it's valid
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    json.load(f)
            except json.JSONDecodeError as e:
                self.logger.error(f"File is not valid JSON: {file_path}. Error: {e}")
                return False
            except Exception as e:
                self.logger.error(f"Error reading file {file_path}: {e}")
                return False
        
        # Check if "options" key exists and is a dictionary
        if "options" not in input_data:
            self.logger.error("input_data must contain 'options' key")
            return False
        
        if not isinstance(input_data["options"], dict):
            self.logger.error(f"'options' must be a dictionary, got {type(input_data['options'])}")
            return False
        
        # Validate required keys in options
        required_options = {"lines_per_chunk", "overlap", "max_query"}
        if not required_options.issubset(input_data["options"].keys()):
            missing = required_options - set(input_data["options"].keys())
            self.logger.error(f"'options' is missing required keys: {missing}")
            return False
        
        # Validate option values are integers
        for key in required_options:
            if not isinstance(input_data["options"][key], int):
                self.logger.error(f"'options[{key}]' must be an integer, got {type(input_data['options'][key])}")
                return False
        
        return True
    
    def execute(self, intput_data):
        summary_file, agenda_file = intput_data["files"][0], intput_data["files"][1]

        agenda_dic = JsonHelper.load_json_data(agenda_file)

        meeting_sum = MeetingSummary(meeting_json_path=summary_file,
                                    chunk_sum_model=MeetingSummary.summary_models["llama-8b"], 
                                    fin_select_model=MeetingSummary.summary_models["llama-8b"],
                                    emb_model=MeetingSummary.embedding_models["qwen-4b"])
        
        meeting_sum.chunk_opts = {
            'method': 'fixed',
            'delim': '\n',
            'lines_per_chunk': intput_data["options"]["lines_per_chunk"],
            'overlap': intput_data["options"]["overlap"],
        }
        
        filter_list = ['Policy', 'Civic', 'Voting']
        filter_list = list(map(lambda a: a['title'], agenda_dic['items']))
        additional_filters = ['Policy', 'Civic', 'Voting']
        filter_list.extend(additional_filters)
        important_events = meeting_sum.gen_important_events_by_query(filter_list=filter_list, 
                                                                     max_query=intput_data["options"]["max_query"])

        summary_file = Path(summary_file)
        summary_file.stem += "Summary"
        s_path = str(summary_file)

        JsonHelper.write_json_data(s_path, important_events)

        return s_path
    
    def cleanup(self):
        return super().cleanup()