import requests
from pipeline.exceptions import PipelineError

from pipeline.stage import PipelineStage

class PdfDownloader(PipelineStage):
    AGENDA = "Agenda"
  
    def validate(self, input_data):
        matching_docs = [d for d in input_data["documentList"] if d["templateName"] == self.AGENDA]

        if not matching_docs:
            return False
        
        return True
    
    def execute(self, intput_data):

        agendaInfo = [d for d in intput_data["documentList"] if d["templateName"] == self.AGENDA][0]

        templateId = agendaInfo["templateId"]
        compileOutputType = agendaInfo["compileOutputType"]

        agenda_path = self.config.temp_dir / f"agenda_{intput_data['id']}.pdf"
        
        AGENDA_URL = f"https://lacity.primegov.com/Public/CompiledDocument?meetingTemplateId={templateId}&compileOutputType={compileOutputType}"

        try:
            response = requests.get(AGENDA_URL, stream=True, timeout=self.config.api_timeout)

            response.raise_for_status()

            with open(agenda_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            return agenda_path
        except Exception as e:
            raise PipelineError(f"Failed to fetch agenda PDF: {e}")
    
    def cleanup(self):
        """No cleanup needed for API calls."""
        pass