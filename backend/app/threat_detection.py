"""
Email Threat Detection - Security Innovation Feature

This module implements advanced threat detection for emails:
- Phishing pattern detection
- Suspicious domain analysis
- Malicious URL detection
- Threat scoring and recommendations
"""

import logging
import re
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class ThreatIndicator(BaseModel):
    """Individual threat indicator"""
    type: str  # phishing, spoofing, malware, suspicious_url, typosquatting
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    description: str
    evidence: str


class EmailThreatAnalysis(BaseModel):
    """Complete threat analysis for an email"""
    email_id: str
    threat_level: str  # SAFE, CAUTION, WARNING, CRITICAL
    threat_score: float  # 0.0 to 1.0
    indicators: List[ThreatIndicator]
    recommendation: str
    timestamp: str


class EmailThreatDetector:
    """
    Advanced email threat detection engine
    
    Detects:
    - Phishing attempts
    - Spoofed domains
    - Suspicious URLs
    - Typosquatting
    - Known threat patterns
    """
    
    # Common legitimate domains (whitelist)
    TRUSTED_DOMAINS = {
        'gmail.com', 'outlook.com', 'yahoo.com', 'icloud.com', 'protonmail.com',
        'ibm.com', 'google.com', 'microsoft.com', 'apple.com', 'amazon.com',
        'github.com', 'linkedin.com', 'slack.com', 'zoom.com', 'stripe.com'
    }
    
    # Phishing keywords
    PHISHING_KEYWORDS = [
        'verify your account', 'confirm your identity', 'update your password',
        'unusual activity', 'click here immediately', 'act now', 'urgent action required',
        'suspended account', 'limited time', 'rare opportunity', 'claim reward',
        'congratulations you won', 'tax refund', 'nigerian prince', 'wire transfer'
    ]
    
    # Suspicious TLDs (often used in phishing)
    SUSPICIOUS_TLDS = {'.tk', '.ml', '.ga', '.cf', '.info', '.biz', '.pw', '.xyz'}
    
    # Known phishing domains (simplified)
    KNOWN_PHISHING_PATTERNS = [
        r'.*paypa[li]\..*', r'.*amazon-security.*', r'.*apple-id-verification.*',
        r'.*microsoft-account.*', r'.*gmail-verify.*', r'.*tax-refund.*'
    ]
    
    # Malicious URL patterns
    MALICIOUS_URL_PATTERNS = [
        r'(?:https?://)?(?:bit\.ly|tinyurl|shortened|x\.co)/',  # URL shorteners
        r'(?:https?://)?[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}',  # IP addresses
        r'(?:https?://)?.*?eval.*?\.js',  # JavaScript eval
        r'(?:https?://)?.*?password.*?reset',  # Fake password resets
    ]
    
    def __init__(self):
        """Initialize threat detector"""
        self.threat_keywords = set(self.PHISHING_KEYWORDS)
        self.malicious_patterns = [re.compile(p, re.IGNORECASE) for p in self.MALICIOUS_URL_PATTERNS]
        self.phishing_domain_patterns = [re.compile(p, re.IGNORECASE) for p in self.KNOWN_PHISHING_PATTERNS]
    
    def analyze(self, email: Dict) -> EmailThreatAnalysis:
        """
        Analyze email for threats
        
        Args:
            email: Email dict with subject, body, from, etc.
            
        Returns:
            EmailThreatAnalysis with threat level and indicators
        """
        indicators: List[ThreatIndicator] = []
        threat_score = 0.0
        
        # Extract email components
        sender = email.get('from', '').lower()
        subject = email.get('subject', '').lower()
        body = email.get('body', '').lower()
        
        # 1. Check for phishing keywords
        keyword_matches = self._check_phishing_keywords(subject + ' ' + body)
        if keyword_matches:
            indicators.extend(keyword_matches)
            threat_score += 0.2
        
        # 2. Check sender domain reputation
        domain_threat = self._check_sender_domain(sender)
        if domain_threat:
            indicators.append(domain_threat)
            threat_score += 0.3
        
        # 3. Check for suspicious URLs
        url_threats = self._check_urls(body)
        if url_threats:
            indicators.extend(url_threats)
            threat_score += 0.25 * len(url_threats)
        
        # 4. Check for typosquatting
        typo_threat = self._check_typosquatting(sender, subject)
        if typo_threat:
            indicators.append(typo_threat)
            threat_score += 0.15
        
        # 5. Check for spoofing indicators
        spoof_threat = self._check_spoofing(email)
        if spoof_threat:
            indicators.append(spoof_threat)
            threat_score += 0.25
        
        # Normalize threat score to 0-1
        threat_score = min(threat_score, 1.0)
        
        # Determine threat level
        threat_level = self._calculate_threat_level(threat_score)
        
        # Generate recommendation
        recommendation = self._generate_recommendation(threat_level, indicators)
        
        return EmailThreatAnalysis(
            email_id=email.get('id', 'unknown'),
            threat_level=threat_level,
            threat_score=round(threat_score, 2),
            indicators=indicators,
            recommendation=recommendation,
            timestamp=datetime.utcnow().isoformat()
        )
    
    def _check_phishing_keywords(self, text: str) -> List[ThreatIndicator]:
        """Check for known phishing keywords"""
        indicators = []
        found_keywords = []
        
        for keyword in self.threat_keywords:
            if keyword in text:
                found_keywords.append(keyword)
        
        if found_keywords:
            indicators.append(ThreatIndicator(
                type='phishing',
                severity='HIGH',
                description=f"Found {len(found_keywords)} phishing-related keywords",
                evidence=', '.join(found_keywords[:3])  # Show first 3
            ))
        
        return indicators
    
    def _check_sender_domain(self, sender: str) -> Optional[ThreatIndicator]:
        """Check sender domain reputation"""
        if not sender or '@' not in sender:
            return None
        
        domain = sender.split('@')[-1]
        
        # Check if domain is in trusted list
        if domain in self.TRUSTED_DOMAINS:
            return None
        
        # Check suspicious TLD
        for tld in self.SUSPICIOUS_TLDS:
            if domain.endswith(tld):
                return ThreatIndicator(
                    type='suspicious_domain',
                    severity='MEDIUM',
                    description=f"Domain uses suspicious TLD: {tld}",
                    evidence=domain
                )
        
        # Check known phishing domains
        for pattern in self.phishing_domain_patterns:
            if pattern.search(domain):
                return ThreatIndicator(
                    type='phishing',
                    severity='CRITICAL',
                    description="Sender domain matches known phishing pattern",
                    evidence=domain
                )
        
        return None
    
    def _check_urls(self, text: str) -> List[ThreatIndicator]:
        """Check for suspicious URLs"""
        indicators = []
        
        # Extract URLs
        url_pattern = r'https?://[^\s\)]+'
        urls = re.findall(url_pattern, text)
        
        for url in urls:
            for malicious_pattern in self.malicious_patterns:
                if malicious_pattern.search(url):
                    indicators.append(ThreatIndicator(
                        type='suspicious_url',
                        severity='HIGH',
                        description="URL matches suspicious pattern",
                        evidence=url[:50] + '...' if len(url) > 50 else url
                    ))
                    break
        
        return indicators
    
    def _check_typosquatting(self, sender: str, subject: str) -> Optional[ThreatIndicator]:
        """Check for typosquatting (domains similar to legitimate ones)"""
        typo_indicators = {
            'gmial': 'gmail', 'gmai.l': 'gmail',
            'redditt': 'reddit', 'twiiter': 'twitter',
            'paypa1': 'paypal', 'instgram': 'instagram',
            'linkedIn': 'linkedin', 'amaz0n': 'amazon'
        }
        
        suspicious_text = (sender + ' ' + subject).lower()
        
        for typo, legitimate in typo_indicators.items():
            if typo in suspicious_text:
                return ThreatIndicator(
                    type='typosquatting',
                    severity='HIGH',
                    description=f"Detected potential typosquatting: {typo} vs {legitimate}",
                    evidence=typo
                )
        
        return None
    
    def _check_spoofing(self, email: Dict) -> Optional[ThreatIndicator]:
        """Check for email spoofing indicators"""
        sender = email.get('from', '').lower()
        subject = email.get('subject', '').lower()
        
        # Check if sender claims to be from trusted company but domain is different
        trusted_names = ['amazon', 'apple', 'microsoft', 'google', 'ibm', 'paypal']
        
        for company in trusted_names:
            if company in subject or company in sender:
                domain = sender.split('@')[-1] if '@' in sender else ''
                if domain and company not in domain and domain not in self.TRUSTED_DOMAINS:
                    return ThreatIndicator(
                        type='spoofing',
                        severity='CRITICAL',
                        description=f"Possible spoofing: mentions {company} but domain is {domain}",
                        evidence=domain
                    )
        
        return None
    
    def _calculate_threat_level(self, score: float) -> str:
        """Convert threat score to level"""
        if score >= 0.75:
            return 'CRITICAL'
        elif score >= 0.5:
            return 'WARNING'
        elif score >= 0.25:
            return 'CAUTION'
        else:
            return 'SAFE'
    
    def _generate_recommendation(self, level: str, indicators: List[ThreatIndicator]) -> str:
        """Generate actionable recommendation"""
        if level == 'CRITICAL':
            return '⚠️ CRITICAL: Delete immediately. This email shows multiple threat indicators.'
        elif level == 'WARNING':
            return '⚠️ WARNING: Exercise caution. Do not click links or download attachments.'
        elif level == 'CAUTION':
            return '⚠️ CAUTION: Be suspicious. Verify sender before responding.'
        else:
            return '✅ SAFE: No significant threats detected.'


# Global threat detector instance
_threat_detector: Optional[EmailThreatDetector] = None


def get_threat_detector() -> EmailThreatDetector:
    """Get or create global threat detector"""
    global _threat_detector
    
    if _threat_detector is None:
        _threat_detector = EmailThreatDetector()
    
    return _threat_detector


def analyze_email_threat(email: Dict) -> EmailThreatAnalysis:
    """
    Convenience function to analyze email threat
    
    Args:
        email: Email dictionary
        
    Returns:
        EmailThreatAnalysis with threat assessment
    """
    detector = get_threat_detector()
    return detector.analyze(email)


def analyze_emails_threats(emails: List[Dict]) -> List[EmailThreatAnalysis]:
    """Analyze multiple emails for threats"""
    detector = get_threat_detector()
    return [detector.analyze(email) for email in emails]
