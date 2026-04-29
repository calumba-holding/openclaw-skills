#!/usr/bin/env python3
"""
GEO Score Calculator
Calculate GEO optimization score for content
"""

import json
import re
from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class GEOScore:
    """GEO scoring result"""
    content_quality: int       # Content quality 0-100
    schema_completeness: int   # Schema completeness 0-100
    faq_coverage: int         # FAQ coverage 0-100
    citation_activity: int     # Citation activity 0-100
    total_score: int          # Overall score 0-100
    suggestions: List[str]     # Optimization suggestions


class GEOScorer:
    """GEO scoring engine"""
    
    def __init__(self):
        self.weights = {
            'content_quality': 0.35,
            'schema_completeness': 0.25,
            'faq_coverage': 0.25,
            'citation_activity': 0.15
        }
    
    def calculate_score(
        self,
        content: str,
        schema: Dict[str, Any] = None,
        faq_count: int = 0,
        citation_count: int = 0
    ) -> GEOScore:
        """Calculate GEO score"""
        
        # 1. Content quality score
        content_score = self._score_content(content)
        
        # 2. Schema completeness score
        schema_score = self._score_schema(schema)
        
        # 3. FAQ coverage score
        faq_score = self._score_faq(faq_count)
        
        # 4. Citation activity score
        citation_score = self._score_citation(citation_count)
        
        # 5. Overall score
        total = int(
            content_score * self.weights['content_quality'] +
            schema_score * self.weights['schema_completeness'] +
            faq_score * self.weights['faq_coverage'] +
            citation_score * self.weights['citation_activity']
        )
        
        # 6. Generate suggestions
        suggestions = self._generate_suggestions(
            content_score, schema_score, faq_score, citation_score
        )
        
        return GEOScore(
            content_quality=content_score,
            schema_completeness=schema_score,
            faq_coverage=faq_score,
            citation_activity=citation_score,
            total_score=total,
            suggestions=suggestions
        )
    
    def _score_content(self, content: str) -> int:
        """Content quality scoring"""
        score = 0
        
        # Word count check (1500+ earns full score)
        word_count = len(content)
        if word_count >= 1500:
            score += 30
        elif word_count >= 1200:
            score += 25
        elif word_count >= 800:
            score += 15
        else:
            score += 5
        
        # Data citation check
        data_patterns = [
            r'\d+%',       # Percentage
            r'\$\d+',      # Dollar amount
            r'\d+ [A-Za-z]+',  # Count with unit
            r'per.*source',    # Data source
        ]
        data_count = sum(len(re.findall(p, content, re.IGNORECASE)) for p in data_patterns)
        if data_count >= 3:
            score += 25
        elif data_count >= 1:
            score += 15
        else:
            score += 0
        
        # Structure check (headings)
        heading_count = len(re.findall(r'^#{1,3}\s+', content, re.MULTILINE))
        if heading_count >= 5:
            score += 20
        elif heading_count >= 3:
            score += 15
        else:
            score += 5
        
        # FAQ section check
        if 'FAQ' in content or 'Frequently Asked' in content:
            score += 25
        else:
            score += 0
        
        return min(score, 100)
    
    def _score_schema(self, schema: Dict[str, Any] = None) -> int:
        """Schema completeness scoring"""
        if not schema:
            return 0
        
        score = 0
        required_types = ['@context', '@type', 'name']
        for req in required_types:
            if req in schema:
                score += 20
            else:
                score += 0
        
        # Bonus for FAQPage schema
        if schema.get('@type') == 'FAQPage':
            score += 20
        
        return min(score, 100)
    
    def _score_faq(self, faq_count: int) -> int:
        """FAQ coverage scoring"""
        if faq_count >= 8:
            return 100
        elif faq_count >= 6:
            return 75
        elif faq_count >= 4:
            return 50
        elif faq_count >= 2:
            return 25
        else:
            return 0
    
    def _score_citation(self, citation_count: int) -> int:
        """Citation activity scoring"""
        if citation_count >= 10:
            return 100
        elif citation_count >= 7:
            return 80
        elif citation_count >= 5:
            return 60
        elif citation_count >= 3:
            return 40
        elif citation_count >= 1:
            return 20
        else:
            return 0
    
    def _generate_suggestions(
        self,
        content_score: int,
        schema_score: int,
        faq_score: int,
        citation_score: int
    ) -> List[str]:
        """Generate optimization suggestions"""
        suggestions = []
        
        if content_score < 60:
            suggestions.append("Content needs more depth — aim for 1200+ words with at least 3 data citations")
        if schema_score < 60:
            suggestions.append("Add structured Schema markup — include Product/FAQPage schema")
        if faq_score < 60:
            suggestions.append("Add more FAQ pairs — aim for at least 6 questions with concise answers")
        if citation_score < 40:
            suggestions.append("Boost citation activity — publish consistently and track rankings weekly")
        
        if not suggestions:
            suggestions.append("Content is well-optimized — continue publishing and monitor citation trends")
        
        return suggestions


if __name__ == '__main__':
    # Demo usage
    scorer = GEOScorer()
    
    sample_content = """
    # How B2B Exporters Use GEO for 127% More Inquiries
    
    In the competitive B2B export market, traditional advertising costs $1.20 per inquiry.
    This article explains how GEO delivers inquiries at just $0.04.
    
    ## What is GEO?
    GEO (Generative Engine Optimization) targets AI engines like Perplexity and ChatGPT.
    
    ## How to Get Started?
    1. Set up brand configuration
    2. Generate GEO content
    3. Publish to LinkedIn and Twitter
    4. Monitor citations
    
    ## FAQ
    Q: How long does GEO take? A: 2–4 weeks for first citation.
    """
    
    sample_schema = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "name": "GEO Guide for Exporters"
    }
    
    result = scorer.calculate_score(
        content=sample_content,
        schema=sample_schema,
        faq_count=4,
        citation_count=3
    )
    
    print(f"Overall GEO Score: {result.total_score}/100")
    print(f"  Content Quality: {result.content_quality}/100")
    print(f"  Schema Completeness: {result.schema_completeness}/100")
    print(f"  FAQ Coverage: {result.faq_coverage}/100")
    print(f"  Citation Activity: {result.citation_activity}/100")
    print("Suggestions:")
    for s in result.suggestions:
        print(f"  - {s}")
