"""
Local SQLite Database Setup for SIX3 Agency
Simple database alternative to PostgreSQL for testing
"""

import sqlite3
import os
from datetime import datetime
from typing import Dict, Any, List, Optional

class LocalDatabase:
    def __init__(self, db_path: str = "six3_agency.db"):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        """Initialize database with required tables"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Agents table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS agents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    agent_name TEXT NOT NULL,
                    agent_type TEXT NOT NULL,
                    phase INTEGER NOT NULL,
                    category TEXT NOT NULL,
                    status TEXT DEFAULT 'active',
                    total_interactions INTEGER DEFAULT 0,
                    success_rate REAL DEFAULT 0.0,
                    avg_response_time REAL DEFAULT 0.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Conversations table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    agent_id INTEGER NOT NULL,
                    user_id TEXT,
                    conversation_data TEXT,
                    status TEXT DEFAULT 'active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (agent_id) REFERENCES agents (id)
                )
            ''')
            
            # Metrics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    agent_id INTEGER NOT NULL,
                    metric_type TEXT NOT NULL,
                    metric_value REAL NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (agent_id) REFERENCES agents (id)
                )
            ''')
            
            # Events table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    agent_id INTEGER,
                    event_type TEXT NOT NULL,
                    event_message TEXT NOT NULL,
                    severity TEXT DEFAULT 'info',
                    acknowledged BOOLEAN DEFAULT FALSE,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (agent_id) REFERENCES agents (id)
                )
            ''')
            
            # Leads table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS leads (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT NOT NULL,
                    name TEXT,
                    company TEXT,
                    status TEXT DEFAULT 'new',
                    source TEXT,
                    agent_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (agent_id) REFERENCES agents (id)
                )
            ''')
            
            conn.commit()
            self.seed_initial_data()
    
    def seed_initial_data(self):
        """Insert sample agents and data"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Check if agents already exist
            cursor.execute("SELECT COUNT(*) FROM agents")
            if cursor.fetchone()[0] > 0:
                return  # Already seeded
            
            # Insert sample agents
            agents = [
                # Phase 1
                ('Prospect Research Agent', 'prospect', 1, 'marketing', 'active', 127, 92.5, 1.3),
                ('FAQ Chatbot', 'faq', 1, 'support', 'active', 445, 89.2, 0.8),
                
                # Phase 2
                ('Sales Pitch Agent', 'sales', 2, 'sales', 'active', 156, 87.4, 2.1),
                ('Content Writer Agent', 'content', 2, 'content', 'active', 92, 94.6, 3.2),
                ('Email Personalizer', 'email', 2, 'content', 'active', 234, 91.8, 1.7),
                ('Social Media Agent', 'social', 2, 'marketing', 'active', 89, 88.3, 2.4),
                ('Intent Classifier', 'classifier', 2, 'analytics', 'active', 178, 96.1, 0.6),
                
                # Phase 3
                ('Orchestrator Agent', 'orchestrator', 3, 'analytics', 'active', 89, 93.7, 1.9),
                ('RAG Research Agent', 'research', 3, 'analytics', 'active', 67, 89.4, 4.1),
                ('Sales Strategist', 'strategist', 3, 'sales', 'active', 45, 92.2, 2.8),
                ('Marketing Campaign Agent', 'campaign', 3, 'marketing', 'active', 56, 90.5, 3.5),
                ('Customer Success Agent', 'success', 3, 'support', 'active', 123, 95.2, 1.4),
                ('Analytics Agent', 'analytics', 3, 'analytics', 'active', 34, 97.8, 2.2),
                
                # Phase 4
                ('Digital Avatar Agent', 'avatar', 4, 'advanced', 'active', 23, 85.7, 5.6),
                ('Voice Conversation Agent', 'voice', 4, 'advanced', 'active', 45, 88.9, 3.8),
                ('Multilingual Agent', 'multilingual', 4, 'advanced', 'active', 67, 91.3, 2.6),
                ('Real-time Conversation Agent', 'realtime', 4, 'advanced', 'active', 34, 89.1, 1.8),
                ('Advanced Personalization Agent', 'personalization', 4, 'advanced', 'active', 78, 93.4, 2.3)
            ]
            
            cursor.executemany('''
                INSERT INTO agents (agent_name, agent_type, phase, category, status, 
                                  total_interactions, success_rate, avg_response_time)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', agents)
            
            # Insert sample events
            events = [
                (1, 'interaction', 'New prospect identified: TechCorp', 'info'),
                (3, 'success', 'Successfully closed deal with client', 'success'),
                (4, 'content_created', 'Generated 3 blog posts', 'info'),
                (2, 'support', 'Resolved customer inquiry in 2 minutes', 'success'),
                (7, 'classification', 'Classified 50 customer intents', 'info'),
                (14, 'avatar_call', 'Completed sales presentation via avatar', 'success'),
                (5, 'email_sent', 'Sent 150 personalized emails', 'info'),
                (12, 'success_follow_up', 'Proactive customer check-in completed', 'success')
            ]
            
            cursor.executemany('''
                INSERT INTO events (agent_id, event_type, event_message, severity)
                VALUES (?, ?, ?, ?)
            ''', events)
            
            # Insert sample leads
            leads = [
                ('john@techcorp.com', 'John Smith', 'TechCorp', 'qualified', 'website', 1),
                ('sarah@startup.io', 'Sarah Johnson', 'Startup.io', 'new', 'social_media', 1),
                ('mike@enterprise.com', 'Mike Wilson', 'Enterprise Co', 'contacted', 'referral', 3),
                ('lisa@innovation.com', 'Lisa Brown', 'Innovation Ltd', 'new', 'content', 1)
            ]
            
            cursor.executemany('''
                INSERT INTO leads (email, name, company, status, source, agent_id)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', leads)
            
            conn.commit()
    
    def get_agents(self) -> List[Dict[str, Any]]:
        """Get all agents"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, agent_name, agent_type, phase, category, status,
                       total_interactions, success_rate, avg_response_time
                FROM agents
                ORDER BY phase, category, agent_name
            ''')
            
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def get_agent_by_id(self, agent_id: int) -> Optional[Dict[str, Any]]:
        """Get specific agent by ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, agent_name, agent_type, phase, category, status,
                       total_interactions, success_rate, avg_response_time
                FROM agents WHERE id = ?
            ''', (agent_id,))
            
            row = cursor.fetchone()
            if row:
                columns = [desc[0] for desc in cursor.description]
                return dict(zip(columns, row))
            return None
    
    def get_recent_events(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent events"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT e.id, e.event_type, e.event_message, e.severity,
                       e.acknowledged, e.timestamp, a.agent_name
                FROM events e
                LEFT JOIN agents a ON e.agent_id = a.id
                ORDER BY e.timestamp DESC
                LIMIT ?
            ''', (limit,))
            
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def get_dashboard_metrics(self) -> Dict[str, Any]:
        """Get dashboard metrics"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Total agents
            cursor.execute("SELECT COUNT(*) FROM agents WHERE status = 'active'")
            total_agents = cursor.fetchone()[0]
            
            # Total interactions
            cursor.execute("SELECT SUM(total_interactions) FROM agents")
            total_interactions = cursor.fetchone()[0] or 0
            
            # Average success rate
            cursor.execute("SELECT AVG(success_rate) FROM agents WHERE status = 'active'")
            avg_success_rate = cursor.fetchone()[0] or 0
            
            # Average response time
            cursor.execute("SELECT AVG(avg_response_time) FROM agents WHERE status = 'active'")
            avg_response_time = cursor.fetchone()[0] or 0
            
            # Phase counts
            cursor.execute("SELECT phase, COUNT(*) FROM agents WHERE status = 'active' GROUP BY phase")
            phase_counts = dict(cursor.fetchall())
            
            return {
                'total_agents': total_agents,
                'total_interactions': total_interactions,
                'avg_success_rate': round(avg_success_rate, 1),
                'avg_response_time': round(avg_response_time, 1),
                'phase_counts': phase_counts
            }
    
    def add_interaction(self, agent_id: int, success: bool = True, response_time: float = 1.0):
        """Add interaction to agent"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE agents 
                SET total_interactions = total_interactions + 1,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (agent_id,))
            conn.commit()
    
    def close(self):
        """Close database connection (for cleanup)"""
        pass

# Global database instance
db = LocalDatabase()

if __name__ == "__main__":
    # Test the database
    print("✅ Database initialized")
    agents = db.get_agents()
    print(f"✅ {len(agents)} agents loaded")
    
    metrics = db.get_dashboard_metrics()
    print(f"✅ Metrics: {metrics}")
    
    events = db.get_recent_events(5)
    print(f"✅ {len(events)} recent events")