from pathlib import Path
from pipeline.stage import PipelineStage
from pipeline.exceptions import PipelineError
from utils.json_helper import JsonHelper

class CombineMeetingData(PipelineStage):
    def validate(self, input_data):
        if not isinstance(input_data, dict):
            raise PipelineError("meeting_info must be a dictionary")

        required_keys = ["summary_file", "agenda_file", "chunk_file", "meeting"]
        missing_keys = [key for key in required_keys if key not in input_data]
        if missing_keys:
            raise PipelineError(f"Missing required keys in meeting_info: {missing_keys}")

        for key in ["summary_file", "agenda_file", "chunk_file"]:
            value = input_data[key]
            if not isinstance(value, (str, Path)):
                raise PipelineError(f"{key} must be a file path string or Path")

            path_value = Path(value)
            if not str(path_value).strip():
                raise PipelineError(f"{key} cannot be empty")

        meeting = input_data["meeting"]
        if not isinstance(meeting, dict):
            raise PipelineError("meeting must be a dictionary")

        for field in ["dateTime", "videoUrl"]:
            if field not in meeting:
                raise PipelineError(f"meeting must include '{field}'")
            if not isinstance(meeting[field], str) or not meeting[field].strip():
                raise PipelineError(f"meeting['{field}'] must be a non-empty string")

        return True
    
    def execute(self, intput_data):
        agenda_items = JsonHelper.load_json_data(intput_data["agenda_file"])
        summaries = JsonHelper.load_json_data(intput_data["summary_file"])
        chunk_data = JsonHelper.load_json_data(intput_data["chunk_file"])

        meeting_data = {
            "title": "City Council Meeting",
            "date": intput_data["meeting"]["dateTime"][:10],
            "video_url": intput_data["meeting"]["videoUrl"],
            "agenda_items": agenda_items,
            "summaries": summaries,
            "chunk_data": chunk_data["chunks_embeddings"],
        }

        output_path = str(Path(self.config.temp_dir / f"Final_{meeting_data['date']}_data.json"))

        JsonHelper.write_json_data(output_path, meeting_data)

        return output_path
    
    def cleanup(self):
        pass