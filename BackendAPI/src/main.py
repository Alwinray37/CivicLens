from typing import cast
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import psycopg

from redisvl.extensions.message_history.schema import ChatMessage
from slowapi.errors import RateLimitExceeded
from starlette.types import HTTPExceptionHandler

from src.chat_history import cached_messages_to_responses
from src.chatbot_service import ChatbotException
from src.models import MeetingsData, MeetingInfo
from src.models.meeting_models import ChatResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.middleware import SlowAPIASGIMiddleware

from config_env import env
from middleware import SessionIdMiddleware

app = FastAPI()


app.add_middleware(SessionIdMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.state.limiter = env.limiter
limit_exceeded_handler = cast(HTTPExceptionHandler, _rate_limit_exceeded_handler)
app.add_exception_handler(RateLimitExceeded, limit_exceeded_handler)
app.add_middleware(SlowAPIASGIMiddleware)


@app.get("/")
def root():
    return {"message": "Hello World"}

@app.get("/dbTestConnection")
def db_test_connection():
    try:
        with psycopg.connect(env.db_conn) as conn:
            return {"message": "Connection okay"} 
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"\nUnexpected error: {str(e)}")

@app.get("/getMeetings", response_model=MeetingsData, response_model_by_alias=True)
def get_meetings():
    try:
        with psycopg.connect(env.db_conn) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                SELECT get_meetings_json();
                """)
                res = cur.fetchone() or None

    except psycopg.OperationalError as e:
        raise HTTPException(status_code=503, detail=f"Database connection failed: {str(e)}")

    except psycopg.ProgrammingError as e:
        raise HTTPException(status_code=400, detail=f"SQL error: {str(e)}")

    except psycopg.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    if res is None:
        raise HTTPException(status_code=404, detail="No meetings found")  
                
    return { "meetings": res[0] }


@app.get("/getMeetingInfo/{meeting_id}", response_model=MeetingInfo, response_model_by_alias=True)
def getMeetingInfo(request: Request, meeting_id: int):
    try:
        session_id = request.scope.get('session_id')
        assert type(session_id) is str
        chat_messages = env.chat_service.chat_history.get_meeting_session_messages(meeting_id, session_id)
        chat_messages = cast(list[dict[str, str]], chat_messages)
        chat_messages = cached_messages_to_responses(chat_messages)
        with psycopg.connect(env.db_conn) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT get_meeting_json(%s);
                    """,
                    (meeting_id,))
                
                res = cur.fetchone() or None

    except psycopg.OperationalError as e:
        raise HTTPException(status_code=503, detail=f"Database connection failed: {str(e)}")

    except psycopg.ProgrammingError as e:
        raise HTTPException(status_code=400, detail=f"SQL error: {str(e)}")

    except psycopg.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    if res is None:
        raise HTTPException(status_code=404, detail="No meetings found")  

    return {
            **res[0],
            'chat_history': chat_messages,
            }


# request param is needed for slowapi limiter
@app.get("/chat/{meeting_id}", response_model=ChatResponse)
@env.limiter.limit(env.limit)
def chat(request: Request, meeting_id: int, query: str):
    session_id = request.scope.get('session_id')
    assert type(session_id) is str

    try:
        ans = env.chat_service.answer(query, meeting_id, session_id=session_id)
        if not isinstance(ans, str):
            raise Exception("Response in incorrect format")

        return ChatResponse(Response=ans, Type="incoming")

    except ChatbotException as e:
        raise HTTPException(status_code=e.status_code, detail=e)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

