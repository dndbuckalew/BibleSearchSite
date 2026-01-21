# Backend run

1. python -m venv venv
2. source venv/bin/activate  (or venv\Scripts\activate on Windows)
3. pip install -r requirements.txt
4. export OPENAI_API_KEY="sk-..."   (or set in .env)
5. uvicorn main:app --reload --port 8000

Security note: Never commit your API keys.
