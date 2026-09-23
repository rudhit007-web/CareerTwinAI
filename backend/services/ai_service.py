"""Google Gemini service used by CareerTwin AI.

The API key is read from GEMINI_API_KEY. If no key is configured, the service
raises a clear setup error instead of silently pretending AI is available.
"""
import json, logging
import httpx
from fastapi import HTTPException
from config import get_settings
from prompts.templates import *

log=logging.getLogger(__name__); settings=get_settings()

async def _generate(prompt: str, *, max_tokens: int=1800, temperature: float=0.3, json_mode: bool=True) -> dict:
    if not settings.gemini_api_key:
        raise HTTPException(503,'Gemini API is not configured. Add GEMINI_API_KEY to backend/.env.')
    url=f'https://generativelanguage.googleapis.com/v1beta/models/{settings.gemini_model}:generateContent'
    payload={'contents':[{'role':'user','parts':[{'text':prompt}]}], 'generationConfig':{'temperature':temperature,'maxOutputTokens':max_tokens}}
    if json_mode:
        payload['generationConfig']['responseMimeType']='application/json'
    try:
        async with httpx.AsyncClient(timeout=settings.gemini_timeout_seconds) as client:
            r=await client.post(url,json=payload,headers={'x-goog-api-key': settings.gemini_api_key, 'Content-Type':'application/json'})
        if r.status_code>=400:
            try: detail=r.json().get('error',{}).get('message',r.text)
            except Exception: detail=r.text
            raise HTTPException(r.status_code,f'Gemini API error: {detail}')
        data=r.json(); text=data['candidates'][0]['content']['parts'][0]['text'].strip()
        usage=data.get('usageMetadata',{})
        return {'text':text,'tokens_used':int(usage.get('totalTokenCount',0) or 0)}
    except httpx.TimeoutException:
        raise HTTPException(504,'Gemini request timed out. Please retry.')
    except HTTPException: raise
    except Exception as exc:
        log.exception('Gemini request failed')
        raise HTTPException(502,f'AI service request failed: {exc}')

def _json(text: str):
    text=text.strip().replace('```json','').replace('```','').strip()
    try: return json.loads(text)
    except json.JSONDecodeError:
        start=text.find('{'); end=text.rfind('}')
        if start>=0 and end>start: return json.loads(text[start:end+1])
        raise

async def analyze_resume(resume_text: str, career_goal: str=''):
    raw=await _generate(resume_analysis_prompt(resume_text,career_goal),max_tokens=1800,temperature=0.2)
    try: data=_json(raw['text'])
    except Exception: raise HTTPException(502,'AI returned an invalid resume-analysis response. Please retry.')
    data['tokens_used']=raw['tokens_used']; return data

async def skill_gap_analysis(career_goal: str,current_skills: list,resume_summary: str=''):
    raw=await _generate(skill_gap_prompt(career_goal,current_skills,resume_summary),max_tokens=1800,temperature=0.25)
    try: data=_json(raw['text'])
    except Exception: raise HTTPException(502,'AI returned an invalid skill-gap response. Please retry.')
    data['tokens_used']=raw['tokens_used']; return data

async def generate_career_roadmap(profile: dict):
    raw=await _generate(roadmap_prompt(profile),max_tokens=2200,temperature=0.35)
    try: data=_json(raw['text'])
    except Exception: raise HTTPException(502,'AI returned an invalid roadmap response. Please retry.')
    data['tokens_used']=raw['tokens_used']; return data

async def recommend_projects(profile: dict,skills:list,career_goal:str):
    raw=await _generate(projects_prompt(profile,skills,career_goal),max_tokens=2200,temperature=0.45)
    try: data=_json(raw['text'])
    except Exception: raise HTTPException(502,'AI returned an invalid project response. Please retry.')
    data['tokens_used']=raw['tokens_used']; return data

async def simulate_careers(profile:dict,option_a:str,option_b:str):
    raw=await _generate(simulation_prompt(profile,option_a,option_b),max_tokens=2200,temperature=0.3)
    try: data=_json(raw['text'])
    except Exception: raise HTTPException(502,'AI returned an invalid career-simulation response. Please retry.')
    data['tokens_used']=raw['tokens_used']; return data

async def interview_questions(profile:dict,role:str,difficulty:str='medium'):
    raw=await _generate(interview_prompt(profile,role,difficulty),max_tokens=1600,temperature=0.4)
    try: data=_json(raw['text'])
    except Exception: raise HTTPException(502,'AI returned an invalid interview response. Please retry.')
    data['tokens_used']=raw['tokens_used']; return data

async def career_chat(user_message:str,history:list,profile:dict):
    raw=await _generate(chat_prompt(user_message,history,profile),max_tokens=1000,temperature=0.65,json_mode=False)
    return {'reply':raw['text'],'tokens_used':raw['tokens_used']}
