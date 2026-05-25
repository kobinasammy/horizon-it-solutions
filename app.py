from dotenv import load_dotenv
load_dotenv()

from flask import Flask, render_template, request, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition
from datetime import datetime
import os
import base64

app = Flask(__name__)

# ── CONFIG ──
app.secret_key = os.environ.get('SECRET_KEY', 'change-this-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///horizon.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB max file size
db = SQLAlchemy(app)

# ── ALLOWED FILE TYPES ──
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ── MODELS ───
class ContactSubmission(db.Model):
    id        = db.Column(db.Integer, primary_key=True)
    name      = db.Column(db.String(100), nullable=False)
    email     = db.Column(db.String(120), nullable=False)
    company   = db.Column(db.String(120))
    service   = db.Column(db.String(100))
    message   = db.Column(db.Text, nullable=False)
    submitted = db.Column(db.DateTime, default=datetime.utcnow)

class JobApplication(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    name       = db.Column(db.String(100), nullable=False)
    email      = db.Column(db.String(120), nullable=False)
    phone      = db.Column(db.String(30))
    role       = db.Column(db.String(100), nullable=False)
    experience = db.Column(db.String(50))
    linkedin   = db.Column(db.String(200))
    cv_link    = db.Column(db.String(200))
    cv_filename = db.Column(db.String(200))
    cover      = db.Column(db.Text, nullable=False)
    submitted  = db.Column(db.DateTime, default=datetime.utcnow)

# ── EMAIL HELPER ────
def send_email(subject, body, attachment_data=None, attachment_name=None, attachment_type=None):
    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        msg = Mail(
            from_email='brownsamuel08@gmail.com',
            to_emails='brownsamuel08@gmail.com',
            subject=subject,
            plain_text_content=body
        )

        if attachment_data and attachment_name:
            encoded = base64.b64encode(attachment_data).decode()
            attachment = Attachment(
                FileContent(encoded),
                FileName(attachment_name),
                FileType(attachment_type or 'application/octet-stream'),
                Disposition('attachment')
            )
            msg.attachment = attachment

        sg.send(msg)
    except Exception as e:
        print(f'Email error: {str(e)}')

# ── ROUTES ───
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/solutions')
def solutions():
    return render_template('solutions.html')

@app.route('/insights')
def insights():
    return render_template('insights.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name    = request.form.get('name')
        email   = request.form.get('email')
        company = request.form.get('company', '')
        service = request.form.get('service')
        message = request.form.get('message')

        db.session.add(ContactSubmission(
            name=name, email=email, company=company,
            service=service, message=message
        ))
        db.session.commit()

        send_email(
            subject=f'New Contact – {service}',
            body=f"""New contact form submission.

Name:    {name}
Email:   {email}
Company: {company or 'Not provided'}
Service: {service}

Message:
{message}"""
        )

        flash("Message sent! We'll be in touch within one business day.", 'success')
        return redirect(url_for('contact'))

    return render_template('contact.html')

@app.route('/careers', methods=['GET', 'POST'])
def careers():
    if request.method == 'POST':
        name       = request.form.get('app_name')
        email      = request.form.get('app_email')
        phone      = request.form.get('app_phone', '')
        role       = request.form.get('app_role')
        experience = request.form.get('app_experience')
        linkedin   = request.form.get('app_linkedin', '')
        cv_link    = request.form.get('app_cv_link', '')
        cover      = request.form.get('app_cover')

        # Handle file upload
        cv_file = request.files.get('app_cv_file')
        attachment_data = None
        attachment_name = None
        attachment_type = None
        cv_filename = None

        if cv_file and cv_file.filename:
            if not allowed_file(cv_file.filename):
                flash('Invalid file type. Please upload a PDF, DOC, or DOCX file.', 'error')
                return redirect(url_for('careers') + '#apply')

            cv_filename = cv_file.filename
            attachment_data = cv_file.read()
            attachment_name = cv_filename

            ext = cv_filename.rsplit('.', 1)[1].lower()
            if ext == 'pdf':
                attachment_type = 'application/pdf'
            elif ext == 'doc':
                attachment_type = 'application/msword'
            elif ext == 'docx':
                attachment_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'

        db.session.add(JobApplication(
            name=name, email=email, phone=phone,
            role=role, experience=experience,
            linkedin=linkedin, cv_link=cv_link,
            cv_filename=cv_filename, cover=cover
        ))
        db.session.commit()

        send_email(
            subject=f'New Job Application – {role}',
            body=f"""New job application received.

Name:       {name}
Email:      {email}
Phone:      {phone or 'Not provided'}
Role:       {role}
Experience: {experience}
LinkedIn:   {linkedin or 'Not provided'}
CV Link:    {cv_link or 'Not provided'}
CV File:    {cv_filename or 'Not uploaded'}

Why Horizon:
{cover}""",
            attachment_data=attachment_data,
            attachment_name=attachment_name,
            attachment_type=attachment_type
        )

        flash("Application received! We'll be in touch within 3 business days.", 'success')
        return redirect(url_for('careers') + '#apply')

    return render_template('careers.html')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run()