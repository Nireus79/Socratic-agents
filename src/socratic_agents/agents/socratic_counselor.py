"""Socratic Counselor Agent - Complete Dialogue Orchestration Engine.

This module provides complete Socratic dialogue orchestration, handling:
- Question generation with full state management
- Answer processing with insight extraction
- Conflict detection and resolution
- Maturity tracking and phase advancement
- User management and subscription validation
- Database persistence
"""

import datetime
import logging
import uuid
from typing import Any, Dict, List, Optional

from .base import BaseAgent


class SocraticCounselor(BaseAgent):
    """
    Complete Socratic dialogue orchestration engine.

    Handles the full lifecycle of Socratic dialogue:
    - Generates contextual questions with knowledge base awareness
    - Processes user responses and extracts insights
    - Detects and resolves specification conflicts
    - Tracks learning progress and phase completion
    - Manages user state and subscription limits

    This is the core orchestration component extracted from the monolithic
    Socratic system and adapted to work as a standalone library.
    """

    def __init__(
        self,
        llm_client: Optional[Any] = None,
        batch_size: int = 1,
        database: Optional[Any] = None,
        logger: Optional[Any] = None,
    ):
        """
        Initialize the Socratic Counselor.

        Args:
            llm_client: LLM client for question and insight generation
            batch_size: Number of questions to generate per request (default: 1)
            database: Optional database client for persistence (will be passed as needed)
            logger: Optional logger instance (uses logging module if not provided)
        """
        super().__init__(name="SocraticCounselor", llm_client=llm_client)
        self.batch_size = max(1, batch_size)
        self.database = database
        self.logger = logger or logging.getLogger("socratic_counselor")
        self.use_dynamic_questions = True
        self.max_questions_per_phase = 5

    def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Route request to appropriate handler (question generation, response processing, etc).

        Args:
            request: Dict with 'action' specifying what to do plus action-specific params

        Returns:
            Dict with status and action-specific results
        """
        action = request.get("action", "generate_question")

        if action == "generate_question":
            return self._generate_question(request)
        elif action == "process_response":
            return self._process_response(request)
        elif action == "extract_insights":
            return self._extract_insights(request)
        elif action == "detect_conflicts":
            return self._handle_conflict_detection(request)
        elif action == "check_phase_completion":
            return self._check_phase_completion(request)
        elif action == "advance_phase":
            return self._advance_phase(request)
        elif action == "generate_hint":
            return self._generate_hint(request)
        else:
            return {"status": "error", "message": f"Unknown action: {action}"}

    # ===== CRITICAL METHODS: QUESTION GENERATION =====

    def _generate_question(self, request: Dict) -> Dict:
        """
        Generate next Socratic question with full orchestration.

        This is the CRITICAL method that handles the complete question generation
        workflow including state management, persistence, and user tracking.

        Steps:
        1. Check for existing unanswered question (prevent double generation)
        2. Get/create user with auto-creation for local users
        3. Validate subscription limits
        4. Gather KB context
        5. Generate question (dynamic or static)
        6. Store in BOTH conversation_history AND pending_questions
        7. Update user metrics
        8. Save to database

        Args:
            request: Dict with:
                - 'project': ProjectContext object
                - 'user_id': String user identifier
                - 'force_refresh': Bool (optional) - regenerate even if unanswered exists
                - 'knowledge_base': Dict (optional) - KB context with chunks/gaps

        Returns:
            Dict with status, question text, and existing flag
        """
        project = request.get("project")
        user_id = request.get("user_id", "default_user")
        force_refresh = request.get("force_refresh", False)
        kb_context = request.get("knowledge_base", {})
        doc_understanding = request.get("document_understanding")
        conversation_context = request.get("conversation_context", "")
        recently_asked = request.get("recently_asked", [])

        # Validate project
        if not project:
            return {"status": "error", "message": "Project context required"}

        # STEP 1: Check for existing unanswered question
        if not force_refresh and hasattr(project, "pending_questions") and project.pending_questions:
            unanswered = [q for q in project.pending_questions if q.get("status") == "unanswered"]
            if unanswered:
                self.logger.debug(f"Returning existing unanswered question for {user_id}")
                return {
                    "status": "success",
                    "question": unanswered[0].get("question"),
                    "existing": True,
                }

        # STEP 2: Get or create user
        user = None
        if self.database:
            user = self.database.load_user(user_id)

        if user is None:
            # Auto-create user with pro tier for local/CLI use
            user = self._create_default_user(user_id)
            self.logger.debug(f"Auto-created user: {user_id}")
            if self.database:
                self.database.save_user(user)

        # STEP 3: Validate subscription
        can_ask, error_msg = self._check_subscription_limit(user)
        if not can_ask:
            return {"status": "error", "message": error_msg}

        # STEP 4: Count questions in phase (for context)
        phase_questions = []
        if hasattr(project, "conversation_history"):
            phase_questions = [
                msg for msg in project.conversation_history
                if msg.get("type") == "assistant" and msg.get("phase") == project.phase
            ]

        # STEP 5: Generate question
        if self.use_dynamic_questions:
            question = self._generate_dynamic_question(
                project,
                len(phase_questions),
                user_id,
                kb_context=kb_context,
                doc_understanding=doc_understanding,
                conversation_context=conversation_context,
                recently_asked=recently_asked,
            )
        else:
            question = self._generate_static_question(project, len(phase_questions))

        if not question:
            return {"status": "error", "message": "Failed to generate question"}

        # STEP 6a: Store in conversation_history
        if hasattr(project, "conversation_history"):
            project.conversation_history.append({
                "timestamp": datetime.datetime.now().isoformat(),
                "type": "assistant",
                "content": question,
                "phase": project.phase,
                "question_number": len(phase_questions) + 1,
            })

        # STEP 6b: Store in pending_questions (unified tracking)
        if not hasattr(project, "pending_questions"):
            project.pending_questions = []

        project.pending_questions.append({
            "id": f"q_{uuid.uuid4().hex[:8]}",
            "question": question,
            "phase": project.phase,
            "status": "unanswered",
            "created_at": datetime.datetime.now().isoformat(),
            "answer": None,
            "answered_at": None,
        })

        # STEP 7: Update user metrics
        if hasattr(user, "increment_question_usage"):
            user.increment_question_usage()
        elif hasattr(user, "questions"):
            if not isinstance(user.questions, list):
                user.questions = []
            user.questions.append(question)

        if self.database:
            self.database.save_user(user)

        # STEP 8: Save project to database
        if self.database:
            self.database.save_project(project)

        self.logger.info(f"Generated question for {user_id} in phase {project.phase}")
        return {"status": "success", "question": question}

    # ===== CRITICAL METHODS: RESPONSE PROCESSING =====

    def _process_response(self, request: Dict) -> Dict:
        """
        Process user response with full orchestration.

        This is the CRITICAL method that handles answer processing including
        insight extraction, conflict detection, maturity updates, and NEXT QUESTION
        GENERATION.

        Steps:
        1. Add response to conversation_history
        2. Extract insights from response
        3. Mark question as answered (BEFORE conflict detection!)
        4. Detect conflicts (early return if found)
        5. Update project maturity
        6. Track question effectiveness
        7. Check phase completion
        8. Generate NEXT question
        9. Save to database

        Args:
            request: Dict with:
                - 'project': ProjectContext object
                - 'user_id': String user identifier
                - 'response': String user response
                - 'knowledge_base': Dict (optional) - KB context

        Returns:
            Dict with insights, next_question, phase status, conflicts if any
        """
        project = request.get("project")
        user_id = request.get("user_id", "default_user")
        user_response = request.get("response", "")
        kb_context = request.get("knowledge_base", {})

        if not project or not user_response:
            return {"status": "error", "message": "Project and response required"}

        debug_log = []

        # STEP 1: Add to conversation_history
        if hasattr(project, "conversation_history"):
            project.conversation_history.append({
                "timestamp": datetime.datetime.now().isoformat(),
                "type": "user",
                "content": user_response,
                "phase": project.phase,
                "author": user_id,
            })
            debug_log.append("response_added")

        # STEP 2: Extract insights
        insights = self._extract_insights_only({"response": user_response, "project": project})
        insights_data = insights.get("insights", {})
        debug_log.append(f"insights_extracted")

        # STEP 3: CRITICAL - Mark question answered BEFORE conflict detection
        if hasattr(project, "pending_questions") and project.pending_questions:
            for q in reversed(project.pending_questions):
                if q.get("status") == "unanswered":
                    q["status"] = "answered"
                    q["answered_at"] = datetime.datetime.now().isoformat()
                    q["answer"] = user_response
                    debug_log.append("question_marked_answered")
                    break

        # STEP 4: Conflict detection
        conflicts = self._handle_conflict_detection(
            {"project": project, "insights": insights_data}
        )
        conflicts_found = conflicts.get("conflicts_found", [])

        if conflicts_found:
            debug_log.append(f"conflicts_detected_{len(conflicts_found)}")
            if self.database:
                self.database.save_project(project)

            return {
                "status": "success",
                "insights": insights_data,
                "conflicts_found": conflicts_found,
                "conflicts_pending": True,
                "debug_summary": ", ".join(debug_log),
            }

        # STEP 5: Update maturity
        self._update_project_maturity(project, insights_data)
        debug_log.append("maturity_updated")

        # STEP 6: Track effectiveness
        self._track_question_effectiveness(project, user_response, insights_data, user_id)
        debug_log.append("effectiveness_tracked")

        # STEP 7: Check phase completion
        phase_complete = self._check_phase_completion_internal(project)
        if phase_complete:
            debug_log.append("phase_complete")

        # STEP 8: Generate NEXT question (CRITICAL!)
        next_question_result = self._generate_question({
            "project": project,
            "user_id": user_id,
            "force_refresh": True,
            "knowledge_base": kb_context,
        })
        next_question = next_question_result.get("question") if next_question_result.get("status") == "success" else None
        debug_log.append("next_question_generated")

        # STEP 9: Save to database
        if self.database:
            self.database.save_project(project)

        self.logger.info(f"Processed response for {user_id}, generated next question")

        return {
            "status": "success",
            "insights": insights_data,
            "next_question": next_question,
            "phase_complete": phase_complete,
            "debug_summary": ", ".join(debug_log),
        }

    # ===== INSIGHT EXTRACTION =====

    def _extract_insights_only(self, request: Dict) -> Dict:
        """
        Extract insights from user response without processing.

        Args:
            request: Dict with 'response' and optionally 'project'

        Returns:
            Dict with extracted insights and confidence
        """
        response = request.get("response", "")
        project = request.get("project")

        if not response:
            return {"status": "error", "message": "Response required", "insights": {}}

        self.logger.debug(f"Extracting insights ({len(response)} chars)")

        # Use LLM to extract insights if available
        if self.llm_client:
            try:
                prompt = f"""Extract key specifications, requirements, and insights from this response:

Response: {response}

Format as structured data. Return as JSON with keys like:
- specifications: list of spec items
- requirements: list of requirements
- gaps: list of knowledge gaps identified
- questions: follow-up questions

Return ONLY the JSON, no explanation."""

                insights_text = self.llm_client.generate_response(prompt)

                # Parse as dict if possible
                if isinstance(insights_text, str):
                    import json
                    try:
                        insights = json.loads(insights_text)
                    except:
                        insights = {"raw_response": insights_text}
                else:
                    insights = insights_text or {}

                return {"status": "success", "insights": insights}
            except Exception as e:
                self.logger.warning(f"Failed to extract insights: {e}")

        # Fallback: return basic extraction
        return {
            "status": "success",
            "insights": {
                "raw_response": response,
                "length": len(response),
                "confidence": 0.5,
            }
        }

    # ===== CONFLICT DETECTION =====

    def _handle_conflict_detection(self, request: Dict) -> Dict:
        """
        Detect conflicts in extracted insights.

        Args:
            request: Dict with 'project' and 'insights'

        Returns:
            Dict with conflicts_found list and has_conflicts flag
        """
        project = request.get("project")
        insights = request.get("insights", {})

        # Simple conflict detection: check for contradictions
        conflicts_found = []

        # If we have LLM capability, use it for smarter detection
        if self.llm_client and project:
            try:
                conflict_prompt = f"""Analyze these insights for conflicts with existing project context:

Existing context: {project.description if hasattr(project, 'description') else 'N/A'}

New insights: {str(insights)}

List any contradictions, conflicts, or inconsistencies found.
Return as JSON with 'conflicts' list and 'severity' per conflict."""

                conflict_response = self.llm_client.generate_response(conflict_prompt)

                if conflict_response:
                    import json
                    try:
                        conflict_data = json.loads(conflict_response)
                        conflicts_found = conflict_data.get("conflicts", [])
                    except:
                        pass

            except Exception as e:
                self.logger.debug(f"Conflict detection error: {e}")

        return {
            "status": "success",
            "conflicts_found": conflicts_found,
            "has_conflicts": len(conflicts_found) > 0,
        }

    # ===== SUPPORTING METHODS =====

    def _generate_dynamic_question(
        self,
        project: Any,
        question_count: int,
        user_id: str = "default",
        kb_context: Optional[Dict] = None,
        doc_understanding: Optional[Dict] = None,
        conversation_context: str = "",
        recently_asked: Optional[List[str]] = None,
    ) -> str:
        """
        Generate contextual question using KB and conversation context.

        Args:
            project: ProjectContext
            question_count: Number of questions already asked
            user_id: User identifier
            kb_context: Knowledge base context dict
            doc_understanding: Document analysis
            conversation_context: Conversation summary
            recently_asked: Questions to avoid

        Returns:
            Generated question string
        """
        recently_asked = recently_asked or []

        # If KB context available, use it
        if kb_context and kb_context.get("chunks"):
            question = self._generate_kb_aware_question(
                topic=getattr(project, "name", "the project"),
                level="intermediate",
                phase=getattr(project, "phase", "discovery"),
                kb_context=kb_context,
                conversation_context=conversation_context,
                recently_asked=recently_asked,
            )
            if question:
                return question

        # Fallback to phase-appropriate question
        phase = getattr(project, "phase", "discovery")
        topic = getattr(project, "name", "the project")

        return self._get_fallback_question(topic, "intermediate", phase)

    def _generate_static_question(self, project: Any, question_count: int) -> str:
        """
        Generate static question when dynamic generation unavailable.

        Args:
            project: ProjectContext
            question_count: Number of questions already asked

        Returns:
            Static question string
        """
        phase = getattr(project, "phase", "discovery")
        topic = getattr(project, "name", "the project")

        static_questions = {
            "discovery": [
                f"What specific problem does {topic} solve?",
                f"Who is your target audience for {topic}?",
                f"What are the core features you envision?",
            ],
            "analysis": [
                f"What technical challenges do you anticipate?",
                f"What are your performance requirements?",
                f"How will you validate your solution?",
            ],
            "design": [
                f"How would you structure {topic}?",
                f"What components does {topic} need?",
                f"What design patterns apply?",
            ],
            "implementation": [
                f"What's the first step to implement?",
                f"What tools would you use?",
                f"How would you test {topic}?",
            ],
        }

        phase_questions = static_questions.get(phase, static_questions["discovery"])
        idx = min(question_count, len(phase_questions) - 1)
        return phase_questions[idx]

    def _generate_kb_aware_question(
        self,
        topic: str,
        level: str,
        phase: str,
        kb_context: Dict[str, Any],
        conversation_context: str = "",
        recently_asked: Optional[List[str]] = None,
    ) -> Optional[str]:
        """
        Generate question using KB chunks and gaps.

        Args:
            topic: Topic to ask about
            level: Difficulty level
            phase: Project phase
            kb_context: KB context with chunks and gaps
            conversation_context: Conversation summary
            recently_asked: Questions to avoid

        Returns:
            KB-aware question or None
        """
        if not self.llm_client:
            return None

        recently_asked = recently_asked or []

        try:
            chunks = kb_context.get("chunks", [])
            gaps = kb_context.get("gaps", [])

            chunk_snippets = []
            if chunks:
                for chunk in chunks[:3]:
                    content = chunk.get("content", str(chunk)) if isinstance(chunk, dict) else str(chunk)
                    chunk_snippets.append(content[:200])

            chunks_context = (
                "\n".join([f"- {s}" for s in chunk_snippets])
                if chunk_snippets
                else "No document context available"
            )

            gaps_context = ""
            if gaps:
                gap_list = [g.get("topic", str(g)) if isinstance(g, dict) else str(g) for g in gaps[:3]]
                gaps_context = f"\nKnowledge gaps: {', '.join(gap_list)}"

            prompt = f"""Generate ONE Socratic question about "{topic}" at {level} level.

Project Phase: {phase}
Available Context:\n{chunks_context}{gaps_context}

Conversation: {conversation_context if conversation_context else "Starting fresh"}

Guidelines:
- Ground in specific project context
- Help discover, don't answer directly
- Address knowledge gaps if identified
- Make it specific, not generic

Return ONLY the question, nothing else."""

            if recently_asked:
                prompt += "\n\nDo NOT ask:\n" + "\n".join([f"- {q}" for q in recently_asked[:5]])

            response = self.llm_client.generate_response(prompt)
            if response:
                question = response.strip()
                if question:
                    return question

        except Exception as e:
            self.logger.warning(f"KB-aware question generation failed: {e}")

        return None

    def _get_fallback_question(self, topic: str, level: str, phase: str) -> str:
        """Get fallback question when generation unavailable."""
        fallback_questions = {
            "discovery": [
                f"What is the main purpose of {topic}?",
                f"Who are the primary users?",
                f"What problem does this solve?",
            ],
            "analysis": [
                f"What are the main requirements?",
                f"What constraints apply?",
                f"How will this be measured?",
            ],
            "design": [
                f"How would you structure this?",
                f"What components are needed?",
                f"What architecture would fit?",
            ],
            "implementation": [
                f"What's the first step?",
                f"What tools would you use?",
                f"How would you test this?",
            ],
        }

        questions = fallback_questions.get(phase, fallback_questions["discovery"])
        return questions[0] if questions else "Tell me more."

    def _update_project_maturity(self, project: Any, insights: Dict) -> None:
        """
        Update project maturity based on insights.

        Args:
            project: ProjectContext
            insights: Extracted insights dict
        """
        if not hasattr(project, "maturity_scores"):
            project.maturity_scores = {}

        # Simple maturity update: increase by response quality
        current_phase = getattr(project, "phase", "discovery")
        current_maturity = project.maturity_scores.get(current_phase, 0)

        # Increase maturity based on insight count
        insight_count = len(str(insights).split()) / 10  # Rough estimate
        new_maturity = min(100, current_maturity + insight_count)

        project.maturity_scores[current_phase] = new_maturity
        self.logger.debug(f"Updated maturity for {current_phase}: {new_maturity:.1f}%")

    def _track_question_effectiveness(
        self,
        project: Any,
        response: str,
        insights: Dict,
        user_id: str,
    ) -> None:
        """
        Track how effective the question was for learning.

        Args:
            project: ProjectContext
            response: User's response
            insights: Extracted insights
            user_id: User identifier
        """
        if not hasattr(project, "question_effectiveness"):
            project.question_effectiveness = []

        effectiveness = {
            "timestamp": datetime.datetime.now().isoformat(),
            "user_id": user_id,
            "response_length": len(response),
            "insights_count": len(str(insights).split()),
            "effectiveness_score": min(100, len(response) / 10),
        }

        project.question_effectiveness.append(effectiveness)
        self.logger.debug(f"Tracked effectiveness: {effectiveness['effectiveness_score']:.1f}")

    def _check_phase_completion_internal(self, project: Any) -> bool:
        """
        Check if current phase is complete based on maturity.

        Args:
            project: ProjectContext

        Returns:
            True if phase complete, False otherwise
        """
        if not hasattr(project, "maturity_scores"):
            return False

        current_phase = getattr(project, "phase", "discovery")
        maturity = project.maturity_scores.get(current_phase, 0)

        # Phase complete when maturity reaches threshold
        threshold = 70  # 70% maturity needed to advance
        is_complete = maturity >= threshold

        if is_complete:
            self.logger.info(f"Phase {current_phase} complete at {maturity:.1f}% maturity")

        return is_complete

    def _check_phase_completion(self, request: Dict) -> Dict:
        """Check phase completion."""
        project = request.get("project")
        if not project:
            return {"is_complete": False}

        is_complete = self._check_phase_completion_internal(project)
        return {
            "status": "success",
            "is_complete": is_complete,
            "current_phase": getattr(project, "phase", "discovery"),
            "maturity": project.maturity_scores.get(getattr(project, "phase", "discovery"), 0) if hasattr(project, "maturity_scores") else 0,
        }

    def _advance_phase(self, request: Dict) -> Dict:
        """Advance project to next phase."""
        project = request.get("project")
        if not project:
            return {"status": "error", "message": "Project required"}

        current = getattr(project, "phase", "discovery")
        phases = ["discovery", "analysis", "design", "implementation"]

        try:
            idx = phases.index(current)
            next_phase = phases[idx + 1] if idx + 1 < len(phases) else current

            if hasattr(project, "phase"):
                project.phase = next_phase

            self.logger.info(f"Advanced from {current} to {next_phase}")
            return {"status": "success", "previous_phase": current, "new_phase": next_phase}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def _generate_hint(self, request: Dict) -> Dict:
        """Generate hint for current question."""
        project = request.get("project")

        if self.llm_client and project:
            try:
                hint_prompt = f"""Generate a helpful hint for working on {getattr(project, 'name', 'this project')} in the {getattr(project, 'phase', 'discovery')} phase.

Make it encouraging but not answer-giving.
Return only the hint, nothing else."""

                hint = self.llm_client.generate_response(hint_prompt)
                return {"status": "success", "hint": hint}
            except Exception as e:
                self.logger.warning(f"Hint generation failed: {e}")

        return {"status": "success", "hint": "Keep exploring and asking questions!"}

    # ===== HELPER METHODS =====

    def _create_default_user(self, user_id: str) -> Dict:
        """
        Create default user for local/CLI usage.

        Args:
            user_id: User identifier

        Returns:
            User dict or object
        """
        return {
            "username": user_id,
            "email": f"{user_id}@localhost",
            "subscription_tier": "pro",
            "created_at": datetime.datetime.now().isoformat(),
            "questions_today": 0,
            "questions_total": 0,
        }

    def _check_subscription_limit(self, user: Any) -> tuple:
        """
        Check if user can ask more questions.

        Args:
            user: User object/dict

        Returns:
            Tuple (can_ask: bool, error_message: str)
        """
        # Get subscription tier
        if isinstance(user, dict):
            tier = user.get("subscription_tier", "pro")
        else:
            tier = getattr(user, "subscription_tier", "pro")

        # Tier-based limits (questions per day)
        limits = {
            "free": 5,
            "pro": 100,
            "enterprise": float("inf"),
        }

        daily_limit = limits.get(tier, 5)

        # Count questions asked today - try multiple ways to access it
        questions_today = 0
        if hasattr(user, "questions_today"):
            questions_today = getattr(user, "questions_today", 0)
        elif isinstance(user, dict) and "questions_today" in user:
            questions_today = user.get("questions_today", 0)

        if questions_today >= daily_limit:
            return False, f"Daily limit of {daily_limit} questions reached for {tier} tier"

        return True, None
