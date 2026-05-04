# run.py
"""
Entry point for the Personal Task Tracker.
"""

from app import create_app

app = create_app()

if __name__ == '__main__':
    # Host 0.0.0.0 so any LAN device can reach it
    app.run(host='0.0.0.0', port=5000, debug=True)

