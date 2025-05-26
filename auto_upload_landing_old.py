import requests
import base64
import random
import os
from dotenv import load_dotenv

# Load GitHub token
load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
USERNAME = "RoyChehmer"
REPO = "auto-contact-share"
BRANCH = "main"
DOCS_URL = "https://docs.google.com/document/d/e/2PACX-1vShHLRW4GLqRv3lMsZf8qXWVuWwo9stv2boj6J9faOuQ1fAso64UybX_26U5XtEZvqOD0u5av9tVQ0L/pub"

# EmailJS details
EMAILJS_USER_ID = "Ed6ccvEXjGg9YLtz5"
EMAILJS_SERVICE_ID = "service_0miq6uw"
EMAILJS_TEMPLATE_ID = "template_5s7dmxv"

def get_random_paragraph_from_docs():
    response = requests.get(DOCS_URL)
    html = response.text
    parts = html.split("</p>")
    paragraphs = [p.split(">")[-1].strip() for p in parts if ">" in p and len(p.split(">")[-1].strip()) > 30]
    return random.choice(paragraphs)

def generate_html(content):
    return f"""
<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>צור קשר</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: auto;
            padding: 20px;
            direction: rtl;
        }}
        form {{
            margin-top: 30px;
        }}
        input, textarea {{
            width: 100%;
            padding: 8px;
            margin: 10px 0;
        }}
        button {{
            padding: 10px 20px;
            background-color: #6200ee;
            color: white;
            border: none;
            cursor: pointer;
        }}
    </style>
</head>
<body>
    <h1>ברוכים הבאים</h1>
    <p>{content}</p>

    <form id="contact-form">
        <label>שם:</label>
        <input type="text" name="from_name" required>
        <label>אימייל:</label>
        <input type="email" name="reply_to" required>
        <label>הודעה:</label>
        <textarea name="message" required></textarea>
        <button type="submit">שלח</button>
    </form>

    <script src="https://cdn.jsdelivr.net/npm/emailjs-com@2/dist/email.min.js"></script>
    <script>
        emailjs.init("{EMAILJS_USER_ID}");
        document.getElementById("contact-form").addEventListener("submit", function(e) {{
            e.preventDefault();
            emailjs.sendForm("{EMAILJS_SERVICE_ID}", "{EMAILJS_TEMPLATE_ID}", this)
            .then(() => {{
                alert("ההודעה נשלחה בהצלחה!");
            }}, (error) => {{
                alert("שגיאה בשליחה: " + error.text);
            }});
        }});
    </script>
</body>
</html>
"""

def upload_to_github(html_content):
    url = f"https://api.github.com/repos/{USERNAME}/{REPO}/contents/index.html"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
    }

    response = requests.get(url, headers=headers)
    sha = response.json().get("sha", None)

    data = {
        "message": "Auto-update landing page",
        "content": base64.b64encode(html_content.encode()).decode(),
        "branch": BRANCH,
    }
    if sha:
        data["sha"] = sha

    put_resp = requests.put(url, headers=headers, json=data)
    if put_resp.status_code in [200, 201]:
        print("✅ דף נחת עודכן והועלה ל־GitHub בהצלחה.")
    else:
        print("❌ שגיאה בהעלאה ל-GitHub:", put_resp.json())

if __name__ == "__main__":
    paragraph = get_random_paragraph_from_docs()
    html = generate_html(paragraph)
    upload_to_github(html)
