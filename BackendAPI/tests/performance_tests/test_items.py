from fastapi.testclient import TestClient
from concurrent.futures import ThreadPoolExecutor
from src.main import app
import requests

client = TestClient(app)

URL = "http://civiclens.website/"
NUM_REQUESTS = 50
MAX_TIME_ALLOWED = 0.5


def _assert_avg_response_time(request_fn, num_requests=NUM_REQUESTS, max_time=MAX_TIME_ALLOWED):
    """Run request_fn concurrently and assert the average response time is under max_time."""
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(request_fn, range(num_requests)))

    avg_time = sum(results) / len(results)
    assert avg_time < max_time


def test_main_url_response_time():
    _assert_avg_response_time(lambda _: requests.get(URL).elapsed.total_seconds())

def test_db_response_time():
    _assert_avg_response_time(lambda _: client.get("/dbTestConnection").elapsed.total_seconds())

def test_get_meetings_time():
    _assert_avg_response_time(lambda _: client.get("/getMeetings").elapsed.total_seconds())

# testing with MeetingID: 2
def test_get_meeting_info_time():
    _assert_avg_response_time(lambda _: client.get("/getMeetingInfo/2").elapsed.total_seconds())