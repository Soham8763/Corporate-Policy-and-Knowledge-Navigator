import os
import re
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel, Field
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import tool, AgentExecutor, create_react_agent
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.memory import ConversationBufferMemory
import json

load_dotenv()

# --- Configuration Constants ---
CHROMA_PATH = "chroma"
MODEL = "sentence-transformers/all-MiniLM-L6-v2"
PROMPTS_PATH = "config/prompts"

# Load role-based prompts
def load_prompt_template(role):
    if role == "HR_Manager":
        prompt_file = "hr_role_prompt.txt"
    elif role == "IT_Admin":
        prompt_file = "it_admin_prompt.txt"
    else:
        prompt_file = "base_prompt.txt"

    file_path = os.path.join(PROMPTS_PATH, prompt_file)
    try:
        with open(file_path, "r") as f:
            return f.read()
    except FileNotFoundError:
        return ""

@tool
def search_knowledge_base(query: str) -> str:
    """
    Searches and returns relevant information from the company knowledge base.
    Use this tool to find and cite information from corporate policies, manuals, etc.
    The output includes citations like.
    """

    embedding_func = HuggingFaceEmbeddings(model_name=MODEL)
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_func)
    results = db.similarity_search_with_score(query, k=10)

    if not results:
        return "I could not find any relevant information for that query."

    context_with_citations = []
    for doc, score in results:
        source = doc.metadata.get('source', 'N/A')
        page = doc.metadata.get('page', 'N/A')
        context_with_citations.append(f"{doc.page_content}")

    return "\n\n---\n\n".join(context_with_citations)

class QueryRequest(BaseModel):
    question: str = Field(..., description="The question to ask the agent")
    chat_history: str = ""
    role: str = "Employee"

class QueryResponse(BaseModel):
    answer: str = Field(..., description="The agent's answer to the question.")

app = FastAPI(
    title="Corporate Knowledge Navigator API",
    description="An API for getting information from corporate documents.",
    version="1.0.0",
)

@app.post("/ask_agent", response_model=QueryResponse)
async def ask_agent_endpoint(request: QueryRequest) -> QueryResponse:
    prompt_template = load_prompt_template(request.role)
    if not prompt_template:
        # Fallback to a base template if file not found
        prompt_template = """
You are the Corporate Knowledge Navigator, a helpful assistant for employees. Your goal is to answer questions based on the corporate policy documents and manuals provided to you.
...
(rest of the base template)
"""

    prompt = PromptTemplate.from_template(prompt_template)

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-pro",
        temperature=0,
        google_api_key=os.getenv("GOOGLE_API_KEY")
    )

    tools = [search_knowledge_base]
    agent = create_react_agent(llm, tools, prompt)

    # Corrected way to handle chat history
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        input_key="input",
        return_messages=True,
        chat_memory=request.chat_history
    )

    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True,
        memory=memory
    )

    response = await agent_executor.ainvoke({"input": request.question})
    return QueryResponse(answer=response["output"])

# The original REACT_PROMPT_TEMPLATE is kept as a fallback.
REACT_PROMPT_TEMPLATE = """
You are the Corporate Knowledge Navigator, a helpful assistant for employees. Your goal is to answer questions based on the corporate policy documents and manuals provided to you.
...
(rest of the original prompt)
"""