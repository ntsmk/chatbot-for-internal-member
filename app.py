from flask import Flask, render_template, request, jsonify
from app.chatbot import answer_question_supabase
import os
import json

app = Flask(__name__)

# tried google.cloud.logging.Client() but it did not work so using print() instead, print() is enough
print(json.dumps({
    "event": "service_started",
    "component": "chatbot-service"
}), flush=True) # meaning "Write this to stdout immediately"

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

    # Adding logging
    print(json.dumps({
        "event": "question_received",
        "endpoint": "/ask",
        "query_length": len(user_query)
    }), flush=True)

    # calling the main chatbot answering function, getting the answer
    response = answer_question_supabase(user_query)

    # returning the answer in json format
    return jsonify({"reply": response})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)