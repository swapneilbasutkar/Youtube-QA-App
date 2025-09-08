from fastapi import HTTPException
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled

def fetch_transcript(video_id: str) -> str:
    """Fetches the transcript for a given YouTube video ID."""
    try:
        fetched_transcript = YouTubeTranscriptApi().fetch(video_id=video_id, languages=['en'])
        return " ".join(snippet.text for snippet in fetched_transcript)
    except TranscriptsDisabled:
        raise HTTPException(status_code=404, detail="No captions available for this video")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))