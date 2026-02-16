#!/usr/bin/env python3
"""
Unit tests for tokenQrusher context classifier.

Tests the classifyComplexity function exhaustively.
"""
import pytest
import sys
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'hooks' / 'token-context'))

from classifier import (
    classifyComplexity,
    getAllowedFiles,
    isValidFileName,
    ComplexityLevel,
    ContextConfig
)


# =============================================================================
# THEOREMS (Test fixtures as constants)
# =============================================================================

SIMPLE_MESSAGES = [
    "hi",
    "hey",
    "hello",
    "yo",
    "sup",
    "howdy",
    "thanks",
    "thank you",
    "thx",
    "ty",
    "ok",
    "okay",
    "sure",
    "got it",
    "yes",
    "yeah",
    "yep",
    "yup",
    "no",
    "nope",
    "nah",
    "good",
    "great",
    "nice",
    "cool",
    "awesome",
    "?",
    "??",
    "???",
]

COMPLEX_MESSAGES = [
    "design a system architecture",
    "architect a microservices system",
    "comprehensive analysis of the codebase",
    "plan a distributed system",
    "create a system from scratch",
    "refactor completely",
    "implement full system",
    "optimize performance",
    "debug complex issue",
    "fix entire codebase",
    "build from scratch",
    "write complex algorithm",
]

STANDARD_MESSAGES = [
    "write a function",
    "create a file",
    "edit this code",
    "fix the bug",
    "how do I use this",
    "what is this",
    "add a feature",
    "remove this line",
    "find the error",
    "search for pattern",
]


# =============================================================================
# THEOREM: classifyComplexity is deterministic
# =============================================================================

class TestClassifierDeterminism:
    """Theorem: Same input always produces same output."""
    
    @pytest.mark.parametrize("message", SIMPLE_MESSAGES)
    def test_simple_messages_are_deterministic(self, message):
        """Same simple message should always return simple."""
        result1 = classifyComplexity(message)
        result2 = classifyComplexity(message)
        
        assert result1.level == result2.level
        assert result1.confidence == result2.confidence
    
    @pytest.mark.parametrize("message", COMPLEX_MESSAGES)
    def test_complex_messages_are_deterministic(self, message):
        """Same complex message should always return complex."""
        result1 = classifyComplexity(message)
        result2 = classifyComplexity(message)
        
        assert result1.level == result2.level
        assert result1.confidence == result2.confidence


# =============================================================================
# THEOREM: Simple messages classified correctly
# =============================================================================

class TestSimpleClassification:
    """Theorem: Greetings/acknowledgments return SIMPLE."""
    
    @pytest.mark.parametrize("message", SIMPLE_MESSAGES)
    def test_simple_greetings(self, message):
        """All greetings should be classified as simple."""
        result = classifyComplexity(message)
        
        assert result.level == ComplexityLevel.SIMPLE, \
            f"Expected SIMPLE for '{message}', got {result.level}"
    
    def test_empty_message(self):
        """Empty message should default to STANDARD."""
        result = classifyComplexity("")
        
        assert result.level == ComplexityLevel.STANDARD
    
    def test_none_message(self):
        """None message should default to STANDARD."""
        result = classifyComplexity(None)
        
        assert result.level == ComplexityLevel.STANDARD
    
    def test_question_marks_only(self):
        """Question marks only should be SIMPLE."""
        result = classifyComplexity("??")
        
        assert result.level == ComplexityLevel.SIMPLE


# =============================================================================
# THEOREM: Complex messages classified correctly
# =============================================================================

class TestComplexClassification:
    """Theorem: Design/architecture tasks return COMPLEX."""
    
    @pytest.mark.parametrize("message", COMPLEX_MESSAGES)
    def test_complex_messages(self, message):
        """Complex design tasks should be classified as complex."""
        result = classifyComplexity(message)
        
        assert result.level == ComplexityLevel.COMPLEX, \
            f"Expected COMPLEX for '{message}', got {result.level}"


# =============================================================================
# THEOREM: Standard messages classified correctly
# =============================================================================

class TestStandardClassification:
    """Theorem: Regular work tasks return STANDARD."""
    
    @pytest.mark.parametrize("message", STANDARD_MESSAGES)
    def test_standard_messages(self, message):
        """Standard work tasks should be classified as standard."""
        result = classifyComplexity(message)
        
        assert result.level == ComplexityLevel.STANDARD, \
            f"Expected STANDARD for '{message}', got {result.level}"


# =============================================================================
# THEOREM: getAllowedFiles returns correct files per level
# =============================================================================

class TestGetAllowedFiles:
    """Theorem: Different levels return different file counts."""
    
    def test_simple_files(self):
        """Simple should return 2 files."""
        files = getAllowedFiles(ComplexityLevel.SIMPLE)
        
        assert len(files) == 2
        assert 'SOUL.md' in files
        assert 'IDENTITY.md' in files
    
    def test_standard_files(self):
        """Standard should return 3 files."""
        files = getAllowedFiles(ComplexityLevel.STANDARD)
        
        assert len(files) == 3
        assert 'SOUL.md' in files
        assert 'IDENTITY.md' in files
        assert 'USER.md' in files
    
    def test_complex_files(self):
        """Complex should return 7 files."""
        files = getAllowedFiles(ComplexityLevel.COMPLEX)
        
        assert len(files) == 7
    
    def test_custom_config(self):
        """Custom config should override defaults."""
        config = ContextConfig(
            files={
                'simple': ['SOUL.md'],
                'standard': ['SOUL.md', 'IDENTITY.md'],
                'complex': ['SOUL.md', 'IDENTITY.md', 'USER.md']
            }
        )
        
        simple_files = getAllowedFiles(ComplexityLevel.SIMPLE, config)
        assert len(simple_files) == 1


# =============================================================================
# THEOREM: isValidFileName prevents path traversal
# =============================================================================

class TestFileNameValidation:
    """Theorem: Invalid file names are rejected."""
    
    @pytest.mark.parametrize("name", [
        "../../../etc/passwd",
        "..\\..\\windows\\system32",
        "file with spaces.md",
        "file\twith\ttabs.md",
        "file\nwith\nnewlines.md",
        "file;rm-rf.md",
        "file`whoami`.md",
        "file$(whoami).md",
    ])
    def test_invalid_names_rejected(self, name):
        """Path traversal and special characters should be rejected."""
        assert isValidFileName(name) is False, f"Should reject: {name}"
    
    @pytest.mark.parametrize("name", [
        "SOUL.md",
        "IDENTITY.md",
        "USER.md",
        "file123.md",
        "file-name.md",
        "file_name.md",
        "File.Name.md",
        "A.md",
    ])
    def test_valid_names_accepted(self, name):
        """Valid file names should be accepted."""
        assert isValidFileName(name) is True, f"Should accept: {name}"


# =============================================================================
# THEOREM: Confidence scores are bounded
# =============================================================================

class TestConfidenceBounds:
    """Theorem: Confidence is always between 0 and 1."""
    
    @pytest.mark.parametrize("message", SIMPLE_MESSAGES + COMPLEX_MESSAGES + STANDARD_MESSAGES)
    def test_confidence_is_valid(self, message):
        """Confidence should be between 0 and 1."""
        result = classifyComplexity(message)
        
        assert 0 <= result.confidence <= 1, \
            f"Confidence {result.confidence} out of bounds for '{message}'"


# =============================================================================
# THEOREM: Reasoning is always provided
# =============================================================================

class TestReasoningProvided:
    """Theorem: Every classification includes reasoning."""
    
    @pytest.mark.parametrize("message", SIMPLE_MESSAGES + COMPLEX_MESSAGES + STANDARD_MESSAGES)
    def test_reasoning_always_present(self, message):
        """Every result should have reasoning."""
        result = classifyComplexity(message)
        
        assert result.reasoning is not None
        assert len(result.reasoning) > 0


# =============================================================================
# EDGE CASES
# =============================================================================

class TestEdgeCases:
    """Theorem: Edge cases handled gracefully."""
    
    def test_very_long_message(self):
        """Very long messages should still classify."""
        long_message = "hi " * 10000
        
        result = classifyComplexity(long_message)
        
        assert result.level in ComplexityLevel
    
    def test_unicode_message(self):
        """Unicode should not break classification."""
        messages = [
            "👋",
            "こんにちは",
            "🎉",
            "привет",
        ]
        
        for msg in messages:
            result = classifyComplexity(msg)
            assert result.level in ComplexityLevel
    
    def test_mixed_case(self):
        """Case insensitivity should work."""
        result1 = classifyComplexity("HI")
        result2 = classifyComplexity("hi")
        
        assert result1.level == result2.level
    
    def test_leading_trailing_whitespace(self):
        """Whitespace should be trimmed."""
        result1 = classifyComplexity("  hi  ")
        result2 = classifyComplexity("hi")
        
        assert result1.level == result2.level


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
