"""
Analytics and statistics module for email insights
"""
import logging
from typing import List, Dict, Any
from collections import Counter, defaultdict
from datetime import datetime, timedelta
import re

logger = logging.getLogger(__name__)


class EmailAnalytics:
    """Generate analytics and insights from emails"""
    
    def __init__(self):
        self.emails = []
        self.classifications = []
        self.search_history = []
    
    def analyze_emails(self, emails: List[Dict], classifications: List[Dict] = None) -> Dict[str, Any]:
        """
        Generate comprehensive email analytics
        
        Args:
            emails: List of email dictionaries
            classifications: Optional list of classification results
        
        Returns:
            Dict with various analytics metrics
        """
        if not emails:
            return self._empty_analytics()
        
        self.emails = emails
        self.classifications = classifications or []
        
        return {
            "overview": self._get_overview(),
            "senders": self._analyze_senders(),
            "categories": self._analyze_categories(),
            "timeline": self._analyze_timeline(),
            "priorities": self._analyze_priorities(),
            "sentiments": self._analyze_sentiments(),
            "keywords": self._extract_keywords(),
            "threads": self._analyze_threads(),
        }
    
    def _empty_analytics(self) -> Dict[str, Any]:
        """Return empty analytics structure"""
        return {
            "overview": {"total_emails": 0, "date_range": None},
            "senders": [],
            "categories": {},
            "timeline": {},
            "priorities": {},
            "sentiments": {},
            "keywords": [],
            "threads": {"total": 0},
        }
    
    def _get_overview(self) -> Dict[str, Any]:
        """Get overview statistics"""
        dates = [email.get("date") for email in self.emails if email.get("date")]
        
        return {
            "total_emails": len(self.emails),
            "date_range": {
                "start": min(dates) if dates else None,
                "end": max(dates) if dates else None,
            },
            "avg_length": sum(len(email.get("body", "")) for email in self.emails) / len(self.emails),
            "with_attachments": sum(1 for c in self.classifications if c.get("has_attachments")),
        }
    
    def _analyze_senders(self) -> List[Dict[str, Any]]:
        """Analyze email senders"""
        sender_counts = Counter(email.get("from") for email in self.emails if email.get("from"))
        
        return [
            {
                "sender": sender,
                "count": count,
                "percentage": (count / len(self.emails)) * 100
            }
            for sender, count in sender_counts.most_common(10)
        ]
    
    def _analyze_categories(self) -> Dict[str, int]:
        """Analyze email categories"""
        if not self.classifications:
            return {}
        
        category_counts = defaultdict(int)
        for classification in self.classifications:
            for category in classification.get("categories", []):
                category_counts[category] += 1
        
        return dict(category_counts)
    
    def _analyze_timeline(self) -> Dict[str, Any]:
        """Analyze email timeline"""
        timeline = defaultdict(int)
        
        for email in self.emails:
            date_str = email.get("date", "")
            if date_str:
                # Extract date (YYYY-MM-DD)
                date_part = date_str.split("T")[0] if "T" in date_str else date_str[:10]
                timeline[date_part] += 1
        
        return {
            "daily": dict(sorted(timeline.items())),
            "total_days": len(timeline),
            "avg_per_day": len(self.emails) / len(timeline) if timeline else 0,
        }
    
    def _analyze_priorities(self) -> Dict[str, int]:
        """Analyze email priorities"""
        if not self.classifications:
            return {"high": 0, "medium": 0, "low": 0}
        
        priority_counts = Counter(c.get("priority", "low") for c in self.classifications)
        return dict(priority_counts)
    
    def _analyze_sentiments(self) -> Dict[str, int]:
        """Analyze email sentiments"""
        if not self.classifications:
            return {"positive": 0, "neutral": 0, "negative": 0}
        
        sentiment_counts = Counter(c.get("sentiment", "neutral") for c in self.classifications)
        return dict(sentiment_counts)
    
    def _extract_keywords(self, top_n: int = 20) -> List[Dict[str, Any]]:
        """Extract most common keywords"""
        # Combine all email text
        all_text = " ".join(
            f"{email.get('subject', '')} {email.get('body', '')}"
            for email in self.emails
        ).lower()
        
        # Remove common words
        stop_words = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
            "of", "with", "by", "from", "as", "is", "was", "are", "were", "be",
            "been", "being", "have", "has", "had", "do", "does", "did", "will",
            "would", "could", "should", "may", "might", "can", "this", "that",
            "these", "those", "i", "you", "he", "she", "it", "we", "they", "me",
            "him", "her", "us", "them", "my", "your", "his", "its", "our", "their"
        }
        
        # Extract words
        words = re.findall(r'\b[a-z]{4,}\b', all_text)
        word_counts = Counter(word for word in words if word not in stop_words)
        
        return [
            {"word": word, "count": count}
            for word, count in word_counts.most_common(top_n)
        ]
    
    def _analyze_threads(self) -> Dict[str, Any]:
        """Analyze email threads"""
        # Count replies and forwards
        replies = sum(1 for c in self.classifications if c.get("is_reply"))
        forwards = sum(1 for c in self.classifications if c.get("is_forward"))
        
        return {
            "total": len(self.emails),
            "replies": replies,
            "forwards": forwards,
            "original": len(self.emails) - replies - forwards,
        }


class SearchAnalytics:
    """Track and analyze search patterns"""
    
    def __init__(self):
        self.search_history = []
    
    def log_search(self, query: str, results_count: int, latency_ms: float):
        """Log a search query"""
        self.search_history.append({
            "query": query,
            "results_count": results_count,
            "latency_ms": latency_ms,
            "timestamp": datetime.utcnow().isoformat(),
        })
        
        # Keep only last 1000 searches
        if len(self.search_history) > 1000:
            self.search_history = self.search_history[-1000:]
    
    def get_search_stats(self) -> Dict[str, Any]:
        """Get search statistics"""
        if not self.search_history:
            return {
                "total_searches": 0,
                "avg_latency_ms": 0,
                "avg_results": 0,
                "popular_queries": [],
                "zero_result_queries": [],
            }
        
        queries = [s["query"] for s in self.search_history]
        latencies = [s["latency_ms"] for s in self.search_history]
        results = [s["results_count"] for s in self.search_history]
        
        query_counts = Counter(queries)
        
        return {
            "total_searches": len(self.search_history),
            "avg_latency_ms": sum(latencies) / len(latencies),
            "avg_results": sum(results) / len(results),
            "popular_queries": [
                {"query": q, "count": c}
                for q, c in query_counts.most_common(10)
            ],
            "zero_result_queries": [
                s["query"] for s in self.search_history if s["results_count"] == 0
            ][-10:],  # Last 10
        }


# Global instances
email_analytics = EmailAnalytics()
search_analytics = SearchAnalytics()