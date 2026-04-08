from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import psycopg
import os

from slowapi.errors import RateLimitExceeded

from src.chatbot_service import ChatbotException, ChatbotService
from src.models import MeetingsData, MeetingInfo
from src.models.meeting_models import ChatResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.middleware import SlowAPIASGIMiddleware
from slowapi.util import get_remote_address


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

chatbot_limit_strat = os.getenv("CHATBOT_LIMIT_STRAT")

match chatbot_limit_strat:
    case "IP":
        chatbot_limit_strat_fn = get_remote_address
    case _:
        # global rate limit
        chatbot_limit_strat_fn = lambda: "global"

chatbot_limit = os.getenv("CHATBOT_LIMIT") or "5/minute"


limiter = Limiter(key_func=chatbot_limit_strat_fn)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIASGIMiddleware)



db_conn_str = os.getenv("DB_CONN") or ""

ollama_conn_str = os.getenv("OLLAMA_CONN") or "http://localhost:11434"

if not db_conn_str:
    db_password = os.getenv("DB_PASSWORD", "")
    db_conn_str = f"host=db dbname=postgres user=postgres password={db_password}"

split_index = db_conn_str.find(':')
db_pgv_conn_str = db_conn_str[0:split_index] + "+asyncpg" + db_conn_str[split_index:]

answer_model = os.getenv("ANSWER_MODEL") or "smollm:135m"
embedding_model = os.getenv("EMBED_MODEL") or "all-minilm:22m"
chat_service = ChatbotService.create(db_url=db_pgv_conn_str, 
                                   answer_model=answer_model, 
                                   table_name="MeetingChunks", 
                                   embedding_model=embedding_model,
                                   ollama_url=ollama_conn_str,
                                   )

@app.get("/")
def root():
    return {"message": "Hello World"}

@app.get("/dbTestConnection")
def db_test_connection():
    try:
        with psycopg.connect(db_conn_str) as conn:
            return {"message": "Connection okay"} 
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"\nUnexpected error: {str(e)}")

@app.get("/getMeetings", response_model=MeetingsData, response_model_by_alias=True)
def get_meetings():
    try:
        with psycopg.connect(db_conn_str) as conn:
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
def getMeetingInfo(meeting_id: int):
    try:
        with psycopg.connect(db_conn_str) as conn:
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

    return res[0]


# request param is needed for slowapi limiter
@app.get("/chat/{meeting_id}", response_model=ChatResponse)
@limiter.limit(chatbot_limit)
def chat(request: Request, meeting_id: int, query: str):
    try:
        ans = chat_service.answer(query, meeting_id)
        if not isinstance(ans, str):
            raise Exception("Response in incorrect format")
        return ChatResponse(Response=ans)

    except ChatbotException as e:
        raise HTTPException(status_code=e.status_code, detail=e)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

