from pydantic import BaseModel

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
    question: str
    answer: str