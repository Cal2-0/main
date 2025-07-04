from flask import Flask, render_template, request, session, redirect, url_for
import os
from dotenv import load_dotenv
import requests
load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")



headers = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json"
}


app = Flask(__name__, template_folder=os.path.dirname(os.path.abspath(__file__)))
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev_secret')

@app.route("/", methods=["GET", "POST"])
def index():
    if "history" not in session:
        session["history"] = []
    history = session["history"]
    loading = False

    if request.method == "POST":
        if request.form.get("clear") == "1":
            session["history"] = []
            return redirect(url_for("index"))

        user_input = request.form.get("inputText", "")
        if user_input.strip():
            # Add user message to history
            history.append({"role": "user", "content": user_input})
            session["history"] = history
            # Prepare messages for API (system + history)
            messages = [
                {"role": "system", "content": "You are calGBT, a helpful AI assistant."}
            ] + history
            payload = {
                "model": "mistralai/mistral-7b-instruct",
                "messages": messages,
                "max_tokens": 500
            }
            try:
                loading = True
                response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
                data = response.json()
                result = data["choices"][0]["message"]["content"]
                # Add assistant message to history
                history.append({"role": "assistant", "content": result})
                session["history"] = history
                loading = False
            except Exception as e:
                error_msg = f"Error: {str(e)}\nFull response: {data if 'data' in locals() else 'No data'}"
                history.append({"role": "assistant", "content": error_msg})
                session["history"] = history
                loading = False

        return redirect(url_for("index"))

    return render_template("index.html", history=history, loading=loading)

if __name__ == "__main__":
    app.run(debug=True)
