from fastapi import FastAPI
from pydantic import BaseModel
from utils.search import search_faiss
from utils.prompt_builder import format_answer

app = FastAPI()

class Query(BaseModel):
    question: str

@app.post("/api/")
def virtual_ta(query: Query):
    matches = search_faiss(query.question)
    return format_answer(query.question, matches)
