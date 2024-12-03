"""
FastAPI server implementation for the Text-to-SQL application.
Provides REST API endpoints for:
- Chat interactions with SQL-powered responses
- Chat history management
Also serves the static frontend files.

The server uses FastAPI with CORS enabled and maintains chat sessions using an
in-memory store.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List

from engine import TextToSQLEngine
from session import SessionManager
from dotenv import load_dotenv

from tracing import init_tracing
from formatters import wrap_sql, format_results_as_markdown_table


load_dotenv()

app = FastAPI(title="Text-to-SQL Chat Application")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Text-to-SQL engine (singleton)
sql_engine = TextToSQLEngine()
init_tracing(sql_engine)

# Initialize SessionManager (singleton)
session_manager = SessionManager()


# Schemas
class NewChatMessage(BaseModel):
    message: str
    session_id: str


class ChatResponse(BaseModel):
    response: str
    sources: List[str]


@app.post("/api/chat", response_model=ChatResponse, tags=["chat"])
async def chat(body: NewChatMessage):
    """
    Process a chat message using Text-to-SQL and return the response with sources.

    Args:
        body (NewChatMessage): The incoming chat message containing
        the message text and session ID.

    Returns:
        ChatResponse: The SQL-generated response along with the query as source.
    """
    # Add user's message to history
    user_message = (body.message, True)
    session_manager.add_message(body.session_id, user_message)

    # Process the query using Text-to-SQL engine
    sql_result = await sql_engine.process_query(body.message)

    # Format the response
    if "error" in sql_result:
        response = f"I encountered an error: {sql_result['error']}"
        sources = []
    else:
        results_text = format_results_as_markdown_table(sql_result["results"])
        response = (
            f"Based on your question, I ran the following SQL query:\n"
            f"```sql\n{wrap_sql(sql_result['query'])}\n```\n\n"
            f"**Rationale:** {sql_result['rationale']}\n"
            f"{results_text}"
        )
        sources = [sql_result["query"]]

    # Add AI's response to history
    ai_message = (response, False)
    session_manager.add_message(body.session_id, ai_message)

    return ChatResponse(response=response, sources=sources)


@app.get("/api/get-history", tags=["chat"])
async def get_history(session_id: str):
    """
    Retrieve the chat history for a given session.
    """
    history = session_manager.get_history(session_id)
    return history


# Mount static files (frontend)
app.mount("/", StaticFiles(directory="./static", html=True), name="frontend")
