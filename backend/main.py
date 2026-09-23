from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database.session import init_db
from config import get_settings
from routes import auth,profile,resume,career,documents,chat,dashboard
settings=get_settings()
@asynccontextmanager
async def lifespan(app):
    await init_db(); yield
app=FastAPI(title='CareerTwin AI API',description='AI Career Digital Twin using Google Gemini and open/free developer resources.',version='2.0.0',lifespan=lifespan)
app.add_middleware(CORSMiddleware,allow_origins=settings.cors_origins,allow_credentials=True,allow_methods=['*'],allow_headers=['*'])
app.include_router(auth.router,prefix='/api/auth',tags=['Authentication']); app.include_router(profile.router,prefix='/api/profile',tags=['Profile']); app.include_router(resume.router,prefix='/api/resume',tags=['Resume']); app.include_router(career.router,prefix='/api/career',tags=['Career']); app.include_router(documents.router,prefix='/api/documents',tags=['Documents']); app.include_router(chat.router,prefix='/api/chat',tags=['Chat']); app.include_router(dashboard.router,prefix='/api/dashboard',tags=['Dashboard'])
@app.get('/')
async def root(): return {'status':'ok','service':'CareerTwin AI API','version':'2.0.0'}
@app.get('/health')
async def health(): return {'status':'healthy','ai_provider':'gemini','model':settings.gemini_model,'api_key_configured':bool(settings.gemini_api_key)}
