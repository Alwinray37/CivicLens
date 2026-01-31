from fastapi.testclient import TestClient
from main import app
import os

client = TestClient(app)

def test_read_root():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == { "message": "Hello World" }

def test_get_meetings():
    response = client.get("/getMeetings")

    assert response.status_code == 200
    assert response.json() == [
                                {
                                    "Date": "2025-09-12",
                                    "Title": "City Council Meeting",
                                    "VideoURL": "https://youtube.com/watch?v=BKg6FTrMvwE",
                                    "MeetingID": 4
                                },
                                {
                                    "Date": "2025-09-10",
                                    "Title": "City Council Meeting",
                                    "VideoURL": "https://youtube.com/watch?v=BazoAgcwpH0",
                                    "MeetingID": 3
                                },
                                {
                                    "Date": "2025-09-09",
                                    "Title": "City Council Meeting",
                                    "VideoURL": "https://youtube.com/watch?v=V-6JeJxgoEw",
                                    "MeetingID": 2
                                }
                            ]
                        

#testing with MeetingID: 2
def test_get_meeting_info():    
    response = client.get("/getMeetingInfo/2")

    assert response.status_code == 200