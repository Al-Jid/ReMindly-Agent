# MD Notes Agent UI

Small local web interface for turning raw explanations into organized Markdown.

## Structure

```text
md-notes-agent-ui/
├── static/
│   ├── index.html
│   ├── style.css
│   └── app.js
├── server.py
├── requirements.txt
├── .env.example
└── .gitignore
```

## Run on Windows

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and add your provider settings.

Then run:

```powershell
uvicorn server:app --reload
```

Open:

```text
http://127.0.0.1:8000
```

## Why the API key is not in JavaScript

Browser JavaScript is visible to anyone who opens DevTools. The key therefore stays inside `.env` and only the local Python backend communicates with the model provider.
