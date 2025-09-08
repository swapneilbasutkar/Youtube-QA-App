import re

def format_docs(retrieved_docs):
    """Formats retrieved documents into a single context string."""
    return "\n".join([doc.page_content for doc in retrieved_docs])

def extract_video_id(youtube_url: str) -> str:
    """Extracts the video ID from a YouTube URL."""
    match = re.search(r'v=([^&]+)', youtube_url)
    if match:
        return match.group(1)
    return None