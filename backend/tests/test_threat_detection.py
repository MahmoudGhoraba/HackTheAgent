"""
Unit tests for Threat Detection System

Tests the email threat detection engine to ensure it correctly
identifies phishing, spoofing, suspicious URLs, and other threats.
"""

import pytest
from app.threat_detection import (
    EmailThreatDetector, analyze_email_threat, ThreatIndicator
)


class TestEmailThreatDetector:
    """Tests for EmailThreatDetector"""
    
    @pytest.fixture
    def detector(self):
        """Create detector instance"""
        return EmailThreatDetector()
    
    def test_phishing_keywords_detection(self, detector):
        """Test detection of common phishing keywords"""
        email = {
            "id": "test_1",
            "from": "support@example.com",
            "subject": "Verify your account immediately",
            "body": "Click here immediately to confirm your identity. Unusual activity detected.",
            "date": "2026-02-01"
        }
        
        analysis = detector.analyze(email)
        
        assert analysis.threat_level != 'SAFE'
        assert 'phishing' in [ind.type for ind in analysis.indicators]
    
    def test_suspicious_domain_detection(self, detector):
        """Test detection of suspicious domains"""
        email = {
            "id": "test_2",
            "from": "admin@malicious-domain.tk",
            "subject": "Update your password",
            "body": "Please verify your credentials",
            "date": "2026-02-01"
        }
        
        analysis = detector.analyze(email)
        
        assert analysis.threat_level in ['WARNING', 'CAUTION', 'CRITICAL']
        assert 'suspicious_domain' in [ind.type for ind in analysis.indicators]
    
    def test_typosquatting_detection(self, detector):
        """Test detection of typosquatting attempts"""
        email = {
            "id": "test_3",
            "from": "support@gmial.com",  # Note: gmial instead of gmail
            "subject": "Verify Gmail account",
            "body": "Please verify your account",
            "date": "2026-02-01"
        }
        
        analysis = detector.analyze(email)
        
        assert 'typosquatting' in [ind.type for ind in analysis.indicators]
    
    def test_spoofing_detection(self, detector):
        """Test detection of email spoofing"""
        email = {
            "id": "test_4",
            "from": "noreply@randomdomain.com",
            "subject": "Apple ID Verification Required",
            "body": "Your Apple ID needs verification immediately",
            "date": "2026-02-01"
        }
        
        analysis = detector.analyze(email)
        
        assert 'spoofing' in [ind.type for ind in analysis.indicators]
    
    def test_suspicious_url_detection(self, detector):
        """Test detection of suspicious URLs"""
        email = {
            "id": "test_5",
            "from": "user@example.com",
            "subject": "Click here",
            "body": "Visit https://bit.ly/shortened or http://192.168.1.1/admin to update",
            "date": "2026-02-01"
        }
        
        analysis = detector.analyze(email)
        
        assert any(ind.type == 'suspicious_url' for ind in analysis.indicators)
    
    def test_safe_email_detection(self, detector):
        """Test that legitimate emails are marked as SAFE"""
        email = {
            "id": "test_6",
            "from": "team@ibm.com",
            "subject": "Meeting at 3 PM",
            "body": "Let's discuss the project roadmap tomorrow at 3 PM. See you then!",
            "date": "2026-02-01"
        }
        
        analysis = detector.analyze(email)
        
        assert analysis.threat_level == 'SAFE'
        assert len(analysis.indicators) == 0
    
    def test_threat_score_calculation(self, detector):
        """Test that threat scores are calculated correctly"""
        email = {
            "id": "test_7",
            "from": "noreply@paypa1.com",
            "subject": "Urgent: Verify your account immediately",
            "body": "Click https://bit.ly/paypal-verify to confirm your identity",
            "date": "2026-02-01"
        }
        
        analysis = detector.analyze(email)
        
        assert 0.0 <= analysis.threat_score <= 1.0
        assert analysis.threat_score > 0.7  # Should be high threat
    
    def test_multiple_indicators(self, detector):
        """Test email with multiple threat indicators"""
        email = {
            "id": "test_8",
            "from": "admin@amaz0n-security.com",
            "subject": "URGENT: Unusual Activity Detected",
            "body": "Verify immediately: https://bit.ly/amazon-verify Your account has suspicious activity",
            "date": "2026-02-01"
        }
        
        analysis = detector.analyze(email)
        
        assert len(analysis.indicators) >= 3  # Multiple threats
        assert analysis.threat_level == 'CRITICAL'
    
    def test_recommendation_generation(self, detector):
        """Test that recommendations are generated"""
        email = {
            "id": "test_9",
            "from": "hacker@malicious.net",
            "subject": "Claim your reward",
            "body": "You've won! Click here to claim",
            "date": "2026-02-01"
        }
        
        analysis = detector.analyze(email)
        
        assert len(analysis.recommendation) > 0
        assert 'caution' in analysis.recommendation.lower() or 'critical' in analysis.recommendation.lower()
    
    def test_trusted_domain_no_threat(self, detector):
        """Test that trusted domains are not flagged"""
        email = {
            "id": "test_10",
            "from": "security@microsoft.com",
            "subject": "Update available",
            "body": "A security update is available for your system",
            "date": "2026-02-01"
        }
        
        analysis = detector.analyze(email)
        
        # Should have few or no threats from trusted domain
        suspicious_types = [ind.type for ind in analysis.indicators 
                           if ind.type in ['suspicious_domain', 'spoofing']]
        assert len(suspicious_types) == 0


class TestThreatAnalysisFunctions:
    """Tests for threat analysis convenience functions"""
    
    def test_analyze_single_email(self):
        """Test analyzing single email"""
        email = {
            "id": "test_single",
            "from": "phisher@example.com",
            "subject": "Verify account",
            "body": "Click here to verify",
            "date": "2026-02-01"
        }
        
        analysis = analyze_email_threat(email)
        
        assert analysis is not None
        assert analysis.email_id == "test_single"
    
    def test_analyze_multiple_emails(self):
        """Test analyzing multiple emails"""
        emails = [
            {
                "id": f"test_multi_{i}",
                "from": f"sender{i}@example.com",
                "subject": "Test email",
                "body": "This is a test email",
                "date": "2026-02-01"
            }
            for i in range(5)
        ]
        
        analyses = [analyze_email_threat(e) for e in emails]
        
        assert len(analyses) == 5
        assert all(a is not None for a in analyses)


class TestThreatLevelClassification:
    """Tests for threat level classification"""
    
    @pytest.fixture
    def detector(self):
        return EmailThreatDetector()
    
    def test_critical_threat(self, detector):
        """Test CRITICAL threat classification"""
        email = {
            "id": "critical",
            "from": "fake@paypa1.com",
            "subject": "URGENT: Account Suspended",
            "body": "Verify immediately: https://bit.ly/urgent-verify Password reset: click here",
            "date": "2026-02-01"
        }
        
        analysis = detector.analyze(email)
        assert analysis.threat_level == 'CRITICAL'
    
    def test_warning_threat(self, detector):
        """Test WARNING threat classification"""
        email = {
            "id": "warning",
            "from": "unknown@unusual-domain.info",
            "subject": "Update your information",
            "body": "Please provide your details",
            "date": "2026-02-01"
        }
        
        analysis = detector.analyze(email)
        assert analysis.threat_level in ['WARNING', 'CAUTION']
    
    def test_safe_email(self, detector):
        """Test SAFE email classification"""
        email = {
            "id": "safe",
            "from": "friend@gmail.com",
            "subject": "Hey, how are you?",
            "body": "Just checking in! How have you been?",
            "date": "2026-02-01"
        }
        
        analysis = detector.analyze(email)
        assert analysis.threat_level == 'SAFE'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
