from flask import Flask, render_template, request, redirect, url_for,session
from datetime import datetime, timedelta
import firebase_admin
import json
from firebase_admin import credentials, firestore
import os ,requests

# Load .env in local dev
from dotenv import load_dotenv
# Load environment variables from .env only in development
if os.environ.get("FLASK_ENV") != "production":
    load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "fallback-dev-secret")

firebase_json = os.environ.get("GOOGLE_CREDENTIALS_JSON")

if not firebase_json:
    raise ValueError("Missing GOOGLE_CREDENTIALS_JSON in environment")

firebase_dict = json.loads(firebase_json)
firebase_dict["private_key"] = firebase_dict["private_key"].replace("\\n", "\n")
class ApiMonitor:
    def __init__(self,  collection="api_usage"):
        if not firebase_admin._apps:
            cred = credentials.Certificate(firebase_dict)
            firebase_admin.initialize_app(cred)

        self.db = firestore.client()
        self.collection = collection

    def _get_today_key(self):
        return datetime.utcnow().strftime("%Y-%m-%d")

    def get_status(self, api_name):
        key = self._get_today_key()
        doc = self.db.collection(self.collection).document(key).get()
        if doc.exists:
            data = doc.to_dict().get(api_name, {})
            return data.get("count", 0), data.get("failures", 0), data.get("is_down", False)
        return 0, 0, False

    def increment_api_count(self, api_name):
        key = self._get_today_key()
        print(key)
        self.db.collection(self.collection).document(key).set(
            {f"{api_name}.count": firestore.Increment(1)}, merge=True
        )

    def increment_failure(self, api_name):
        key = self._get_today_key()
        self.db.collection(self.collection).document(key).set(
            {f"{api_name}.failures": firestore.Increment(1)}, merge=True
        )

    def reset_failure_count(self, api_name):
        key = self._get_today_key()
        self.db.collection(self.collection).document(key).set(
            {f"{api_name}.failures": 0}, merge=True
        )

    def mark_api_status(self, api_name, is_down):
        key = self._get_today_key()
        self.db.collection(self.collection).document(key).set(
            {f"{api_name}.is_down": is_down}, merge=True
        )
monitor = ApiMonitor()  # adjust path if needed
reservations_collection = monitor.db.collection("reservations")
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1358363882833313882/TIip_rNgIAj5uIxAYJbmZ2YAHOQ-C9iwi-bFQ3qqY5FNqMcTUVD7udJM8_9ZMZzCDIVv"  # Replace with your webhook

API_NAME = "tomtom"  # you can choose a name
def API_VERCEL_PAGE_visited():
    embed = {
        "title": "🚀 API_VERCEL_PAGE_visited",
        "color": 3066993,
    }
    try:
        requests.post(DISCORD_WEBHOOK_URL, json={"embeds": [embed]})
    except Exception as e:
        console.log(f"Failed to send container start alert: {e}")

def send_skip_alert_to_discord():
    embed = {
        "title": "⏭️ Info Form Skipped",
        "color": 15158332,
        "description": "Someone **ran the container** and skipped the info form.",
    }
    try:
        requests.post(DISCORD_WEBHOOK_URL, json={"embeds": [embed]})
    except Exception as e:
        st.warning(f"⚠️ Could not send to Discord: {e}")       

def send_to_discord(name,email, role, purpose, message):
    embed = {
        "title": "🚀 Vercel form user Info",
        "color": 3447003,
        "fields": [
            {"name": "🧑 Name", "value": name, "inline": True},
            {"name": "📫 Email/Linkedin", "value": email if email else "Not provided", "inline": True},
            {"name": "🎯 Role / Interest", "value": role if role else "Not provided", "inline": False},
            {"name": "📝 purpose", "value": purpose if purpose else "Not provided", "inline": False},
            {"name": "📝 Message", "value": message if message else "Not provided", "inline": False},

        ]
    }
    if message:
        embed["fields"].append({"name": "💬 Feedback / Comment", "value": message, "inline": False})

    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json={"embeds": [embed]})
        if response.status_code != 204:
            print(f"⚠️ Discord webhook failed with status {response.status_code}")
    except Exception as e:
        print(f"⚠️ Could not send to Discord: {e}")    

def send_to_discord_fedback(name,email,message):
    embed = {
        "title": "🚀 Vercel form feedback user Info",
        "color": 3447003,
        "fields": [
            {"name": "🧑 Name", "value": name, "inline": True},
            {"name": "📫 Email/Linkedin", "value": email if email else "Not provided", "inline": True},
            {"name": "🎯 message", "value": message if role else "Not provided", "inline": False},
           
        ]
    }
    if message:
        embed["fields"].append({"name": "💬 Feedback / Comment", "value": message, "inline": False})

    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json={"embeds": [embed]})
        if response.status_code != 204:
            print(f"⚠️ Discord webhook failed with status {response.status_code}")
    except Exception as e:
        print(f"⚠️ Could not send to Discord: {e}")     

        
@app.route("/", methods=["GET","POST"])
def index():
    show_api_info = False
    user_info = {}
    if not session.get("visited_page"):
        API_VERCEL_PAGE_visited()
        monitor.increment_api_count("Vercel_API_Visitors")
        session["visited_page"] = True  # 🔐 prevent repeat counts
    if request.method == 'POST':
       if not session.get("form_submitted"):
            
            user_info['name'] = request.form.get('name')
            user_info['email'] = request.form.get('email')
            user_info['purpose'] = request.form.get('purpose')
            user_info['role'] = request.form.get('role')
            user_info['message'] = request.form.get('message')

           
            send_to_discord(user_info['name'],user_info['email'], user_info['role'], user_info['purpose'], user_info['message'])
            monitor.increment_api_count("Vercel_API_form_submitters")
            session["form_submitted"] = True
            flash('Thanks for submitting your details! 🚀', 'thank_you')  
       return redirect(url_for("index", show_api="1"))


     # User came from a redirect? Show API info
    if request.args.get("show_api") == "1" or session.get("form_submitted") or session.get("skipped"):
        show_api_info = True
    
    count, failures, is_down = monitor.get_status("tomtom")
    # Determine if API is down due to limit or flag
    if count >= 2500 or is_down:
        api_status = "DOWN"
        if count >= 2500:
            api_down_reason = "API usage exceeded daily limit of 2500 calls."
        else:
            api_down_reason = "API marked as unavailable by system health check."
    else:
        api_status = "UP"
        api_down_reason = None

    # Get current reservations sorted by reservation time
    today = datetime.utcnow().date()
    reservations = monitor.db.collection("reservations") \
        .where("reserved_at", ">=", datetime(today.year, today.month, today.day)) \
        .order_by("reserved_at") \
        .stream()

    queue = [doc.to_dict().get("username") for doc in reservations]

    return render_template("index.html",
                           show_api_info=show_api_info,

                           api_status=api_status,
                           api_down_reason=api_down_reason,
                           count=count,
                           failures=failures,
                           queue=queue,
                           reserved=request.args.get("reserved"),
                           duplicate=request.args.get("duplicate"),
                           current_year=datetime.utcnow().year)


from flask import flash

@app.route("/reserve", methods=["POST"])
def reserve():
    username = request.form.get("username")
    today = datetime.utcnow().date()

    reservations_collection = monitor.db.collection("reservations")

    # Check for duplicate reservation
    docs = reservations_collection.where("username", "==", username).stream()
    for doc in docs:
        data = doc.to_dict()
        if "reserved_at" in data and data["reserved_at"].date() == today:
            flash(username, "duplicate")
            return redirect(url_for("index"))

    # Add new reservation
    reservations_collection.add({
    "username": username,
    "reserved_at": datetime.utcnow(),
    "expire_at": datetime.utcnow() + timedelta(days=1)
})
    flash(username, "reserved")
    return redirect(url_for("index", show_api="1"))


@app.route("/submit-feedback", methods=["POST"])
def submitfeedback():
    nameFeedback = request.form.get("nameFeedback")
    emailFeedback = request.form.get("emailFeedback")
    messageFeedback = request.form.get("messageFeedback")

    send_to_discord_fedback(nameFeedback ,emailFeedback,messageFeedback)

    
    flash(username, "submit-feedback")
    return redirect(url_for("index", show_api="1"))


    
if __name__ == "__main__":
    app.run(debug=True)
app = app
