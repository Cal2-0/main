import re
from flask import Flask, render_template, request
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

@app.route("/", methods=["GET", "POST"])
def index():
    parts = []

    if request.method == "POST":
        user_country = request.form.get("inputText", "")
        start_date = request.form.get("StartDate", "")
        return_date = request.form.get("ReturnDate", "")
        extra_conditions = request.form.get("Text", "")

        prompt = f"""
You are a smart travel assistant.

A user will provide you with:

- Their home country or preferred starting country: {user_country}
- A start date for their holiday: {start_date}
- A return date: {return_date}
- And any extra conditions or preferences: {extra_conditions}

When suggesting destinations, take into account the season and hemisphere differences based on the dates and location.

Recommend destinations where the weather is likely to be favorable for travel during the requested dates, unless the user specifically asks for winter or cold weather holidays.

Using this information, generate a clear, engaging, and well-organized list of the top 3 holiday destinations that fit their criteria.
For each destination, provide:
1. Destination name and country,
2. Why it’s a great choice considering popularity, weather during the requested dates, affordability, and fun activities,

Please format your response as a numbered list with clear headings for each destination.

Use line breaks, bullet points or sub-headings for:

- Destination name and country
- Why it’s a great choice

Make the response easy to read with blank lines separating each destination.
"""

        payload = {
            "model": "mistralai/mistral-7b-instruct",
            "messages": [
                {"role": "system", "content": "You are calGBT, a helpful AI assistant."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 700
        }

        try:
            response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
            data = response.json()
            result = data["choices"][0]["message"]["content"]

            # Remove leading numbering (like "1. ", "2. ") from paragraphs or lines
            cleaned = re.sub(r'(?m)^\s*\d+\.\s*', '', result)

            # Split result into parts (optional - just for formatting in template)
            parts = [part.strip() for part in cleaned.split("\n\n") if part.strip()]

        except Exception as e:
            parts = [f"Error: {str(e)}"]

    return render_template("index.html", parts=parts)

if __name__ == "__main__":
    app.run(debug=True)
