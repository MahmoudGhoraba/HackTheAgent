"""
SQLite Database Layer for Persistence

Stores:
- Email indexes and embeddings
- Threat analysis results
- User queries and history
- Workflow executions
"""

import sqlite3
import logging
import json
from datetime import datetime
from typing import List, Dict, Optional, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class EmailDatabase:
    """SQLite database for HackTheAgent"""
    
    def __init__(self, db_path: str = "data/emails.db"):
        """Initialize database"""
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.init_schema()
    
    def get_connection(self) -> sqlite3.Connection:
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_schema(self):
        """Initialize database schema"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Emails table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS emails (
                id TEXT PRIMARY KEY,
                from_addr TEXT,
                to_addr TEXT,
                subject TEXT,
                body TEXT,
                date TEXT,
                source TEXT,  -- 'gmail' or 'file'
                indexed BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            # Embeddings table (for vector search)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS embeddings (
                id TEXT PRIMARY KEY,
                email_id TEXT,
                embedding BLOB,  -- Serialized numpy array
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (email_id) REFERENCES emails(id)
            )
            """)
            
            # Threat analysis results
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS threat_analysis (
                id TEXT PRIMARY KEY,
                email_id TEXT,
                threat_level TEXT,
                threat_score REAL,
                indicators TEXT,  -- JSON
                recommendation TEXT,
                analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (email_id) REFERENCES emails(id)
            )
            """)
            
            # User queries and history
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS queries (
                id TEXT PRIMARY KEY,
                query_text TEXT,
                intent_type TEXT,
                results_count INTEGER,
                execution_time_ms REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            # Workflow executions
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS workflow_executions (
                id TEXT PRIMARY KEY,
                workflow_id TEXT,
                status TEXT,  -- COMPLETED, FAILED, RUNNING
                steps_executed TEXT,  -- JSON
                result TEXT,  -- JSON
                execution_time_ms REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            # Indexes for faster queries
            cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_emails_source ON emails(source)
            """)
            
            cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_threat_level ON threat_analysis(threat_level)
            """)
            
            cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_queries_created ON queries(created_at)
            """)
            
            conn.commit()
            logger.info(f"Database initialized: {self.db_path}")
            
        except sqlite3.Error as e:
            logger.error(f"Database initialization error: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    def store_email(self, email: Dict[str, Any]) -> bool:
        """Store email in database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
            INSERT OR REPLACE INTO emails 
            (id, from_addr, to_addr, subject, body, date, source)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                email.get('id'),
                email.get('from'),
                email.get('to'),
                email.get('subject'),
                email.get('body'),
                email.get('date'),
                email.get('source', 'file')
            ))
            
            conn.commit()
            logger.debug(f"Stored email: {email.get('id')}")
            return True
            
        except sqlite3.Error as e:
            logger.error(f"Error storing email: {e}")
            return False
        finally:
            conn.close()
    
    def store_emails_batch(self, emails: List[Dict[str, Any]]) -> int:
        """Store multiple emails efficiently"""
        conn = self.get_connection()
        cursor = conn.cursor()
        stored = 0
        
        try:
            for email in emails:
                cursor.execute("""
                INSERT OR REPLACE INTO emails 
                (id, from_addr, to_addr, subject, body, date, source)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    email.get('id'),
                    email.get('from'),
                    email.get('to'),
                    email.get('subject'),
                    email.get('body'),
                    email.get('date'),
                    email.get('source', 'file')
                ))
                stored += 1
            
            conn.commit()
            logger.info(f"Stored {stored} emails")
            return stored
            
        except sqlite3.Error as e:
            logger.error(f"Error storing emails: {e}")
            conn.rollback()
            return stored
        finally:
            conn.close()
    
    def get_email(self, email_id: str) -> Optional[Dict]:
        """Retrieve email by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT * FROM emails WHERE id = ?", (email_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()
    
    def get_emails(self, limit: int = 100) -> List[Dict]:
        """Get emails"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT * FROM emails LIMIT ?", (limit,))
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()
    
    def store_threat_analysis(self, analysis: Dict[str, Any]) -> bool:
        """Store threat analysis result"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
            INSERT OR REPLACE INTO threat_analysis
            (id, email_id, threat_level, threat_score, indicators, recommendation)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (
                analysis.get('email_id'),
                analysis.get('email_id'),
                analysis.get('threat_level'),
                analysis.get('threat_score'),
                json.dumps(analysis.get('indicators', [])),
                analysis.get('recommendation')
            ))
            
            conn.commit()
            return True
            
        except sqlite3.Error as e:
            logger.error(f"Error storing threat analysis: {e}")
            return False
        finally:
            conn.close()
    
    def get_threat_analysis(self, email_id: str) -> Optional[Dict]:
        """Get threat analysis for email"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
            SELECT * FROM threat_analysis WHERE email_id = ?
            """, (email_id,))
            
            row = cursor.fetchone()
            if row:
                result = dict(row)
                result['indicators'] = json.loads(result['indicators'])
                return result
            return None
            
        finally:
            conn.close()
    
    def get_threats_by_level(self, level: str, limit: int = 50) -> List[Dict]:
        """Get threats by severity level"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
            SELECT * FROM threat_analysis 
            WHERE threat_level = ? 
            ORDER BY analyzed_at DESC 
            LIMIT ?
            """, (level, limit))
            
            return [dict(row) for row in cursor.fetchall()]
            
        finally:
            conn.close()
    
    def store_query(self, query: Dict[str, Any]) -> bool:
        """Store user query"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
            INSERT INTO queries
            (id, query_text, intent_type, results_count, execution_time_ms)
            VALUES (?, ?, ?, ?, ?)
            """, (
                query.get('id'),
                query.get('query_text'),
                query.get('intent_type'),
                query.get('results_count', 0),
                query.get('execution_time_ms', 0)
            ))
            
            conn.commit()
            return True
            
        except sqlite3.Error as e:
            logger.error(f"Error storing query: {e}")
            return False
        finally:
            conn.close()
    
    def get_query_history(self, limit: int = 100) -> List[Dict]:
        """Get recent queries"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
            SELECT * FROM queries 
            ORDER BY created_at DESC 
            LIMIT ?
            """, (limit,))
            
            return [dict(row) for row in cursor.fetchall()]
            
        finally:
            conn.close()
    
    def store_workflow_execution(self, execution: Dict[str, Any]) -> bool:
        """Store workflow execution"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
            INSERT INTO workflow_executions
            (id, workflow_id, status, steps_executed, result, execution_time_ms)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (
                execution.get('id'),
                execution.get('workflow_id'),
                execution.get('status'),
                json.dumps(execution.get('steps_executed', [])),
                json.dumps(execution.get('result', {})),
                execution.get('execution_time_ms', 0)
            ))
            
            conn.commit()
            return True
            
        except sqlite3.Error as e:
            logger.error(f"Error storing workflow execution: {e}")
            return False
        finally:
            conn.close()
    
    def get_workflow_history(self, limit: int = 50) -> List[Dict]:
        """Get recent workflow executions"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
            SELECT * FROM workflow_executions 
            ORDER BY created_at DESC 
            LIMIT ?
            """, (limit,))
            
            results = []
            for row in cursor.fetchall():
                r = dict(row)
                r['steps_executed'] = json.loads(r['steps_executed'])
                r['result'] = json.loads(r['result'])
                results.append(r)
            
            return results
            
        finally:
            conn.close()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT COUNT(*) as count FROM emails")
            email_count = cursor.fetchone()['count']
            
            cursor.execute("SELECT COUNT(*) as count FROM threat_analysis WHERE threat_level = 'CRITICAL'")
            critical_threats = cursor.fetchone()['count']
            
            cursor.execute("SELECT COUNT(*) as count FROM queries")
            query_count = cursor.fetchone()['count']
            
            cursor.execute("SELECT COUNT(*) as count FROM workflow_executions WHERE status = 'COMPLETED'")
            completed_workflows = cursor.fetchone()['count']
            
            return {
                'total_emails': email_count,
                'critical_threats': critical_threats,
                'total_queries': query_count,
                'completed_workflows': completed_workflows,
                'database_path': self.db_path
            }
            
        finally:
            conn.close()


# Global database instance
_db_instance: Optional[EmailDatabase] = None


def get_database() -> EmailDatabase:
    """Get or create global database instance"""
    global _db_instance
    
    if _db_instance is None:
        _db_instance = EmailDatabase()
    
    return _db_instance
