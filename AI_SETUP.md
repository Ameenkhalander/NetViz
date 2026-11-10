# AI tutor setup
1. Create an API key at https://platform.openai.com/api-keys.
2. Set `OPENAI_API_KEY` in the environment or Streamlit Secrets.
3. Optionally set `OPENAI_MODEL` (default `gpt-4.1-mini`).
4. Restart the app and ask a question in a lesson.
API calls may incur charges. Without a key or if the API is unavailable, the application continues with an offline fallback. Never commit keys.
