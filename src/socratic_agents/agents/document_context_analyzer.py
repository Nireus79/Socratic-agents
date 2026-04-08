"""Document Context Analyzer Agent - Document semantic analysis and context building.

This agent:
1. Analyzes document structure and semantics
2. Extracts contextual information from documents
3. Identifies document themes and topics
4. Builds semantic relationships within documents
5. Performs text analysis and summarization
6. Generates document metadata and annotations
7. Tracks document evolution and versions
"""

import re
from collections import Counter, defaultdict
from datetime import datetime
from typing import Any, Dict, List, Optional, Set, cast

from .base import BaseAgent


class DocumentAnalysis:
    """Represents analysis of a document."""

    def __init__(self, doc_id: str, content: str):
        self.id = doc_id
        self.content = content
        self.content_length = len(content)
        self.analyzed_at = datetime.utcnow()

        # Structure analysis
        self.paragraphs = content.split("\n\n")
        self.sentences = re.split(r"[.!?]+", content)
        self.words = re.findall(r"\b\w+\b", content)

        # Computed metrics
        self.paragraph_count = len(self.paragraphs)
        self.sentence_count = len([s for s in self.sentences if s.strip()])
        self.word_count = len(self.words)
        self.avg_word_length = (
            sum(len(w) for w in self.words) / len(self.words) if self.words else 0
        )
        self.avg_sentence_length = (
            self.word_count / self.sentence_count if self.sentence_count > 0 else 0
        )

        # Linguistic features
        self.word_frequency = Counter(w.lower() for w in self.words)
        self.unique_words = len(set(w.lower() for w in self.words))
        self.lexical_diversity = self.unique_words / self.word_count if self.word_count > 0 else 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "content_length": self.content_length,
            "paragraph_count": self.paragraph_count,
            "sentence_count": self.sentence_count,
            "word_count": self.word_count,
            "avg_word_length": round(self.avg_word_length, 2),
            "avg_sentence_length": round(self.avg_sentence_length, 2),
            "unique_words": self.unique_words,
            "lexical_diversity": round(self.lexical_diversity, 3),
            "analyzed_at": self.analyzed_at.isoformat(),
        }


class DocumentTheme:
    """Represents an identified theme in a document."""

    def __init__(self, name: str, keywords: List[str], strength: float):
        self.id = f"theme_{datetime.utcnow().timestamp()}"
        self.name = name
        self.keywords = keywords
        self.strength = strength  # 0.0-1.0
        self.created_at = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "keywords": self.keywords,
            "strength": round(self.strength, 3),
            "created_at": self.created_at.isoformat(),
        }


class DocumentContextAnalyzer(BaseAgent):
    """
    Agent that performs comprehensive document semantic analysis.

    Provides:
    - Structural analysis (paragraphs, sentences, words)
    - Linguistic feature extraction
    - Theme and topic detection
    - Semantic relationship mapping
    - Document summarization
    - Metadata and annotation generation
    - Document versioning and evolution tracking
    """

    def __init__(self, llm_client: Optional[Any] = None):
        """Initialize the Document Context Analyzer."""
        super().__init__(name="DocumentContextAnalyzer", llm_client=llm_client)
        self.analyzed_docs: Dict[str, DocumentAnalysis] = {}
        self.document_themes: Dict[str, List[DocumentTheme]] = {}
        self.document_index: Dict[str, Set[str]] = defaultdict(set)
        self.semantic_graph: Dict[str, Set[str]] = defaultdict(set)
        self.document_versions: Dict[str, List[str]] = defaultdict(list)

    def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process document context analysis requests."""
        action = request.get("action", "analyze")

        if action == "analyze":
            return self.analyze_document(cast(str, request.get("document")), cast(Optional[str], request.get("doc_id")))
        elif action == "extract_context":
            return self.extract_context(cast(str, request.get("document")))
        elif action == "extract_themes":
            return self.extract_themes(cast(str, request.get("document")))
        elif action == "extract_topics":
            return self.extract_topics(cast(str, request.get("document")), cast(int, request.get("limit", 5)))
        elif action == "build_semantic_graph":
            return self.build_semantic_graph(cast(str, request.get("document")))
        elif action == "summarize":
            return self.summarize_document(cast(str, request.get("document")), cast(float, request.get("ratio", 0.3)))
        elif action == "generate_metadata":
            return self.generate_metadata(cast(str, request.get("document")), cast(Optional[str], request.get("doc_id")))
        elif action == "analyze_structure":
            return self.analyze_structure(cast(str, request.get("document")))
        elif action == "list":
            return self.list_analyzed()
        elif action == "get_analysis":
            return self.get_analysis(cast(str, request.get("doc_id")))
        else:
            return {"status": "error", "message": f"Unknown action: {action}"}

    def analyze_document(self, document: str, doc_id: Optional[str] = None) -> Dict[str, Any]:
        """Comprehensive document analysis."""
        if not document:
            return {"status": "error", "message": "Document required"}

        if not doc_id:
            doc_id = f"doc_{datetime.utcnow().timestamp()}"

        # Perform structural analysis
        analysis = DocumentAnalysis(doc_id, document)
        self.analyzed_docs[doc_id] = analysis

        # Extract themes
        themes = self._detect_themes(document)
        self.document_themes[doc_id] = themes

        # Build semantic graph
        self._build_semantic_relationships(document, doc_id)

        # Track version
        self.document_versions[doc_id].append(datetime.utcnow().isoformat())

        return {
            "status": "success",
            "agent": self.name,
            "doc_id": doc_id,
            "analysis": analysis.to_dict(),
            "themes_detected": len(themes),
            "top_themes": [t.to_dict() for t in themes[:3]],
        }

    def extract_context(self, document: str) -> Dict[str, Any]:
        """Extract contextual information from document."""
        if not document:
            return {"status": "error", "message": "Document required"}

        # Identify context regions (paragraphs with substantial content)
        lines = document.split("\n")
        context_lines = [line for line in lines if len(line.strip()) > 10]

        # Extract key concepts
        words = re.findall(r"\b\w+\b", document)
        word_freq = Counter(words)
        key_concepts = [word for word, _ in word_freq.most_common(10)]

        # Analyze context density
        total_lines = len(lines)
        context_density = len(context_lines) / max(total_lines, 1)

        return {
            "status": "success",
            "agent": self.name,
            "context_extracted": len(context_lines),
            "context_density": round(context_density, 3),
            "key_concepts": key_concepts,
            "content_lines": len(context_lines),
            "total_lines": total_lines,
        }

    def extract_themes(self, document: str) -> Dict[str, Any]:
        """Extract themes from document."""
        if not document:
            return {"status": "error", "message": "Document required"}

        themes = self._detect_themes(document)

        return {
            "status": "success",
            "agent": self.name,
            "themes_detected": len(themes),
            "themes": [t.to_dict() for t in themes],
        }

    def extract_topics(self, document: str, limit: int = 5) -> Dict[str, Any]:
        """Extract main topics from document."""
        if not document:
            return {"status": "error", "message": "Document required"}

        # Extract capitalized words (likely topics)
        topics = re.findall(r"\b[A-Z][a-z]+(?:\s[A-Z][a-z]+)*\b", document)
        topic_freq = Counter(topics)
        top_topics = [topic for topic, _ in topic_freq.most_common(limit)]

        return {
            "status": "success",
            "agent": self.name,
            "topics_extracted": len(top_topics),
            "topics": top_topics,
            "topic_frequencies": dict(topic_freq.most_common(limit)),
        }

    def build_semantic_graph(self, document: str) -> Dict[str, Any]:
        """Build semantic graph of concepts in document."""
        if not document:
            return {"status": "error", "message": "Document required"}

        # Extract concepts (words that appear frequently and have context)
        words = re.findall(r"\b\w{4,}\b", document.lower())  # Words with 4+ chars
        word_freq = Counter(words)
        concepts = [word for word, count in word_freq.most_common(10) if count > 1]

        # Create relationships based on co-occurrence
        sentences = re.split(r"[.!?]+", document)
        relationships = set()
        for sentence in sentences:
            sent_concepts = [w for w in concepts if w in sentence.lower()]
            for i, c1 in enumerate(sent_concepts):
                for c2 in sent_concepts[i + 1 :]:
                    relationships.add((c1, c2))
                    self.semantic_graph[c1].add(c2)
                    self.semantic_graph[c2].add(c1)

        return {
            "status": "success",
            "agent": self.name,
            "concepts_identified": len(concepts),
            "concepts": concepts,
            "relationships_found": len(relationships),
            "graph_density": len(relationships) / max(len(concepts) * (len(concepts) - 1) / 2, 1),
        }

    def summarize_document(self, document: str, ratio: float = 0.3) -> Dict[str, Any]:
        """Generate summary of document."""
        if not document:
            return {"status": "error", "message": "Document required"}

        # Extract sentences and score them
        sentences = re.split(r"[.!?]+", document)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 10]

        # Score sentences by keyword frequency
        words = re.findall(r"\b\w+\b", document.lower())
        word_freq = Counter(words)

        sentence_scores = []
        for sentence in sentences:
            score = sum(word_freq.get(w.lower(), 0) for w in sentence.split())
            sentence_scores.append((sentence, score))

        # Select top sentences
        summary_count = max(1, int(len(sentences) * ratio))
        top_sentences = sorted(sentence_scores, key=lambda x: x[1], reverse=True)[:summary_count]
        summary = ". ".join(
            s[0] for s in sorted(top_sentences, key=lambda x: sentences.index(x[0]))
        )

        return {
            "status": "success",
            "agent": self.name,
            "original_sentences": len(sentences),
            "summary_sentences": len(top_sentences),
            "compression_ratio": round(summary_count / len(sentences), 3) if sentences else 0,
            "summary": summary,
        }

    def generate_metadata(self, document: str, doc_id: Optional[str] = None) -> Dict[str, Any]:
        """Generate metadata for document."""
        if not document:
            return {"status": "error", "message": "Document required"}

        if not doc_id:
            doc_id = f"doc_{datetime.utcnow().timestamp()}"

        # Analyze document
        analysis = DocumentAnalysis(doc_id, document)

        # Extract main topics
        topics = re.findall(r"\b[A-Z][a-z]+\b", document)
        top_topics = [t for t, _ in Counter(topics).most_common(5)]

        # Detect language (simplified)
        language = "english"  # Simplified
        encoding = "utf-8"

        metadata = {
            "doc_id": doc_id,
            "created": datetime.utcnow().isoformat(),
            "language": language,
            "encoding": encoding,
            "length": analysis.content_length,
            "word_count": analysis.word_count,
            "topic_count": len(top_topics),
            "topics": top_topics,
            "lexical_diversity": round(analysis.lexical_diversity, 3),
            "complexity": self._calculate_complexity(analysis),
        }

        return {
            "status": "success",
            "agent": self.name,
            "metadata": metadata,
        }

    def analyze_structure(self, document: str) -> Dict[str, Any]:
        """Analyze document structure."""
        if not document:
            return {"status": "error", "message": "Document required"}

        analysis = DocumentAnalysis(f"struct_{datetime.utcnow().timestamp()}", document)

        return {
            "status": "success",
            "agent": self.name,
            "structure": analysis.to_dict(),
        }

    def list_analyzed(self) -> Dict[str, Any]:
        """List all analyzed documents."""
        return {
            "status": "success",
            "agent": self.name,
            "documents_analyzed": len(self.analyzed_docs),
            "total_words": sum(a.word_count for a in self.analyzed_docs.values()),
            "avg_word_count": round(
                sum(a.word_count for a in self.analyzed_docs.values())
                / max(len(self.analyzed_docs), 1),
                0,
            ),
            "document_ids": list(self.analyzed_docs.keys()),
        }

    def get_analysis(self, doc_id: str) -> Dict[str, Any]:
        """Get analysis for specific document."""
        if not doc_id:
            return {"status": "error", "message": "Document ID required"}

        if doc_id not in self.analyzed_docs:
            return {"status": "error", "message": f"Document {doc_id} not found"}

        analysis = self.analyzed_docs[doc_id]
        themes = self.document_themes.get(doc_id, [])

        return {
            "status": "success",
            "agent": self.name,
            "analysis": analysis.to_dict(),
            "themes": [t.to_dict() for t in themes],
        }

    # Helper methods
    def _detect_themes(self, content: str) -> List[DocumentTheme]:
        """Detect themes in content."""
        themes = []

        # Programming-related theme
        if any(kw in content.lower() for kw in ["function", "class", "code", "algorithm"]):
            keywords = ["function", "class", "code", "algorithm"]
            themes.append(DocumentTheme("Programming", keywords, 0.85))

        # Data-related theme
        if any(kw in content.lower() for kw in ["data", "database", "query", "schema"]):
            keywords = ["data", "database", "query"]
            themes.append(DocumentTheme("Data", keywords, 0.80))

        # Documentation theme
        if any(kw in content.lower() for kw in ["documentation", "guide", "tutorial", "example"]):
            keywords = ["documentation", "guide", "example"]
            themes.append(DocumentTheme("Documentation", keywords, 0.75))

        return themes

    def _build_semantic_relationships(self, content: str, doc_id: str) -> None:
        """Build semantic relationships within document."""
        # Index keywords for document
        keywords = re.findall(r"\b[a-zA-Z]{4,}\b", content)
        self.document_index[doc_id] = set(keywords)

    def _calculate_complexity(self, analysis: DocumentAnalysis) -> str:
        """Calculate document complexity."""
        if analysis.avg_word_length < 4 and analysis.avg_sentence_length < 10:
            return "simple"
        elif analysis.avg_word_length < 6 and analysis.avg_sentence_length < 15:
            return "moderate"
        else:
            return "complex"
