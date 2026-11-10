# Streamlit deployment
Push the project to GitHub. At https://share.streamlit.io/, create an app, select repository/branch and set main file to `app.py`. Add `DATABASE_URL` and optional `OPENAI_API_KEY` under app Secrets, then deploy/reboot. Use PostgreSQL for durable hosted progress; ephemeral local SQLite should not be treated as durable storage. Keep secrets out of Git.
