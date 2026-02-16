from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import psycopg
import os

from src.chatbot_service import ChatbotService
from src.models import MeetingsData, MeetingInfo
from src.models.meeting_models import ChatResponse

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

db_conn_str = os.getenv("DB_CONN") or ""
db_pgv_conn_str = os.getenv("DB_PGV_CONN") or ""
ollam_conn_str = os.getenv("OLLAMA_CONN") or ""

chat_service = ChatbotService.create(db_url=db_pgv_conn_str, 
                                   answer_model="llama3.1:8b", 
                                   table_name="MeetingChunks", 
                                   embedding_model="qwen3-embedding:4b",
                                   ollama_url=ollam_conn_str,
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

@app.get("/getMeetings", response_model=MeetingsData)
def get_meetings():
    try:
        with psycopg.connect(db_conn_str) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                SELECT get_meetings_json();
                """)
                res = cur.fetchone() or None
        if res is None:
            raise HTTPException(status_code=404, detail="No meetings found")  
                    
        return { "meetings": res[0] }

    except psycopg.OperationalError as e:
        raise HTTPException(status_code=503, detail=f"Database connection failed: {e.pgerror or str(e)}`")

    except psycopg.ProgrammingError as e:
        raise HTTPException(status_code=400, detail=f"SQL error: {e.pgerror or str(e)}")

    except psycopg.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e.pgerror or str(e)}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@app.get("/getMeetingInfo/{meeting_id}", response_model=MeetingInfo)
def getMeetingInfo(meeting_id: int):
    try:
        with psycopg.connect(db_conn_str) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT get_meeting_json(%s);
                    """,
                    (meeting_id,))
                
                res = cur.fetchone() or None

        if res is None:
            raise HTTPException(status_code=404, detail="No meetings found")  

        return res[0]

    except psycopg.OperationalError as e:
        raise HTTPException(status_code=503, detail=f"Database connection failed: {e.pgerror or str(e)}`")

    except psycopg.ProgrammingError as e:
        raise HTTPException(status_code=400, detail=f"SQL error: {e.pgerror or str(e)}")

    except psycopg.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e.pgerror or str(e)}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@app.get("/chat/{meeting_id}", response_model=ChatResponse)
def chat(meeting_id: int, query: str):
    try:
        ans = chat_service.answer(query, meeting_id)
        if not isinstance(ans, str):
            raise Exception("Response in incorrect format")
        return ChatResponse(Response=ans)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

