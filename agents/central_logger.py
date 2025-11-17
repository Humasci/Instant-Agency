"""
Centralized Activity Logger & Monitoring System

Tracks all agent activities, interactions, and events in a unified database.
Provides centralized logging, reporting, and real-time monitoring.

Key Features:
- Unified activity log across all agents
- Real-time event tracking
- Performance metrics aggregation
- Error tracking and alerting
- Agent status monitoring
- Inter-agent communication tracking

Database Schema:
- agent_activities: All agent interactions
- agent_status: Current status of each agent
- agent_metrics: Performance metrics over time
- inter_agent_messages: Agent-to-agent communication
- system_events: System-wide events and alerts
"""

import os
import json
import time
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import sqlite3
from enum import Enum


class AgentStatus(Enum):
    """Agent status states"""
    ACTIVE = "active"
    IDLE = "idle"
    PROCESSING = "processing"
    ERROR = "error"
    OFFLINE = "offline"


class EventType(Enum):
    """Event types for logging"""
    AGENT_START = "agent_start"
    AGENT_STOP = "agent_stop"
    INTERACTION = "interaction"
    ERROR = "error"
    WARNING = "warning"
    COLLABORATION = "collaboration"
    ESCALATION = "escalation"
    SUCCESS = "success"


class CentralActivityLogger:
    """
    Centralized logger for all agent activities
    """

    def __init__(self, db_path: str = "data/central_activity.db"):
        """Initialize centralized logger"""
        self.db_path = db_path

        # Create data directory if it doesn't exist
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

        # Initialize database
        self._init_database()

        # In-memory cache for real-time metrics
        self.real_time_metrics = defaultdict(lambda: {
            'total_interactions': 0,
            'successful': 0,
            'failed': 0,
            'avg_response_time': 0,
            'last_activity': None
        })

        print(f"✓ Central Activity Logger initialized")
        print(f"  Database: {db_path}")

    def _init_database(self):
        """Initialize SQLite database with schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Agent Activities Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agent_activities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                agent_name TEXT NOT NULL,
                agent_type TEXT,
                event_type TEXT NOT NULL,
                input_data TEXT,
                output_data TEXT,
                success BOOLEAN,
                response_time_ms REAL,
                error_message TEXT,
                user_id TEXT,
                session_id TEXT,
                workflow_id TEXT,
                metadata TEXT
            )
        """)

        # Agent Status Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agent_status (
                agent_name TEXT PRIMARY KEY,
                status TEXT NOT NULL,
                last_updated TEXT NOT NULL,
                total_interactions INTEGER DEFAULT 0,
                success_rate REAL,
                avg_response_time REAL,
                current_load INTEGER DEFAULT 0,
                error_count INTEGER DEFAULT 0,
                uptime_seconds INTEGER DEFAULT 0
            )
        """)

        # Agent Metrics Table (time-series)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agent_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                agent_name TEXT NOT NULL,
                metric_name TEXT NOT NULL,
                metric_value REAL NOT NULL,
                metric_unit TEXT
            )
        """)

        # Inter-Agent Messages Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS inter_agent_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                from_agent TEXT NOT NULL,
                to_agent TEXT NOT NULL,
                message_type TEXT NOT NULL,
                payload TEXT,
                workflow_id TEXT,
                processed BOOLEAN DEFAULT 0
            )
        """)

        # System Events Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                event_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                message TEXT NOT NULL,
                details TEXT,
                acknowledged BOOLEAN DEFAULT 0
            )
        """)

        # Create indexes for performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_activities_agent_timestamp
            ON agent_activities(agent_name, timestamp)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_activities_workflow
            ON agent_activities(workflow_id)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_messages_unprocessed
            ON inter_agent_messages(processed, timestamp)
        """)

        conn.commit()
        conn.close()

    def log_activity(
        self,
        agent_name: str,
        event_type: EventType,
        input_data: Dict[str, Any],
        output_data: Optional[Dict[str, Any]] = None,
        success: bool = True,
        response_time_ms: Optional[float] = None,
        error_message: Optional[str] = None,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        workflow_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Log agent activity to central database

        Returns:
            activity_id: ID of the logged activity
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        timestamp = datetime.now().isoformat()

        cursor.execute("""
            INSERT INTO agent_activities (
                timestamp, agent_name, agent_type, event_type,
                input_data, output_data, success, response_time_ms,
                error_message, user_id, session_id, workflow_id, metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            timestamp,
            agent_name,
            input_data.get('agent_type', 'unknown'),
            event_type.value,
            json.dumps(input_data),
            json.dumps(output_data) if output_data else None,
            success,
            response_time_ms,
            error_message,
            user_id,
            session_id,
            workflow_id,
            json.dumps(metadata) if metadata else None
        ))

        activity_id = cursor.lastrowid
        conn.commit()
        conn.close()

        # Update in-memory metrics
        self._update_real_time_metrics(agent_name, success, response_time_ms)

        return activity_id

    def update_agent_status(
        self,
        agent_name: str,
        status: AgentStatus,
        **kwargs
    ):
        """Update agent status in real-time"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        timestamp = datetime.now().isoformat()

        # Check if agent exists
        cursor.execute("SELECT agent_name FROM agent_status WHERE agent_name = ?", (agent_name,))
        exists = cursor.fetchone()

        if exists:
            # Update existing
            update_fields = ["status = ?", "last_updated = ?"]
            values = [status.value, timestamp]

            for key, value in kwargs.items():
                if key in ['total_interactions', 'success_rate', 'avg_response_time',
                          'current_load', 'error_count', 'uptime_seconds']:
                    update_fields.append(f"{key} = ?")
                    values.append(value)

            values.append(agent_name)

            cursor.execute(f"""
                UPDATE agent_status
                SET {', '.join(update_fields)}
                WHERE agent_name = ?
            """, values)
        else:
            # Insert new
            cursor.execute("""
                INSERT INTO agent_status (
                    agent_name, status, last_updated, total_interactions,
                    success_rate, avg_response_time, current_load, error_count
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                agent_name,
                status.value,
                timestamp,
                kwargs.get('total_interactions', 0),
                kwargs.get('success_rate', 0.0),
                kwargs.get('avg_response_time', 0.0),
                kwargs.get('current_load', 0),
                kwargs.get('error_count', 0)
            ))

        conn.commit()
        conn.close()

    def log_metric(
        self,
        agent_name: str,
        metric_name: str,
        metric_value: float,
        metric_unit: Optional[str] = None
    ):
        """Log performance metric"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO agent_metrics (timestamp, agent_name, metric_name, metric_value, metric_unit)
            VALUES (?, ?, ?, ?, ?)
        """, (
            datetime.now().isoformat(),
            agent_name,
            metric_name,
            metric_value,
            metric_unit
        ))

        conn.commit()
        conn.close()

    def send_inter_agent_message(
        self,
        from_agent: str,
        to_agent: str,
        message_type: str,
        payload: Dict[str, Any],
        workflow_id: Optional[str] = None
    ) -> int:
        """Send message from one agent to another"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO inter_agent_messages (
                timestamp, from_agent, to_agent, message_type, payload, workflow_id, processed
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.now().isoformat(),
            from_agent,
            to_agent,
            message_type,
            json.dumps(payload),
            workflow_id,
            False
        ))

        message_id = cursor.lastrowid
        conn.commit()
        conn.close()

        # Log system event
        self.log_system_event(
            event_type="collaboration",
            severity="info",
            message=f"Agent {from_agent} sent {message_type} to {to_agent}",
            details={'message_id': message_id, 'workflow_id': workflow_id}
        )

        return message_id

    def get_unprocessed_messages(self, agent_name: str) -> List[Dict[str, Any]]:
        """Get unprocessed messages for an agent"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, timestamp, from_agent, message_type, payload, workflow_id
            FROM inter_agent_messages
            WHERE to_agent = ? AND processed = 0
            ORDER BY timestamp ASC
        """, (agent_name,))

        messages = []
        for row in cursor.fetchall():
            messages.append({
                'id': row[0],
                'timestamp': row[1],
                'from_agent': row[2],
                'message_type': row[3],
                'payload': json.loads(row[4]) if row[4] else {},
                'workflow_id': row[5]
            })

        conn.close()
        return messages

    def mark_message_processed(self, message_id: int):
        """Mark message as processed"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE inter_agent_messages SET processed = 1 WHERE id = ?
        """, (message_id,))

        conn.commit()
        conn.close()

    def log_system_event(
        self,
        event_type: str,
        severity: str,  # info, warning, error, critical
        message: str,
        details: Optional[Dict[str, Any]] = None
    ):
        """Log system-wide event"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO system_events (timestamp, event_type, severity, message, details)
            VALUES (?, ?, ?, ?, ?)
        """, (
            datetime.now().isoformat(),
            event_type,
            severity,
            message,
            json.dumps(details) if details else None
        ))

        conn.commit()
        conn.close()

    def get_recent_activities(
        self,
        agent_name: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
        workflow_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get recent activities, optionally filtered by agent or workflow"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = "SELECT * FROM agent_activities WHERE 1=1"
        params = []

        if agent_name:
            query += " AND agent_name = ?"
            params.append(agent_name)

        if workflow_id:
            query += " AND workflow_id = ?"
            params.append(workflow_id)

        query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        cursor.execute(query, params)

        activities = []
        for row in cursor.fetchall():
            activities.append({
                'id': row[0],
                'timestamp': row[1],
                'agent_name': row[2],
                'agent_type': row[3],
                'event_type': row[4],
                'input_data': json.loads(row[5]) if row[5] else {},
                'output_data': json.loads(row[6]) if row[6] else {},
                'success': bool(row[7]),
                'response_time_ms': row[8],
                'error_message': row[9],
                'user_id': row[10],
                'session_id': row[11],
                'workflow_id': row[12],
                'metadata': json.loads(row[13]) if row[13] else {}
            })

        conn.close()
        return activities

    def get_all_agent_status(self) -> List[Dict[str, Any]]:
        """Get status of all agents"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM agent_status ORDER BY agent_name")

        statuses = []
        for row in cursor.fetchall():
            statuses.append({
                'agent_name': row[0],
                'status': row[1],
                'last_updated': row[2],
                'total_interactions': row[3],
                'success_rate': row[4],
                'avg_response_time': row[5],
                'current_load': row[6],
                'error_count': row[7],
                'uptime_seconds': row[8]
            })

        conn.close()
        return statuses

    def get_system_events(
        self,
        severity: Optional[str] = None,
        limit: int = 100,
        unacknowledged_only: bool = False
    ) -> List[Dict[str, Any]]:
        """Get system events"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = "SELECT * FROM system_events WHERE 1=1"
        params = []

        if severity:
            query += " AND severity = ?"
            params.append(severity)

        if unacknowledged_only:
            query += " AND acknowledged = 0"

        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)

        cursor.execute(query, params)

        events = []
        for row in cursor.fetchall():
            events.append({
                'id': row[0],
                'timestamp': row[1],
                'event_type': row[2],
                'severity': row[3],
                'message': row[4],
                'details': json.loads(row[5]) if row[5] else {},
                'acknowledged': bool(row[6])
            })

        conn.close()
        return events

    def get_workflow_trace(self, workflow_id: str) -> Dict[str, Any]:
        """Get complete trace of a workflow across all agents"""
        activities = self.get_recent_activities(workflow_id=workflow_id, limit=1000)

        # Get inter-agent messages for this workflow
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT timestamp, from_agent, to_agent, message_type, payload
            FROM inter_agent_messages
            WHERE workflow_id = ?
            ORDER BY timestamp ASC
        """, (workflow_id,))

        messages = []
        for row in cursor.fetchall():
            messages.append({
                'timestamp': row[0],
                'from_agent': row[1],
                'to_agent': row[2],
                'message_type': row[3],
                'payload': json.loads(row[4]) if row[4] else {}
            })

        conn.close()

        # Build workflow timeline
        timeline = sorted(
            activities + messages,
            key=lambda x: x['timestamp']
        )

        # Calculate workflow metrics
        if activities:
            start_time = datetime.fromisoformat(activities[-1]['timestamp'])
            end_time = datetime.fromisoformat(activities[0]['timestamp'])
            total_duration = (end_time - start_time).total_seconds() * 1000

            agents_involved = list(set(a['agent_name'] for a in activities))
            success_count = sum(1 for a in activities if a.get('success'))

            return {
                'workflow_id': workflow_id,
                'start_time': activities[-1]['timestamp'],
                'end_time': activities[0]['timestamp'],
                'total_duration_ms': total_duration,
                'agents_involved': agents_involved,
                'total_steps': len(activities),
                'successful_steps': success_count,
                'success_rate': success_count / len(activities) if activities else 0,
                'timeline': timeline,
                'inter_agent_messages': len(messages)
            }

        return {'workflow_id': workflow_id, 'timeline': [], 'error': 'No activities found'}

    def _update_real_time_metrics(
        self,
        agent_name: str,
        success: bool,
        response_time_ms: Optional[float]
    ):
        """Update in-memory real-time metrics"""
        metrics = self.real_time_metrics[agent_name]

        metrics['total_interactions'] += 1
        if success:
            metrics['successful'] += 1
        else:
            metrics['failed'] += 1

        if response_time_ms is not None:
            # Running average
            current_avg = metrics['avg_response_time']
            total = metrics['total_interactions']
            metrics['avg_response_time'] = (
                (current_avg * (total - 1) + response_time_ms) / total
            )

        metrics['last_activity'] = datetime.now().isoformat()

    def get_real_time_metrics(self, agent_name: Optional[str] = None) -> Dict:
        """Get real-time metrics from memory"""
        if agent_name:
            return dict(self.real_time_metrics.get(agent_name, {}))
        return {k: dict(v) for k, v in self.real_time_metrics.items()}

    def get_statistics(self, time_period: str = '24h') -> Dict[str, Any]:
        """Get system-wide statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Calculate time cutoff
        if time_period == '1h':
            cutoff = datetime.now() - timedelta(hours=1)
        elif time_period == '24h':
            cutoff = datetime.now() - timedelta(hours=24)
        elif time_period == '7d':
            cutoff = datetime.now() - timedelta(days=7)
        else:
            cutoff = datetime.now() - timedelta(hours=24)

        cutoff_str = cutoff.isoformat()

        # Total interactions
        cursor.execute("""
            SELECT COUNT(*), SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END), AVG(response_time_ms)
            FROM agent_activities
            WHERE timestamp >= ?
        """, (cutoff_str,))

        total, successful, avg_response = cursor.fetchone()

        # Interactions by agent
        cursor.execute("""
            SELECT agent_name, COUNT(*), SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END)
            FROM agent_activities
            WHERE timestamp >= ?
            GROUP BY agent_name
        """, (cutoff_str,))

        by_agent = {}
        for row in cursor.fetchall():
            by_agent[row[0]] = {
                'total': row[1],
                'successful': row[2],
                'success_rate': row[2] / row[1] if row[1] > 0 else 0
            }

        # Error count
        cursor.execute("""
            SELECT COUNT(*)
            FROM agent_activities
            WHERE timestamp >= ? AND success = 0
        """, (cutoff_str,))

        errors = cursor.fetchone()[0]

        # Active workflows
        cursor.execute("""
            SELECT COUNT(DISTINCT workflow_id)
            FROM agent_activities
            WHERE timestamp >= ? AND workflow_id IS NOT NULL
        """, (cutoff_str,))

        workflows = cursor.fetchone()[0]

        conn.close()

        return {
            'time_period': time_period,
            'total_interactions': total or 0,
            'successful_interactions': successful or 0,
            'success_rate': (successful / total * 100) if total else 0,
            'avg_response_time_ms': avg_response or 0,
            'error_count': errors,
            'active_workflows': workflows,
            'by_agent': by_agent
        }


# Global instance
_central_logger = None

def get_central_logger() -> CentralActivityLogger:
    """Get global central logger instance"""
    global _central_logger
    if _central_logger is None:
        _central_logger = CentralActivityLogger()
    return _central_logger


if __name__ == "__main__":
    # Test the central logger
    print("\n" + "="*80)
    print("Testing Central Activity Logger")
    print("="*80 + "\n")

    logger = CentralActivityLogger(db_path="data/test_activity.db")

    # Test 1: Log activities
    print("Test 1: Logging activities")
    logger.log_activity(
        agent_name="phase1_prospect",
        event_type=EventType.INTERACTION,
        input_data={'query': 'Test lead'},
        output_data={'score': 85},
        success=True,
        response_time_ms=234.5,
        workflow_id="wf_001"
    )

    logger.log_activity(
        agent_name="phase2_sales_pitch",
        event_type=EventType.INTERACTION,
        input_data={'prospect': 'John Doe'},
        output_data={'pitch': 'Generated pitch'},
        success=True,
        response_time_ms=5678.2,
        workflow_id="wf_001"
    )

    print("✓ Logged 2 activities")

    # Test 2: Update agent status
    print("\nTest 2: Updating agent status")
    logger.update_agent_status(
        "phase1_prospect",
        AgentStatus.ACTIVE,
        total_interactions=10,
        success_rate=0.95,
        avg_response_time=250.0
    )
    print("✓ Updated agent status")

    # Test 3: Inter-agent message
    print("\nTest 3: Inter-agent messaging")
    msg_id = logger.send_inter_agent_message(
        from_agent="phase3_orchestrator",
        to_agent="phase2_sales_pitch",
        message_type="generate_pitch",
        payload={'prospect_id': '123'},
        workflow_id="wf_001"
    )
    print(f"✓ Sent message ID: {msg_id}")

    # Test 4: Get workflow trace
    print("\nTest 4: Workflow trace")
    trace = logger.get_workflow_trace("wf_001")
    print(f"✓ Workflow: {trace['total_steps']} steps, {trace['agents_involved']} agents")

    # Test 5: Get statistics
    print("\nTest 5: Statistics")
    stats = logger.get_statistics('24h')
    print(f"✓ Total interactions: {stats['total_interactions']}")
    print(f"✓ Success rate: {stats['success_rate']:.1f}%")

    print("\n" + "="*80)
    print("Central Activity Logger Tests Complete!")
    print("="*80)
