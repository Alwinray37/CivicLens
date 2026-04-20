from fastapi.testclient import TestClient
from src.main import app

from src.models import MeetingsData, MeetingInfo

client = TestClient(app)


def test_read_root():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == { "message": "Hello World" }

def test_db_conn():
    response = client.get("/dbTestConnection")

    assert response.status_code == 200
    assert response.json() == {"message": "Connection okay"}

def test_get_meetings():
    response = client.get("/getMeetings")
    
    assert response.status_code == 200
    MeetingsData.model_validate(response.json())

#testing with MeetingID: 2
def test_get_meeting_info():    
    response = client.get("/getMeetingInfo/2")

    assert response.status_code == 200
    MeetingInfo.model_validate(response.json())