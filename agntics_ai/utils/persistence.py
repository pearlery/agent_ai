"""
Persistence layer for storing and retrieving processed data.
"""
import json
import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
import asyncio
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)


class JSONFilePersistence:
    """Simple JSON file-based persistence for development/testing."""
    
    def __init__(self, data_dir: str = "data"):
        """
        Initialize JSON file persistence.
        
        Args:
            data_dir: Directory to store JSON files
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # Create subdirectories
        (self.data_dir / "sessions").mkdir(exist_ok=True)
        (self.data_dir / "alerts").mkdir(exist_ok=True)
        (self.data_dir / "analyses").mkdir(exist_ok=True)
        (self.data_dir / "reports").mkdir(exist_ok=True)
    
    def save_alert(self, alert_id: str, alert_data: Dict[str, Any]) -> None:
        """
        Save alert data to file.
        
        Args:
            alert_id: Unique alert identifier
            alert_data: Alert data to save
        """
        try:
            alert_file = self.data_dir / "alerts" / f"{alert_id}.json"
            with open(alert_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "alert_id": alert_id,
                    "timestamp": datetime.now().isoformat(),
                    "data": alert_data
                }, f, indent=2, ensure_ascii=False)
            
            logger.debug(f"Saved alert {alert_id} to {alert_file}")
            
        except Exception as e:
            logger.error(f"Failed to save alert {alert_id}: {e}")
    
    def load_alert(self, alert_id: str) -> Optional[Dict[str, Any]]:
        """
        Load alert data from file.
        
        Args:
            alert_id: Alert identifier to load
            
        Returns:
            Alert data or None if not found
        """
        try:
            alert_file = self.data_dir / "alerts" / f"{alert_id}.json"
            if not alert_file.exists():
                return None
            
            with open(alert_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        except Exception as e:
            logger.error(f"Failed to load alert {alert_id}: {e}")
            return None
    
    def save_analysis(self, session_id: str, analysis_data: Dict[str, Any]) -> None:
        """
        Save analysis results to file.
        
        Args:
            session_id: Session identifier
            analysis_data: Analysis results to save
        """
        try:
            analysis_file = self.data_dir / "analyses" / f"{session_id}.json"
            with open(analysis_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "session_id": session_id,
                    "timestamp": datetime.now().isoformat(),
                    "analysis": analysis_data
                }, f, indent=2, ensure_ascii=False)
            
            logger.debug(f"Saved analysis for session {session_id}")
            
        except Exception as e:
            logger.error(f"Failed to save analysis for session {session_id}: {e}")
    
    def load_analysis(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Load analysis results from file.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Analysis data or None if not found
        """
        try:
            analysis_file = self.data_dir / "analyses" / f"{session_id}.json"
            if not analysis_file.exists():
                return None
            
            with open(analysis_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        except Exception as e:
            logger.error(f"Failed to load analysis for session {session_id}: {e}")
            return None
    
    def save_report(self, session_id: str, report_data: Dict[str, Any]) -> None:
        """
        Save final report to file.
        
        Args:
            session_id: Session identifier
            report_data: Report data to save
        """
        try:
            report_file = self.data_dir / "reports" / f"{session_id}.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "session_id": session_id,
                    "timestamp": datetime.now().isoformat(),
                    "report": report_data
                }, f, indent=2, ensure_ascii=False)
            
            logger.debug(f"Saved report for session {session_id}")
            
        except Exception as e:
            logger.error(f"Failed to save report for session {session_id}: {e}")
    
    def load_report(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Load report from file.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Report data or None if not found
        """
        try:
            report_file = self.data_dir / "reports" / f"{session_id}.json"
            if not report_file.exists():
                return None
            
            with open(report_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        except Exception as e:
            logger.error(f"Failed to load report for session {session_id}: {e}")
            return None
    
    def save_session_data(self, session_id: str, session_data: Dict[str, Any]) -> None:
        """
        Save complete session data.
        
        Args:
            session_id: Session identifier
            session_data: Complete session data
        """
        try:
            session_file = self.data_dir / "sessions" / f"{session_id}.json"
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "session_id": session_id,
                    "timestamp": datetime.now().isoformat(),
                    "data": session_data
                }, f, indent=2, ensure_ascii=False)
            
            logger.debug(f"Saved session data for {session_id}")
            
        except Exception as e:
            logger.error(f"Failed to save session data for {session_id}: {e}")
    
    def load_session_data(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Load complete session data.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session data or None if not found
        """
        try:
            session_file = self.data_dir / "sessions" / f"{session_id}.json"
            if not session_file.exists():
                return None
            
            with open(session_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        except Exception as e:
            logger.error(f"Failed to load session data for {session_id}: {e}")
            return None
    
    def list_sessions(self) -> List[str]:
        """
        List all available session IDs.
        
        Returns:
            List of session IDs
        """
        try:
            sessions_dir = self.data_dir / "sessions"
            session_files = sessions_dir.glob("*.json")
            return [f.stem for f in session_files]
        
        except Exception as e:
            logger.error(f"Failed to list sessions: {e}")
            return []
    
    def cleanup_old_data(self, days_to_keep: int = 30) -> None:
        """
        Clean up old data files.
        
        Args:
            days_to_keep: Number of days to keep data
        """
        try:
            import time
            cutoff_time = time.time() - (days_to_keep * 24 * 60 * 60)
            
            for subdir in ["sessions", "alerts", "analyses", "reports"]:
                dir_path = self.data_dir / subdir
                for file_path in dir_path.glob("*.json"):
                    if file_path.stat().st_mtime < cutoff_time:
                        file_path.unlink()
                        logger.debug(f"Deleted old file: {file_path}")
            
            logger.info(f"Cleaned up data older than {days_to_keep} days")
            
        except Exception as e:
            logger.error(f"Failed to cleanup old data: {e}")


class SQLitePersistence:
    """SQLite-based persistence for production use."""
    
    def __init__(self, db_path: str = "data/agent_ai.db"):
        """
        Initialize SQLite persistence.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        
        # Initialize database
        self._init_database()
    
    def _init_database(self) -> None:
        """Initialize the database with required tables."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Sessions table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS sessions (
                        session_id TEXT PRIMARY KEY,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        status TEXT DEFAULT 'active',
                        data JSON
                    )
                ''')
                
                # Alerts table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS alerts (
                        alert_id TEXT PRIMARY KEY,
                        session_id TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        data JSON,
                        FOREIGN KEY (session_id) REFERENCES sessions (session_id)
                    )
                ''')
                
                # Analyses table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS analyses (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        analysis_data JSON,
                        FOREIGN KEY (session_id) REFERENCES sessions (session_id)
                    )
                ''')
                
                # Reports table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS reports (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        report_data JSON,
                        FOREIGN KEY (session_id) REFERENCES sessions (session_id)
                    )
                ''')
                
                conn.commit()
                logger.info("SQLite database initialized")
        
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    def save_session(self, session_id: str, session_data: Dict[str, Any]) -> None:
        """Save session data to database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO sessions (session_id, updated_at, data)
                    VALUES (?, ?, ?)
                ''', (session_id, datetime.now(), json.dumps(session_data)))
                conn.commit()
            
            logger.debug(f"Saved session {session_id} to database")
        
        except Exception as e:
            logger.error(f"Failed to save session {session_id}: {e}")
    
    def load_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Load session data from database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT data FROM sessions WHERE session_id = ?', (session_id,))
                result = cursor.fetchone()
                
                if result:
                    return json.loads(result[0])
                return None
        
        except Exception as e:
            logger.error(f"Failed to load session {session_id}: {e}")
            return None


# Factory function to get persistence instance
def get_persistence_handler(persistence_type: str = "json", **kwargs) -> Any:
    """
    Get a persistence handler instance.
    
    Args:
        persistence_type: Type of persistence ('json' or 'sqlite')
        **kwargs: Additional arguments for the persistence handler
        
    Returns:
        Persistence handler instance
    """
    if persistence_type.lower() == "sqlite":
        return SQLitePersistence(**kwargs)
    else:
        return JSONFilePersistence(**kwargs)


# Global persistence instance
_persistence_handler = None

def get_default_persistence() -> JSONFilePersistence:
    """Get the default persistence handler."""
    global _persistence_handler
    if _persistence_handler is None:
        _persistence_handler = JSONFilePersistence()
    return _persistence_handler