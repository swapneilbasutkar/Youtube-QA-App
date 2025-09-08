import re
import os
from typing import Dict, List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Youtube Video Q&A API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class VideoRequest(BaseModel):
    youtube_url: str

class QuestionRequest(BaseModel):
    session_id: str
    question: str

class VideoResponse(BaseModel):
    session_id: str
    video_id: str
    title: str = "Youtube Video"
    message: str

class QuestionResponse(BaseModel):
    answer: str
    question: str

# In-memory session store
sessions: Dict[str, Dict] = {}

def format_docs(retrieved_docs):
    """Formats retrieved documents into a single context string."""
    return "\n".join([doc.page_content for doc in retrieved_docs])

def extract_video_id(youtube_url: str) -> str:
    """Extracts the video ID from a YouTube URL."""
    match = re.search(r'v=([^&]+)', youtube_url)
    if match:
        return match.group(1)
    return None

def create_qa_chain(transcript: str):
    """Creates a QA chain for the given video ID."""
    # Chunk the transcript
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = splitter.create_documents([transcript])

    # Create embeddings and vector store
    embedding_model = OpenAIEmbeddings(model="text-embedding-3-small")
    vector_store = FAISS.from_documents(chunks, embedding_model)
    retriever = vector_store.as_retriever(search_type='similarity', search_kwargs={"k": 4})

    # Create LLM and prompt
    llm_model = ChatOpenAI(model='gpt-4o-mini', temperature=0.2)
    prompt = PromptTemplate(
        template="""
            You are a helpful assistant.
            Answer ONLY from the provided transcript context.
            If the context is insufficient, just say you don't know.

            {context}
            Question: {question}
            """,
        input_variables=['context', 'question']
    )

    # Wire the chain
    parallel_chain = RunnableParallel({
        'context': retriever | RunnableLambda(format_docs),
        'question': RunnablePassthrough()
    })

    parser = StrOutputParser()
    qa_chain = parallel_chain | prompt | llm_model | parser
    return qa_chain

@app.get("/")
async def root():
    return {"message": "Welcome to the Youtube Video Q&A API!"}

@app.get("/sessions")
async def list_sessions():
    return {
        "sessions": [
            {"session_id": sid, "video_id": data["video_id"], "url": data["url"]}
            for sid, data in sessions.items()
        ]
    }

@app.post("/process_video", response_model=VideoResponse)
async def process_video(request: VideoRequest):
    """Process a Youtube video and create a QA chain"""
    try:
        video_id = extract_video_id(request.youtube_url)
        if not video_id:
            raise HTTPException(status_code=400, detail="Invalid YouTube URL")

        try:
            fetched_transcript = YouTubeTranscriptApi().fetch(video_id=video_id, languages=['en'])
            transcript_flat = " ".join(snippet.text for snippet in fetched_transcript)
        except TranscriptsDisabled:
            raise HTTPException(status_code=404, detail="No captions available for this video")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

        qa_chain = create_qa_chain(transcript_flat)

        session_id = f"session_{len(sessions) + 1}_{video_id}"
        sessions[session_id] = {
            "video_id": video_id,
            "url": request.youtube_url,
            "qa_chain": qa_chain,
            "transcript": transcript_flat
        }

        return VideoResponse(session_id=session_id, video_id=video_id, message="Video processed successfully.")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/ask_question", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest):
    """Ask a question about the processed video"""
    try:
        session = sessions.get(request.session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        qa_chain = session["qa_chain"]
        answer = qa_chain.invoke(request.question)

        return QuestionResponse(answer=answer, question=request.question)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """Delete a video processing session"""
    if session_id in sessions:
        del sessions[session_id]
        return {"message": f"Session {session_id} deleted successfully."}
    else:
        raise HTTPException(status_code=404, detail="Session not found")
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
