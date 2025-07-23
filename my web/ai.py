from flask import Flask, render_template, request, session, redirect, url_for,Blueprint
import os
from dotenv import load_dotenv
import requests
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

ai_bp = Blueprint('ai',__name__)
ai_bp.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev_secret')

@ai_bp.route("/ai", methods=["GET", "POST"])
def ai():
    if "history" not in session:
        session["history"] = []
    history = session["history"]
    loading = False

    if request.method == "POST":
        if request.form.get("clear") == "1":
            session["history"] = []
            return redirect(url_for("ai.ai"))

        user_input = request.form.get("inputText", "")
        if user_input.strip():
            # Add user message to history
            history.append({"role": "user", "content": user_input})
            session["history"] = history
            # Gemini API expects a specific payload
            gemini_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
            gemini_headers = {
                "Content-Type": "application/json",
                "X-goog-api-key": GEMINI_API_KEY
            }
            gemini_data = {
                "contents": [
                    {
                        "parts": [
                            {"text": user_input}
                        ]
                    }
                ]
            }
            try:
                loading = True
                response = requests.post(gemini_url, headers=gemini_headers, json=gemini_data)
                data = response.json()
                # Gemini's response structure
                result = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "[No response]")
                history.append({"role": "assistant", "content": result})
                session["history"] = history
                loading = False
            except Exception as e:
                error_msg = f"Error: {str(e)}\nFull response: {data if 'data' in locals() else 'No data'}"
                history.append({"role": "assistant", "content": error_msg})
                session["history"] = history
                loading = False

        return redirect(url_for("ai.ai"))

    return render_template("ai.html", history=history, loading=loading)

if __name__ == "__main__":
    ai_bp.run(debug=True)
