import requests
from pipeline.stage import PipelineStage
from pipeline.exceptions import PipelineError

class MeetingFetcher(PipelineStage):
    CITY_COUNCIL_URL = "https://lacity.primegov.com/api/v2/PublicPortal/ListArchivedMeetings"
    COUNCIL_MEETINGS_ID = 1
    NO_SAP = "SAP"
    AGENDA = "Agenda"

    def validate(self, input_data):
        return hasattr(self.config, 'meeting_year') and self.config.meeting_year > 0
    
    def execute(self, intput_data):
        try:
            url = f"{self.CITY_COUNCIL_URL}?year={self.config.meeting_year}"
            response = requests.get(url, timeout=self.config.api_timeout)
            response.raise_for_status()
            
            meetings_data = response.json()
            
            # Filter for council meetings with video and agenda
            council_meetings = [
                meeting for meeting in meetings_data
                if meeting["meetingTypeId"] == self.COUNCIL_MEETINGS_ID
                and self.NO_SAP not in meeting["title"]
                and meeting.get("videoUrl")
                and any(doc["templateName"] == self.AGENDA for doc in meeting.get("documentList", []))
            ]
            
            self.logger.info(f"Found {len(council_meetings)} valid council meetings")
            return council_meetings
            
        except requests.RequestException as e:
            raise PipelineError(f"Failed to fetch meetings: {e}")
    
    def cleanup(self):
        """No cleanup needed for API calls."""
        pass