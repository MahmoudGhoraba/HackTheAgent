"""
Local Agent Execution Engine
Executes Watson Orchestrate agents locally
"""

import yaml
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

class LocalAgentEngine:
    """Execute agents locally"""
    
    def __init__(self, agents_dir: Path = None):
        if agents_dir is None:
            agents_dir = Path(__file__).parent.parent.parent / "adk-project" / "agents"
        
        self.agents_dir = agents_dir
        self.agents = {}
        self._load_agents()
    
    def _load_agents(self):
        """Load all agent YAML files"""
        if not self.agents_dir.exists():
            logger.warning(f"Agents directory not found: {self.agents_dir}")
            return
        
        for agent_file in self.agents_dir.glob("*.yaml"):
            try:
                with open(agent_file, 'r') as f:
                    agent_config = yaml.safe_load(f)
                    agent_name = agent_config.get('name')
                    self.agents[agent_name] = agent_config
                    logger.info(f"✅ Loaded agent: {agent_name}")
            except Exception as e:
                logger.error(f"Failed to load {agent_file}: {e}")
    
    def get_agent(self, agent_name: str) -> Optional[Dict]:
        """Get agent configuration"""
        return self.agents.get(agent_name)
    
    def list_agents(self) -> List[Dict[str, Any]]:
        """List all agents"""
        return [
            {
                "name": name,
                "display_name": config.get('display_name'),
                "description": config.get('description'),
                "status": "available",
                "tools": config.get('tools', [])
            }
            for name, config in self.agents.items()
        ]
    
    def parse_intent(self, query: str) -> Dict[str, Any]:
        """Parse user intent"""
        logger.info(f"Parsing intent: {query}")
        
        intent_keywords = {
            "search": ["find", "search", "look for", "get"],
            "classify": ["categorize", "organize", "sort", "classify"],
            "analyze": ["analyze", "check", "review", "examine"],
            "threat": ["threat", "phishing", "spam", "malware", "suspicious"],
            "answer": ["answer", "explain", "tell me", "what is"]
        }
        
        query_lower = query.lower()
        detected_intent = "general"
        confidence = 0.5
        
        for intent_type, keywords in intent_keywords.items():
            if any(kw in query_lower for kw in keywords):
                detected_intent = intent_type
                confidence = 0.8
                break
        
        entities = self._extract_entities(query)
        
        return {
            "success": True,
            "agent": "intent_detection_agent",
            "input": query,
            "output": {
                "intent": detected_intent,
                "confidence": confidence,
                "entities": entities
            }
        }
    
    def _extract_entities(self, text: str) -> List[Dict[str, str]]:
        """Extract named entities from text"""
        entities = []
        words = text.split()
        for i, word in enumerate(words):
            if word and word[0].isupper() and i > 0:
                entities.append({
                    "text": word,
                    "type": "PERSON"
                })
        return entities
    
    def semantic_search(self, query: str, email_ids: List[str] = None) -> Dict[str, Any]:
        """Perform semantic search"""
        logger.info(f"Semantic search: {query}")
        
        results = [
            {
                "email_id": "email_001",
                "subject": f"RE: {query}",
                "similarity_score": 0.92,
                "snippet": f"This email discusses {query}..."
            },
            {
                "email_id": "email_002",
                "subject": f"Fwd: {query} updates",
                "similarity_score": 0.85,
                "snippet": f"Important information about {query}"
            }
        ]
        
        return {
            "success": True,
            "agent": "semantic_search_agent",
            "input": {"query": query, "email_ids": email_ids},
            "output": {
                "results": results,
                "total_matches": len(results)
            }
        }
    
    def classify_emails(self, emails: List[Dict]) -> Dict[str, Any]:
        """Classify emails"""
        logger.info(f"Classifying {len(emails)} emails")
        
        classified = []
        for email in emails:
            classification = {
                "email_id": email.get("id", "unknown"),
                "category": self._classify_category(email.get("subject", "")),
                "priority": self._classify_priority(email.get("body", "")),
                "sentiment": self._analyze_sentiment(email.get("body", ""))
            }
            classified.append(classification)
        
        return {
            "success": True,
            "agent": "classification_agent",
            "input": {"email_count": len(emails)},
            "output": {
                "classified_emails": classified
            }
        }
    
    def _classify_category(self, text: str) -> str:
        """Classify email category"""
        categories = {
            "work": ["project", "meeting", "deadline", "report"],
            "personal": ["family", "friend", "personal"],
            "marketing": ["offer", "promotion", "sale", "subscribe"],
            "spam": ["click here", "limited time", "unsubscribe"]
        }
        
        text_lower = text.lower()
        for category, keywords in categories.items():
            if any(kw in text_lower for kw in keywords):
                return category
        return "general"
    
    def _classify_priority(self, text: str) -> str:
        """Classify email priority"""
        if any(word in text.lower() for word in ["urgent", "asap", "important", "critical"]):
            return "high"
        elif any(word in text.lower() for word in ["soon", "tomorrow"]):
            return "medium"
        return "low"
    
    def _analyze_sentiment(self, text: str) -> str:
        """Analyze email sentiment"""
        positive_words = ["great", "excellent", "happy", "thanks", "appreciate"]
        negative_words = ["angry", "upset", "problem", "issue", "complaint"]
        
        text_lower = text.lower()
        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)
        
        if pos_count > neg_count:
            return "positive"
        elif neg_count > pos_count:
            return "negative"
        return "neutral"
    
    def generate_answer(self, query: str, context: List[str]) -> Dict[str, Any]:
        """Generate grounded answer"""
        logger.info(f"Generating answer for: {query}")
        
        answer = f"Based on the provided context, {query.lower()}. "
        answer += " ".join(context[:2]) if context else "No context provided."
        
        return {
            "success": True,
            "agent": "rag_generation_agent",
            "input": {"query": query, "context_items": len(context)},
            "output": {
                "answer": answer,
                "citations": [
                    {"source": f"context_{i}", "text": ctx[:50]}
                    for i, ctx in enumerate(context[:3])
                ],
                "confidence": 0.85
            }
        }
    
    def detect_threats(self, emails: List[Dict]) -> Dict[str, Any]:
        """Detect security threats"""
        logger.info(f"Detecting threats in {len(emails)} emails")
        
        threats = []
        for email in emails:
            threat_score = self._calculate_threat_score(email)
            if threat_score > 0.3:
                threats.append({
                    "email_id": email.get("id", "unknown"),
                    "threat_type": self._identify_threat_type(email),
                    "threat_score": threat_score,
                    "recommendations": ["Review carefully", "Do not click links"]
                })
        
        return {
            "success": True,
            "agent": "threat_detection_agent",
            "input": {"email_count": len(emails)},
            "output": {
                "threats_detected": len(threats),
                "threats": threats
            }
        }
    
    def _calculate_threat_score(self, email: Dict) -> float:
        """Calculate threat score for email"""
        score = 0.0
        
        phishing_indicators = ["verify account", "confirm password", "click here", "urgency"]
        subject = email.get("subject", "").lower()
        body = email.get("body", "").lower()
        
        for indicator in phishing_indicators:
            if indicator in subject or indicator in body:
                score += 0.2
        
        return min(score, 1.0)
    
    def _identify_threat_type(self, email: Dict) -> str:
        """Identify type of threat"""
        content = (email.get("subject", "") + email.get("body", "")).lower()
        
        if "verify" in content or "confirm" in content:
            return "phishing"
        elif "malware" in content or "virus" in content:
            return "malware"
        elif any(word in content for word in ["offer", "click", "urgent"]):
            return "spam"
        
        return "unknown"
    
    def persist_data(self, data_type: str, data: Any) -> Dict[str, Any]:
        """Persist data"""
        logger.info(f"Persisting {data_type} data")
        
        return {
            "success": True,
            "agent": "database_persistence_agent",
            "input": {"data_type": data_type},
            "output": {
                "stored": True,
                "records": 1,
                "timestamp": "2026-02-01T13:30:00Z"
            }
        }


_agent_engine = None

def get_agent_engine() -> LocalAgentEngine:
    """Get or create local agent engine"""
    global _agent_engine
    if _agent_engine is None:
        _agent_engine = LocalAgentEngine()
    return _agent_engine
