from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import psycopg
import os

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

db_conn_str = os.getenv("DB_CONN") or ""


@app.get("/getMeetings")
def get_meetings():
    try:
        with psycopg.connect(db_conn_str) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                SELECT get_meetings_json();
                """)
                res = cur.fetchone() or []
                rows = res[0]
                return rows

    except psycopg.OperationalError as e:
        raise HTTPException(status_code=503, detail=f"Database connection failed: {e.pgerror or str(e)}`")

    except psycopg.ProgrammingError as e:
        raise HTTPException(status_code=400, detail=f"SQL error: {e.pgerror or str(e)}")

    except psycopg.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e.pgerror or str(e)}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@app.get("/getMeetingInfo/{meeting_id}")
def getMeetingInfo(meeting_id: int):
    # Connect to an existing database
    with psycopg.connect(db_conn_str) as conn:

        # Open a cursor to perform database operations
        with conn.cursor() as cur:
            # Execute a command: this creates a new table
            cur.execute("""
                SELECT get_meeting_json(%s);
                """,
                (meeting_id,))
            
            res = cur.fetchone() or []
            return res[0]

@app.get("/")
def root():
    return {"message": "Hello World"}