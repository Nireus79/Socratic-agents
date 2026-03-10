"""Note Manager Agent - Note and memory management."""

from typing import Any, Dict, Optional

from .base import BaseAgent


class NoteManager(BaseAgent):
    """Agent that manages notes and memory."""

    def __init__(self, llm_client: Optional[Any] = None):
        """Initialize the Note Manager."""
        super().__init__(name="NoteManager", llm_client=llm_client)
        self.notes: Dict[str, Any] = {}
        self.note_count = 0

    def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process note management requests."""
        action = request.get("action", "list")
        if action == "create":
            return self.create_note(request.get("title"), request.get("content"))  # type: ignore[arg-type]
        elif action == "get":
            return self.get_note(request.get("note_id"))  # type: ignore[arg-type]
        elif action == "update":
            return self.update_note(request.get("note_id"), request.get("content"))  # type: ignore[arg-type]
        elif action == "list":
            return self.list_notes()
        else:
            return {"status": "error", "message": f"Unknown action: {action}"}

    def create_note(self, title: str, content: str) -> Dict[str, Any]:
        """Create a new note."""
        if not title:
            return {"status": "error", "message": "Title required"}
        note_id = f"note_{self.note_count + 1}"
        self.notes[note_id] = {
            "title": title,
            "content": content or "",
            "created_at": str(self.created_at),
        }
        self.note_count += 1
        return {
            "status": "success",
            "agent": self.name,
            "note_id": note_id,
            "total_notes": len(self.notes),
        }

    def get_note(self, note_id: str) -> Dict[str, Any]:
        """Get a note."""
        if not note_id:
            return {"status": "error", "message": "Note ID required"}
        if note_id not in self.notes:
            return {"status": "error", "message": f"Note {note_id} not found"}
        return {"status": "success", "agent": self.name, "note": self.notes[note_id]}

    def update_note(self, note_id: str, content: str) -> Dict[str, Any]:
        """Update note content."""
        if not note_id or not content:
            return {"status": "error", "message": "Note ID and content required"}
        if note_id not in self.notes:
            return {"status": "error", "message": f"Note {note_id} not found"}
        self.notes[note_id]["content"] = content
        return {"status": "success", "agent": self.name, "note_id": note_id, "updated": True}

    def list_notes(self) -> Dict[str, Any]:
        """List all notes."""
        note_list = [{"id": nid, "title": n["title"]} for nid, n in self.notes.items()]
        return {
            "status": "success",
            "agent": self.name,
            "notes": note_list,
            "note_count": len(self.notes),
        }
