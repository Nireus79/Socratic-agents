"""Context Analyzer Agent - Context extraction and semantic analysis.

This agent:
1. Extracts contextual information from content
2. Identifies semantic relationships and meaning
3. Tracks context hierarchies and dependencies
4. Provides context-aware recommendations
5. Manages context switching and transitions
6. Analyzes context relevance and applicability
7. Builds context ontologies and models
"""

import re
from collections import defaultdict
from datetime import datetime
from typing import Any, Dict, List, Optional, Set, Tuple

from .base import BaseAgent


class ContextEntity:
    """Represents a context entity with attributes."""

    def __init__(self, name: str, entity_type: str, attributes: Optional[Dict[str, Any]] = None):
        self.id = f"entity_{datetime.utcnow().timestamp()}"
        self.name = name
        self.entity_type = entity_type  # domain, object, concept, role, action
        self.attributes = attributes or {}
        self.relationships: Dict[str, Set[str]] = defaultdict(set)
        self.created_at = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.entity_type,
            "attributes": self.attributes,
            "relationship_count": sum(len(r) for r in self.relationships.values()),
        }


class ContextModel:
    """Represents a semantic context model."""

    def __init__(self, name: str, domain: str):
        self.id = f"model_{datetime.utcnow().timestamp()}"
        self.name = name
        self.domain = domain
        self.entities: Dict[str, ContextEntity] = {}
        self.relationships: List[Tuple[str, str, str]] = []  # (entity1, relation, entity2)
        self.created_at = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "domain": self.domain,
            "entity_count": len(self.entities),
            "relationship_count": len(self.relationships),
            "created_at": self.created_at.isoformat(),
        }


class ContextAnalyzer(BaseAgent):
    """
    Agent that extracts and analyzes contextual information.

    Provides comprehensive context analysis including:
    - Semantic entity extraction from content
    - Context model building and management
    - Relationship detection between entities
    - Domain identification and classification
    - Context hierarchy management
    - Relevance scoring and applicability analysis
    - Context switching and transition management
    """

    def __init__(self, llm_client: Optional[Any] = None):
        """Initialize the Context Analyzer."""
        super().__init__(name="ContextAnalyzer", llm_client=llm_client)
        self.contexts: Dict[str, Dict[str, Any]] = {}
        self.context_models: Dict[str, ContextModel] = {}
        self.entity_index: Dict[str, ContextEntity] = {}
        self.domain_index: Dict[str, Set[str]] = defaultdict(set)
        self.context_hierarchy: Dict[str, List[str]] = defaultdict(list)
        self.context_relationships: Dict[str, Set[str]] = defaultdict(set)

    def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process context analysis requests."""
        action = request.get("action", "analyze")

        if action == "analyze":
            return self.analyze_context(request.get("content"), request.get("domain"))
        elif action == "extract_entities":
            return self.extract_entities(request.get("content"))
        elif action == "build_model":
            return self.build_context_model(
                request.get("name"), request.get("content"), request.get("domain")
            )
        elif action == "detect_relationships":
            return self.detect_relationships(request.get("content"))
        elif action == "identify_domain":
            return self.identify_domain(request.get("content"))
        elif action == "find_relevant_context":
            return self.find_relevant_context(request.get("query"), request.get("limit", 5))
        elif action == "store":
            return self.store_context(
                request.get("name"), request.get("content"), request.get("metadata")
            )
        elif action == "retrieve":
            return self.retrieve_context(request.get("name"))
        elif action == "list":
            return self.list_contexts()
        elif action == "get_hierarchy":
            return self.get_context_hierarchy(request.get("context_name"))
        else:
            return {"status": "error", "message": f"Unknown action: {action}"}

    def analyze_context(self, content: str, domain: Optional[str] = None) -> Dict[str, Any]:
        """Analyze content and extract context."""
        if not content:
            return {"status": "error", "message": "Content required"}

        # Extract entities
        entities = self._extract_semantic_entities(content)

        # Identify domain
        detected_domain = domain or self._identify_domain_impl(content)

        # Analyze relationships
        relationships = self._analyze_entity_relationships(entities)

        # Build context information
        context_info = {
            "entities": entities,
            "relationships": relationships,
            "domain": detected_domain,
            "timestamp": datetime.utcnow().isoformat(),
            "content_length": len(content),
        }

        return {
            "status": "success",
            "agent": self.name,
            "domain": detected_domain,
            "entities_found": len(entities),
            "relationships_found": len(relationships),
            "context": context_info,
        }

    def extract_entities(self, content: str) -> Dict[str, Any]:
        """Extract semantic entities from content."""
        if not content:
            return {"status": "error", "message": "Content required"}

        entities = self._extract_semantic_entities(content)

        # Store entities
        for entity_name, entity_type in entities.items():
            if entity_name not in self.entity_index:
                entity = ContextEntity(entity_name, entity_type)
                self.entity_index[entity_name] = entity

        return {
            "status": "success",
            "agent": self.name,
            "entities_extracted": len(entities),
            "entities": entities,
            "total_entities_stored": len(self.entity_index),
        }

    def build_context_model(
        self, name: str, content: str, domain: Optional[str] = None
    ) -> Dict[str, Any]:
        """Build a semantic context model."""
        if not name or not content:
            return {"status": "error", "message": "Name and content required"}

        detected_domain = domain or self._identify_domain_impl(content)
        model = ContextModel(name, detected_domain)

        # Extract entities for model
        entities = self._extract_semantic_entities(content)
        for entity_name, entity_type in entities.items():
            entity = ContextEntity(entity_name, entity_type)
            model.entities[entity_name] = entity

        # Detect relationships
        relationships = self._analyze_entity_relationships(entities)
        for rel_type, pairs in relationships.items():
            for entity1, entity2 in pairs:
                model.relationships.append((entity1, rel_type, entity2))

        self.context_models[name] = model

        return {
            "status": "success",
            "agent": self.name,
            "model_name": name,
            "domain": detected_domain,
            "entity_count": len(model.entities),
            "relationship_count": len(model.relationships),
            "model": model.to_dict(),
        }

    def detect_relationships(self, content: str) -> Dict[str, Any]:
        """Detect semantic relationships in content."""
        if not content:
            return {"status": "error", "message": "Content required"}

        entities = self._extract_semantic_entities(content)
        relationships = self._analyze_entity_relationships(entities)

        return {
            "status": "success",
            "agent": self.name,
            "relationships_found": sum(len(pairs) for pairs in relationships.values()),
            "relationships": relationships,
            "relationship_types": list(relationships.keys()),
        }

    def identify_domain(self, content: str) -> Dict[str, Any]:
        """Identify the domain of content."""
        if not content:
            return {"status": "error", "message": "Content required"}

        domain = self._identify_domain_impl(content)
        confidence = self._calculate_domain_confidence(content, domain)

        return {
            "status": "success",
            "agent": self.name,
            "domain": domain,
            "confidence": confidence,
            "description": f"Content identified as {domain} domain",
        }

    def find_relevant_context(self, query: str, limit: int = 5) -> Dict[str, Any]:
        """Find relevant contexts for a query."""
        if not query:
            return {"status": "error", "message": "Query required"}

        # Score contexts by relevance
        scored_contexts = []
        for context_name, context_info in self.contexts.items():
            relevance = self._calculate_relevance(query, context_info.get("content", ""))
            scored_contexts.append((context_name, relevance))

        # Sort by relevance
        scored_contexts.sort(key=lambda x: x[1], reverse=True)
        relevant = scored_contexts[:limit]

        return {
            "status": "success",
            "agent": self.name,
            "query": query,
            "relevant_contexts": [name for name, _ in relevant],
            "relevance_scores": {name: score for name, score in relevant},
        }

    def store_context(
        self, name: str, content: str, metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Store a context."""
        if not name or not content:
            return {"status": "error", "message": "Name and content required"}

        context = {
            "name": name,
            "content": content,
            "metadata": metadata or {},
            "created_at": datetime.utcnow().isoformat(),
            "entities": self._extract_semantic_entities(content),
        }

        self.contexts[name] = context

        # Update domain index
        domain = self._identify_domain_impl(content)
        self.domain_index[domain].add(name)

        return {
            "status": "success",
            "agent": self.name,
            "context_stored": name,
            "domain": domain,
            "total_contexts": len(self.contexts),
        }

    def retrieve_context(self, name: str) -> Dict[str, Any]:
        """Retrieve a stored context."""
        if not name:
            return {"status": "error", "message": "Name required"}

        if name not in self.contexts:
            return {"status": "error", "message": f"Context '{name}' not found"}

        return {
            "status": "success",
            "agent": self.name,
            "context": self.contexts[name],
        }

    def list_contexts(self) -> Dict[str, Any]:
        """List all stored contexts."""
        context_list = [
            {
                "name": name,
                "domain": self._identify_domain_impl(ctx.get("content", "")),
                "created_at": ctx.get("created_at"),
                "entity_count": len(ctx.get("entities", {})),
            }
            for name, ctx in self.contexts.items()
        ]

        return {
            "status": "success",
            "agent": self.name,
            "contexts_count": len(context_list),
            "contexts": context_list,
            "domains": list(self.domain_index.keys()),
        }

    def get_context_hierarchy(self, context_name: Optional[str] = None) -> Dict[str, Any]:
        """Get hierarchy for a context or all contexts."""
        if context_name:
            hierarchy = self.context_hierarchy.get(context_name, [])
            return {
                "status": "success",
                "agent": self.name,
                "context": context_name,
                "hierarchy": hierarchy,
            }
        else:
            return {
                "status": "success",
                "agent": self.name,
                "hierarchies": dict(self.context_hierarchy),
                "total_hierarchies": len(self.context_hierarchy),
            }

    # Helper methods
    def _extract_semantic_entities(self, content: str) -> Dict[str, str]:
        """Extract semantic entities from content."""
        entities = {}

        # Extract capitalized words (likely proper nouns/entities)
        proper_nouns = re.findall(r"\b[A-Z][a-z]+\b", content)
        for noun in set(proper_nouns):
            entities[noun] = "entity"

        # Extract code-like identifiers
        identifiers = re.findall(r"\b[a-z_][a-z0-9_]*\b", content)
        for identifier in set(identifiers)[:5]:  # Limit to avoid noise
            if len(identifier) > 2:
                entities[identifier] = "concept"

        # Extract key terms from patterns
        if re.search(r"\b(function|method|class|interface|module)\b", content):
            entities["function"] = "concept"
        if re.search(r"\b(parameter|argument|variable|data)\b", content):
            entities["data"] = "concept"

        return entities

    def _analyze_entity_relationships(
        self, entities: Dict[str, str]
    ) -> Dict[str, List[Tuple[str, str]]]:
        """Analyze relationships between entities."""
        relationships = defaultdict(list)

        entity_list = list(entities.keys())
        for i, entity1 in enumerate(entity_list):
            for entity2 in entity_list[i + 1 :]:
                # Simple heuristic: entities close in name might be related
                if set(entity1.lower()) & set(entity2.lower()):
                    relationships["semantic_similarity"].append((entity1, entity2))

        return dict(relationships)

    def _identify_domain_impl(self, content: str) -> str:
        """Identify the domain of content."""
        domain_patterns = {
            "programming": ["function", "class", "variable", "algorithm", "code"],
            "data": ["data", "database", "query", "schema", "table"],
            "web": ["html", "css", "javascript", "api", "endpoint"],
            "devops": ["docker", "kubernetes", "deployment", "ci/cd", "infrastructure"],
            "security": ["encryption", "authentication", "authorization", "vulnerability"],
            "general": [],
        }

        content_lower = content.lower()
        scores = {}

        for domain, keywords in domain_patterns.items():
            score = sum(1 for kw in keywords if kw in content_lower)
            scores[domain] = score

        best_domain = max(scores, key=scores.get)
        return best_domain if scores[best_domain] > 0 else "general"

    def _calculate_domain_confidence(self, content: str, domain: str) -> float:
        """Calculate confidence in domain identification."""
        domain_keywords = {
            "programming": ["function", "class", "variable"],
            "data": ["database", "schema", "query"],
            "web": ["html", "api", "endpoint"],
        }

        keywords = domain_keywords.get(domain, [])
        if not keywords:
            return 0.5

        matches = sum(1 for kw in keywords if kw in content.lower())
        return min(matches / len(keywords), 1.0)

    def _calculate_relevance(self, query: str, content: str) -> float:
        """Calculate relevance score between query and content."""
        query_terms = set(query.lower().split())
        content_terms = set(content.lower().split())

        if not query_terms:
            return 0.0

        overlap = query_terms & content_terms
        return len(overlap) / len(query_terms)
