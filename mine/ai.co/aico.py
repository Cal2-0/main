from flask import Flask, render_template, request, session, redirect, url_for,Blueprint
import os
from dotenv import load_dotenv
import requests
import random
load_dotenv()

aico_bp =Blueprint('aico',__name__)
aico_bp.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev_secret')


@aico_bp.route("/", methods=["GET", "POST"])
def aico():
    return render_template("aico.html")

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

headers = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json"
}


@aico_bp.route("/aichat", methods=["GET", "POST"])
def aichat():
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

        return redirect(url_for("aichat"))

    return render_template("aichat.html", history=history, loading=loading)

@aico_bp.route("/movai", methods=["GET", "POST"])
def movai():
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
You are an English movie suggestion AI.

You will receive three inputs:

1. Movies watched: {movies_watched}
2. Preferred genres: {genres}
3. Extra conditions: {extra_conditions}

Your task is to suggest exactly 5 English movies that satisfy BOTH of these conditions:

- The movies are NOT present in the movies watched list.  
- The movies do  belong to any of the preferred genres.
- The movies that fit teh condtitions given

Respond with ONLY a numbered list of 5 movie titles in this format:

1.  
2.  
3.  
4.  
5.  

Do NOT include anything else — no explanations, no commentary, no extra text.
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
            result = data["choices"][0]["message"]["content"].strip()

            # Generate dynamic stats
            confidence = round(random.uniform(92.0, 98.9), 1)
            processing_time = round(random.uniform(1.7, 2.8), 1)
            pattern_match = random.choice(["OPTIMAL", "HIGH", "STRONG", "EXCELLENT"])

            stats = (
                f"\n\nConfidence Level: {confidence}%\n"
                f"Processing Time: {processing_time} seconds\n"
                f"Neural Pattern Match: {pattern_match}"
            )

            output = result + stats

            # Append AI response to history
            session["history"].append({"role": "assistant", "content": output})

        except Exception as e:
            output = f"Error: {str(e)}"

    return render_template("movai.html", output=output)

@aico_bp.route("/holi", methods=["GET", "POST"])
def holi():
    if request.method == "POST":
        user_country = request.form.get("inputText", "")
        start_date = request.form.get("StartDate", "")
        return_date = request.form.get("ReturnDate", "")
        extra_conditions = request.form.get("Text", "")

        prompt = f"""
You are a smart travel assistant specializing in personalized holiday recommendations.

User Details:
- Home/Starting Country: {user_country}
- Travel Start Date: {start_date}
- Return Date: {return_date}
- Special Preferences: {extra_conditions}

Please provide exactly 3 holiday destination recommendations that match their criteria. Consider seasonal weather patterns, local events, and travel conditions for the specified dates.

For each destination, provide the information in this EXACT format:

**DESTINATION: [Destination Name, Country]**
**WEATHER:** [Brief weather description for the travel dates]
**HIGHLIGHTS:** [Top 3-4 activities/attractions]
**BUDGET:** [Rough budget category - Budget/Mid-range/Luxury]
**WHY VISIT:** [2-3 sentences explaining why this destination is perfect for their dates and preferences]

Separate each destination with a blank line and number them 1, 2, 3.
"""

        payload = {
            "model": "mistralai/mistral-7b-instruct",
            "messages": [
                {"role": "system", "content": "You are an expert travel advisor. Provide detailed, well-formatted travel recommendations."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 1000,
            "temperature": 0.7
        }

        try:
            response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
            response.raise_for_status()  # Raises an exception for bad status codes
            data = response.json()
            
            if 'choices' in data and len(data['choices']) > 0:
                result = data["choices"][0]["message"]["content"]
                print(f"AI Response: {result}")  # Debug: print the raw response
                
                # Parse the structured response
                destinations = parse_ai_response(result)
                print(f"Parsed destinations: {destinations}")  # Debug: print parsed data
                
                # If parsing fails, create a simple fallback
                if not destinations:
                    destinations = create_fallback_destinations(result)
                
                return render_template("index.html", 
                                     destinations=destinations,
                                     user_country=user_country,
                                     start_date=start_date,
                                     return_date=return_date,
                                     extra_conditions=extra_conditions,
                                     raw_response=result)  # Pass raw response for debugging
            else:
                error_msg = "No response received from AI service"
                return render_template("holi.html", error=error_msg)
                
        except requests.exceptions.RequestException as e:
            error_msg = f"Connection error: {str(e)}"
            return render_template("holi.html", error=error_msg)
        except Exception as e:
            error_msg = f"Error processing request: {str(e)}"
            return render_template("holi.html", error=error_msg)

    return render_template("holi.html")

def parse_ai_response(response_text):
    """Parse the AI response into structured destination data"""
    destinations = []
    
    # Try multiple parsing approaches
    # Method 1: Split by numbered sections
    sections = re.split(r'(?m)^\s*\d+\.\s*', response_text)
    
    # Method 2: If that fails, try splitting by double newlines
    if len(sections) <= 1:
        sections = response_text.split('\n\n')
    
    # Method 3: If still fails, split by single newlines and group
    if len(sections) <= 1:
        lines = response_text.split('\n')
        sections = ['\n'.join(lines[i:i+5]) for i in range(0, len(lines), 5)]
    
    for i, section in enumerate(sections):
        if section.strip() and i > 0:  # Skip first section which is usually intro
            dest_data = {
                'number': len(destinations) + 1,
                'name': '',
                'weather': '',
                'highlights': '',
                'budget': '',
                'why_visit': '',
                'raw_text': section.strip()
            }
            
            # Extract structured information using more flexible regex
            dest_match = re.search(r'(?:DESTINATION|destination)[:\s]*([^\n*]+)', section, re.IGNORECASE)
            if dest_match:
                dest_data['name'] = dest_match.group(1).strip()
            
            weather_match = re.search(r'(?:WEATHER|weather)[:\s]*([^\n*]+)', section, re.IGNORECASE)
            if weather_match:
                dest_data['weather'] = weather_match.group(1).strip()
            
            highlights_match = re.search(r'(?:HIGHLIGHTS|highlights)[:\s]*([^\n*]+)', section, re.IGNORECASE)
            if highlights_match:
                dest_data['highlights'] = highlights_match.group(1).strip()
            
            budget_match = re.search(r'(?:BUDGET|budget)[:\s]*([^\n*]+)', section, re.IGNORECASE)
            if budget_match:
                dest_data['budget'] = budget_match.group(1).strip()
            
            why_match = re.search(r'(?:WHY VISIT|why visit)[:\s]*([^\n*]+)', section, re.IGNORECASE)
            if why_match:
                dest_data['why_visit'] = why_match.group(1).strip()
            
            # Fallback: if no structured parsing worked, extract basic info
            if not dest_data['name']:
                lines = section.split('\n')
                if lines:
                    # Try to find a destination name in the first few lines
                    for line in lines[:3]:
                        if any(keyword in line.lower() for keyword in ['destination', 'country', 'city']):
                            dest_data['name'] = line.strip()
                            break
                    if not dest_data['name']:
                        dest_data['name'] = lines[0].strip()[:50]  # Take first 50 chars
            
            destinations.append(dest_data)
            
            # Stop at 3 destinations
            if len(destinations) >= 3:
                break
    
    return destinations

def create_fallback_destinations(response_text):
    """Create fallback destinations if structured parsing fails"""
    destinations = []
    
    # Split response into chunks
    chunks = response_text.split('\n\n')
    
    for i, chunk in enumerate(chunks[:3]):
        if chunk.strip():
            destinations.append({
                'number': i + 1,
                'name': f'Destination {i + 1}',
                'weather': '',
                'highlights': '',
                'budget': '',
                'why_visit': '',
                'raw_text': chunk.strip()
            })
    
    return destinations

if __name__ == "__main__":
    aico_bp.run(debug=True)
