from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///leads.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Lead(db.Model):
    __tablename__ = 'leads'

    id = db.Column(db.Integer, primary_key=True)

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
        return f'<Lead {self.full_name}>'


with app.app_context():
    db.create_all()


@app.route('/')
def home():
    return render_template('landing.html')


@app.route('/capture-lead', methods=['POST'])
def capture_lead():

    lead = Lead(
        full_name=request.form.get('full_name'),
        company_name=request.form.get('company_name'),
        email=request.form.get('email'),
        phone=request.form.get('phone')
    )

    db.session.add(lead)
    db.session.commit()

    return redirect(url_for('success'))


@app.route('/success')
def success():
    return render_template('success.html')

@app.route('/profile')
def profile():
    return render_template('profile.html')


if __name__ == '__main__':
    app.run(debug=True)