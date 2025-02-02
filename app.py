import os
from datetime import datetime

import psycopg2

from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

DB_URL = os.getenv("DB_URL")

GET_FEEDBACKS_SQL = """
SELECT username, first_name, text, created_at FROM feedbacks
"""
SAVE_FEEDBACK_SQL = """
INSERT INTO FEEDBACKS (username, first_name, text, created_at) VALUES (%s, %s, %s, %s);
"""

app = Flask(__name__)
CORS(app)

def get_feedbacks():
    conn = psycopg2.connect(DB_URL)
    cursor = conn.cursor()

    cursor.execute(GET_FEEDBACKS_SQL)
    records = cursor.fetchall()

    cursor.close()
    conn.close()

    return list(map(lambda record: {"username": record[0], "first_name": record[1], "text": record[2], "created_at": record[3]}, records))


def save_feedback(data:dict):
    conn = psycopg2.connect(DB_URL)

    cursor = conn.cursor()
    cursor.execute(SAVE_FEEDBACK_SQL, (data["username"], data["first_name"], data["text"], datetime.now()))

    conn.commit()
    cursor.close()
    conn.close()


@app.route("/", methods=["GET"])
def index():
    return "Index Page"


@app.route('/feedbacks', methods=['GET', 'POST'])
def hello_world():
    if request.method == 'GET':
        return jsonify(get_feedbacks())
    elif request.method == 'POST':
        data = request.get_json()
        if not all(k in data for k in ("username", "first_name", "text")):
            return jsonify({"error": "Missing fields"}), 400
        save_feedback(data)
        return jsonify({"status": "success"})


if __name__ == '__main__':
    app.run()
