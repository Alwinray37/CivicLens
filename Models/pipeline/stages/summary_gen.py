
from pipeline.stage import PipelineStage
from pipeline.exceptions import PipelineError
from utils.meeting_summary import MeetingSummary

class SummaryGen(PipelineStage):
    def validate(self, input_data):
        return super().validate(input_data)
    
    def execute(self, intput_data):
        return super().execute(intput_data)
    def cleanup(self):
        return super().cleanup()