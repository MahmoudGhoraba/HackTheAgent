"""
Email classification and tagging module
"""
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime
import re

logger = logging.getLogger(__name__)


class EmailClassifier:
    """Classify emails into categories and extract tags"""
    
    # Category keywords
    CATEGORIES = {
        "work": ["meeting", "project", "deadline", "task", "report", "presentation", "team", "client"],
        "urgent": ["urgent", "asap", "immediately", "critical", "emergency", "important", "priority"],
        "financial": ["invoice", "payment", "bill", "receipt", "transaction", "cost", "budget", "expense"],
        "security": ["security", "vulnerability", "breach", "alert", "warning", "threat", "patch", "update"],
        "social": ["invitation", "event", "party", "celebration", "gathering", "meetup"],
        "notification": ["notification", "alert", "reminder", "update", "status", "confirmation"],
        "newsletter": ["newsletter", "digest", "weekly", "monthly", "subscription", "unsubscribe"],
        "personal": ["personal", "private", "family", "friend", "vacation", "holiday"],
    }
    
    # Priority scoring
    PRIORITY_KEYWORDS = {
        "high": ["urgent", "asap", "critical", "emergency", "immediately", "deadline"],
        "medium": ["important", "soon", "priority", "attention", "review"],
        "low": ["fyi", "info", "update", "newsletter", "digest"],
    }
    
    def classify_email(self, email: Dict[str, Any]) -> Dict[str, Any]:
        """
        Classify a single email
        
        Returns:
            Dict with categories, tags, priority, and sentiment
        """
        subject = email.get("subject", "")
        body = email.get("body", "")
        text = f"{subject} {body}".lower()
        
        # Detect categories
        categories = self._detect_categories(text)
        
        # Extract tags
        tags = self._extract_tags(text)
        
        # Calculate priority
        priority = self._calculate_priority(text, subject)
        
        # Detect sentiment (basic)
        sentiment = self._detect_sentiment(text)
        
        # Detect if it's a reply/forward
        is_reply = self._is_reply(subject)
        is_forward = self._is_forward(subject)
        
        return {
            "id": email.get("id", ""),
            "categories": categories,
            "tags": tags,
            "priority": priority,
            "sentiment": sentiment,
            "is_reply": is_reply,
            "is_forward": is_forward,
            "has_attachments": False,  # TODO: detect attachments
            "word_count": len(body.split()),
        }
    
    def classify_batch(self, emails: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Classify multiple emails"""
        return [self.classify_email(email) for email in emails]
    
    def _detect_categories(self, text: str) -> List[str]:
        """Detect categories based on keywords"""
        detected = []
        
        for category, keywords in self.CATEGORIES.items():
            if any(keyword in text for keyword in keywords):
                detected.append(category)
        
        return detected if detected else ["general"]
    
    def _extract_tags(self, text: str) -> List[str]:
        """Extract hashtags and important keywords"""
        tags = []
        
        # Extract hashtags
        hashtags = re.findall(r'#(\w+)', text)
        tags.extend(hashtags)
        
        # Extract common project/product names (capitalized words)
        # This is a simple heuristic
        words = text.split()
        for word in words:
            if word.istitle() and len(word) > 3:
                tags.append(word.lower())
        
        # Remove duplicates and limit
        return list(set(tags))[:10]
    
    def _calculate_priority(self, text: str, subject: str) -> str:
        """Calculate email priority"""
        score = 0
        
        # Check high priority keywords
        for keyword in self.PRIORITY_KEYWORDS["high"]:
            if keyword in text:
                score += 3
        
        # Check medium priority keywords
        for keyword in self.PRIORITY_KEYWORDS["medium"]:
            if keyword in text:
                score += 2
        
        # Check low priority keywords
        for keyword in self.PRIORITY_KEYWORDS["low"]:
            if keyword in text:
                score -= 1
        
        # Subject in all caps suggests urgency
        if subject.isupper() and len(subject) > 5:
            score += 2
        
        # Multiple exclamation marks
        if text.count('!') >= 2:
            score += 1
        
        # Determine priority
        if score >= 5:
            return "high"
        elif score >= 2:
            return "medium"
        else:
            return "low"
    
    def _detect_sentiment(self, text: str) -> str:
        """Basic sentiment detection"""
        positive_words = ["thank", "great", "excellent", "good", "happy", "pleased", "wonderful", "appreciate"]
        negative_words = ["issue", "problem", "error", "fail", "wrong", "bad", "concern", "unfortunately"]
        
        positive_count = sum(1 for word in positive_words if word in text)
        negative_count = sum(1 for word in negative_words if word in text)
        
        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"
    
    def _is_reply(self, subject: str) -> bool:
        """Check if email is a reply"""
        return subject.lower().startswith("re:")
    
    def _is_forward(self, subject: str) -> bool:
        """Check if email is a forward"""
        return subject.lower().startswith("fwd:") or subject.lower().startswith("fw:")


class ThreadDetector:
    """Detect email conversation threads"""
    
    def detect_threads(self, emails: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Group emails into conversation threads
        
        Returns:
            Dict with threads and email_to_thread mapping
        """
        threads = {}
        email_to_thread = {}
        
        # Sort by date
        sorted_emails = sorted(emails, key=lambda e: e.get("date", ""))
        
        for email in sorted_emails:
            # Normalize subject (remove Re:, Fwd:, etc.)
            normalized_subject = self._normalize_subject(email.get("subject", ""))
            
            # Check if this subject already has a thread
            thread_id = None
            for tid, subject in threads.items():
                if subject == normalized_subject:
                    thread_id = tid
                    break
            
            # Create new thread if needed
            if thread_id is None:
                thread_id = f"thread_{len(threads) + 1}"
                threads[thread_id] = {
                    "subject": normalized_subject,
                    "emails": [],
                    "participants": set(),
                    "start_date": email.get("date", ""),
                    "last_date": email.get("date", ""),
                }
            
            # Add email to thread
            threads[thread_id]["emails"].append(email.get("id", ""))
            threads[thread_id]["participants"].add(email.get("from", ""))
            threads[thread_id]["participants"].add(email.get("to", ""))
            threads[thread_id]["last_date"] = email.get("date", "")
            
            email_to_thread[email.get("id", "")] = thread_id
        
        # Convert sets to lists for JSON serialization
        for thread in threads.values():
            thread["participants"] = list(thread["participants"])
        
        return {
            "threads": threads,
            "email_to_thread": email_to_thread,
        }
    
    def _normalize_subject(self, subject: str) -> str:
        """Remove Re:, Fwd:, etc. from subject"""
        normalized = subject
        
        # Remove common prefixes
        prefixes = ["re:", "fwd:", "fw:", "re[", "fwd["]
        for prefix in prefixes:
            while normalized.lower().startswith(prefix):
                normalized = normalized[len(prefix):].strip()
        
        return normalized.strip()


# Global instances
classifier = EmailClassifier()
thread_detector = ThreadDetector()