from flask import Flask, render_template, request, jsonify
from app.chatbot import answer_question_supabase
import os
import json
import logging

app = Flask(__name__)

# changed print() to built-in logging
logging.basicConfig(level=logging.INFO)
logging.info({
    "event": "service_started",
    "component": "chatbot-service"
})

@app.route("/")
def index():
    return render_template("index.html")

# this is called in script.js
@app.route("/ask", methods=["POST"])
def ask():

    # getting user input raw data as json
    data = request.get_json()

    # separating the message and getting actual user input data
    user_query = data.get("message", "")

    # # test for logging error
    # raise Exception("alert setup test")

    # changed print() to built-in logging
    logging.info({
        "event": "question_received",
        "endpoint": "/ask",
        "query_length": len(user_query)
    })

    try:
        # calling the main chatbot answering function, getting the answer
        response = answer_question_supabase(user_query)

        # returning the answer in json format
        return jsonify({"reply": response})

    except Exception as e:
        logging.exception({
            "event": "question_failed",
            "endpoint": "/ask",
            "error_type": type(e).__name__
        })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)