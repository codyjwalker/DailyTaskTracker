# Personal Task Tracker

A lightweight local web application for tracking daily tasks with a monthly overview.

## Features

- **Daily Overview** – View and toggle tasks for any chosen day.
- **Monthly Overview** – See a calendar grid with completion status for each task per day.
- **ToDo List** – See a list of specific tasks that aren't dailies and track progress on completing them.
- **Local Server** – Host on your local network so any device on the same LAN can view the site.
- **Persistent Storage** – Tasks are saved in a JSON file (`tasks.json`) and ToDo List items in JSON file (`todolist.json`).

## Setup

### Prerequisites

- Python 3.8+ (or any recent Python 3.x)
- `pip` (Python package installer)

### Installation

```bash
# Clone the repository or copy the folder structure locally
cd path/to/personal-task-tracker

# (Optional) Create a virtual environment
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Running the server
python run.py

```

### Docker

```bash
# Startup
docker compose up --build -d

# Shutdown
docker compose down
