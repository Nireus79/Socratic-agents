"""
Socratic Counselor Agent - Complete Dialogue Orchestration Engine.

This module provides the complete Socratic dialogue orchestration extracted from the
monolithic Socratic system. It handles:
- Full question generation with orchestration and state management
- Complete answer processing with insight extraction
- Conflict detection and resolution
- Maturity tracking and phase advancement
- Knowledge base context integration
- User management and subscription validation
- Database persistence
- Document explanation and analysis
- Workflow optimization and phase management
- Answer suggestions and question effectiveness tracking

This is the core dialogue engine that was previously part of the monolithic system.
Now adapted as a standalone module for use in modular Socrates architecture.
"""

import datetime
import json
import logging
import uuid
from typing import Any, Dict, List, Optional, Tuple


class SocraticCounselor:
    """
    Complete Socratic dialogue orchestration engine.

    This agent provides comprehensive Socratic dialogue functionality including:
    - Dynamic and static question generation with KB awareness
    - Full answer processing with automatic next question generation
    - Insight extraction and conflict detection
    - Learning progress tracking and phase management
    - User lifecycle management
    - Database persistence integration

    The agent can work standalone or be integrated into a larger orchestration system.
    All dependencies (LLM, database, logger) are optional and can be provided at init time.
    """

    def __init__(
        self,
        llm_client: Optional[Any] = None,
        database: Optional[Any] = None,
        logger: Optional[Any] = None,
        batch_size: int = 1,
    ):
        """
        Initialize the Socratic Counselor agent.

        Args:
            llm_client: Optional LLM client for question/insight generation.
                       Required for dynamic question generation.
            database: Optional database client for persistence.
                     If provided, project and user state will be saved automatically.
                     If not provided, all operations work in memory only.
            logger: Optional logger instance. Uses standard logging if not provided.
            batch_size: Number of questions to generate per request (default: 1).
                       For compatibility, can be set to 3 for legacy behavior.
        """
        self.name = "SocraticCounselor"
        self.llm_client = llm_client
        self.database = database
        self.logger = logger or logging.getLogger("socratic_counselor")
        self.batch_size = max(1, batch_size)

        # Configuration
        self.use_dynamic_questions = True
        self.max_questions_per_phase = 5
        self.phase_docs_cache: Dict[str, Any] = {}

        # Static questions for fallback
        self.static_questions = {
            "discovery": [
                "What specific problem does your project solve?",
                "Who is your target audience or user base?",
                "What are the core features you envision?",
                "Are there similar solutions that exist? How will yours differ?",
                "What are your success criteria for this project?",
            ],
            "analysis": [
                "What technical challenges do you anticipate?",
                "What are your performance requirements?",
                "How will you handle user authentication and security?",
                "What third-party integrations might you need?",
                "How will you test and validate your solution?",
            ],
            "design": [
                "How will you structure your application architecture?",
                "What design patterns will you use?",
                "How will you organize your code and modules?",
                "What development workflow will you follow?",
                "How will you handle error cases and edge scenarios?",
            ],
            "implementation": [
                "What will be your first implementation milestone?",
                "How will you handle deployment and DevOps?",
                "What monitoring and logging will you implement?",
                "How will you document your code and API?",
                "What's your plan for maintenance and updates?",
            ],
        }

    def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Route incoming requests to appropriate handler methods.

        This is the main entry point for all Socratic Counselor operations.
        The action parameter determines which method is called.

        Args:
            request: Dictionary with action and action-specific parameters.
                    Required key: 'action' - specifies which handler to call.
                    Other keys depend on the action.

        Returns:
            Dictionary with status and action-specific results.

        Supported actions:
            - 'generate_question': Generate next Socratic question
            - 'process_response': Process user response and generate insights
            - 'extract_insights_only': Extract insights without processing
            - 'detect_conflicts': Detect conflicts in specifications
            - 'check_phase_completion': Check if phase is complete
            - 'advance_phase': Move to next phase
            - 'rollback_phase': Move to previous phase
            - 'generate_hint': Generate helpful hint
            - 'explain_document': Explain a project document
            - 'answer_question': Generate answer suggestions
            - 'skip_question': Mark current question as skipped
            - 'reopen_question': Reopen a previously answered question
            - 'generate_answer_suggestions': Generate multiple answer options
            - 'toggle_dynamic_questions': Toggle between dynamic and static modes
        """
        action = request.get("action", "generate_question")

        handlers = {
            "generate_question": self._generate_question,
            "process_response": self._process_response,
            "extract_insights_only": self._extract_insights_only,
            "detect_conflicts": self._handle_conflict_detection,
            "check_phase_completion": self._check_phase_completion,
            "advance_phase": self._advance_phase,
            "rollback_phase": self._rollback_phase,
            "generate_hint": self._generate_hint,
            "explain_document": self._explain_document,
            "answer_question": self._answer_question,
            "skip_question": self._skip_question,
            "reopen_question": self._reopen_question,
            "generate_answer_suggestions": self._generate_answer_suggestions,
        }

        handler = handlers.get(action)
        if not handler:
            return {"status": "error", "message": f"Unknown action: {action}"}

        try:
            return handler(request)
        except Exception as e:
            self.logger.error(f"Error in {action}: {e}", exc_info=True)
            return {"status": "error", "message": str(e)}

    # ===== CRITICAL ORCHESTRATION METHODS =====

    def _generate_question(self, request: Dict) -> Dict:
        """
        Generate the next Socratic question with complete orchestration.

        This is the primary method for question generation. It handles the complete
        workflow including checking for existing questions, validating subscriptions,
        auto-creating users, gathering KB context, generating questions, and storing state.

        Orchestration steps:
        1. Validate project exists
        2. Check for existing unanswered questions (prevent double generation)
        3. Get or auto-create user
        4. Validate subscription limits
        5. Count questions in current phase
        6. Generate question (dynamic or static)
        7. Store in BOTH conversation_history AND pending_questions
        8. Increment user metrics
        9. Save to database

        Args:
            request: Dictionary with:
                - 'project': ProjectContext object (required)
                - 'user_id': String user identifier (required)
                - 'force_refresh': Boolean to regenerate even if unanswered exists (optional)
                - 'knowledge_base': KB context dict with chunks/gaps (optional)
                - 'conversation_context': Conversation summary (optional)
                - 'recently_asked': List of questions to avoid repeating (optional)

        Returns:
            Dictionary with:
            - 'status': 'success' or 'error'
            - 'question': Generated question text
            - 'existing': Boolean, True if returned existing unanswered question
            - 'message': Error message if status is 'error'
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
        if (
            not force_refresh
            and hasattr(project, "pending_questions")
            and project.pending_questions
        ):
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
            user = self._create_default_user(user_id)
            self.logger.debug(f"Auto-created user: {user_id}")
            if self.database:
                self.database.save_user(user)

        # STEP 3: Validate subscription
        can_ask, error_msg = self._check_subscription_limit(user)
        if not can_ask:
            return {"status": "error", "message": error_msg}

        # STEP 4: Count questions in phase
        phase_questions = []
        if hasattr(project, "conversation_history"):
            phase_questions = [
                msg
                for msg in project.conversation_history
                if msg.get("type") == "assistant"
                and msg.get("phase") == getattr(project, "phase", "discovery")
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

        # STEP 6: Store in conversation_history
        if hasattr(project, "conversation_history"):
            project.conversation_history.append(
                {
                    "timestamp": datetime.datetime.now().isoformat(),
                    "type": "assistant",
                    "content": question,
                    "phase": getattr(project, "phase", "discovery"),
                    "question_number": len(phase_questions) + 1,
                }
            )

        # STEP 7: Store in pending_questions
        if not hasattr(project, "pending_questions"):
            project.pending_questions = []

        project.pending_questions.append(
            {
                "id": f"q_{uuid.uuid4().hex[:8]}",
                "question": question,
                "phase": getattr(project, "phase", "discovery"),
                "status": "unanswered",
                "created_at": datetime.datetime.now().isoformat(),
                "answer": None,
                "answered_at": None,
            }
        )

        # STEP 8: Update user metrics
        if hasattr(user, "increment_question_usage"):
            user.increment_question_usage()

        if self.database:
            self.database.save_user(user)

        # STEP 9: Save project
        if self.database:
            self.database.save_project(project)

        self.logger.info(f"Generated question for {user_id}")
        return {"status": "success", "question": question}

    def _process_response(self, request: Dict) -> Dict:
        """
        Process user response with complete orchestration.

        This is the primary method for answer processing. It handles insight extraction,
        question state tracking, conflict detection, maturity updates, and most importantly,
        GENERATES THE NEXT QUESTION.

        Orchestration steps (CRITICAL ORDERING):
        1. Add response to conversation_history
        2. Extract insights from response
        3. Mark question answered (BEFORE conflict detection - CRITICAL!)
        4. Detect conflicts (early return if found)
        5. Update project maturity
        6. Track question effectiveness
        7. Check phase completion
        8. Generate NEXT question (CRITICAL for dialogue)
        9. Save to database

        Args:
            request: Dictionary with:
                - 'project': ProjectContext object (required)
                - 'user_id': String user identifier (required)
                - 'response': String user response (required)
                - 'knowledge_base': KB context dict (optional)

        Returns:
            Dictionary with:
            - 'status': 'success' or 'error'
            - 'insights': Extracted insights dictionary
            - 'next_question': The next Socratic question (CRITICAL)
            - 'phase_complete': Boolean if phase is complete
            - 'conflicts_found': List of conflicts if any
            - 'conflicts_pending': Boolean if conflicts need resolution
            - 'debug_summary': Summary of processing steps
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
            project.conversation_history.append(
                {
                    "timestamp": datetime.datetime.now().isoformat(),
                    "type": "user",
                    "content": user_response,
                    "phase": getattr(project, "phase", "discovery"),
                    "author": user_id,
                }
            )
            debug_log.append("response_added")

        # STEP 2: Extract insights
        insights_result = self._extract_insights_only(
            {"response": user_response, "project": project}
        )
        insights_data = insights_result.get("insights", {})
        debug_log.append("insights_extracted")

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
        conflicts = self._handle_conflict_detection({"project": project, "insights": insights_data})
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
        next_question_result = self._generate_question(
            {
                "project": project,
                "user_id": user_id,
                "force_refresh": True,
                "knowledge_base": kb_context,
            }
        )
        next_question = (
            next_question_result.get("question")
            if next_question_result.get("status") == "success"
            else None
        )
        debug_log.append("next_question_generated")

        # STEP 9: Save to database
        if self.database:
            self.database.save_project(project)

        self.logger.info(f"Processed response for {user_id}")

        return {
            "status": "success",
            "insights": insights_data,
            "next_question": next_question,
            "phase_complete": phase_complete,
            "debug_summary": ", ".join(debug_log),
        }

    # ===== QUESTION GENERATION METHODS =====

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
        Generate contextual question using KB context and conversation history.

        This method generates questions that are grounded in the project's knowledge base
        and conversation context. It tries KB-aware generation first, then falls back
        to phase-appropriate questions.

        Args:
            project: ProjectContext object
            question_count: Number of questions already asked in this phase
            user_id: User identifier for context
            kb_context: Knowledge base context with chunks and gaps
            doc_understanding: Document semantic analysis
            conversation_context: Summary of conversation so far
            recently_asked: Questions to avoid repeating

        Returns:
            Generated question string or fallback question
        """
        recently_asked = recently_asked or []

        # Try KB-aware generation if context available
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
        Generate static question from predefined list.

        Returns phase and level-appropriate static questions when dynamic generation
        is not available or disabled. Rotates through questions to avoid repetition.

        Args:
            project: ProjectContext object
            question_count: Number of questions already asked in this phase

        Returns:
            Static question string appropriate for phase
        """
        phase = getattr(project, "phase", "discovery")
        phase_questions = self.static_questions.get(phase, self.static_questions["discovery"])

        idx = min(question_count, len(phase_questions) - 1)
        return phase_questions[idx] if phase_questions else "Tell me more about your project."

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
        Generate question using KB chunks and identified gaps.

        Creates questions that are grounded in specific project documentation and
        address identified knowledge gaps. Uses LLM to generate contextual, specific
        questions rather than generic ones.

        Args:
            topic: Topic to ask about
            level: Difficulty level (beginner, intermediate, advanced)
            phase: Project phase (discovery, analysis, design, implementation)
            kb_context: KB context with chunks and gaps
            conversation_context: Summary of conversation so far
            recently_asked: Questions to avoid repeating

        Returns:
            KB-aware question string or None if generation fails
        """
        if not self.llm_client:
            return None

        recently_asked = recently_asked or []

        try:
            chunks = kb_context.get("chunks", [])
            gaps = kb_context.get("gaps", [])

            # Extract snippet previews from chunks
            chunk_snippets = []
            if chunks:
                for chunk in chunks[:3]:
                    content = (
                        chunk.get("content", str(chunk)) if isinstance(chunk, dict) else str(chunk)
                    )
                    chunk_snippets.append(content[:200])

            chunks_context = (
                "\n".join([f"- {s}" for s in chunk_snippets])
                if chunk_snippets
                else "No document context available"
            )

            # Build gaps context
            gaps_context = ""
            if gaps:
                gap_list = [
                    g.get("topic", str(g)) if isinstance(g, dict) else str(g) for g in gaps[:3]
                ]
                gaps_context = f"\nKnowledge gaps: {', '.join(gap_list)}"

            # Build prompt for LLM
            prompt = f"""Generate ONE Socratic question about "{topic}" at {level} level.

Project Phase: {phase}
Available Context:
{chunks_context}{gaps_context}

Conversation Context: {conversation_context if conversation_context else "Starting fresh"}

Guidelines:
- Ground question in specific project context
- Help the learner discover answers themselves
- Consider the project phase
- Make it specific, not generic
- Address identified gaps if any

Return ONLY the question text, nothing else."""

            if recently_asked:
                prompt += "\n\nDo NOT ask:\n" + "\n".join([f"- {q}" for q in recently_asked[:5]])

            response = self.llm_client.generate_response(prompt)
            if response:
                question = response.strip()
                if question:
                    return question

        except Exception as e:
            self.logger.warning(f"KB-aware generation failed: {e}")

        return None

    def _get_fallback_question(self, topic: str, level: str, phase: str) -> str:
        """
        Get fallback question when dynamic generation unavailable.

        Provides phase and level-appropriate generic questions when LLM is unavailable
        or KB context is missing.

        Args:
            topic: Topic to ask about
            level: Difficulty level
            phase: Project phase

        Returns:
            Generic but appropriate question string
        """
        fallback_questions = {
            "discovery": [
                f"What is the main purpose of {topic}?",
                "Who are the primary users?",
                "What problem does this solve?",
            ],
            "analysis": [
                "What are the main requirements?",
                "What constraints apply?",
                "How will this be measured?",
            ],
            "design": [
                "How would you structure this?",
                "What components are needed?",
                "What architecture would fit?",
            ],
            "implementation": [
                "What's the first step?",
                "What tools would you use?",
                "How would you test this?",
            ],
        }

        questions = fallback_questions.get(phase, fallback_questions["discovery"])
        return questions[0] if questions else "Tell me more."

    # ===== RESPONSE PROCESSING METHODS =====

    def _extract_insights_only(self, request: Dict) -> Dict:
        """
        Extract insights from response without full processing.

        Performs insight extraction independently without other processing steps.
        Useful for confirmation mode or when full processing will happen later.

        Args:
            request: Dictionary with:
                - 'response': String user response (required)
                - 'project': ProjectContext object (optional)

        Returns:
            Dictionary with:
            - 'status': 'success' or 'error'
            - 'insights': Extracted insights dictionary
        """
        response = request.get("response", "")

        if not response:
            return {"status": "error", "message": "Response required", "insights": {}}

        self.logger.debug(f"Extracting insights ({len(response)} chars)")

        # Use LLM to extract insights
        if self.llm_client:
            try:
                prompt = f"""Extract key specifications, requirements, and insights from this response:

Response: {response}

Format as structured JSON with keys like:
- specifications: list of specs
- requirements: list of requirements
- gaps: list of knowledge gaps
- decisions: list of decisions made
- questions: follow-up questions

Return ONLY the JSON."""

                insights_text = self.llm_client.generate_response(prompt)

                if isinstance(insights_text, str):
                    try:
                        insights = json.loads(insights_text)
                    except (ValueError, TypeError):
                        insights = {"raw_response": insights_text}
                else:
                    insights = insights_text or {}

                return {"status": "success", "insights": insights}
            except Exception as e:
                self.logger.warning(f"Insight extraction failed: {e}")

        # Fallback
        return {
            "status": "success",
            "insights": {
                "raw_response": response,
                "length": len(response),
                "confidence": 0.5,
            },
        }

    def _handle_conflict_detection(self, request: Dict) -> Dict:
        """
        Detect conflicts in extracted insights using socratic-conflict library.

        Analyzes insights for contradictions or inconsistencies with existing
        project context using full conflict detection capabilities.

        Supported detection modes:
        - LLM-based: Uses LLM to analyze insights for contradictions
        - socratic-conflict: Full multi-agent conflict detection with severity assessment
        - Fallback: Simple contradiction detection

        Args:
            request: Dictionary with:
                - 'project': ProjectContext object (optional)
                - 'insights': Extracted insights dictionary
                - 'response': User response (optional)

        Returns:
            Dictionary with:
            - 'status': 'success'
            - 'conflicts_found': List of conflict dictionaries
            - 'has_conflicts': Boolean flag
            - 'conflict_count': Number of conflicts
            - 'severity_levels': Count by severity
        """
        from .conflict_detector import AgentConflictDetector

        project = request.get("project")
        insights = request.get("insights", {})
        response = request.get("response", "")

        conflicts_found = []

        # Initialize conflict detector with LLM client
        conflict_detector = AgentConflictDetector(llm_client=self.llm_client)

        # Strategy 1: Try socratic-conflict library if available
        if conflict_detector.use_full_detection:
            try:
                # Prepare agent states for full conflict detection
                agent_states = {
                    "project_state": {
                        "goal": getattr(project, "description", ""),
                        "phase": getattr(project, "phase", "discovery"),
                        "requirements": getattr(project, "requirements", []),
                    },
                    "user_response": {"content": response} if response else {},
                    "insights": insights,
                }

                detection_result = conflict_detector.detect_from_agent_states(agent_states)
                if detection_result["status"] == "success":
                    conflicts_found = detection_result.get("conflicts", [])
                    self.logger.debug(f"Full detection: found {len(conflicts_found)} conflicts")

            except Exception as e:
                self.logger.debug(f"Full conflict detection error: {e}")

        # Strategy 2: Fallback to LLM-based analysis if no conflicts found
        if not conflicts_found and self.llm_client and project:
            try:
                conflict_prompt = f"""Analyze these insights for contradictions:

Project Context: {getattr(project, 'description', 'N/A')}
Current Phase: {getattr(project, 'phase', 'discovery')}

User Response: {response}

Extracted Insights: {str(insights)}

Identify any contradictions, conflicts, or inconsistencies.
Return JSON with 'conflicts' list, each having: 'type', 'description', 'severity'"""

                response_text = self.llm_client.generate_response(conflict_prompt)
                if response_text:
                    try:
                        conflict_data = json.loads(response_text)
                        conflicts_found = conflict_data.get("conflicts", [])
                        self.logger.debug(f"LLM detection: found {len(conflicts_found)} conflicts")
                    except json.JSONDecodeError:
                        pass

            except Exception as e:
                self.logger.debug(f"LLM conflict detection error: {e}")

        # Strategy 3: Simple text-based conflict detection as last resort
        if not conflicts_found and response and insights:
            try:
                response_lower = response.lower()
                insight_str = str(insights).lower()

                # Check for simple contradictions
                contradiction_keywords = [
                    ("but", "however"),
                    ("conflict", "contradiction"),
                    ("disagree", "different"),
                    ("not", "never"),
                ]

                for keyword_pair in contradiction_keywords:
                    if keyword_pair[0] in response_lower and keyword_pair[1] in insight_str:
                        conflicts_found.append(
                            {
                                "type": "contradiction",
                                "description": "Potential contradiction detected in user response",
                                "severity": "low",
                            }
                        )
                        break

            except Exception as e:
                self.logger.debug(f"Simple conflict detection error: {e}")

        # Calculate severity summary
        severity_summary = {
            "high": sum(1 for c in conflicts_found if c.get("severity") == "high"),
            "medium": sum(1 for c in conflicts_found if c.get("severity") == "medium"),
            "low": sum(1 for c in conflicts_found if c.get("severity") == "low"),
        }

        return {
            "status": "success",
            "conflicts_found": conflicts_found,
            "has_conflicts": len(conflicts_found) > 0,
            "conflict_count": len(conflicts_found),
            "severity_levels": severity_summary,
            "detection_mode": "full" if conflict_detector.use_full_detection else "fallback",
        }

    def _update_project_maturity(self, project: Any, insights: Dict) -> None:
        """
        Update project maturity based on extracted insights.

        Increases phase maturity based on quality and quantity of insights.
        When maturity reaches threshold (70%), phase can be advanced.

        Args:
            project: ProjectContext object
            insights: Extracted insights dictionary
        """
        if not hasattr(project, "maturity_scores"):
            project.maturity_scores = {}

        current_phase = getattr(project, "phase", "discovery")
        current_maturity = project.maturity_scores.get(current_phase, 0)

        # Increase maturity based on insight quality
        insight_words = len(str(insights).split())
        maturity_increase = min(10, insight_words / 100)
        new_maturity = min(100, current_maturity + maturity_increase)

        project.maturity_scores[current_phase] = new_maturity
        self.logger.debug(f"Updated {current_phase} maturity: {new_maturity:.1f}%")

    def _track_question_effectiveness(
        self,
        project: Any,
        response: str,
        insights: Dict,
        user_id: str,
    ) -> None:
        """
        Track how effective this question was for learning.

        Records metrics about question effectiveness for learning analytics
        and question quality improvement.

        Args:
            project: ProjectContext object
            response: User's response text
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

        Phase is considered complete when maturity reaches 70% threshold.

        Args:
            project: ProjectContext object

        Returns:
            True if phase complete, False otherwise
        """
        if not hasattr(project, "maturity_scores"):
            return False

        current_phase = getattr(project, "phase", "discovery")
        maturity = project.maturity_scores.get(current_phase, 0)

        is_complete = maturity >= 70  # 70% threshold

        if is_complete:
            self.logger.info(f"Phase {current_phase} complete at {maturity:.1f}% maturity")

        return is_complete

    def _check_phase_completion(self, request: Dict) -> Dict:
        """
        Check phase completion status.

        Args:
            request: Dictionary with:
                - 'project': ProjectContext object (optional)

        Returns:
            Dictionary with:
            - 'status': 'success'
            - 'is_complete': Boolean
            - 'current_phase': Current phase name
            - 'maturity': Current maturity percentage
        """
        project = request.get("project")
        if not project:
            return {"is_complete": False}

        is_complete = self._check_phase_completion_internal(project)
        phase = getattr(project, "phase", "discovery")
        maturity = (
            project.maturity_scores.get(phase, 0) if hasattr(project, "maturity_scores") else 0
        )

        return {
            "status": "success",
            "is_complete": is_complete,
            "current_phase": phase,
            "maturity": maturity,
        }

    def _advance_phase(self, request: Dict) -> Dict:
        """
        Advance project to next phase.

        Moves project from current phase to next in sequence.
        Phase sequence: discovery → analysis → design → implementation

        Args:
            request: Dictionary with:
                - 'project': ProjectContext object

        Returns:
            Dictionary with:
            - 'status': 'success' or 'error'
            - 'previous_phase': Name of previous phase
            - 'new_phase': Name of new phase
        """
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

            if self.database:
                self.database.save_project(project)

            return {"status": "success", "previous_phase": current, "new_phase": next_phase}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def _rollback_phase(self, request: Dict) -> Dict:
        """
        Rollback project to previous phase.

        Moves project back one phase in sequence if possible.

        Args:
            request: Dictionary with:
                - 'project': ProjectContext object

        Returns:
            Dictionary with status and phase information
        """
        project = request.get("project")
        if not project:
            return {"status": "error", "message": "Project required"}

        current = getattr(project, "phase", "discovery")
        phases = ["discovery", "analysis", "design", "implementation"]

        try:
            idx = phases.index(current)
            prev_phase = phases[idx - 1] if idx > 0 else current

            if hasattr(project, "phase"):
                project.phase = prev_phase

            self.logger.info(f"Rolled back from {current} to {prev_phase}")

            if self.database:
                self.database.save_project(project)

            return {"status": "success", "previous_phase": current, "new_phase": prev_phase}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def _generate_hint(self, request: Dict) -> Dict:
        """
        Generate helpful hint for current question.

        Creates a nudge without giving away the answer, helping users
        when they're stuck without breaking Socratic learning.

        Args:
            request: Dictionary with:
                - 'project': ProjectContext object (optional)

        Returns:
            Dictionary with:
            - 'status': 'success'
            - 'hint': Helpful hint text
        """
        project = request.get("project")

        if self.llm_client and project:
            try:
                hint_prompt = f"""Generate a helpful hint for working on {getattr(project, 'name', 'this project')}
in the {getattr(project, 'phase', 'discovery')} phase.

Make it encouraging but don't give away the answer.
Return only the hint."""

                hint = self.llm_client.generate_response(hint_prompt)
                return {"status": "success", "hint": hint}
            except Exception as e:
                self.logger.warning(f"Hint generation failed: {e}")

        return {"status": "success", "hint": "Keep exploring and asking questions!"}

    def _explain_document(self, request: Dict) -> Dict:
        """
        Explain a project document or artifact.

        Provides clear explanation of project documentation, code, or specifications
        to help user understand context.

        Args:
            request: Dictionary with:
                - 'project': ProjectContext object
                - 'document': Document text to explain (optional)

        Returns:
            Dictionary with explanation
        """
        project = request.get("project")
        document = request.get("document", "")

        if self.llm_client:
            try:
                explain_prompt = f"""Explain this {getattr(project, 'phase', 'project')} document clearly:

{document[:500]}

Provide a clear explanation suitable for learning."""

                explanation = self.llm_client.generate_response(explain_prompt)
                return {"status": "success", "explanation": explanation}
            except Exception as e:
                self.logger.warning(f"Explanation generation failed: {e}")

        return {"status": "success", "explanation": "Unable to generate explanation at this time."}

    def _answer_question(self, request: Dict) -> Dict:
        """
        Provide answer guidance for current question.

        Generates a suggested answer approach without directly answering,
        maintaining Socratic learning principles.

        Args:
            request: Dictionary with:
                - 'project': ProjectContext object
                - 'question': Current question text

        Returns:
            Dictionary with guidance
        """
        question = request.get("question", "")

        if self.llm_client:
            try:
                answer_prompt = f"""Given this question: {question}

Provide guidance on how to approach answering it.
Don't give the answer, guide the thinking process."""

                guidance = self.llm_client.generate_response(answer_prompt)
                return {"status": "success", "guidance": guidance}
            except Exception as e:
                self.logger.warning(f"Answer guidance failed: {e}")

        return {"status": "success", "guidance": "Consider the question from different angles."}

    def _skip_question(self, request: Dict) -> Dict:
        """
        Mark current question as skipped.

        Allows user to skip a question, moving to next without answering.

        Args:
            request: Dictionary with:
                - 'project': ProjectContext object

        Returns:
            Dictionary with status and next question
        """
        project = request.get("project")

        if project and hasattr(project, "pending_questions") and project.pending_questions:
            for q in reversed(project.pending_questions):
                if q.get("status") == "unanswered":
                    q["status"] = "skipped"
                    q["skipped_at"] = datetime.datetime.now().isoformat()
                    break

        if self.database:
            self.database.save_project(project)

        return {"status": "success", "message": "Question skipped"}

    def _reopen_question(self, request: Dict) -> Dict:
        """
        Reopen a previously answered question.

        Allows revisiting and re-answering a question to refine understanding.

        Args:
            request: Dictionary with:
                - 'project': ProjectContext object
                - 'question_id': ID of question to reopen (optional)

        Returns:
            Dictionary with status and question details
        """
        project = request.get("project")
        question_id = request.get("question_id")

        if project and hasattr(project, "pending_questions"):
            for q in project.pending_questions:
                if q.get("status") == "answered" and (
                    not question_id or q.get("id") == question_id
                ):
                    q["status"] = "unanswered"
                    q["answered_at"] = None
                    q["answer"] = None
                    break

        if self.database:
            self.database.save_project(project)

        return {"status": "success", "message": "Question reopened for review"}

    def _generate_answer_suggestions(self, request: Dict) -> Dict:
        """
        Generate multiple answer suggestions for current question.

        Provides several different ways to approach answering the current question,
        helping users think comprehensively.

        Args:
            request: Dictionary with:
                - 'project': ProjectContext object
                - 'question': Current question text

        Returns:
            Dictionary with list of suggestion approaches
        """
        question = request.get("question", "")

        suggestions = []

        if self.llm_client:
            try:
                suggest_prompt = f"""Given this question: {question}

Generate 3-4 different approaches or angles to answer it.
Format as a list of brief approaches."""

                response = self.llm_client.generate_response(suggest_prompt)
                if response:
                    suggestions = response.split("\n")

            except Exception as e:
                self.logger.warning(f"Suggestion generation failed: {e}")

        return {"status": "success", "suggestions": suggestions}

    # ===== HELPER METHODS =====

    def _create_default_user(self, user_id: str) -> Dict:
        """
        Create default user for local/CLI usage.

        Auto-creates a user with pro tier when no user exists for local
        development or CLI usage.

        Args:
            user_id: User identifier

        Returns:
            User dictionary
        """
        return {
            "username": user_id,
            "email": f"{user_id}@localhost",
            "subscription_tier": "pro",
            "created_at": datetime.datetime.now().isoformat(),
            "questions_today": 0,
            "questions_total": 0,
        }

    def _check_subscription_limit(self, user: Any) -> Tuple[bool, Optional[str]]:
        """
        Check if user can ask more questions based on subscription.

        Validates that user hasn't exceeded daily question limit for their tier.

        Subscription tiers:
        - free: 5 questions per day
        - pro: 100 questions per day
        - enterprise: unlimited

        Args:
            user: User object or dictionary

        Returns:
            Tuple of (can_ask: bool, error_message: str or None)
        """
        # Get subscription tier
        if isinstance(user, dict):
            tier = user.get("subscription_tier", "pro")
        else:
            tier = getattr(user, "subscription_tier", "pro")

        # Define limits
        limits = {
            "free": 5,
            "pro": 100,
            "enterprise": float("inf"),
        }

        daily_limit = limits.get(tier, 5)

        # Count questions asked today
        questions_today = 0
        if hasattr(user, "questions_today"):
            questions_today = getattr(user, "questions_today", 0)
        elif isinstance(user, dict) and "questions_today" in user:
            questions_today = user.get("questions_today", 0)

        if questions_today >= daily_limit:
            return False, f"Daily limit of {daily_limit} questions reached for {tier} tier"

        return True, None

    def toggle_dynamic_questions(self) -> Dict:
        """
        Toggle between dynamic and static question modes.

        Switches from LLM-based dynamic questions to static questions from template.

        Returns:
            Dictionary with new mode status
        """
        self.use_dynamic_questions = not self.use_dynamic_questions
        return {"status": "success", "dynamic_mode": self.use_dynamic_questions}
