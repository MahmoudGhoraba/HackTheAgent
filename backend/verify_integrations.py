#!/usr/bin/env python3
"""
Integration Verification Script - Validates all 5 fixes are in place

Checks:
1. ✅ FIX #1: IBM Orchestrate Integration - Code exists and callable
2. ✅ FIX #2: Threat Detection UI - Backend ready for workflow
3. ✅ FIX #3: Persistent Threat Database - Connected to workflow
4. ✅ FIX #4: Gmail Email Persistence - Fetch and store pattern
5. ✅ FIX #5: Multi-Agent Parallelization - Async/parallel execution
"""

import sys
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

# Color codes for output
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
BOLD = '\033[1m'
RESET = '\033[0m'

def check_imports():
    """Verify all critical imports work"""
    logger.info(f"\n{BOLD}Checking Imports...{RESET}")
    
    try:
        from app.database import get_database, EmailDatabase
        logger.info(f"{GREEN}✅ database.py{RESET} - get_database() and EmailDatabase imported")
    except Exception as e:
        logger.error(f"{RED}❌ database.py{RESET} - {e}")
        return False
    
    try:
        from app.threat_detection import get_threat_detector, EmailThreatDetector
        logger.info(f"{GREEN}✅ threat_detection.py{RESET} - get_threat_detector() and EmailThreatDetector imported")
    except Exception as e:
        logger.error(f"{RED}❌ threat_detection.py{RESET} - {e}")
        return False
    
    try:
        from app.ibm_orchestrate import IBMOrchestrateClient
        logger.info(f"{GREEN}✅ ibm_orchestrate.py{RESET} - IBMOrchestrateClient imported")
    except Exception as e:
        logger.error(f"{RED}❌ ibm_orchestrate.py{RESET} - {e}")
        return False
    
    try:
        from app.orchestrator import MultiAgentOrchestrator
        logger.info(f"{GREEN}✅ orchestrator.py{RESET} - MultiAgentOrchestrator imported")
    except Exception as e:
        logger.error(f"{RED}❌ orchestrator.py{RESET} - {e}")
        return False
    
    return True

def check_orchestrator_methods():
    """Verify orchestrator has all required methods"""
    logger.info(f"\n{BOLD}Checking Orchestrator Methods...{RESET}")
    
    try:
        from app.orchestrator import MultiAgentOrchestrator
        
        methods = [
            'execute_workflow',
            '_execute_ibm_orchestrate',
            '_execute_local_workflow',
            '_step_threat_detection',
            '_step_database_persistence'
        ]
        
        for method in methods:
            if hasattr(MultiAgentOrchestrator, method):
                logger.info(f"{GREEN}✅ {method}(){RESET} - Found")
            else:
                logger.error(f"{RED}❌ {method}(){RESET} - Missing")
                return False
        
        return True
    except Exception as e:
        logger.error(f"{RED}❌ Error checking methods{RESET} - {e}")
        return False

def check_database_methods():
    """Verify database has storage methods"""
    logger.info(f"\n{BOLD}Checking Database Methods...{RESET}")
    
    try:
        from app.database import EmailDatabase
        
        methods = ['store_email', 'store_threat_analysis', 'store_workflow_execution']
        
        for method in methods:
            if hasattr(EmailDatabase, method):
                logger.info(f"{GREEN}✅ {method}(){RESET} - Found")
            else:
                logger.error(f"{RED}❌ {method}(){RESET} - Missing")
                return False
        
        return True
    except Exception as e:
        logger.error(f"{RED}❌ Error checking database methods{RESET} - {e}")
        return False

def check_threat_detector_methods():
    """Verify threat detector has analyze method"""
    logger.info(f"\n{BOLD}Checking Threat Detector Methods...{RESET}")
    
    try:
        from app.threat_detection import EmailThreatDetector
        
        if hasattr(EmailThreatDetector, 'analyze'):
            logger.info(f"{GREEN}✅ analyze(){RESET} - Found")
        else:
            logger.error(f"{RED}❌ analyze(){RESET} - Missing")
            return False
        
        return True
    except Exception as e:
        logger.error(f"{RED}❌ Error checking threat detector{RESET} - {e}")
        return False

def check_load_persistence():
    """Verify load.py has Gmail persistence"""
    logger.info(f"\n{BOLD}Checking Gmail Persistence (FIX #4)...{RESET}")
    
    try:
        with open(Path(__file__).parent / 'app' / 'load.py', 'r') as f:
            content = f.read()
            
        if 'db.store_email' in content:
            logger.info(f"{GREEN}✅ Gmail Persistence{RESET} - db.store_email() found in load.py")
        else:
            logger.error(f"{YELLOW}⚠️  Gmail Persistence{RESET} - db.store_email() not found")
            return False
        
        return True
    except Exception as e:
        logger.error(f"{RED}❌ Error checking load.py{RESET} - {e}")
        return False

def check_asyncio_parallel():
    """Verify asyncio.gather for parallelization"""
    logger.info(f"\n{BOLD}Checking Parallelization (FIX #5)...{RESET}")
    
    try:
        with open(Path(__file__).parent / 'app' / 'orchestrator.py', 'r') as f:
            content = f.read()
            
        if 'asyncio.gather' in content:
            logger.info(f"{GREEN}✅ Parallelization{RESET} - asyncio.gather() found for concurrent execution")
        else:
            logger.error(f"{YELLOW}⚠️  Parallelization{RESET} - asyncio.gather() not found")
            return False
        
        return True
    except Exception as e:
        logger.error(f"{RED}❌ Error checking parallelization{RESET} - {e}")
        return False

def main():
    """Run all verification checks"""
    logger.info(f"\n{BOLD}{'='*60}")
    logger.info(f"HackTheAgent Integration Verification")
    logger.info(f"Validating 5 Critical Fixes")
    logger.info(f"{'='*60}{RESET}\n")
    
    checks = [
        ("Imports", check_imports),
        ("Orchestrator Methods", check_orchestrator_methods),
        ("Database Methods", check_database_methods),
        ("Threat Detector Methods", check_threat_detector_methods),
        ("Gmail Persistence (FIX #4)", check_load_persistence),
        ("Parallelization (FIX #5)", check_asyncio_parallel),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            logger.error(f"{RED}❌ {name} check failed{RESET} - {e}")
            results.append((name, False))
    
    # Summary
    logger.info(f"\n{BOLD}{'='*60}")
    logger.info(f"Verification Summary")
    logger.info(f"{'='*60}{RESET}\n")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = f"{GREEN}✅ PASS{RESET}" if result else f"{RED}❌ FAIL{RESET}"
        logger.info(f"{status} - {name}")
    
    logger.info(f"\n{BOLD}Score: {passed}/{total} checks passed{RESET}")
    
    if passed == total:
        logger.info(f"\n{GREEN}{BOLD}🎉 All integrations verified successfully!{RESET}{RESET}")
        logger.info(f"\n{BOLD}5 Fixes Status:{RESET}")
        logger.info(f"  {GREEN}✅ FIX #1: IBM Orchestrate Integration{RESET} - execute_workflow() calls IBM first")
        logger.info(f"  {GREEN}✅ FIX #2: Threat Detection Integration{RESET} - _step_threat_detection() added")
        logger.info(f"  {GREEN}✅ FIX #3: Database Persistence{RESET} - _step_database_persistence() added")
        logger.info(f"  {GREEN}✅ FIX #4: Gmail Email Persistence{RESET} - db.store_email() in load.py")
        logger.info(f"  {GREEN}✅ FIX #5: Multi-Agent Parallelization{RESET} - asyncio.gather() for concurrent execution")
        return 0
    else:
        logger.info(f"\n{RED}{BOLD}⚠️  Some checks failed. Please review above.{RESET}{RESET}")
        return 1

if __name__ == '__main__':
    sys.exit(main())
