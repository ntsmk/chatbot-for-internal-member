from flask import Flask, render_template, request, jsonify
from app.chatbot import answer_question_supabase

# todo need to deploy this and make it work on GCP
app = Flask(__name__)

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

    # calling the main chatbot answering function, getting the answer
    response = answer_question_supabase(user_query)

    # returning the answer in json format
    return jsonify({"reply": response})

if __name__ == "__main__":
    app.run(debug=True)