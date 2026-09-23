# CareerTwin AI — Clean Free-API Edition

CareerTwin AI is an AI-powered **Career Digital Twin** for students and early-career users. This version removes the IBM watsonx/Granite dependency and uses Google Gemini through a backend-only API integration.

## What is included

- Secure registration/login with JWT
- Persistent SQLite profile and career data
- Resume upload: PDF, DOCX and TXT
- AI resume analysis + ATS-style score
- Skill extraction and skill-gap analysis
- Personalized 6-month roadmap
- Portfolio project recommendations
- AI Career Mentor chat with stored conversations
- **Career Simulation Engine** comparing two career paths
- **Mock Interview** question generator
- Dashboard with career-readiness snapshot
- Free/open learning-resource suggestions
- Clean React/Vite UI based on the original project

## AI provider

The default provider is **Google Gemini API** using `gemini-3.5-flash-lite`. Keep the key on the backend only. The application does not ship with an API key.

## Project structure

```text
CareerTwinAI/
├── backend/
│   ├── main.py
│   ├── config.py
│   ├── requirements.txt
│   ├── .env.example
│   ├── database/
│   ├── routes/
│   ├── services/
│   ├── prompts/
│   └── utils/
└── frontend/
    ├── package.json
    ├── .env.example
    └── src/
```

## Local setup

### 1. Backend

Use Python 3.11–3.13 for the easiest dependency experience.

Windows PowerShell:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Open `backend/.env` and set `GEMINI_API_KEY` and a strong `SECRET_KEY`.

Start the API:

```powershell
python -m uvicorn main:app --reload --port 8000
```

Open http://127.0.0.1:8000/docs

### 2. Frontend

Open a second terminal:

```powershell
cd frontend
npm install
Copy-Item .env.example .env
npm run dev
```

Open http://localhost:5173

## Getting the Gemini API key

1. Open Google AI Studio.
2. Create/sign in to a Google account.
3. Create an API key for Gemini.
4. Put it in `backend/.env` as `GEMINI_API_KEY=...`.
5. Never put the Gemini key in React/Vite code or commit it to GitHub.

## Free resources used by the product

The AI can recommend public learning resources such as official documentation, freeCodeCamp, MDN, Python documentation and Kaggle Learn. URLs are only returned when the model is confident about them; the application does not pretend that unverified links are official.

## Deployment

Recommended simple setup:

- **Backend:** Render Web Service
- **Frontend:** Vercel or Render Static Site
- **Database for college demo:** SQLite on the backend
- **For a production MVP:** move the database to PostgreSQL and file uploads to object storage

### Render backend

Set the backend service root directory to `backend`.

Build command:

```text
pip install -r requirements.txt
```

Start command:

```text
uvicorn main:app --host 0.0.0.0 --port $PORT
```

Environment variables:

```text
SECRET_KEY=<strong-secret>
GEMINI_API_KEY=<your-key>
GEMINI_MODEL=gemini-3.5-flash-lite
DATABASE_URL=sqlite+aiosqlite:///./data/careertwin.db
ALLOWED_ORIGINS=https://your-frontend.vercel.app
```

### Frontend deployment

Set `VITE_API_URL` to the deployed backend URL plus `/api`, for example:

```text
https://your-backend.onrender.com/api
```

Build command:

```text
npm run build
```

Publish directory:

```text
dist
```

For React Router, configure the host to rewrite unknown routes to `/index.html`.

## Important production note

SQLite and local uploaded files are convenient for a college demo, but many free hosting environments use ephemeral disks. For a real public product, use PostgreSQL plus persistent/object storage for resumes.

## No IBM APIs

This repository intentionally contains **no IBM watsonx, Granite, IBM IAM or IBM API credentials**.
