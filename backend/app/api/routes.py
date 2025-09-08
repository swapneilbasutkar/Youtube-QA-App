from fastapi import APIRouter, HTTPException
from app.models.schemas import (
    VideoRequest, QuestionRequest, VideoResponse, QuestionResponse
)
from app.stores.sessions import sessions
from app.utils.text import extract_video_id
from app.services.youtube import fetch_transcript
from app.services.qa import create_qa_chain

router = APIRouter()

@router.get("/")
async def root():
    return {"message": "Welcome to the Youtube Video Q&A API!"}

@router.get("/sessions")
async def list_sessions():
    return {
        "sessions": [
            {"session_id": sid, "video_id": data["video_id"], "url": data["url"]}
            for sid, data in sessions.items()
        ]
    }

@router.post("/process_video", response_model=VideoResponse)
async def process_video(request: VideoRequest):
    video_id = extract_video_id(request.youtube_url)
    if not video_id:
        raise HTTPException(status_code=400, detail="Invalid YouTube URL")

    transcript_flat = fetch_transcript(video_id)
    qa_chain = create_qa_chain(transcript_flat)

    session_id = f"session_{len(sessions) + 1}_{video_id}"
    sessions[session_id] = {
        "video_id": video_id,
        "url": request.youtube_url,
        "qa_chain": qa_chain,
        "transcript": transcript_flat,
    }
    return VideoResponse(session_id=session_id, video_id=video_id, message="Video processed successfully.")

@router.post("/ask_question", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest):
    session = sessions.get(request.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    qa_chain = session["qa_chain"]
    answer = qa_chain.invoke(request.question)
    return QuestionResponse(answer=answer, question=request.question)

@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    if session_id in sessions:
        del sessions[session_id]
        return {"message": f"Session {session_id} deleted successfully."}
    raise HTTPException(status_code=404, detail="Session not found")
