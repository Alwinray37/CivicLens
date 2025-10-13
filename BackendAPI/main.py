from fastapi import FastAPI
import psycopg

app = FastAPI()




@app.get("/getMeetings")
def getMeetings():
    # Connect to an existing database
    with psycopg.connect("dbname=CivicLensDB user=postgres password=postgres") as conn:

        # Open a cursor to perform database operations
        with conn.cursor() as cur:
            breakpoint()
            # Execute a command: this creates a new table
            cur.execute("""
                SELECT * FROM public."Meetings"
                    ORDER BY "ID" ASC 
                """)
            
            rows = cur.fetchall()
            return {"data": rows}


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
    with psycopg.connect("dbname=CivicLensDB user=postgres password=postgres") as conn:

        # Open a cursor to perform database operations
        with conn.cursor() as cur:
            breakpoint()
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