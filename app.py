from flask import Flask, render_template, request, jsonify
import datetime, os, re, time, random
import requests

# =========================
# APP CONFIG
# =========================
app = Flask(__name__)

# =========================
# GLOBAL CONTEXT MEMORY 🧠
# =========================
assistant_state = {
    "current_site": None,
    "last_search": None,
    "youtube_playing": False,
    "listening": True,
    "notes": [],
    "wake_active": True
}

# =========================
# TEXT CLEANING
# =========================
def clean_text(text):
    return re.sub(r"[^a-z0-9\s]", "", text.lower())

# =========================
# INTENT DETECTION
# =========================
def detect_intent(text):
    if text.startswith("open"): return "open"
    if text.startswith("search"): return "search"
    if text.startswith("play"): return "play"
    if "pause" in text: return "pause"
    if "resume" in text: return "resume"
    if "next" in text: return "next"
    if "open first" in text or "play first" in text: return "open_first"
    if "time" in text: return "time"
    if "date" in text: return "date"
    if any(x in text for x in ["+", "-", "*", "/"]): return "math"
    if "joke" in text: return "joke"
    if "stop listening" in text: return "stop"
    return "unknown"

# =========================
# ENTITY EXTRACTION
# =========================
def extract_entity(text):
    apps = [
        "youtube", "google", "gmail", "github",
        "spotify", "amazon", "flipkart",
        "instagram", "facebook", "twitter",
        "linkedin", "netflix", "whatsapp web"
    ]
    for app in apps:
        if app in text:
            return app
    return None

# =========================
# LOCAL OLLAMA AI
# =========================
def ask_ollama(prompt):
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "llama3", "prompt": prompt, "stream": False},
            timeout=30
        )
        return response.json().get("response", "")
    except:
        return "Local AI is not running."

# =========================
# ROUTES
# =========================
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/command", methods=["POST"])
def command():
    if not assistant_state["listening"]:
        return jsonify({"reply": "Assistant stopped."})

    raw = request.json["text"]
    text = clean_text(raw)
    intent = detect_intent(text)
    entity = extract_entity(text)

    websites = {
        "youtube": "https://youtube.com",
        "google": "https://google.com",
        "gmail": "https://mail.google.com",
        "github": "https://github.com",
        "spotify": "https://open.spotify.com",
        "amazon": "https://amazon.in",
        "flipkart": "https://flipkart.com",
        "instagram": "https://instagram.com",
        "facebook": "https://facebook.com",
        "twitter": "https://twitter.com",
        "linkedin": "https://linkedin.com",
        "netflix": "https://netflix.com",
        "whatsapp web": "https://web.whatsapp.com"
    }

    # =========================
    # OPEN
    # =========================
    if intent == "open" and entity:
        assistant_state["current_site"] = entity
        return jsonify({
            "reply": f"{entity} opened.",
            "url": websites.get(entity)
        })

    # =========================
    # SEARCH
    # =========================
    if intent == "search":
        query = text.replace("search", "").strip()
        assistant_state["last_search"] = query

        if assistant_state["current_site"] == "youtube":
            return jsonify({
                "reply": f"Searching {query} on YouTube.",
                "url": f"https://www.youtube.com/results?search_query={query}"
            })

        assistant_state["current_site"] = "google"
        return jsonify({
            "reply": f"Searching {query} on Google.",
            "url": f"https://google.com/search?q={query}"
        })

    # =========================
    # PLAY (WEB SAFE)
    # =========================
    if intent == "play":
        query = text.replace("play", "").strip()
        assistant_state["current_site"] = "youtube"
        assistant_state["youtube_playing"] = True

        return jsonify({
            "reply": f"Playing {query} on YouTube.",
            "url": f"https://www.youtube.com/results?search_query={query}"
        })

    # =========================
    # BASIC FEATURES
    # =========================
    if intent == "time":
        return jsonify({"reply": datetime.datetime.now().strftime("%I:%M %p")})

    if intent == "date":
        return jsonify({"reply": datetime.date.today().strftime("%d %B %Y")})

    if intent == "joke":
        return jsonify({"reply": random.choice([
            "Why do programmers hate nature? Too many bugs 😄",
            "AI won’t take your job, bad code will 😅"
        ])})

    if intent == "stop":
        assistant_state["listening"] = False
        return jsonify({"reply": "Assistant stopped listening."})

    ai_reply = ask_ollama(raw)
    return jsonify({"reply": ai_reply})

# =========================
# RUN SERVER
# =========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
