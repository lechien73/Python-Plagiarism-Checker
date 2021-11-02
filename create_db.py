import os
import psycopg2
import env

DATABASE_URL = os.environ.get("DATABASE_URL")

try:
    conn = psycopg2.connect(DATABASE_URL)
except:
    print("I am unable to connect to the database") 

cur = conn.cursor()
try:
    cur.execute("DROP TABLE repos;")
    cur.execute("CREATE TABLE repos (repo_id SERIAL PRIMARY KEY, parent_id CHAR(100), repo CHAR(100), filename CHAR(100), url CHAR(200), internet json, database json, scan_id CHAR(100), score FLOAT);")
except:
    print("I can't create it!")

conn.commit()
conn.close()
cur.close()