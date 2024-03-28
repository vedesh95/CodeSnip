from typing import Annotated
from fastapi import FastAPI, HTTPException, status
from pymongo import MongoClient
from bson import ObjectId
from pydantic import BaseModel
from jinja2 import Environment, FileSystemLoader
from fastapi.responses import HTMLResponse, RedirectResponse

app = FastAPI()

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["code_snippets"]
collection = db["snippets"]

# Jinja2 Environment setup
templates_env = Environment(loader=FileSystemLoader("templates"))

class Snippet(BaseModel):
    title: str
    language: str
    code: str

class UpdatedSnip(BaseModel):
    snipID: str
    code: str

#get home page to view the form
@app.get("/", response_class=HTMLResponse)
async def read_snippets():
    template = templates_env.get_template("index.html")
    return template.render()

#get a snippet
@app.get("/snippets/{snippet_id}", response_class=HTMLResponse)
async def read_snippet(snippet_id: str,update: int = 0):
    print(update)
    snippet = collection.find_one({"_id": ObjectId(snippet_id)})
    if not snippet:
        raise HTTPException(status_code=404, detail="Snippet not found")
    template = templates_env.get_template("view_snippet.html")
    return template.render(snippet=snippet,update=update)

#create a snippet
@app.post("/snippets/")
async def create_snippet(snippet: Snippet):
    snippet_data = snippet.dict()
    inserted_snippet = collection.insert_one(snippet_data)
    if not inserted_snippet:
        raise HTTPException(status_code=404, detail="Snippet not found")
    snippet_id = str(inserted_snippet.inserted_id)
    return snippet_id

#Update a snippet
@app.post("/updatesnippet/")
async def update_snippet(updatedSnip: UpdatedSnip):
    snippet = collection.update_one({"_id": ObjectId(updatedSnip.snipID)}, {"$set": {"code": updatedSnip.code}})
    if snippet.matched_count == 0:
        raise HTTPException(status_code=404, detail="Snippet not found")
    return {"message": "Snippet updated successfully","status_code": "200"}

#delete a snippet
@app.post("/deletesnippet/{snippet_id}")
async def delete_snippet(snippet_id: str):
    result = collection.delete_one({"_id": ObjectId(snippet_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Snippet not found")
    return {"message": "Snippet updated successfully"}
