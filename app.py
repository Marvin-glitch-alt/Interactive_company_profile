from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash
)
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)

app.secret_key = os.environ.get(
    "SECRET_KEY",
    "change-this-in-production"
)

ADMIN_USERNAME = os.environ.get(
    "ADMIN_USERNAME",
    "admin"
)

ADMIN_PASSWORD = os.environ.get(
    "ADMIN_PASSWORD",
    "ChangeMe123!"
)

# ==========================================
# DATABASE CONFIGURATION
# ==========================================

# For local development:
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
INSTANCE_DIR = os.path.join(BASE_DIR, "instance")

os.makedirs(INSTANCE_DIR, exist_ok=True)

# SQLite locally, PostgreSQL in production
DATABASE_URL = os.environ.get("DATABASE_URL")

if DATABASE_URL:
    # Render/Neon/Supabase PostgreSQL
    app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
else:
    # Local SQLite database
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"sqlite:///{os.path.join(INSTANCE_DIR, 'leads.db')}"
    )

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# ==========================================
# MODELS
# ==========================================

class Lead(db.Model):
    __tablename__ = "leads"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    full_name = db.Column(
        db.String(100),
        nullable=False
    )

    company_name = db.Column(
        db.String(100),
        nullable=False
    )

    email = db.Column(
        db.String(120),
        nullable=False
    )

    phone = db.Column(
        db.String(30)
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    def __repr__(self):
        return f"<Lead {self.full_name}>"

# ==========================================
# CREATE DATABASE TABLES
# ==========================================

with app.app_context():
    db.create_all()

# ==========================================
# ROUTES
# ==========================================

from flask import session

@app.route('/')
def home():
    return render_template("landing.html")


@app.route("/capture-lead", methods=["POST"])
def capture_lead():

    lead = Lead(
        full_name=request.form.get("full_name"),
        company_name=request.form.get("company_name"),
        email=request.form.get("email"),
        phone=request.form.get("phone")
    )

    db.session.add(lead)
    db.session.commit()

    return redirect(url_for("success"))


@app.route("/success")
def success():

    if not session.get('allowed_access'):
        return redirect(url_for('home'))
    
    return render_template("success.html") 


@app.route('/profile')
def profile():

    if not session.get('allowed_access'):
        return redirect(url_for('home'))

    return render_template('profile.html')


# ==========================================
# ADMIN LEADS DASHBOARD
# ==========================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        if (
            username == ADMIN_USERNAME
            and password == ADMIN_PASSWORD
        ):
            session["admin_logged_in"] = True

            return redirect(url_for("leads"))

        flash("Invalid username or password")

    return render_template("login.html")

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login"))

@app.route("/leads")
def leads():

    if not session.get("admin_logged_in"):
        return redirect(url_for("login"))

    all_leads = Lead.query.order_by(
        Lead.created_at.desc()
    ).all()

    return render_template(
        "leads.html",
        leads=all_leads
    )


# ==========================================
# RUN APP
# ==========================================

if __name__ == "__main__":
    app.run(debug=True)
