import json
import os

from quart import Quart, request, render_template
import psycopg2
from urllib.parse import urlparse

from helpers.copyleaks import Copyleaks, Products
from helpers.get_urls import get_urls
from helpers.run_checks import process_checks

app = Quart(__name__)

EMAIL_ADDRESS = os.environ.get("CL_EMAIL_ADDRESS")
KEY = os.environ.get("CL_KEY")

DATABASE_URL = os.environ.get("DATABASE_URL")
app.secret_key = os.environ.get("SECRET_KEY")


def get_connection():

    conn = psycopg2.connect(DATABASE_URL)
    return conn


async def store_data(parent, uuid, repo, url, filename, score, internet, database):

    conn = get_connection()
    cur = conn.cursor()

    sql_string = 'INSERT INTO repos (parent_id, scan_id, repo, url, filename, internet, database, score) VALUES(%s, %s, %s, %s, %s, %s, %s, %s);'
    values_tuple = (parent, uuid, repo, url, filename, internet, database, score)

    cur.execute(sql_string, values_tuple)

    conn.commit()
    conn.close()
    cur.close()


def get_report(parent_id):

    conn = get_connection()
    cur = conn.cursor()

    sql_string = "SELECT * FROM repos WHERE parent_id = %s ORDER BY score DESC;"
    values_tuple = (parent_id,)

    cur.execute(sql_string, values_tuple)

    report = cur.fetchall()

    rs = {}

    for r in report:
        rs[r[0]] = {}
        rs[r[0]]["parent_id"] = r[1].strip()
        rs[r[0]]["repo"] = r[2].strip()
        rs[r[0]]["filename"] = r[3].strip()
        rs[r[0]]["url"] = r[4].strip()
        rs[r[0]]["internet"] = r[5]
        rs[r[0]]["databases"] = r[6]
        rs[r[0]]["scan_id"] = r[7].strip()
        rs[r[0]]["score"] = r[8]

    conn.close()
    cur.close()

    return rs if rs else None


@app.route("/")
async def index():

    return await render_template("index.html")


@app.route("/submit", methods=["POST"])
async def submit():

    auth_token = Copyleaks.login(EMAIL_ADDRESS, KEY)

    repo = await request.form

    base_url = urlparse(request.base_url)

    parent_id = process_checks(repo["repo"], get_urls(repo["repo"]), auth_token, base_url.hostname)

    return await render_template("ok.html", parent=parent_id)


@app.route("/scans/<string:uuid>", methods=["POST"])
async def scans(uuid):

    data = await request.data
    result = json.loads(data)
    scan_id = result["scannedDocument"]["scanId"]

    if "metadata" in result["scannedDocument"]:

        metadata = result["scannedDocument"]["metadata"]
        filename = metadata["filename"] if "filename" in metadata else "no_file"
        url = metadata["finalUrl"] if "finalUrl" in metadata else "no_url"

        score = result["results"]["score"]["aggregatedScore"] or 0.0
        payload = result["developerPayload"].split(":") if result["developerPayload"] else ["repo_error", "0"]
        repo = payload[0]
        parent = payload[1]
        internet = json.dumps(result["results"]["internet"]) or ""
        database = json.dumps(result["results"]["database"]) or ""
        await store_data(parent, uuid, repo, url, filename, score, internet, database)
        print(f"Stored: {uuid}, {filename}, {score}")
    
    return await request.data


@app.route("/report/<string:uuid>")
async def report(uuid):

    report = get_report(uuid)

    repo = list(report.values())[0]["repo"]
    parent_id = list(report.values())[0]["parent_id"]

    return await render_template("report.html", content=report, repo=repo, parent_id=parent_id)


if __name__ == "__main__":
    app.run(host=os.getenv("IP", "0.0.0.0"), port=int(
        os.getenv("PORT", "5000")), debug=False)