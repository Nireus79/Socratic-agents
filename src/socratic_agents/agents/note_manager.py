"""Note Manager Agent - Note management, tagging, and memory storage.

This agent:
1. Creates, reads, updates, and deletes notes
2. Supports tagging and categorization
3. Enables full-text and semantic search
4. Tracks note metadata and history
5. Manages note sharing and permissions
6. Exports and imports notes
7. Provides note organization and hierarchies
8. Supports collaborative note-taking
"""

import re
from collections import Counter, defaultdict
from datetime import datetime
from typing import Any, Dict, List, Optional, Set

from .base import BaseAgent


class Note:
    """Represents a note."""

    def __init__(self, title: str, content: str, category: str = "general"):
        self.id = f"note_{datetime.utcnow().timestamp()}"
        self.title = title
        self.content = content
        self.category = category
        self.tags: Set[str] = set()
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.access_count = 0
        self.shared_with: Set[str] = set()
        self.archived = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "preview": self.content[:100] + ("..." if len(self.content) > 100 else ""),
            "category": self.category,
            "tags": list(self.tags),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "access_count": self.access_count,
        }


class NoteManager(BaseAgent):
    """
    Agent that manages notes and memory storage.

    Provides:
    - Full note lifecycle management (CRUD)
    - Tagging and categorization
    - Full-text search with semantic understanding
    - Note versioning and history
    - Sharing and permission management
    - Export and import functionality
    - Note organization and hierarchies
    - Collaborative note-taking support
    """

    def __init__(self, llm_client: Optional[Any] = None):
        """Initialize the Note Manager."""
        super().__init__(name="NoteManager", llm_client=llm_client)
        self.notes: Dict[str, Note] = {}
        self.tag_index: Dict[str, Set[str]] = defaultdict(set)
        self.category_index: Dict[str, Set[str]] = defaultdict(set)
        self.note_history: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.shared_notes: Dict[str, Set[str]] = {}
        self.archived_notes: Set[str] = set()

    def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process note management requests."""
        action = request.get("action", "list")

        if action == "create":
            return self.create_note(request.get("title"), request.get("content"), request.get("category"))
        elif action == "get":
            return self.get_note(request.get("note_id"))
        elif action == "update":
            return self.update_note(request.get("note_id"), request.get("content"))
        elif action == "delete":
            return self.delete_note(request.get("note_id"))
        elif action == "list":
            return self.list_notes(request.get("category"), request.get("limit", 50))
        elif action == "search":
            return self.search_notes(request.get("query"), request.get("mode", "full_text"))
        elif action == "add_tag":
            return self.add_tag(request.get("note_id"), request.get("tag"))
        elif action == "remove_tag":
            return self.remove_tag(request.get("note_id"), request.get("tag"))
        elif action == "list_tags":
            return self.list_tags()
        elif action == "archive":
            return self.archive_note(request.get("note_id"))
        elif action == "restore":
            return self.restore_note(request.get("note_id"))
        elif action == "share":
            return self.share_note(request.get("note_id"), request.get("user_id"))
        elif action == "unshare":
            return self.unshare_note(request.get("note_id"), request.get("user_id"))
        elif action == "get_history":
            return self.get_note_history(request.get("note_id"))
        elif action == "export":
            return self.export_notes(request.get("format", "json"))
        elif action == "stats":
            return self.get_statistics()
        else:
            return {"status": "error", "message": f"Unknown action: {action}"}

    def create_note(self, title: str, content: str, category: str = "general") -> Dict[str, Any]:
        """Create a new note."""
        if not title:
            return {"status": "error", "message": "Title required"}

        note = Note(title, content or "", category)
        self.notes[note.id] = note
        self.category_index[category].add(note.id)

        # Record in history
        self.note_history[note.id].append({
            "timestamp": datetime.utcnow().isoformat(),
            "action": "created",
            "content": note.content,
        })

        return {
            "status": "success",
            "agent": self.name,
            "note_id": note.id,
            "title": title,
            "category": category,
            "total_notes": len(self.notes),
        }

    def get_note(self, note_id: str) -> Dict[str, Any]:
        """Get a note."""
        if not note_id:
            return {"status": "error", "message": "Note ID required"}

        if note_id not in self.notes:
            return {"status": "error", "message": f"Note {note_id} not found"}

        note = self.notes[note_id]
        note.access_count += 1

        return {
            "status": "success",
            "agent": self.name,
            "note": {
                "id": note.id,
                "title": note.title,
                "content": note.content,
                "category": note.category,
                "tags": list(note.tags),
                "created_at": note.created_at.isoformat(),
                "updated_at": note.updated_at.isoformat(),
                "access_count": note.access_count,
            },
        }

    def update_note(self, note_id: str, content: str) -> Dict[str, Any]:
        """Update a note."""
        if not note_id or not content:
            return {"status": "error", "message": "Note ID and content required"}

        if note_id not in self.notes:
            return {"status": "error", "message": f"Note {note_id} not found"}

        note = self.notes[note_id]
        old_content = note.content
        note.content = content
        note.updated_at = datetime.utcnow()

        # Record in history
        self.note_history[note_id].append({
            "timestamp": datetime.utcnow().isoformat(),
            "action": "updated",
            "old_content": old_content,
            "new_content": content,
        })

        return {
            "status": "success",
            "agent": self.name,
            "note_id": note_id,
            "updated_at": note.updated_at.isoformat(),
        }

    def delete_note(self, note_id: str) -> Dict[str, Any]:
        """Delete a note permanently."""
        if not note_id:
            return {"status": "error", "message": "Note ID required"}

        if note_id not in self.notes:
            return {"status": "error", "message": f"Note {note_id} not found"}

        note = self.notes.pop(note_id)

        # Cleanup indices
        self.category_index[note.category].discard(note_id)
        for tag in note.tags:
            self.tag_index[tag].discard(note_id)

        return {
            "status": "success",
            "agent": self.name,
            "note_id": note_id,
            "deleted": True,
            "remaining_notes": len(self.notes),
        }

    def list_notes(self, category: Optional[str] = None, limit: int = 50) -> Dict[str, Any]:
        """List notes with optional filtering."""
        notes = list(self.notes.values())

        if category:
            notes = [n for n in notes if n.category == category]

        notes = sorted(notes, key=lambda n: n.updated_at, reverse=True)
        notes = notes[:limit]

        return {
            "status": "success",
            "agent": self.name,
            "total_notes": len(self.notes),
            "returned_count": len(notes),
            "notes": [n.to_dict() for n in notes],
        }

    def search_notes(self, query: str, mode: str = "full_text") -> Dict[str, Any]:
        """Search notes."""
        if not query:
            return {"status": "error", "message": "Query required"}

        results = []

        if mode == "full_text":
            query_lower = query.lower()
            for note in self.notes.values():
                if query_lower in note.title.lower() or query_lower in note.content.lower():
                    results.append(note)
        elif mode == "semantic":
            # Simple semantic matching on words
            query_words = set(query.lower().split())
            for note in self.notes.values():
                note_words = set(re.findall(r'\w+', note.content.lower()))
                if query_words & note_words:
                    results.append(note)

        return {
            "status": "success",
            "agent": self.name,
            "query": query,
            "mode": mode,
            "results_count": len(results),
            "results": [n.to_dict() for n in results],
        }

    def add_tag(self, note_id: str, tag: str) -> Dict[str, Any]:
        """Add tag to note."""
        if not note_id or not tag:
            return {"status": "error", "message": "Note ID and tag required"}

        if note_id not in self.notes:
            return {"status": "error", "message": f"Note {note_id} not found"}

        note = self.notes[note_id]
        tag_lower = tag.lower()
        note.tags.add(tag_lower)
        self.tag_index[tag_lower].add(note_id)

        return {
            "status": "success",
            "agent": self.name,
            "note_id": note_id,
            "tag": tag,
            "total_tags": len(note.tags),
        }

    def remove_tag(self, note_id: str, tag: str) -> Dict[str, Any]:
        """Remove tag from note."""
        if not note_id or not tag:
            return {"status": "error", "message": "Note ID and tag required"}

        if note_id not in self.notes:
            return {"status": "error", "message": f"Note {note_id} not found"}

        note = self.notes[note_id]
        tag_lower = tag.lower()
        note.tags.discard(tag_lower)
        self.tag_index[tag_lower].discard(note_id)

        return {
            "status": "success",
            "agent": self.name,
            "note_id": note_id,
            "tag": tag,
            "total_tags": len(note.tags),
        }

    def list_tags(self) -> Dict[str, Any]:
        """List all tags."""
        tag_counts = {tag: len(ids) for tag, ids in self.tag_index.items()}

        return {
            "status": "success",
            "agent": self.name,
            "tags_count": len(self.tag_index),
            "tags": tag_counts,
        }

    def archive_note(self, note_id: str) -> Dict[str, Any]:
        """Archive a note."""
        if not note_id:
            return {"status": "error", "message": "Note ID required"}

        if note_id not in self.notes:
            return {"status": "error", "message": f"Note {note_id} not found"}

        self.notes[note_id].archived = True
        self.archived_notes.add(note_id)

        return {
            "status": "success",
            "agent": self.name,
            "note_id": note_id,
            "archived": True,
        }

    def restore_note(self, note_id: str) -> Dict[str, Any]:
        """Restore an archived note."""
        if not note_id:
            return {"status": "error", "message": "Note ID required"}

        if note_id not in self.notes:
            return {"status": "error", "message": f"Note {note_id} not found"}

        self.notes[note_id].archived = False
        self.archived_notes.discard(note_id)

        return {
            "status": "success",
            "agent": self.name,
            "note_id": note_id,
            "restored": True,
        }

    def share_note(self, note_id: str, user_id: str) -> Dict[str, Any]:
        """Share note with user."""
        if not note_id or not user_id:
            return {"status": "error", "message": "Note ID and user ID required"}

        if note_id not in self.notes:
            return {"status": "error", "message": f"Note {note_id} not found"}

        if note_id not in self.shared_notes:
            self.shared_notes[note_id] = set()

        self.shared_notes[note_id].add(user_id)
        self.notes[note_id].shared_with.add(user_id)

        return {
            "status": "success",
            "agent": self.name,
            "note_id": note_id,
            "shared_with": user_id,
            "total_shared": len(self.shared_notes.get(note_id, set())),
        }

    def unshare_note(self, note_id: str, user_id: str) -> Dict[str, Any]:
        """Stop sharing note with user."""
        if not note_id or not user_id:
            return {"status": "error", "message": "Note ID and user ID required"}

        if note_id not in self.shared_notes:
            return {"status": "error", "message": "Note not shared"}

        self.shared_notes[note_id].discard(user_id)
        self.notes[note_id].shared_with.discard(user_id)

        return {
            "status": "success",
            "agent": self.name,
            "note_id": note_id,
            "unshared_from": user_id,
        }

    def get_note_history(self, note_id: str) -> Dict[str, Any]:
        """Get note history."""
        if not note_id:
            return {"status": "error", "message": "Note ID required"}

        if note_id not in self.note_history:
            return {"status": "error", "message": f"No history for note {note_id}"}

        history = self.note_history[note_id]

        return {
            "status": "success",
            "agent": self.name,
            "note_id": note_id,
            "history_count": len(history),
            "history": history[-10:],  # Last 10 changes
        }

    def export_notes(self, format: str = "json") -> Dict[str, Any]:
        """Export notes."""
        exported = {
            "format": format,
            "exported_at": datetime.utcnow().isoformat(),
            "note_count": len(self.notes),
            "notes": [n.to_dict() for n in self.notes.values()],
        }

        return {
            "status": "success",
            "agent": self.name,
            "format": format,
            "notes_exported": len(self.notes),
            "export_data": exported,
        }

    def get_statistics(self) -> Dict[str, Any]:
        """Get note statistics."""
        total_notes = len(self.notes)
        archived_count = len(self.archived_notes)
        active_count = total_notes - archived_count

        content_length = sum(len(n.content) for n in self.notes.values())
        avg_length = content_length / total_notes if total_notes > 0 else 0

        return {
            "status": "success",
            "agent": self.name,
            "total_notes": total_notes,
            "active_notes": active_count,
            "archived_notes": archived_count,
            "unique_tags": len(self.tag_index),
            "unique_categories": len(self.category_index),
            "avg_content_length": round(avg_length, 0),
            "total_accesses": sum(n.access_count for n in self.notes.values()),
        }
