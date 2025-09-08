# YouTube Video Q&A Application

A full-stack application that allows users to ask questions about YouTube videos using AI. Built with FastAPI backend and Streamlit frontend.

## Features

- 🎥 Process YouTube videos with transcripts
- 💬 Ask questions about video content
- 🎯 AI-powered answers based on video transcripts
- 💾 Multiple session support
- 🔄 Chat history for each session
- 🗑️ Session management (create/delete)

## Setup Instructions

### Prerequisites

- Python 3.8+
- OpenAI API key
- YouTube videos with available transcripts

### Installation

1. **Clone or create the project files**

   ```bash
   mkdir youtube-qa-app
   cd youtube-qa-app
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Setup**
   Create a `.env` file in the root directory:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   ```

### Running the Application

#### Method 1: Separate Terminals (without Docker)

1. **Start the FastAPI Backend**

   ```bash
   python main.py
   ```

   The backend will be available at: http://localhost:8000

2. **Start the Streamlit Frontend** (in a new terminal)
   ```bash
   streamlit run streamlit_app.py
   ```
   The frontend will be available at: http://localhost:8501

#### Method 2: Run with Docker (Recommended)

1. **Create a .env file in root directory:**

   ```bash
   OPENAI_API_KEY=your_openai_api_key_here
   ```

2. **Build and run containers**

   ```bash
   docker compose up --build
   ```

3. **Access the app**

   - Streamlit frontend → http://localhost:8501
   - FastAPI backend → http://localhost:8000

4. **Stop container**
   ```bash
   docker compose down
   ```

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### File Structure

```
youtube-qa-app/
├── main.py                 # FastAPI backend
├── streamlit_app.py        # Streamlit frontend
├── requirements.txt        # Python dependencies
├── .env                   # Environment variables
└── README.md              # This file
```

## Usage

1. **Open the Streamlit app** in your browser (http://localhost:8501)

2. **Process a YouTube video:**

   - Paste a YouTube URL in the sidebar
   - Click "Process Video"
   - Wait for processing to complete

3. **Ask questions:**

   - Type questions in the chat input
   - Get AI-powered answers based on the video transcript

4. **Manage sessions:**
   - Switch between different video sessions
   - Delete sessions when done

## API Endpoints

The FastAPI backend provides the following endpoints:

- `GET /` - Health check
- `POST /process_video` - Process a YouTube video
- `POST /ask_question` - Ask a question about a processed video
- `GET /sessions` - List all active sessions
- `DELETE /sessions/{session_id}` - Delete a specific session

## Configuration

### Backend Configuration

The backend can be configured by modifying variables in `main.py`:

- **LLM Model**: Change `gpt-4o-mini` to other OpenAI models
- **Embedding Model**: Modify `text-embedding-3-small`
- **Chunk Size**: Adjust `chunk_size=1000` for different text splitting
- **Temperature**: Modify `temperature=0.2` for response creativity

### Frontend Configuration

Modify `API_BASE_URL` in `streamlit_app.py` if running backend on different host/port.

## Troubleshooting

### Common Issues

1. **"No captions available for this video"**

   - The YouTube video doesn't have transcripts/captions
   - Try a different video with captions enabled

2. **Connection errors**

   - Ensure the FastAPI backend is running
   - Check the API_BASE_URL in streamlit_app.py

3. **OpenAI API errors**

   - Verify your OPENAI_API_KEY in .env file
   - Check your OpenAI account has sufficient credits

4. **Import errors**
   - Ensure all dependencies are installed: `pip install -r requirements.txt`

### Performance Notes

- First question for each video may take longer (embedding creation)
- Subsequent questions are faster (cached embeddings)
- Session data is stored in memory (will be lost on restart)

## Production Deployment

For production deployment:

1. **Use a proper database** instead of in-memory storage
2. **Add authentication** and rate limiting
3. **Use Redis** for session caching
4. **Configure CORS** properly for your domain
5. **Use environment-specific configurations**
6. **Add logging and monitoring**

## Dependencies

Key dependencies:

- **FastAPI**: Web framework for the API
- **Streamlit**: Frontend framework
- **LangChain**: LLM orchestration framework
- **OpenAI**: Language model and embeddings
- **FAISS**: Vector database for semantic search
- **YouTube Transcript API**: Fetching video transcripts
