from typing import Dict, Any

# In-memory store (swap with Redis/DB later)
sessions: Dict[str, Dict[str, Any]] = {}
