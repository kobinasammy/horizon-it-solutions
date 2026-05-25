# Horizon IT Solutions

A web app built with Python Flask, deployed live on Microsoft Azure.

Live site: https://horizonitsolutions-eabcdkbudrb9fuhb.austriaeast-01.azurewebsites.net 

## How this started

This didn't start with code. It started with the basics learning how RAM gets installed in a PC, how Active Directory manages users across a company network, and how IT infrastructure actually works under the hood. From there I wanted to build something real. So I designed a landing page in Figma, turned it into a working website, and deployed it to the cloud.

## What's in it

- 7 pages — Home, Services, Solutions, Insights, About, Contact, Careers
- Contact form that emails me when someone submits it
- Job application form where candidates can upload their CV
- Everything saves to a PostgreSQL database on Azure
- Built with Python, Flask, and custom CSS — no UI frameworks

## Tech used

Python · Flask · PostgreSQL · SendGrid · Azure App Service · Git · GitHub

## What I learned

Going from Figma mockup to a live deployed web app taught me more than any tutorial. I broke it constantly, empty config files, crashing Azure, authentication errors, database tables that didn't exist yet and fixed it every time.

Built with help from **Claude by Anthropic** as a learning tool throughout the process.


## Run it locally

```bash
git clone https://github.com/kobinasammy/horizon-it-solutions.git
cd horizon-it-solutions
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

---

Samuel Brown · brownsamuel08@gmail.com

