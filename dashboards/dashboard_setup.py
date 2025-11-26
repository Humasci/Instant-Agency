#!/usr/bin/env python3
"""
Dashboard Setup Script for SIX3 Agency
Sets up all Metabase dashboards with pre-built templates and configurations.
"""

import os
import sys
import json
import logging
from typing import Dict, List, Optional
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from dashboards.metabase_dashboard_manager import MetabaseDashboardManager, DashboardType
from integrations.database.postgresql_manager import PostgreSQLManager

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DashboardSetup:
    """
    Complete dashboard setup for SIX3 Agency.
    Creates database tables, imports templates, and configures Metabase.
    """
    
    def __init__(self):
        self.dashboard_manager = MetabaseDashboardManager()
        self.db_manager = PostgreSQLManager()
        self.template_dir = Path(__file__).parent / "dashboard_templates"
        
        logger.info("Dashboard Setup initialized")
    
    def create_required_tables(self) -> bool:
        """Create database tables required for dashboard data"""
        try:
            logger.info("Creating required database tables...")
            
            # Agent logs table
            agent_logs_sql = """
            CREATE TABLE IF NOT EXISTS agent_logs (
                id SERIAL PRIMARY KEY,
                agent_name VARCHAR(255) NOT NULL,
                status VARCHAR(50) NOT NULL,
                response_time FLOAT,
                error_message TEXT,
                journey_execution_id INTEGER,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            );
            CREATE INDEX IF NOT EXISTS idx_agent_logs_created_at ON agent_logs(created_at);
            CREATE INDEX IF NOT EXISTS idx_agent_logs_agent_name ON agent_logs(agent_name);
            """
            
            # CRM data table
            crm_data_sql = """
            CREATE TABLE IF NOT EXISTS crm_data (
                id SERIAL PRIMARY KEY,
                customer_id VARCHAR(255),
                company_name VARCHAR(255),
                lead_score INTEGER DEFAULT 0,
                pipeline_stage VARCHAR(100),
                status VARCHAR(50),
                deal_value DECIMAL(15,2) DEFAULT 0,
                win_probability INTEGER DEFAULT 0,
                source VARCHAR(100),
                acquisition_cost DECIMAL(15,2) DEFAULT 0,
                expected_close_date DATE,
                closed_date DATE,
                stage_entered_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            );
            CREATE INDEX IF NOT EXISTS idx_crm_data_status ON crm_data(status);
            CREATE INDEX IF NOT EXISTS idx_crm_data_created_at ON crm_data(created_at);
            """
            
            # Customer health table
            customer_health_sql = """
            CREATE TABLE IF NOT EXISTS customer_health (
                id SERIAL PRIMARY KEY,
                customer_id VARCHAR(255) UNIQUE,
                customer_name VARCHAR(255),
                segment VARCHAR(100),
                health_score INTEGER DEFAULT 50,
                status VARCHAR(50) DEFAULT 'active',
                churn_risk_factor VARCHAR(255),
                lifetime_value DECIMAL(15,2) DEFAULT 0,
                mrr DECIMAL(15,2) DEFAULT 0,
                monthly_revenue DECIMAL(15,2) DEFAULT 0,
                current_plan VARCHAR(100),
                expansion_potential DECIMAL(15,2) DEFAULT 0,
                last_interaction_date DATE,
                csm_assigned VARCHAR(255),
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            );
            CREATE INDEX IF NOT EXISTS idx_customer_health_status ON customer_health(status);
            CREATE INDEX IF NOT EXISTS idx_customer_health_score ON customer_health(health_score);
            """
            
            # Customer feedback table
            customer_feedback_sql = """
            CREATE TABLE IF NOT EXISTS customer_feedback (
                id SERIAL PRIMARY KEY,
                customer_id VARCHAR(255),
                customer_segment VARCHAR(100),
                nps_score INTEGER,
                csat_score FLOAT,
                feedback_text TEXT,
                created_at TIMESTAMP DEFAULT NOW()
            );
            CREATE INDEX IF NOT EXISTS idx_customer_feedback_created_at ON customer_feedback(created_at);
            """
            
            # Customer interventions table
            customer_interventions_sql = """
            CREATE TABLE IF NOT EXISTS customer_interventions (
                id SERIAL PRIMARY KEY,
                customer_id VARCHAR(255),
                customer_segment VARCHAR(100),
                intervention_type VARCHAR(255),
                outcome VARCHAR(100),
                health_score_improvement INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT NOW()
            );
            CREATE INDEX IF NOT EXISTS idx_interventions_created_at ON customer_interventions(created_at);
            """
            
            # Journey executions table (for Phase 3)
            journey_executions_sql = """
            CREATE TABLE IF NOT EXISTS journey_executions (
                id SERIAL PRIMARY KEY,
                journey_name VARCHAR(255),
                customer_id VARCHAR(255),
                status VARCHAR(50) DEFAULT 'in_progress',
                current_step VARCHAR(255),
                started_at TIMESTAMP DEFAULT NOW(),
                completed_at TIMESTAMP,
                step_started_at TIMESTAMP,
                step_completed_at TIMESTAMP,
                customer_value_generated DECIMAL(15,2) DEFAULT 0,
                execution_cost DECIMAL(15,2) DEFAULT 0,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            );
            CREATE INDEX IF NOT EXISTS idx_journey_executions_status ON journey_executions(status);
            CREATE INDEX IF NOT EXISTS idx_journey_executions_journey ON journey_executions(journey_name);
            """
            
            # Journey handoffs table
            journey_handoffs_sql = """
            CREATE TABLE IF NOT EXISTS journey_handoffs (
                id SERIAL PRIMARY KEY,
                journey_execution_id INTEGER REFERENCES journey_executions(id),
                from_department VARCHAR(100),
                to_department VARCHAR(100),
                handoff_status VARCHAR(50) DEFAULT 'pending',
                handoff_duration_minutes FLOAT,
                created_at TIMESTAMP DEFAULT NOW()
            );
            CREATE INDEX IF NOT EXISTS idx_handoffs_created_at ON journey_handoffs(created_at);
            """
            
            # Agent performance table
            agent_performance_sql = """
            CREATE TABLE IF NOT EXISTS agent_performance (
                id SERIAL PRIMARY KEY,
                agent_name VARCHAR(255),
                cost_savings DECIMAL(15,2) DEFAULT 0,
                efficiency_gain FLOAT DEFAULT 0,
                roi_percentage FLOAT DEFAULT 0,
                total_interactions INTEGER DEFAULT 0,
                calculated_at TIMESTAMP DEFAULT NOW()
            );
            CREATE INDEX IF NOT EXISTS idx_agent_performance_calculated ON agent_performance(calculated_at);
            """
            
            # Execute all table creation queries
            tables = [
                ("agent_logs", agent_logs_sql),
                ("crm_data", crm_data_sql), 
                ("customer_health", customer_health_sql),
                ("customer_feedback", customer_feedback_sql),
                ("customer_interventions", customer_interventions_sql),
                ("journey_executions", journey_executions_sql),
                ("journey_handoffs", journey_handoffs_sql),
                ("agent_performance", agent_performance_sql)
            ]
            
            if self.db_manager.connect():
                for table_name, sql in tables:
                    if self.db_manager.execute_query(sql):
                        logger.info(f"✅ Created/verified table: {table_name}")
                    else:
                        logger.error(f"❌ Failed to create table: {table_name}")
                        return False
                
                logger.info("All required tables created successfully")
                return True
            else:
                logger.error("Failed to connect to database")
                return False
                
        except Exception as e:
            logger.error(f"Error creating tables: {e}")
            return False
    
    def load_dashboard_template(self, template_name: str) -> Optional[Dict]:
        """Load a dashboard template from JSON file"""
        try:
            template_path = self.template_dir / f"{template_name}.json"
            
            if not template_path.exists():
                logger.error(f"Template not found: {template_path}")
                return None
            
            with open(template_path, 'r') as f:
                template_data = json.load(f)
            
            logger.info(f"Loaded template: {template_name}")
            return template_data
            
        except Exception as e:
            logger.error(f"Error loading template {template_name}: {e}")
            return None
    
    def create_dashboard_from_template(self, template_name: str) -> Optional[int]:
        """Create a dashboard in Metabase from a template"""
        try:
            template = self.load_dashboard_template(template_name)
            if not template:
                return None
            
            # Create dashboard via Metabase API using template data
            # This is simplified - actual implementation would need to map
            # template structure to Metabase API calls
            
            logger.info(f"Creating dashboard from template: {template_name}")
            
            # For now, use the existing dashboard manager methods
            if template_name == "agent_performance":
                return self.dashboard_manager.create_dashboard(
                    self.dashboard_manager.get_agent_performance_dashboard()
                )
            elif template_name == "sales_pipeline":
                return self.dashboard_manager.create_dashboard(
                    self.dashboard_manager.get_sales_pipeline_dashboard()
                )
            elif template_name == "customer_health":
                return self.dashboard_manager.create_dashboard(
                    self.dashboard_manager.get_customer_health_dashboard()
                )
            elif template_name == "executive_summary":
                return self.dashboard_manager.create_dashboard(
                    self.dashboard_manager.get_executive_summary_dashboard()
                )
            elif template_name == "journey_analytics":
                return self.dashboard_manager.create_dashboard(
                    self.dashboard_manager.get_journey_analytics_dashboard()
                )
            else:
                logger.warning(f"Unknown template: {template_name}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating dashboard from template {template_name}: {e}")
            return None
    
    def populate_sample_data(self) -> bool:
        """Populate tables with sample data for testing dashboards"""
        try:
            logger.info("Populating sample data for dashboard testing...")
            
            if not self.db_manager.connect():
                logger.error("Failed to connect to database")
                return False
            
            # Sample agent logs
            agent_logs_data = """
            INSERT INTO agent_logs (agent_name, status, response_time, created_at) VALUES
            ('Prospect Qualification Agent', 'success', 245.5, NOW() - INTERVAL '1 hour'),
            ('FAQ Chatbot', 'success', 156.2, NOW() - INTERVAL '2 hours'),
            ('Sales Pitch Agent', 'success', 389.7, NOW() - INTERVAL '3 hours'),
            ('Content Writer Agent', 'error', 1250.0, NOW() - INTERVAL '4 hours'),
            ('Email Personalizer Agent', 'success', 178.9, NOW() - INTERVAL '5 hours'),
            ('Social Media Agent', 'success', 234.1, NOW() - INTERVAL '6 hours'),
            ('Intent Classifier Agent', 'success', 98.4, NOW() - INTERVAL '7 hours')
            ON CONFLICT DO NOTHING;
            """
            
            # Sample CRM data
            crm_data_sample = """
            INSERT INTO crm_data (company_name, lead_score, pipeline_stage, status, deal_value, win_probability, source, created_at) VALUES
            ('TechCorp Solutions', 85, 'Proposal', 'open', 50000, 75, 'Website', NOW() - INTERVAL '5 days'),
            ('Digital Marketing Inc', 92, 'Negotiation', 'open', 75000, 85, 'LinkedIn', NOW() - INTERVAL '3 days'),
            ('StartupXYZ', 68, 'Discovery', 'open', 25000, 45, 'Referral', NOW() - INTERVAL '2 days'),
            ('Enterprise Corp', 95, 'Closing', 'closed_won', 150000, 90, 'Sales Call', NOW() - INTERVAL '1 day'),
            ('Local Business', 45, 'Qualification', 'open', 12000, 30, 'Google Ads', NOW() - INTERVAL '4 days')
            ON CONFLICT DO NOTHING;
            """
            
            # Sample customer health data
            customer_health_data = """
            INSERT INTO customer_health (customer_name, segment, health_score, status, lifetime_value, mrr, created_at) VALUES
            ('TechCorp Solutions', 'Enterprise', 85, 'active', 250000, 8500, NOW() - INTERVAL '30 days'),
            ('Digital Marketing Inc', 'Mid-Market', 92, 'active', 180000, 6200, NOW() - INTERVAL '25 days'),
            ('StartupXYZ', 'Small Business', 68, 'active', 50000, 2100, NOW() - INTERVAL '20 days'),
            ('Enterprise Corp', 'Enterprise', 95, 'active', 500000, 15000, NOW() - INTERVAL '15 days'),
            ('Local Business', 'Small Business', 35, 'at_risk', 25000, 1200, NOW() - INTERVAL '10 days')
            ON CONFLICT (customer_id) DO NOTHING;
            """
            
            # Sample journey executions (for Phase 3)
            journey_executions_data = """
            INSERT INTO journey_executions (journey_name, customer_id, status, current_step, customer_value_generated, execution_cost, created_at) VALUES
            ('B2B Sales Journey', 'cust_001', 'completed', 'Deal Closed', 50000, 500, NOW() - INTERVAL '2 days'),
            ('Content Marketing Journey', 'cust_002', 'in_progress', 'Content Distribution', 0, 150, NOW() - INTERVAL '1 day'),
            ('Customer Onboarding Journey', 'cust_003', 'completed', 'Success Review', 25000, 300, NOW() - INTERVAL '3 days'),
            ('Lead Nurturing Journey', 'cust_004', 'in_progress', 'Qualification Call', 0, 75, NOW() - INTERVAL '6 hours')
            ON CONFLICT DO NOTHING;
            """
            
            # Sample agent performance data
            agent_performance_data = """
            INSERT INTO agent_performance (agent_name, cost_savings, efficiency_gain, roi_percentage, total_interactions) VALUES
            ('Prospect Qualification Agent', 15000, 65.5, 250.0, 1250),
            ('FAQ Chatbot', 8500, 45.2, 180.0, 2100),
            ('Sales Pitch Agent', 12000, 55.8, 220.0, 850),
            ('Content Writer Agent', 18000, 72.3, 290.0, 650),
            ('Email Personalizer Agent', 10500, 48.7, 195.0, 1800)
            ON CONFLICT DO NOTHING;
            """
            
            # Execute sample data insertions
            sample_data_queries = [
                ("Agent Logs", agent_logs_data),
                ("CRM Data", crm_data_sample),
                ("Customer Health", customer_health_data),
                ("Journey Executions", journey_executions_data),
                ("Agent Performance", agent_performance_data)
            ]
            
            for data_name, query in sample_data_queries:
                if self.db_manager.execute_query(query):
                    logger.info(f"✅ Populated sample data: {data_name}")
                else:
                    logger.warning(f"⚠️  Could not populate sample data: {data_name}")
            
            logger.info("Sample data population completed")
            return True
            
        except Exception as e:
            logger.error(f"Error populating sample data: {e}")
            return False
    
    def verify_dashboard_data(self) -> Dict[str, int]:
        """Verify that required data exists for dashboards"""
        try:
            logger.info("Verifying dashboard data availability...")
            
            if not self.db_manager.connect():
                return {}
            
            verification_queries = {
                "agent_logs": "SELECT COUNT(*) FROM agent_logs",
                "crm_data": "SELECT COUNT(*) FROM crm_data", 
                "customer_health": "SELECT COUNT(*) FROM customer_health",
                "journey_executions": "SELECT COUNT(*) FROM journey_executions",
                "agent_performance": "SELECT COUNT(*) FROM agent_performance"
            }
            
            results = {}
            for table, query in verification_queries.items():
                count = self.db_manager.fetch_one(query)
                results[table] = count[0] if count else 0
                logger.info(f"📊 {table}: {results[table]} records")
            
            return results
            
        except Exception as e:
            logger.error(f"Error verifying data: {e}")
            return {}
    
    def setup_all_dashboards(self) -> Dict[str, Optional[int]]:
        """Complete dashboard setup process"""
        try:
            logger.info("🚀 Starting complete dashboard setup...")
            
            # Step 1: Create required tables
            if not self.create_required_tables():
                logger.error("Failed to create required tables")
                return {}
            
            # Step 2: Populate sample data
            if not self.populate_sample_data():
                logger.warning("Failed to populate sample data - dashboards may be empty")
            
            # Step 3: Verify data
            data_counts = self.verify_dashboard_data()
            logger.info(f"Data verification: {data_counts}")
            
            # Step 4: Connect to Metabase
            if not self.dashboard_manager.connect():
                logger.error("Failed to connect to Metabase")
                return {}
            
            # Step 5: Create all dashboards
            dashboard_templates = [
                "agent_performance",
                "sales_pipeline", 
                "customer_health",
                "executive_summary",
                "journey_analytics"
            ]
            
            results = {}
            for template in dashboard_templates:
                dashboard_id = self.create_dashboard_from_template(template)
                results[template] = dashboard_id
                
                if dashboard_id:
                    url = self.dashboard_manager.get_dashboard_url(dashboard_id)
                    logger.info(f"✅ Created dashboard: {template} -> {url}")
                else:
                    logger.error(f"❌ Failed to create dashboard: {template}")
            
            logger.info("Dashboard setup completed!")
            return results
            
        except Exception as e:
            logger.error(f"Error in dashboard setup: {e}")
            return {}
    
    def generate_setup_report(self, results: Dict[str, Optional[int]]) -> str:
        """Generate a setup report"""
        successful = len([r for r in results.values() if r is not None])
        total = len(results)
        
        report = f"""
🎯 SIX3 Agency Dashboard Setup Report
{'=' * 50}

📊 Dashboard Creation Results:
{'-' * 30}
"""
        
        for name, dashboard_id in results.items():
            status = "✅ SUCCESS" if dashboard_id else "❌ FAILED"
            url = f" -> {self.dashboard_manager.get_dashboard_url(dashboard_id)}" if dashboard_id else ""
            report += f"{status} {name.replace('_', ' ').title()}{url}\n"
        
        report += f"""
📈 Summary:
{'-' * 30}
• Successful: {successful}/{total} dashboards
• Success Rate: {(successful/total)*100:.1f}%

🔗 Access Information:
{'-' * 30}
• Metabase URL: {self.dashboard_manager.metabase_url}
• Username: {self.dashboard_manager.metabase_user}
• Database: PostgreSQL (SIX3_Analytics)

🚀 Next Steps:
{'-' * 30}
1. Configure environment variables in .env
2. Set up automated data collection
3. Configure dashboard refresh schedules
4. Train team on dashboard usage
5. Set up automated reporting

🛠️ Troubleshooting:
{'-' * 30}
• Check Metabase connection if dashboards failed
• Verify database credentials and permissions
• Ensure all required tables exist
• Check sample data was populated correctly
"""
        
        return report

def main():
    """Main function to set up all dashboards"""
    print("🚀 SIX3 Agency Dashboard Setup")
    print("=" * 40)
    
    setup = DashboardSetup()
    
    # Run complete setup
    results = setup.setup_all_dashboards()
    
    # Generate and display report
    report = setup.generate_setup_report(results)
    print(report)
    
    # Save report to file
    with open("dashboard_setup_report.txt", "w") as f:
        f.write(report)
    
    print("\n📝 Setup report saved to: dashboard_setup_report.txt")
    return results

if __name__ == "__main__":
    main()