#!/usr/bin/env python3
"""Monolithic Pattern Example: Question Generation Workflow"""

from datetime import datetime, timezone

class MockProject:
    def __init__(self):
        self.phase = "discovery"
        self.name = "Python Calculator"
        self.goals = []
        self.conversation_history = [
            {
                "type": "user",
                "content": "I want to build a calculator",
                "phase": "discovery",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
            {
                "type": "assistant",
                "content": "What is the main purpose of this calculator?",
                "phase": "discovery",
                "response_turn": 1,
            },
        ]

def extract_recently_asked(project, phase):
    """Extract previously asked questions (MONOLITHIC PATTERN)."""
    return [
        msg.get("content")
        for msg in project.conversation_history
        if msg.get("type") == "assistant" and msg.get("phase") == phase
    ]

def demonstrate_pattern():
    """Demonstrate the question generation pattern."""
    project = MockProject()
    
    # Extract recently asked (filter by type and phase)
    recently_asked = extract_recently_asked(project, project.phase)
    print(f"Recently asked ({len(recently_asked)}): {recently_asked}")
    
    # Generate new question (would call counselor.process)
    new_question = "What features should it support?"
    
    # Store in conversation_history (CRITICAL)
    project.conversation_history.append({
        "type": "assistant",
        "content": new_question,
        "phase": project.phase,
        "response_turn": len([m for m in project.conversation_history if m.get("type") == "assistant"]) + 1,
    })
    
    print(f"\nGenerated: {new_question}")
    print(f"Stored in conversation_history\n")
    
    # Next generation will see this question
    recently_asked_v2 = extract_recently_asked(project, project.phase)
    print(f"Next request will see: {recently_asked_v2}")
    print("✓ Pattern prevents repetition!")

if __name__ == "__main__":
    demonstrate_pattern()
