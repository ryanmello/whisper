"""
Context Analyzer for understanding and parsing analysis requests.

This module analyzes context from the frontend to determine the appropriate
analysis strategy and tool selection.
"""

import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

from tools.base_tool import AnalysisContext
from utils.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class ParsedIntent:
    """Result of intent parsing."""
    primary_intent: str
    secondary_intents: List[str]
    confidence: float
    reasoning: str


@dataclass
class LanguageDetection:
    """Result of language detection from context."""
    detected_languages: List[str]
    confidence_scores: Dict[str, float]
    evidence: Dict[str, List[str]]


class ContextAnalyzer:
    """
    Analyzes context from frontend requests to determine analysis strategy.
    
    This class parses natural language context, detects intent, identifies
    target languages, and creates structured analysis contexts.
    """
    
    def __init__(self):
        # Intent keywords mapping
        self.intent_keywords = {
            "explore": [
                "explore", "analyze", "understand", "overview", "architecture",
                "structure", "examine", "investigate", "scan", "review", "study"
            ],
            "find_vulnerabilities": [
                "vulnerability", "vulnerabilities", "security", "exploit", "cve",
                "weakness", "flaw", "breach", "attack", "threat", "risk"
            ],
            "security_audit": [
                "audit", "security audit", "security review", "penetration",
                "assessment", "compliance", "hardening"
            ],
            "analyze_performance": [
                "performance", "optimization", "speed", "slow", "bottleneck",
                "efficiency", "resource", "memory", "cpu"
            ],
            "code_quality": [
                "quality", "best practices", "standards", "clean", "maintainability",
                "technical debt", "smell", "refactor"
            ],
            "documentation": [
                "document", "documentation", "readme", "comments", "explain"
            ]
        }
        
        # Language keywords and patterns
        self.language_patterns = {
            "go": [
                r"go\.mod", r"go\.sum", r"\.go$", "golang", "go lang", "go project"
            ],
            "python": [
                r"requirements\.txt", r"setup\.py", r"\.py$", "python", "pip", "conda"
            ],
            "javascript": [
                r"package\.json", r"\.js$", r"\.ts$", "node", "npm", "yarn", "typescript"
            ],
            "java": [
                r"pom\.xml", r"build\.gradle", r"\.java$", "maven", "gradle"
            ],
            "rust": [
                r"Cargo\.toml", r"\.rs$", "rust", "cargo"
            ],
            "c++": [
                r"CMakeLists\.txt", r"Makefile", r"\.(cpp|cc|cxx)$", "c++", "cpp"
            ],
            "c": [
                r"Makefile", r"\.c$", "c language"
            ]
        }
    
    def analyze_context(
        self, 
        context_text: str, 
        repository_url: str, 
        additional_params: Optional[Dict] = None
    ) -> AnalysisContext:
        """
        Analyze context and create structured AnalysisContext.
        
        Args:
            context_text: Natural language context from frontend
            repository_url: URL of repository to analyze
            additional_params: Optional additional parameters
            
        Returns:
            Structured AnalysisContext object
        """
        logger.info(f"Analyzing context: {context_text[:100]}...")
        
        # Parse intent from context
        parsed_intent = self._parse_intent(context_text)
        
        # Detect target languages
        language_detection = self._detect_languages(context_text, repository_url)
        
        # Determine scope and depth
        scope = self._determine_scope(context_text, parsed_intent)
        depth = self._determine_depth(context_text, parsed_intent)
        
        # Extract specific files if mentioned
        specific_files = self._extract_specific_files(context_text)
        
        return AnalysisContext(
            repository_path="",  # Will be set when repository is cloned
            repository_url=repository_url,
            intent=parsed_intent.primary_intent,
            target_languages=language_detection.detected_languages,
            scope=scope,
            specific_files=specific_files,
            depth=depth,
            additional_params=additional_params or {}
        )
    
    def _parse_intent(self, context_text: str) -> ParsedIntent:
        """
        Parse the primary intent from context text.
        
        Args:
            context_text: Context text to analyze
            
        Returns:
            ParsedIntent object with analysis results
        """
        context_lower = context_text.lower()
        intent_scores = {}
        
        # Score each intent based on keyword matches
        for intent, keywords in self.intent_keywords.items():
            score = 0
            matched_keywords = []
            
            for keyword in keywords:
                if keyword in context_lower:
                    # Give higher score for exact matches
                    if keyword == context_lower.strip():
                        score += 10
                    else:
                        score += 1
                    matched_keywords.append(keyword)
            
            if score > 0:
                intent_scores[intent] = {
                    "score": score,
                    "keywords": matched_keywords
                }
        
        # Determine primary intent
        if not intent_scores:
            # Default intent if no keywords match
            primary_intent = "explore"
            confidence = 0.3
            reasoning = "No specific keywords found, defaulting to exploration"
        else:
            # Get highest scoring intent
            primary_intent = max(intent_scores.keys(), key=lambda x: intent_scores[x]["score"])
            max_score = intent_scores[primary_intent]["score"]
            total_score = sum(data["score"] for data in intent_scores.values())
            confidence = max_score / total_score if total_score > 0 else 0.5
            
            matched_keywords = intent_scores[primary_intent]["keywords"]
            reasoning = f"Matched keywords: {', '.join(matched_keywords)}"
        
        # Get secondary intents (other high-scoring intents)
        secondary_intents = [
            intent for intent, data in intent_scores.items()
            if intent != primary_intent and data["score"] >= 2
        ]
        
        return ParsedIntent(
            primary_intent=primary_intent,
            secondary_intents=secondary_intents,
            confidence=confidence,
            reasoning=reasoning
        )
    
    def _detect_languages(self, context_text: str, repository_url: str) -> LanguageDetection:
        """
        Detect target programming languages from context and repository URL.
        
        Args:
            context_text: Context text to analyze
            repository_url: Repository URL for additional clues
            
        Returns:
            LanguageDetection object with results
        """
        context_lower = context_text.lower()
        repo_url_lower = repository_url.lower()
        
        language_scores = {}
        language_evidence = {}
        
        for language, patterns in self.language_patterns.items():
            score = 0
            evidence = []
            
            for pattern in patterns:
                # Check in context text
                if re.search(pattern, context_lower):
                    score += 2
                    evidence.append(f"Found '{pattern}' in context")
                
                # Check in repository URL
                if re.search(pattern, repo_url_lower):
                    score += 1
                    evidence.append(f"Found '{pattern}' in repository URL")
            
            # Check for explicit language mentions
            if language in context_lower:
                score += 3
                evidence.append(f"Explicit mention of {language}")
            
            if score > 0:
                language_scores[language] = score
                language_evidence[language] = evidence
        
        # Convert scores to confidence percentages
        if language_scores:
            max_score = max(language_scores.values())
            confidence_scores = {
                lang: score / max_score for lang, score in language_scores.items()
            }
            # Only include languages with confidence > 0.3
            detected_languages = [
                lang for lang, conf in confidence_scores.items() if conf > 0.3
            ]
        else:
            confidence_scores = {}
            detected_languages = []
        
        return LanguageDetection(
            detected_languages=detected_languages,
            confidence_scores=confidence_scores,
            evidence=language_evidence
        )
    
    def _determine_scope(self, context_text: str, parsed_intent: ParsedIntent) -> str:
        """
        Determine analysis scope from context.
        
        Args:
            context_text: Context text
            parsed_intent: Parsed intent information
            
        Returns:
            Scope string ("full", "security_focused", "performance_focused")
        """
        context_lower = context_text.lower()
        
        # Intent-based scope determination
        if parsed_intent.primary_intent in ["find_vulnerabilities", "security_audit"]:
            return "security_focused"
        elif parsed_intent.primary_intent == "analyze_performance":
            return "performance_focused"
        
        # Keyword-based scope determination
        security_keywords = ["security", "vulnerability", "exploit", "threat"]
        performance_keywords = ["performance", "optimization", "bottleneck", "speed"]
        
        if any(keyword in context_lower for keyword in security_keywords):
            return "security_focused"
        elif any(keyword in context_lower for keyword in performance_keywords):
            return "performance_focused"
        
        return "full"
    
    def _determine_depth(self, context_text: str, parsed_intent: ParsedIntent) -> str:
        """
        Determine analysis depth from context.
        
        Args:
            context_text: Context text
            parsed_intent: Parsed intent information
            
        Returns:
            Depth string ("surface", "deep", "comprehensive")
        """
        context_lower = context_text.lower()
        
        # Depth indicators
        surface_keywords = ["quick", "brief", "overview", "summary", "fast"]
        deep_keywords = ["detailed", "thorough", "comprehensive", "in-depth", "complete"]
        
        if any(keyword in context_lower for keyword in surface_keywords):
            return "surface"
        elif any(keyword in context_lower for keyword in deep_keywords):
            return "comprehensive"
        
        # Default based on intent
        if parsed_intent.primary_intent in ["find_vulnerabilities", "security_audit"]:
            return "deep"
        
        return "comprehensive"
    
    def _extract_specific_files(self, context_text: str) -> List[str]:
        """
        Extract specific file mentions from context.
        
        Args:
            context_text: Context text to analyze
            
        Returns:
            List of specific files mentioned
        """
        # Common file patterns
        file_patterns = [
            r'go\.mod', r'go\.sum', r'package\.json', r'requirements\.txt',
            r'Dockerfile', r'README\.md', r'\.gitignore',
            r'\w+\.(go|py|js|ts|java|cpp|c|rs|rb|php)(?:\s|$|,|\.)',
            r'[a-zA-Z0-9_-]+/[a-zA-Z0-9_.-]+\.[a-zA-Z]{1,4}'
        ]
        
        specific_files = []
        for pattern in file_patterns:
            matches = re.findall(pattern, context_text, re.IGNORECASE)
            specific_files.extend(matches)
        
        # Clean up the matches
        cleaned_files = []
        for file_match in specific_files:
            # Remove trailing punctuation
            cleaned = re.sub(r'[,.\s]+$', '', file_match)
            if cleaned and cleaned not in cleaned_files:
                cleaned_files.append(cleaned)
        
        return cleaned_files
    
    def enhance_context_with_repository_info(
        self, 
        context: AnalysisContext, 
        repository_path: str,
        detected_languages: Optional[List[str]] = None
    ) -> AnalysisContext:
        """
        Enhance context with information gathered from the repository.
        
        Args:
            context: Existing analysis context
            repository_path: Path to cloned repository
            detected_languages: Languages detected from repository scanning
            
        Returns:
            Enhanced AnalysisContext
        """
        enhanced_context = AnalysisContext(
            repository_path=repository_path,
            repository_url=context.repository_url,
            intent=context.intent,
            target_languages=detected_languages or context.target_languages,
            scope=context.scope,
            specific_files=context.specific_files,
            depth=context.depth,
            additional_params=context.additional_params
        )
        
        return enhanced_context 