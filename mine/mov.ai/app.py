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
    output = ""
    if "history" not in session:
        session["history"] = []

    if request.method == "POST":
        if request.form.get("clear") == "1":
            session["history"] = []
            return redirect(url_for("index"))

        movies_watched = request.form.get("movie_input", "").strip()
        genres = request.form.get("genres", "").strip()
        extra_conditions = request.form.get("extra", "").strip()

        # Build prompt with user inputs
        prompt = f"""
You are a movie suggestion AI. You will receive three inputs:

1. Movies watched: {movies_watched}
2. Preferred genres: {genres}
3. Extra conditions: {extra_conditions}

Using this information, suggest exactly 5 movies that fit the criteria. Provide only a numbered list of movie titles, like this:

1.
2.
3.
4.
5.

Do not include any explanations, descriptions, or additional text—just the list.
"""
        # Update session history with user prompt
        session["history"].append({"role": "user", "content": prompt})

        messages = [
            {"role": "system", "content": "You are Mov.ai, a helpful movie suggestions assistant."}
        ] + session["history"]

        payload = {
            "model": "mistralai/mistral-7b-instruct",
            "messages": messages,
            "max_tokens": 500
        }

        try:
            response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
            data = response.json()
            result = data["choices"][0]["message"]["content"]

            # Append AI response to history
            session["history"].append({"role": "assistant", "content": result})

            output = result

        except Exception as e:
            output = f"Error: {str(e)}"

    return render_template("index.html", output=output)

if __name__ == "__main__":
    app.run(debug=True)
