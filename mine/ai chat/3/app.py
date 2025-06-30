from flask import Flask, render_template, request, session, redirect, url_for
from dotenv import load_dotenv
import os
import requests

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

headers = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json"
}

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "calgbt_secret")  # Needed for session

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        session["history"] = []
    if "history" not in session:
        session["history"] = []
    output = ""
    user_input = ""
    loading = False
    if request.method == "POST":
        if "clear" in request.form:
            print("[DEBUG] Clear chat triggered")
            session["history"] = []
            return redirect(url_for("index"))
        user_input = request.form.get("inputText", "")
        if not OPENROUTER_API_KEY:
            output = "Error: OPENROUTER_API_KEY not found. Please set it in your .env file."
            session["history"].append({"role": "user", "content": user_input})
            session["history"].append({"role": "assistant", "content": output})
            session.modified = True
            return render_template("index.html", history=session["history"], loading=loading)
        session["history"].append({"role": "user", "content": user_input})
        if len(session["history"]) > 20:
            session["history"] = session["history"][-20:]
        data = {
            "model": "mistralai/mistral-7b-instruct",
            "messages": [
                {"role": "system", "content": "You are calGBT, a helpful AI assistant."},
                *[{"role": m["role"], "content": m["content"]} for m in session["history"]],
            ],
            "max_tokens": 500
        }
        loading = True
        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=data
            )
            if response.status_code == 200:
                result = response.json()
                output = result["choices"][0]["message"]["content"] if "choices" in result else str(result)
            else:
                output = f"Error: {response.status_code} - {response.text}"
        except Exception as e:
            output = f"Error: {str(e)}"
        session["history"].append({"role": "assistant", "content": output})
        if len(session["history"]) > 20:
            session["history"] = session["history"][-20:]
        session.modified = True
        loading = False
    return render_template("index.html", history=session.get("history", []), loading=loading)

if __name__ == "__main__":
    app.run(debug=True)
