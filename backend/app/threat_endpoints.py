"""
New Threat Detection Endpoint - Innovation Feature

Detects email security threats using advanced threat detection engine.
This is the key innovation feature that differentiates HackTheAgent.
"""

from fastapi import FastAPI, HTTPException, status, Query
from pydantic import BaseModel
from typing import List, Dict, Any
import logging
from datetime import datetime
import uuid

from app.threat_detection import analyze_email_threat, analyze_emails_threats, EmailThreatAnalysis
from app.database import get_database
from app.semantic import get_search_engine
from app.load import load_emails

logger = logging.getLogger(__name__)


class ThreatDetectionRequest(BaseModel):
    """Request for threat detection"""
    query: str = Query("security threats phishing", description="Search query for threats")
    num_results: int = Query(50, ge=1, le=500, description="Number of emails to analyze")


class ThreatDetectionResponse(BaseModel):
    """Response with threat analysis"""
    total_emails_analyzed: int
    critical_count: int
    warning_count: int
    caution_count: int
    safe_count: int
    threats: List[Dict[str, Any]]
    recommendations: List[str]


def register_threat_detection_endpoints(app: FastAPI):
    """Register threat detection endpoints"""
    
    @app.post(
        "/security/threat-detection",
        tags=["Security - INNOVATION"],
        summary="Detect email security threats",
        description="Advanced threat detection: finds phishing, spoofing, malware attempts, and suspicious emails",
        response_model=ThreatDetectionResponse
    )
    async def detect_threats(request: ThreatDetectionRequest):
        """
        **INNOVATION FEATURE**: Email Threat Detection
        
        This endpoint performs advanced security analysis to identify:
        1. **Phishing attempts** - Detects common phishing keywords and tactics
        2. **Spoofing** - Identifies emails impersonating legitimate companies
        3. **Suspicious URLs** - Flags URL shorteners, IP addresses, suspicious domains
        4. **Typosquatting** - Detects domain names misspelling legitimate companies
        5. **Malware vectors** - Identifies common malware distribution patterns
        
        Returns:
        - Threat level classification (SAFE, CAUTION, WARNING, CRITICAL)
        - Individual threat indicators with evidence
        - Actionable recommendations per email
        - Summary statistics and critical threat list
        
        Example:
        ```
        POST /security/threat-detection
        {
            "query": "phishing spoofing threats",
            "num_results": 50
        }
        ```
        """
        try:
            logger.info(f"Starting threat detection analysis for query: {request.query}")
            
            # Step 1: Search for emails matching query
            search_engine = get_search_engine()
            search_results = search_engine.search(request.query, top_k=request.num_results)
            
            if not search_results:
                return ThreatDetectionResponse(
                    total_emails_analyzed=0,
                    critical_count=0,
                    warning_count=0,
                    caution_count=0,
                    safe_count=0,
                    threats=[],
                    recommendations=["No emails found matching the query"]
                )
            
            # Convert SearchResult objects to dicts
            emails = [
                {
                    "id": r.id,
                    "subject": r.subject,
                    "date": r.date,
                    "body": r.snippet or r.get("body", ""),
                    "from": r.get("from", "")
                } for r in search_results
            ]
            
            # Step 2: Analyze each email for threats
            threat_analyses = analyze_emails_threats(emails)
            
            # Step 3: Store results in database
            db = get_database()
            for analysis in threat_analyses:
                db.store_threat_analysis(analysis.dict())
            
            # Step 4: Aggregate results
            critical_threats = []
            warning_threats = []
            caution_threats = []
            safe_threats = []
            
            threat_counts = {
                'CRITICAL': 0,
                'WARNING': 0,
                'CAUTION': 0,
                'SAFE': 0
            }
            
            for analysis in threat_analyses:
                threat_dict = analysis.dict()
                threat_counts[analysis.threat_level] += 1
                
                if analysis.threat_level == 'CRITICAL':
                    critical_threats.append(threat_dict)
                elif analysis.threat_level == 'WARNING':
                    warning_threats.append(threat_dict)
                elif analysis.threat_level == 'CAUTION':
                    caution_threats.append(threat_dict)
                else:
                    safe_threats.append(threat_dict)
            
            # Step 5: Generate recommendations
            recommendations = []
            
            if threat_counts['CRITICAL'] > 0:
                recommendations.append(f"🚨 CRITICAL: {threat_counts['CRITICAL']} emails require immediate attention. Delete or quarantine immediately.")
            
            if threat_counts['WARNING'] > 0:
                recommendations.append(f"⚠️ WARNING: {threat_counts['WARNING']} emails are suspicious. Do not click links or download attachments.")
            
            if threat_counts['CAUTION'] > 0:
                recommendations.append(f"⚠️ CAUTION: {threat_counts['CAUTION']} emails need careful review. Verify sender before responding.")
            
            if threat_counts['SAFE'] == len(threat_analyses):
                recommendations.append("✅ All analyzed emails appear safe.")
            
            # Combine all threats, sorting by severity
            all_threats = critical_threats + warning_threats + caution_threats + safe_threats
            
            logger.info(f"Threat analysis complete: {len(all_threats)} emails analyzed")
            
            return ThreatDetectionResponse(
                total_emails_analyzed=len(threat_analyses),
                critical_count=threat_counts['CRITICAL'],
                warning_count=threat_counts['WARNING'],
                caution_count=threat_counts['CAUTION'],
                safe_count=threat_counts['SAFE'],
                threats=all_threats[:100],  # Limit response size
                recommendations=recommendations
            )
            
        except Exception as e:
            logger.error(f"Threat detection error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Threat detection failed: {str(e)}"
            )
    
    @app.get(
        "/security/threat-report",
        tags=["Security - INNOVATION"],
        summary="Get threat analysis report",
        description="Retrieve threat analysis history and statistics"
    )
    async def get_threat_report(
        level: str = Query("CRITICAL", description="Threat level: CRITICAL, WARNING, CAUTION, SAFE"),
        limit: int = Query(50, ge=1, le=500)
    ):
        """Get threat analysis report for specific threat level"""
        try:
            db = get_database()
            threats = db.get_threats_by_level(level, limit)
            
            return {
                "threat_level": level,
                "total_threats": len(threats),
                "threats": threats
            }
            
        except Exception as e:
            logger.error(f"Error getting threat report: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
    
    @app.get(
        "/security/stats",
        tags=["Security - INNOVATION"],
        summary="Get security statistics",
        description="Overall security statistics and threat metrics"
    )
    async def get_security_stats():
        """Get security statistics"""
        try:
            db = get_database()
            stats = db.get_stats()
            
            return {
                "total_emails_analyzed": stats['total_emails'],
                "critical_threats_found": stats['critical_threats'],
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting security stats: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
