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

db_conn_str = os.getenv("DB_CONN")


@app.get("/getMeetings")
def get_meetings():
    try:
        with psycopg.connect(db_conn_str) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                SELECT get_meetings_json();
                """)
                rows = cur.fetchall()
                return {"data": rows}

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
            
            rows = cur.fetchone()
            return rows


# Test and example code: 

# @app.get("/")
# def root():
#     return {"message": "Hello World"}

# @app.get("/items/{item_id}")
# def read_item(item_id: int):
#     return {"item_id": item_id}

@app.get("/test")
def test():
    # Connect to an existing database
    with psycopg.connect(db_conn_str) as conn:

        # Open a cursor to perform database operations
        with conn.cursor() as cur:
            # Execute a command: this creates a new table
            cur.execute("""
                SELECT * FROM public."Meetings"
                    ORDER BY "ID" ASC 
                """)
            
            rows = cur.fetchall()
            return {"data": rows}

            # Pass data to fill a query placeholders and let Psycopg perform
            # the correct conversion (no SQL injections!)
            # cur.execute(
            #     "INSERT INTO test (num, data) VALUES (%s, %s)",
            #     (100, "abc'def"))

            # Query the database and obtain data as Python objects.
            # cur.execute("SELECT * FROM test")
            # print(cur.fetchone())
            # will print (1, 100, "abc'def")

            # You can use `cur.executemany()` to perform an operation in batch
            # cur.executemany(
            #     "INSERT INTO test (num) values (%s)",
            #     [(33,), (66,), (99,)])

            # You can use `cur.fetchmany()`, `cur.fetchall()` to return a list
            # of several records, or even iterate on the cursor
            # cur.execute("SELECT id, num FROM test order by num")
            # for record in cur:
            #     print(record)

            # Make the changes to the database persistent
            conn.commit()