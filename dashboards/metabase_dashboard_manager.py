#!/usr/bin/env python3
"""
Metabase Dashboard Manager for SIX3 Agency
Creates and manages pre-built dashboards for agent monitoring and analytics.
"""

import requests
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import os
from dataclasses import dataclass, asdict
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DashboardType(Enum):
    AGENT_PERFORMANCE = "agent_performance"
    SALES_PIPELINE = "sales_pipeline"
    CUSTOMER_HEALTH = "customer_health"
    EXECUTIVE_SUMMARY = "executive_summary"
    JOURNEY_ANALYTICS = "journey_analytics"
    MARKETING_FUNNEL = "marketing_funnel"

@dataclass
class DashboardCard:
    """Represents a card/chart on a dashboard"""
    title: str
    description: str
    card_type: str  # "scalar", "line", "bar", "pie", "table", etc.
    query: str
    position_x: int
    position_y: int
    width: int
    height: int
    visualization_settings: Dict[str, Any] = None

@dataclass
class Dashboard:
    """Represents a complete dashboard"""
    name: str
    description: str
    dashboard_type: DashboardType
    cards: List[DashboardCard]
    filters: List[Dict[str, Any]] = None
    auto_refresh: int = 60  # seconds

class MetabaseDashboardManager:
    """
    Manages Metabase dashboards for SIX3 Agency analytics.
    Creates pre-built dashboards for different business areas.
    """
    
    def __init__(self):
        self.metabase_url = os.getenv('METABASE_URL', 'http://localhost:3000')
        self.metabase_user = os.getenv('METABASE_USER', 'admin@six3.agency')
        self.metabase_password = os.getenv('METABASE_PASSWORD', 'six3agency123')
        self.session_id = None
        self.database_id = None
        
        logger.info("Metabase Dashboard Manager initialized")
    
    def connect(self) -> bool:
        """Connect to Metabase and authenticate"""
        try:
            # Login to Metabase
            login_data = {
                "username": self.metabase_user,
                "password": self.metabase_password
            }
            
            response = requests.post(
                f"{self.metabase_url}/api/session",
                json=login_data
            )
            
            if response.status_code == 200:
                self.session_id = response.json().get('id')
                logger.info("Successfully connected to Metabase")
                
                # Get database ID
                self._get_database_id()
                return True
            else:
                logger.error(f"Failed to connect to Metabase: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error connecting to Metabase: {e}")
            return False
    
    def _get_database_id(self) -> Optional[int]:
        """Get the database ID for SIX3 Agency database"""
        try:
            headers = {"X-Metabase-Session": self.session_id}
            response = requests.get(f"{self.metabase_url}/api/database", headers=headers)
            
            if response.status_code == 200:
                databases = response.json()
                for db in databases:
                    if db.get('name') == 'SIX3_Analytics' or 'postgres' in db.get('engine', '').lower():
                        self.database_id = db['id']
                        logger.info(f"Found database ID: {self.database_id}")
                        return self.database_id
                        
            logger.warning("Database not found, using default ID")
            self.database_id = 1  # Default fallback
            return self.database_id
            
        except Exception as e:
            logger.error(f"Error getting database ID: {e}")
            self.database_id = 1
            return self.database_id
    
    def create_dashboard(self, dashboard: Dashboard) -> Optional[int]:
        """Create a dashboard in Metabase"""
        try:
            headers = {"X-Metabase-Session": self.session_id}
            
            dashboard_data = {
                "name": dashboard.name,
                "description": dashboard.description,
                "parameters": dashboard.filters or []
            }
            
            response = requests.post(
                f"{self.metabase_url}/api/dashboard",
                json=dashboard_data,
                headers=headers
            )
            
            if response.status_code == 200:
                dashboard_id = response.json()['id']
                logger.info(f"Created dashboard '{dashboard.name}' with ID: {dashboard_id}")
                
                # Add cards to dashboard
                for card in dashboard.cards:
                    self._add_card_to_dashboard(dashboard_id, card)
                
                return dashboard_id
            else:
                logger.error(f"Failed to create dashboard: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating dashboard: {e}")
            return None
    
    def _add_card_to_dashboard(self, dashboard_id: int, card: DashboardCard) -> Optional[int]:
        """Add a card to a dashboard"""
        try:
            headers = {"X-Metabase-Session": self.session_id}
            
            # First create the question/card
            question_data = {
                "name": card.title,
                "description": card.description,
                "dataset_query": {
                    "type": "native",
                    "native": {
                        "query": card.query
                    },
                    "database": self.database_id
                },
                "display": card.card_type,
                "visualization_settings": card.visualization_settings or {}
            }
            
            response = requests.post(
                f"{self.metabase_url}/api/card",
                json=question_data,
                headers=headers
            )
            
            if response.status_code == 200:
                card_id = response.json()['id']
                
                # Add card to dashboard
                dashcard_data = {
                    "cardId": card_id,
                    "row": card.position_y,
                    "col": card.position_x,
                    "sizeX": card.width,
                    "sizeY": card.height
                }
                
                response = requests.post(
                    f"{self.metabase_url}/api/dashboard/{dashboard_id}/cards",
                    json=dashcard_data,
                    headers=headers
                )
                
                if response.status_code == 200:
                    logger.info(f"Added card '{card.title}' to dashboard")
                    return card_id
                else:
                    logger.error(f"Failed to add card to dashboard: {response.text}")
                    
            else:
                logger.error(f"Failed to create card: {response.text}")
                
        except Exception as e:
            logger.error(f"Error adding card to dashboard: {e}")
            
        return None
    
    def get_agent_performance_dashboard(self) -> Dashboard:
        """Create Agent Performance dashboard"""
        cards = [
            DashboardCard(
                title="Total Conversations",
                description="Total number of conversations across all agents",
                card_type="scalar",
                query="""
                SELECT COUNT(*) as total_conversations
                FROM agent_logs 
                WHERE created_at >= NOW() - INTERVAL '30 days'
                """,
                position_x=0, position_y=0, width=6, height=4
            ),
            DashboardCard(
                title="Active Agents",
                description="Number of agents that processed requests in the last 24 hours",
                card_type="scalar",
                query="""
                SELECT COUNT(DISTINCT agent_name) as active_agents
                FROM agent_logs 
                WHERE created_at >= NOW() - INTERVAL '1 day'
                """,
                position_x=6, position_y=0, width=6, height=4
            ),
            DashboardCard(
                title="Agent Response Times",
                description="Average response time by agent",
                card_type="bar",
                query="""
                SELECT 
                    agent_name,
                    AVG(response_time) as avg_response_time
                FROM agent_logs 
                WHERE created_at >= NOW() - INTERVAL '7 days'
                GROUP BY agent_name
                ORDER BY avg_response_time DESC
                """,
                position_x=0, position_y=4, width=12, height=6
            ),
            DashboardCard(
                title="Success Rate by Agent",
                description="Success rate percentage for each agent",
                card_type="bar",
                query="""
                SELECT 
                    agent_name,
                    (COUNT(CASE WHEN status = 'success' THEN 1 END) * 100.0 / COUNT(*)) as success_rate
                FROM agent_logs 
                WHERE created_at >= NOW() - INTERVAL '7 days'
                GROUP BY agent_name
                ORDER BY success_rate DESC
                """,
                position_x=0, position_y=10, width=12, height=6
            ),
            DashboardCard(
                title="Agent Usage Over Time",
                description="Agent usage trends over the past 30 days",
                card_type="line",
                query="""
                SELECT 
                    DATE(created_at) as date,
                    agent_name,
                    COUNT(*) as usage_count
                FROM agent_logs 
                WHERE created_at >= NOW() - INTERVAL '30 days'
                GROUP BY DATE(created_at), agent_name
                ORDER BY date
                """,
                position_x=0, position_y=16, width=12, height=8
            ),
            DashboardCard(
                title="Error Rate Trends",
                description="Daily error rates across all agents",
                card_type="line",
                query="""
                SELECT 
                    DATE(created_at) as date,
                    (COUNT(CASE WHEN status = 'error' THEN 1 END) * 100.0 / COUNT(*)) as error_rate
                FROM agent_logs 
                WHERE created_at >= NOW() - INTERVAL '30 days'
                GROUP BY DATE(created_at)
                ORDER BY date
                """,
                position_x=0, position_y=24, width=12, height=6
            )
        ]
        
        return Dashboard(
            name="Agent Performance Dashboard",
            description="Real-time monitoring of AI agent performance and metrics",
            dashboard_type=DashboardType.AGENT_PERFORMANCE,
            cards=cards,
            auto_refresh=30
        )
    
    def get_sales_pipeline_dashboard(self) -> Dashboard:
        """Create Sales Pipeline dashboard"""
        cards = [
            DashboardCard(
                title="Total Pipeline Value",
                description="Total value of all opportunities in pipeline",
                card_type="scalar",
                query="""
                SELECT COALESCE(SUM(deal_value), 0) as total_pipeline
                FROM crm_data 
                WHERE status NOT IN ('closed_won', 'closed_lost')
                """,
                position_x=0, position_y=0, width=4, height=4
            ),
            DashboardCard(
                title="Qualified Leads This Month",
                description="Number of qualified leads generated this month",
                card_type="scalar",
                query="""
                SELECT COUNT(*) as qualified_leads
                FROM crm_data 
                WHERE lead_score >= 70 
                AND created_at >= DATE_TRUNC('month', NOW())
                """,
                position_x=4, position_y=0, width=4, height=4
            ),
            DashboardCard(
                title="Conversion Rate",
                description="Lead to customer conversion rate",
                card_type="scalar",
                query="""
                SELECT 
                    ROUND(
                        (COUNT(CASE WHEN status = 'closed_won' THEN 1 END) * 100.0 / 
                         NULLIF(COUNT(*), 0)), 2
                    ) as conversion_rate
                FROM crm_data 
                WHERE created_at >= NOW() - INTERVAL '30 days'
                """,
                position_x=8, position_y=0, width=4, height=4,
                visualization_settings={"suffix": "%"}
            ),
            DashboardCard(
                title="Pipeline by Stage",
                description="Distribution of deals across pipeline stages",
                card_type="pie",
                query="""
                SELECT 
                    pipeline_stage,
                    COUNT(*) as deal_count
                FROM crm_data 
                WHERE status NOT IN ('closed_won', 'closed_lost')
                GROUP BY pipeline_stage
                """,
                position_x=0, position_y=4, width=6, height=8
            ),
            DashboardCard(
                title="Lead Sources Performance",
                description="Lead quality and volume by source",
                card_type="bar",
                query="""
                SELECT 
                    source,
                    COUNT(*) as total_leads,
                    AVG(lead_score) as avg_score,
                    COUNT(CASE WHEN status = 'closed_won' THEN 1 END) as won_deals
                FROM crm_data 
                WHERE created_at >= NOW() - INTERVAL '30 days'
                GROUP BY source
                ORDER BY avg_score DESC
                """,
                position_x=6, position_y=4, width=6, height=8
            ),
            DashboardCard(
                title="Sales Velocity",
                description="Revenue closed over time",
                card_type="line",
                query="""
                SELECT 
                    DATE_TRUNC('week', closed_date) as week,
                    SUM(deal_value) as revenue
                FROM crm_data 
                WHERE status = 'closed_won' 
                AND closed_date >= NOW() - INTERVAL '90 days'
                GROUP BY DATE_TRUNC('week', closed_date)
                ORDER BY week
                """,
                position_x=0, position_y=12, width=12, height=8
            )
        ]
        
        return Dashboard(
            name="Sales Pipeline Dashboard",
            description="Sales performance and pipeline analytics",
            dashboard_type=DashboardType.SALES_PIPELINE,
            cards=cards,
            auto_refresh=60
        )
    
    def get_customer_health_dashboard(self) -> Dashboard:
        """Create Customer Health dashboard"""
        cards = [
            DashboardCard(
                title="Healthy Customers",
                description="Percentage of customers with health score > 70",
                card_type="scalar",
                query="""
                SELECT 
                    ROUND(
                        (COUNT(CASE WHEN health_score > 70 THEN 1 END) * 100.0 / 
                         NULLIF(COUNT(*), 0)), 1
                    ) as healthy_percentage
                FROM customer_health 
                WHERE status = 'active'
                """,
                position_x=0, position_y=0, width=4, height=4,
                visualization_settings={"suffix": "%"}
            ),
            DashboardCard(
                title="At-Risk Customers",
                description="Number of customers with health score < 40",
                card_type="scalar",
                query="""
                SELECT COUNT(*) as at_risk_customers
                FROM customer_health 
                WHERE health_score < 40 AND status = 'active'
                """,
                position_x=4, position_y=0, width=4, height=4
            ),
            DashboardCard(
                title="Avg Customer Health",
                description="Average health score across all active customers",
                card_type="scalar",
                query="""
                SELECT ROUND(AVG(health_score), 1) as avg_health
                FROM customer_health 
                WHERE status = 'active'
                """,
                position_x=8, position_y=0, width=4, height=4
            ),
            DashboardCard(
                title="Health Distribution",
                description="Distribution of customer health scores",
                card_type="bar",
                query="""
                SELECT 
                    CASE 
                        WHEN health_score >= 80 THEN 'Excellent (80-100)'
                        WHEN health_score >= 60 THEN 'Good (60-79)'
                        WHEN health_score >= 40 THEN 'Fair (40-59)'
                        ELSE 'Poor (0-39)'
                    END as health_category,
                    COUNT(*) as customer_count
                FROM customer_health 
                WHERE status = 'active'
                GROUP BY health_category
                ORDER BY MIN(health_score) DESC
                """,
                position_x=0, position_y=4, width=6, height=8
            ),
            DashboardCard(
                title="Churn Risk Factors",
                description="Primary factors contributing to customer churn risk",
                card_type="bar",
                query="""
                SELECT 
                    churn_risk_factor,
                    COUNT(*) as customer_count,
                    AVG(health_score) as avg_health
                FROM customer_health 
                WHERE status = 'active' AND health_score < 50
                GROUP BY churn_risk_factor
                ORDER BY customer_count DESC
                """,
                position_x=6, position_y=4, width=6, height=8
            ),
            DashboardCard(
                title="Health Trends",
                description="Customer health score trends over time",
                card_type="line",
                query="""
                SELECT 
                    DATE_TRUNC('week', updated_at) as week,
                    AVG(health_score) as avg_health,
                    COUNT(CASE WHEN health_score < 40 THEN 1 END) as at_risk_count
                FROM customer_health 
                WHERE updated_at >= NOW() - INTERVAL '90 days'
                GROUP BY DATE_TRUNC('week', updated_at)
                ORDER BY week
                """,
                position_x=0, position_y=12, width=12, height=8
            ),
            DashboardCard(
                title="Intervention Success Rate",
                description="Success rate of customer success interventions",
                card_type="table",
                query="""
                SELECT 
                    intervention_type,
                    COUNT(*) as total_interventions,
                    COUNT(CASE WHEN outcome = 'successful' THEN 1 END) as successful,
                    ROUND(
                        COUNT(CASE WHEN outcome = 'successful' THEN 1 END) * 100.0 / 
                        NULLIF(COUNT(*), 0), 1
                    ) as success_rate
                FROM customer_interventions 
                WHERE created_at >= NOW() - INTERVAL '30 days'
                GROUP BY intervention_type
                ORDER BY success_rate DESC
                """,
                position_x=0, position_y=20, width=12, height=6
            )
        ]
        
        return Dashboard(
            name="Customer Health Dashboard",
            description="Customer health monitoring and churn prevention",
            dashboard_type=DashboardType.CUSTOMER_HEALTH,
            cards=cards,
            auto_refresh=120
        )
    
    def get_executive_summary_dashboard(self) -> Dashboard:
        """Create Executive Summary dashboard"""
        cards = [
            DashboardCard(
                title="Monthly Recurring Revenue",
                description="Current MRR from all active customers",
                card_type="scalar",
                query="""
                SELECT COALESCE(SUM(mrr), 0) as total_mrr
                FROM customer_health 
                WHERE status = 'active'
                """,
                position_x=0, position_y=0, width=3, height=4,
                visualization_settings={"prefix": "$"}
            ),
            DashboardCard(
                title="Customer Acquisition Cost",
                description="Average cost to acquire a new customer",
                card_type="scalar",
                query="""
                SELECT COALESCE(AVG(acquisition_cost), 0) as avg_cac
                FROM crm_data 
                WHERE status = 'closed_won' 
                AND created_at >= NOW() - INTERVAL '30 days'
                """,
                position_x=3, position_y=0, width=3, height=4,
                visualization_settings={"prefix": "$"}
            ),
            DashboardCard(
                title="Customer Lifetime Value",
                description="Average lifetime value per customer",
                card_type="scalar",
                query="""
                SELECT COALESCE(AVG(lifetime_value), 0) as avg_ltv
                FROM customer_health 
                WHERE status = 'active'
                """,
                position_x=6, position_y=0, width=3, height=4,
                visualization_settings={"prefix": "$"}
            ),
            DashboardCard(
                title="Net Promoter Score",
                description="Current NPS based on recent surveys",
                card_type="scalar",
                query="""
                SELECT COALESCE(AVG(nps_score), 0) as nps
                FROM customer_feedback 
                WHERE created_at >= NOW() - INTERVAL '30 days'
                """,
                position_x=9, position_y=0, width=3, height=4
            ),
            DashboardCard(
                title="Revenue Growth",
                description="Monthly revenue growth trend",
                card_type="line",
                query="""
                SELECT 
                    DATE_TRUNC('month', closed_date) as month,
                    SUM(deal_value) as revenue
                FROM crm_data 
                WHERE status = 'closed_won' 
                AND closed_date >= NOW() - INTERVAL '12 months'
                GROUP BY DATE_TRUNC('month', closed_date)
                ORDER BY month
                """,
                position_x=0, position_y=4, width=8, height=8
            ),
            DashboardCard(
                title="Key Metrics Summary",
                description="Overview of critical business metrics",
                card_type="table",
                query="""
                SELECT 
                    'Total Customers' as metric,
                    COUNT(*) as value,
                    'Active customers' as description
                FROM customer_health WHERE status = 'active'
                UNION ALL
                SELECT 
                    'Churn Rate %',
                    ROUND(
                        COUNT(CASE WHEN status = 'churned' THEN 1 END) * 100.0 / 
                        NULLIF(COUNT(*), 0), 2
                    ),
                    'Monthly churn rate'
                FROM customer_health 
                WHERE updated_at >= NOW() - INTERVAL '30 days'
                """,
                position_x=8, position_y=4, width=4, height=8
            ),
            DashboardCard(
                title="AI Agent ROI",
                description="Return on investment from AI automation",
                card_type="bar",
                query="""
                SELECT 
                    agent_name,
                    cost_savings,
                    efficiency_gain,
                    roi_percentage
                FROM agent_performance 
                WHERE calculated_at >= NOW() - INTERVAL '30 days'
                ORDER BY roi_percentage DESC
                """,
                position_x=0, position_y=12, width=12, height=8
            )
        ]
        
        return Dashboard(
            name="Executive Summary Dashboard",
            description="High-level business metrics and KPIs for executive team",
            dashboard_type=DashboardType.EXECUTIVE_SUMMARY,
            cards=cards,
            auto_refresh=300  # 5 minutes
        )
    
    def get_journey_analytics_dashboard(self) -> Dashboard:
        """Create Journey Analytics dashboard for Phase 3"""
        cards = [
            DashboardCard(
                title="Active Journeys",
                description="Number of customer journeys currently in progress",
                card_type="scalar",
                query="""
                SELECT COUNT(*) as active_journeys
                FROM journey_executions 
                WHERE status = 'in_progress'
                """,
                position_x=0, position_y=0, width=4, height=4
            ),
            DashboardCard(
                title="Journey Completion Rate",
                description="Percentage of journeys that complete successfully",
                card_type="scalar",
                query="""
                SELECT 
                    ROUND(
                        COUNT(CASE WHEN status = 'completed' THEN 1 END) * 100.0 / 
                        NULLIF(COUNT(*), 0), 1
                    ) as completion_rate
                FROM journey_executions 
                WHERE created_at >= NOW() - INTERVAL '30 days'
                """,
                position_x=4, position_y=0, width=4, height=4,
                visualization_settings={"suffix": "%"}
            ),
            DashboardCard(
                title="Avg Journey Duration",
                description="Average time to complete customer journeys",
                card_type="scalar",
                query="""
                SELECT 
                    ROUND(AVG(EXTRACT(EPOCH FROM (completed_at - started_at))/3600), 1) as avg_hours
                FROM journey_executions 
                WHERE status = 'completed' 
                AND completed_at >= NOW() - INTERVAL '30 days'
                """,
                position_x=8, position_y=0, width=4, height=4,
                visualization_settings={"suffix": " hrs"}
            ),
            DashboardCard(
                title="Journey Performance",
                description="Success rate and duration by journey type",
                card_type="bar",
                query="""
                SELECT 
                    journey_name,
                    COUNT(*) as total_executions,
                    COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed,
                    ROUND(
                        COUNT(CASE WHEN status = 'completed' THEN 1 END) * 100.0 / 
                        NULLIF(COUNT(*), 0), 1
                    ) as success_rate
                FROM journey_executions 
                WHERE created_at >= NOW() - INTERVAL '30 days'
                GROUP BY journey_name
                ORDER BY success_rate DESC
                """,
                position_x=0, position_y=4, width=8, height=8
            ),
            DashboardCard(
                title="Department Handoffs",
                description="Cross-department handoff success rates",
                card_type="pie",
                query="""
                SELECT 
                    CONCAT(from_department, ' → ', to_department) as handoff,
                    COUNT(CASE WHEN handoff_status = 'success' THEN 1 END) as successful_handoffs
                FROM journey_handoffs 
                WHERE created_at >= NOW() - INTERVAL '30 days'
                GROUP BY from_department, to_department
                """,
                position_x=8, position_y=4, width=4, height=8
            ),
            DashboardCard(
                title="Journey Stage Bottlenecks",
                description="Stages where journeys most commonly get stuck",
                card_type="bar",
                query="""
                SELECT 
                    current_step,
                    COUNT(*) as stuck_count,
                    AVG(EXTRACT(EPOCH FROM (NOW() - step_started_at))/3600) as avg_stuck_hours
                FROM journey_executions 
                WHERE status = 'in_progress' 
                AND step_started_at < NOW() - INTERVAL '4 hours'
                GROUP BY current_step
                ORDER BY stuck_count DESC
                """,
                position_x=0, position_y=12, width=12, height=6
            ),
            DashboardCard(
                title="Journey ROI by Type",
                description="Return on investment for different journey types",
                card_type="table",
                query="""
                SELECT 
                    journey_name,
                    COUNT(*) as executions,
                    AVG(customer_value_generated) as avg_value,
                    SUM(customer_value_generated) as total_value,
                    AVG(execution_cost) as avg_cost,
                    ROUND(
                        AVG(customer_value_generated) / NULLIF(AVG(execution_cost), 0), 2
                    ) as roi_ratio
                FROM journey_executions 
                WHERE status = 'completed' 
                AND created_at >= NOW() - INTERVAL '30 days'
                GROUP BY journey_name
                ORDER BY roi_ratio DESC
                """,
                position_x=0, position_y=18, width=12, height=8
            )
        ]
        
        return Dashboard(
            name="Journey Analytics Dashboard",
            description="End-to-end customer journey performance and optimization",
            dashboard_type=DashboardType.JOURNEY_ANALYTICS,
            cards=cards,
            auto_refresh=60
        )
    
    def create_all_dashboards(self) -> Dict[str, Optional[int]]:
        """Create all pre-built dashboards"""
        if not self.connect():
            logger.error("Failed to connect to Metabase")
            return {}
        
        dashboards = [
            self.get_agent_performance_dashboard(),
            self.get_sales_pipeline_dashboard(),
            self.get_customer_health_dashboard(),
            self.get_executive_summary_dashboard(),
            self.get_journey_analytics_dashboard()
        ]
        
        results = {}
        for dashboard in dashboards:
            dashboard_id = self.create_dashboard(dashboard)
            results[dashboard.name] = dashboard_id
            
        logger.info(f"Created {len([d for d in results.values() if d])} dashboards successfully")
        return results
    
    def update_dashboard_data(self, dashboard_type: DashboardType) -> bool:
        """Refresh data for a specific dashboard type"""
        try:
            # This would trigger data refresh in Metabase
            # Implementation depends on specific Metabase setup
            logger.info(f"Refreshing data for {dashboard_type.value} dashboard")
            return True
        except Exception as e:
            logger.error(f"Error refreshing dashboard data: {e}")
            return False
    
    def get_dashboard_url(self, dashboard_id: int) -> str:
        """Get the public URL for a dashboard"""
        return f"{self.metabase_url}/dashboard/{dashboard_id}"
    
    def export_dashboard_config(self, dashboard_id: int) -> Optional[Dict]:
        """Export dashboard configuration for backup"""
        try:
            headers = {"X-Metabase-Session": self.session_id}
            response = requests.get(
                f"{self.metabase_url}/api/dashboard/{dashboard_id}",
                headers=headers
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to export dashboard config: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error exporting dashboard: {e}")
            return None

def main():
    """Main function to create all dashboards"""
    manager = MetabaseDashboardManager()
    
    print("🚀 Creating SIX3 Agency Metabase Dashboards...")
    print("=" * 50)
    
    # Create all dashboards
    results = manager.create_all_dashboards()
    
    print("\n📊 Dashboard Creation Results:")
    print("-" * 30)
    
    for name, dashboard_id in results.items():
        if dashboard_id:
            url = manager.get_dashboard_url(dashboard_id)
            print(f"✅ {name}: {url}")
        else:
            print(f"❌ {name}: Failed to create")
    
    print("\n🎯 Next Steps:")
    print("1. Configure Metabase environment variables")
    print("2. Set up database connections")
    print("3. Verify dashboard data sources")
    print("4. Test real-time data updates")
    print("5. Configure automated reports")
    
    return results

if __name__ == "__main__":
    main()