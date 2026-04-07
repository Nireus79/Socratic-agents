"""Knowledge Analysis Agent - Knowledge pattern recognition and insight generation.

This agent:
1. Analyzes knowledge patterns and extracts key themes
2. Detects relationships between knowledge entities
3. Generates actionable insights from data
4. Tracks knowledge evolution and temporal patterns
5. Performs semantic clustering and categorization
6. Identifies knowledge gaps and opportunities
7. Supports multi-level knowledge hierarchies
"""

import asyncio
import re
from collections import Counter, defaultdict
from datetime import datetime
from typing import Any, Dict, List, Optional, Set, Tuple

from .base import BaseAgent


class KnowledgePattern:
    """Represents a detected pattern in knowledge."""

    def __init__(
        self,
        pattern_type: str,
        description: str,
        confidence: float,
        supporting_evidence: List[str],
    ):
        self.id = f"pattern_{datetime.utcnow().timestamp()}"
        self.pattern_type = pattern_type  # frequency, relationship, trend, anomaly
        self.description = description
        self.confidence = confidence
        self.supporting_evidence = supporting_evidence
        self.created_at = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "type": self.pattern_type,
            "description": self.description,
            "confidence": self.confidence,
            "evidence_count": len(self.supporting_evidence),
            "created_at": self.created_at.isoformat(),
        }


class Insight:
    """Represents a generated insight."""

    def __init__(
        self,
        title: str,
        description: str,
        insight_type: str,
        importance: float,
        related_patterns: List[str],
    ):
        self.id = f"insight_{datetime.utcnow().timestamp()}"
        self.title = title
        self.description = description
        self.insight_type = insight_type  # opportunity, risk, trend, anomaly
        self.importance = importance
        self.related_patterns = related_patterns
        self.created_at = datetime.utcnow()
        self.actionable = importance > 0.7

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "type": self.insight_type,
            "importance": self.importance,
            "actionable": self.actionable,
            "pattern_count": len(self.related_patterns),
            "created_at": self.created_at.isoformat(),
        }


class KnowledgeAnalysis(BaseAgent):
    """
    Agent that analyzes knowledge base for patterns and generates insights.

    Provides comprehensive knowledge analysis including:
    - Pattern detection (frequency, relationships, trends, anomalies)
    - Insight generation and prioritization
    - Relationship mapping between knowledge entities
    - Semantic clustering and categorization
    - Knowledge evolution tracking
    - Gap identification and opportunity discovery
    """

    def __init__(self, llm_client: Optional[Any] = None):
        """Initialize the Knowledge Analysis agent."""
        super().__init__(name="KnowledgeAnalysis", llm_client=llm_client)
        self.patterns: Dict[str, KnowledgePattern] = {}
        self.insights: Dict[str, Insight] = {}
        self.topic_index: Dict[str, Set[str]] = defaultdict(set)
        self.entity_relationships: Dict[str, Set[str]] = defaultdict(set)
        self.knowledge_history: List[Dict[str, Any]] = []
        self.category_distribution: Dict[str, int] = {}

    def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process knowledge analysis requests."""
        action = request.get("action", "analyze")

        if action == "analyze":
            return self.analyze_knowledge(
                request.get("knowledge"),
                request.get("analysis_depth", "standard"),
            )
        elif action == "extract_patterns":
            return self.extract_patterns(request.get("knowledge"))
        elif action == "generate_insights":
            return self.generate_insights(request.get("patterns"))
        elif action == "detect_relationships":
            return self.detect_relationships(request.get("entities"))
        elif action == "identify_gaps":
            return self.identify_knowledge_gaps(request.get("knowledge"))
        elif action == "categorize":
            return self.categorize_knowledge(request.get("items"), request.get("categories"))
        elif action == "list_patterns":
            return self.list_patterns()
        elif action == "list_insights":
            return self.list_insights()
        elif action == "get_summary":
            return self.get_analysis_summary()
        else:
            return {"status": "error", "message": f"Unknown action: {action}"}

    async def process_async(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process knowledge analysis requests asynchronously."""
        action = request.get("action", "analyze")

        if action == "analyze":
            return await self._analyze_knowledge_async(
                request.get("knowledge"),
                request.get("analysis_depth", "standard"),
            )
        elif action == "extract_patterns":
            return await self._extract_patterns_async(request.get("knowledge"))
        elif action == "generate_insights":
            return await self._generate_insights_async(request.get("patterns"))
        elif action == "detect_relationships":
            return await self._detect_relationships_async(request.get("entities"))
        elif action == "identify_gaps":
            return await self._identify_knowledge_gaps_async(request.get("knowledge"))
        elif action == "categorize":
            return await self._categorize_knowledge_async(
                request.get("items"), request.get("categories")
            )
        elif action == "list_patterns":
            return await asyncio.to_thread(self.list_patterns)
        elif action == "list_insights":
            return await asyncio.to_thread(self.list_insights)
        elif action == "get_summary":
            return await asyncio.to_thread(self.get_analysis_summary)
        else:
            return {"status": "error", "message": f"Unknown action: {action}"}

    # Async wrapper methods
    async def _analyze_knowledge_async(
        self, knowledge: str, analysis_depth: str = "standard"
    ) -> Dict[str, Any]:
        """Analyze knowledge asynchronously."""
        return await asyncio.to_thread(self.analyze_knowledge, knowledge, analysis_depth)

    async def _extract_patterns_async(self, knowledge: str) -> Dict[str, Any]:
        """Extract patterns asynchronously."""
        return await asyncio.to_thread(self.extract_patterns, knowledge)

    async def _generate_insights_async(self, patterns: List[KnowledgePattern]) -> Dict[str, Any]:
        """Generate insights asynchronously."""
        return await asyncio.to_thread(self.generate_insights, patterns)

    async def _detect_relationships_async(self, entities: List[str]) -> Dict[str, Any]:
        """Detect relationships asynchronously."""
        return await asyncio.to_thread(self.detect_relationships, entities)

    async def _identify_knowledge_gaps_async(self, knowledge: str) -> Dict[str, Any]:
        """Identify knowledge gaps asynchronously."""
        return await asyncio.to_thread(self.identify_knowledge_gaps, knowledge)

    async def _categorize_knowledge_async(
        self, items: List[str], categories: List[str]
    ) -> Dict[str, Any]:
        """Categorize knowledge asynchronously."""
        return await asyncio.to_thread(self.categorize_knowledge, items, categories)

    def analyze_knowledge(self, knowledge: str, analysis_depth: str = "standard") -> Dict[str, Any]:
        """Comprehensive knowledge analysis."""
        if not knowledge:
            return {"status": "error", "message": "Knowledge content required"}

        self.knowledge_history.append(
            {
                "timestamp": datetime.utcnow().isoformat(),
                "content_length": len(knowledge),
            }
        )

        # Extract patterns
        patterns = self._detect_patterns(knowledge)
        for pattern in patterns:
            self.patterns[pattern.id] = pattern

        # Generate insights from patterns
        insights = self._generate_insights_from_patterns(patterns, analysis_depth)
        for insight in insights:
            self.insights[insight.id] = insight

        # Build topic index
        self._build_topic_index(knowledge)

        return {
            "status": "success",
            "agent": self.name,
            "analysis_depth": analysis_depth,
            "patterns_found": len(patterns),
            "insights_generated": len(insights),
            "topics_identified": list(self.topic_index.keys())[:10],
            "top_insights": [
                i.to_dict() for i in sorted(insights, key=lambda x: x.importance, reverse=True)[:3]
            ],
        }

    def extract_patterns(self, knowledge: str) -> Dict[str, Any]:
        """Extract all patterns from knowledge."""
        if not knowledge:
            return {"status": "error", "message": "Knowledge content required"}

        patterns = self._detect_patterns(knowledge)
        for pattern in patterns:
            self.patterns[pattern.id] = pattern

        return {
            "status": "success",
            "agent": self.name,
            "patterns_detected": len(patterns),
            "patterns": [p.to_dict() for p in patterns],
            "pattern_types": list(set(p.pattern_type for p in patterns)),
        }

    def generate_insights(self, patterns: Optional[List[str]] = None) -> Dict[str, Any]:
        """Generate insights from detected patterns."""
        if not self.patterns:
            return {"status": "error", "message": "No patterns available for analysis"}

        pattern_list = []
        if patterns:
            pattern_list = [self.patterns.get(pid) for pid in patterns if pid in self.patterns]
        else:
            pattern_list = list(self.patterns.values())

        insights = self._generate_insights_from_patterns(pattern_list, "detailed")
        for insight in insights:
            self.insights[insight.id] = insight

        return {
            "status": "success",
            "agent": self.name,
            "patterns_analyzed": len(pattern_list),
            "insights_generated": len(insights),
            "insights": [i.to_dict() for i in insights],
            "actionable_insights": len([i for i in insights if i.actionable]),
        }

    def detect_relationships(self, entities: Optional[List[str]] = None) -> Dict[str, Any]:
        """Detect relationships between knowledge entities."""
        if not entities:
            return {"status": "error", "message": "Entities list required"}

        relationships = {}
        for entity in entities:
            related = self.entity_relationships.get(entity, set())
            relationships[entity] = list(related)

        return {
            "status": "success",
            "agent": self.name,
            "entities_analyzed": len(entities),
            "relationships_found": sum(len(r) for r in relationships.values()),
            "relationships": relationships,
        }

    def identify_knowledge_gaps(self, knowledge: str) -> Dict[str, Any]:
        """Identify gaps in knowledge coverage."""
        if not knowledge:
            return {"status": "error", "message": "Knowledge content required"}

        # Analyze what's present
        words = set(re.findall(r"\b\w+\b", knowledge.lower()))
        common_domains = {
            "architecture": {"design", "pattern", "structure", "component"},
            "testing": {"test", "unit", "integration", "coverage"},
            "documentation": {"doc", "readme", "comment", "guide"},
            "security": {"security", "auth", "encrypt", "validate"},
            "performance": {"performance", "optimize", "scale", "cache"},
        }

        gaps = []
        for domain, keywords in common_domains.items():
            coverage = len(keywords & words) / len(keywords)
            if coverage < 0.5:
                gaps.append(
                    {
                        "domain": domain,
                        "coverage": coverage,
                        "missing_concepts": list(keywords - words),
                    }
                )

        return {
            "status": "success",
            "agent": self.name,
            "gaps_identified": len(gaps),
            "gaps": gaps,
            "coverage_score": 1.0 - (len(gaps) / len(common_domains)),
        }

    def categorize_knowledge(
        self, items: Optional[List[str]] = None, categories: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Categorize knowledge items."""
        if not items:
            return {"status": "error", "message": "Items list required"}
        if not categories:
            categories = ["general", "technical", "conceptual"]

        categorized = defaultdict(list)
        for item in items:
            # Simple heuristic: categorize based on keywords
            if any(kw in item.lower() for kw in ["algorithm", "code", "function", "class"]):
                category = "technical"
            elif any(kw in item.lower() for kw in ["theory", "principle", "concept", "idea"]):
                category = "conceptual"
            else:
                category = "general"

            categorized[category].append(item)
            self.category_distribution[category] = self.category_distribution.get(category, 0) + 1

        return {
            "status": "success",
            "agent": self.name,
            "items_categorized": len(items),
            "categorized": dict(categorized),
            "distribution": self.category_distribution,
        }

    def list_patterns(self) -> Dict[str, Any]:
        """List all detected patterns."""
        sorted_patterns = sorted(
            self.patterns.values(),
            key=lambda p: p.confidence,
            reverse=True,
        )

        return {
            "status": "success",
            "agent": self.name,
            "patterns_count": len(sorted_patterns),
            "patterns": [p.to_dict() for p in sorted_patterns],
            "pattern_types": list(set(p.pattern_type for p in sorted_patterns)),
        }

    def list_insights(self) -> Dict[str, Any]:
        """List all generated insights."""
        sorted_insights = sorted(
            self.insights.values(),
            key=lambda i: i.importance,
            reverse=True,
        )

        return {
            "status": "success",
            "agent": self.name,
            "insights_count": len(sorted_insights),
            "insights": [i.to_dict() for i in sorted_insights],
            "actionable_count": len([i for i in sorted_insights if i.actionable]),
            "insight_types": list(set(i.insight_type for i in sorted_insights)),
        }

    def get_analysis_summary(self) -> Dict[str, Any]:
        """Get summary of all analyses."""
        return {
            "status": "success",
            "agent": self.name,
            "patterns_count": len(self.patterns),
            "insights_count": len(self.insights),
            "topics_count": len(self.topic_index),
            "relationships_count": sum(len(r) for r in self.entity_relationships.values()),
            "analysis_history_count": len(self.knowledge_history),
            "top_patterns": [
                p.to_dict()
                for p in sorted(self.patterns.values(), key=lambda p: p.confidence, reverse=True)[
                    :3
                ]
            ],
            "top_insights": [
                i.to_dict()
                for i in sorted(self.insights.values(), key=lambda i: i.importance, reverse=True)[
                    :3
                ]
            ],
            "category_distribution": self.category_distribution,
        }

    # Helper methods
    def _detect_patterns(self, content: str) -> List[KnowledgePattern]:
        """Detect patterns in content."""
        patterns = []

        # Frequency patterns
        words = re.findall(r"\b\w+\b", content.lower())
        word_freq = Counter(words)
        common_words = word_freq.most_common(5)

        if common_words:
            top_word = common_words[0][0]
            frequency = common_words[0][1] / len(words)
            patterns.append(
                KnowledgePattern(
                    "frequency",
                    f"High frequency term: '{top_word}' appears {frequency:.1%}",
                    min(frequency, 1.0),
                    [top_word],
                )
            )

        # Structure patterns (code-like content)
        if re.search(r"\b(def|class|function|method|interface)\b", content):
            patterns.append(
                KnowledgePattern(
                    "structure",
                    "Code structure detected (definitions, classes, methods)",
                    0.85,
                    ["def", "class", "function"],
                )
            )

        # Documentation patterns
        if re.search(r"\b(parameter|return|argument|example)\b", content, re.IGNORECASE):
            patterns.append(
                KnowledgePattern(
                    "documentation",
                    "Documentation patterns detected (parameters, returns, examples)",
                    0.80,
                    ["parameter", "return", "example"],
                )
            )

        return patterns

    def _build_topic_index(self, content: str) -> None:
        """Build index of topics."""
        # Extract noun-like words (simple heuristic)
        words = re.findall(r"\b[A-Z][a-z]+\b", content)  # Capitalized words
        for word in set(words):
            self.topic_index[word] = self.topic_index.get(word, set())

    def _generate_insights_from_patterns(
        self, patterns: List[KnowledgePattern], depth: str = "standard"
    ) -> List[Insight]:
        """Generate insights from patterns."""
        insights = []

        for pattern in patterns:
            if pattern.pattern_type == "frequency":
                insights.append(
                    Insight(
                        "Dominant Theme Identified",
                        f"Key topic '{pattern.description.split(chr(39))[1]}' dominates the knowledge",
                        "trend",
                        pattern.confidence,
                        [pattern.id],
                    )
                )
            elif pattern.pattern_type == "structure":
                insights.append(
                    Insight(
                        "Structural Knowledge Present",
                        "Knowledge contains well-structured, organized information",
                        "opportunity",
                        pattern.confidence,
                        [pattern.id],
                    )
                )
            elif pattern.pattern_type == "documentation":
                insights.append(
                    Insight(
                        "Well-Documented Content",
                        "Knowledge includes comprehensive documentation patterns",
                        "trend",
                        pattern.confidence,
                        [pattern.id],
                    )
                )

        return insights
