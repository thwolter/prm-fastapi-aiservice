from fastapi import APIRouter, HTTPException
import requests
from langchain_openai import ChatOpenAI
from app.core.config import settings
from langchain import hub
router = APIRouter()

@router.get("/health-check")
async def health_check():
    return {"status": "ok"}


@router.get("/health-check/openai/check-connection")
async def check_openai_connection():
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", api_key=settings.OPENAI_API_KEY)
    try:
        response = llm(["Answer: yes"])
        if response:
            return {"message": "OpenAI connection successful"}
        else:
            raise HTTPException(status_code=500, detail="OpenAI connection failed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health-check/smith/check-connection")
async def check_smith_connection():
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", api_key=settings.OPENAI_API_KEY)
    try:
        prompt_template = hub.pull("health-check").template
        response = llm.invoke([prompt_template])
        if response:
            return {"message": "Smith connection successful"}
        else:
            raise HTTPException(status_code=500, detail="Smith connection failed")
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))