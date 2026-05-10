# Personal Task Tracker

A lightweight local web application for tracking daily tasks with a monthly overview, a dedicated To‑Do list, and a light/dark theme toggle.

## Features

- **Daily Overview** – View and toggle tasks for any chosen day.
- **Monthly Overview** – Calendar grid with completion status for each task per day.
- **To‑Do List** – Schedule items, see upcoming due dates, and mark them completed.
- **User Accounts** – Login / register with secure password hashing.
- **Light/Dark Theme** – Persisted with `localStorage` and can be switched from any page.
- **Secure** – CSRF protection, password hashing, session‑based authentication.

## Quick Start

```bash
# Clone the repo
git clone <repo-url>
cd personal-task-tracker

# Optional: create a virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# Install deps
pip install -r requirements.txt

# Create a secret key (one line, no quotes)
echo 'YOUR_RANDOM_KEY' > secret_key.txt

# Run locally
python run.py

```

### Docker
```bash
# Startup
docker compose up --build -d

```

```bash
# Shutdown
docker compose down
