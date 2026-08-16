from fastapi import APIRouter
from backend.app.llm.client import LLMClient
from backend.app.rag.history import History
from backend.app.rag.retriver import Retriver
from backend.app.rag.pipeline import RagPipelines
import backend.app.models.schema as schema

router =  APIRouter()

retriver = Retriver()
history = History()
llmclient = LLMClient()

pipeline = RagPipelines(retriver, llmclient, history)

@router.post("/api/chat/", response_model = schema.ChatResponse)
def chat(request: schema.ChatRequest) -> schema.ChatResponse:
    result = pipeline.answer(request.message, request.session_id)
    return schema.ChatResponse(answer = result["answer"], source = result.get("source", []))

@router.get("/api/health", response_model = schema.Health)
def health() -> schema.Health:
    return schema.Health(status = "Healthy")