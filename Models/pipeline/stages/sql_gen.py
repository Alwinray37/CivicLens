from pipeline.stage import PipelineStage
from utils.json_helper import JsonHelper

class SqlGen(PipelineStage):
    def validate(self, input_data):
        return super().validate(input_data)
    
    def execute(self, intput_data):
        meeting_data = JsonHelper.load_json_data(intput_data)
        
        chunks = meeting_data["chunks"]
        embeddings = meeting_data["embeddings"]

        sql_text = ""

        return super().execute(intput_data)
    
    def cleanup(self):
        pass