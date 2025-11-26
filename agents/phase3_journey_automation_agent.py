"""
Phase 3 End-to-End Journey Automation Agent

Manages complete customer journeys from first touchpoint to loyal customer.
Orchestrates cross-department workflows and tracks every step.

Key Capabilities:
- Complete journey mapping and tracking
- Cross-department handoffs
- Journey analytics and optimization
- Automated workflow triggers
- Real-time journey monitoring
- Journey performance analytics
"""

import os
import sys
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from enum import Enum
from dataclasses import dataclass, asdict
import uuid
import asyncio

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from base_agent import BaseAgent

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    print("Warning: Redis not available. Install with: pip install redis")


logger = logging.getLogger(__name__)


class JourneyStage(Enum):
    """Customer journey stages"""
    AWARENESS = "awareness"
    INTEREST = "interest"
    CONSIDERATION = "consideration"
    INTENT = "intent"
    EVALUATION = "evaluation"
    PURCHASE = "purchase"
    ONBOARDING = "onboarding"
    ADOPTION = "adoption"
    EXPANSION = "expansion"
    ADVOCACY = "advocacy"
    RETENTION = "retention"
    CHURN_RISK = "churn_risk"


class JourneyTrigger(Enum):
    """Journey automation triggers"""
    TIME_BASED = "time_based"
    BEHAVIOR_BASED = "behavior_based"
    SCORE_BASED = "score_based"
    EVENT_BASED = "event_based"
    MANUAL = "manual"


class JourneyStatus(Enum):
    """Journey execution status"""
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class JourneyStep:
    """Individual step in a customer journey"""
    id: str
    name: str
    department: str
    agent: str
    action: str
    conditions: Dict[str, Any]
    success_criteria: Dict[str, Any]
    failure_actions: List[str]
    estimated_duration: int  # minutes
    dependencies: List[str] = None
    parallel: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Journey:
    """Complete customer journey definition"""
    id: str
    name: str
    description: str
    trigger_conditions: Dict[str, Any]
    steps: List[JourneyStep]
    success_metrics: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    version: str = "1.0"
    active: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        data['steps'] = [step.to_dict() for step in self.steps]
        return data


@dataclass
class JourneyExecution:
    """Active journey execution for a customer"""
    id: str
    journey_id: str
    customer_id: str
    customer_email: str
    current_step: str
    status: JourneyStatus
    started_at: datetime
    current_step_started_at: datetime
    completed_steps: List[str]
    failed_steps: List[str]
    context_data: Dict[str, Any]
    metrics: Dict[str, Any]
    estimated_completion: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['status'] = self.status.value
        data['started_at'] = self.started_at.isoformat()
        data['current_step_started_at'] = self.current_step_started_at.isoformat()
        data['estimated_completion'] = self.estimated_completion.isoformat() if self.estimated_completion else None
        data['completed_at'] = self.completed_at.isoformat() if self.completed_at else None
        return data


class JourneyAutomationAgent(BaseAgent):
    """
    Phase 3 Journey Automation Agent
    
    Orchestrates end-to-end customer journeys across all departments
    and provides comprehensive journey analytics.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """Initialize the Journey Automation Agent"""
        
        agent_config = {
            "name": "Journey Automation Agent",
            "description": "End-to-end customer journey orchestration and automation",
            "version": "3.0",
            "capabilities": [
                "journey_mapping",
                "cross_department_orchestration",
                "journey_tracking",
                "automated_triggers",
                "journey_analytics",
                "real_time_monitoring",
                "optimization_recommendations"
            ]
        }
        
        if config:
            agent_config.update(config)
            
        super().__init__(agent_config)
        
        # Initialize Redis for real-time journey tracking
        if REDIS_AVAILABLE:
            redis_host = os.getenv('REDIS_HOST', 'localhost')
            redis_port = int(os.getenv('REDIS_PORT', '6379'))
            redis_db = int(os.getenv('REDIS_DB', '0'))
            
            try:
                self.redis_client = redis.Redis(
                    host=redis_host, 
                    port=redis_port, 
                    db=redis_db,
                    decode_responses=True
                )
                self.redis_client.ping()
            except Exception as e:
                logger.warning(f"Redis connection failed: {e}")
                self.redis_client = None
        else:
            self.redis_client = None
        
        # Initialize journey templates
        self.journey_templates = self._load_journey_templates()
        
        # Department agent mapping
        self.department_agents = {
            'marketing': ['phase2_content_writer_agent', 'phase2_social_media_agent', 'phase3_marketing_campaign_agent'],
            'sales': ['phase2_sales_pitch_agent', 'phase3_sales_strategist_agent', 'phase1_prospect_agent'],
            'customer_success': ['phase3_customer_success_agent', 'phase1_faq_chatbot'],
            'support': ['phase1_faq_chatbot', 'escalation_system'],
            'analytics': ['phase3_analytics_agent']
        }
        
        logger.info(f"Journey Automation Agent initialized")
    
    def create_journey(self, 
                      name: str,
                      description: str,
                      trigger_conditions: Dict[str, Any],
                      steps: List[Dict[str, Any]],
                      success_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new customer journey
        
        Args:
            name: Journey name
            description: Journey description
            trigger_conditions: Conditions that start this journey
            steps: List of journey steps
            success_metrics: Success criteria and KPIs
            
        Returns:
            Dict with journey creation response
        """
        try:
            journey_id = str(uuid.uuid4())
            
            # Convert step dictionaries to JourneyStep objects
            journey_steps = []
            for i, step_data in enumerate(steps):
                step = JourneyStep(
                    id=step_data.get('id', f"step_{i+1}"),
                    name=step_data['name'],
                    department=step_data['department'],
                    agent=step_data['agent'],
                    action=step_data['action'],
                    conditions=step_data.get('conditions', {}),
                    success_criteria=step_data.get('success_criteria', {}),
                    failure_actions=step_data.get('failure_actions', []),
                    estimated_duration=step_data.get('estimated_duration', 60),
                    dependencies=step_data.get('dependencies', []),
                    parallel=step_data.get('parallel', False)
                )
                journey_steps.append(step)
            
            # Create journey
            journey = Journey(
                id=journey_id,
                name=name,
                description=description,
                trigger_conditions=trigger_conditions,
                steps=journey_steps,
                success_metrics=success_metrics,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            # Store journey
            if self.redis_client:
                journey_key = f"journey:{journey_id}"
                self.redis_client.setex(
                    journey_key,
                    timedelta(days=365),  # Store for 1 year
                    json.dumps(journey.to_dict())
                )
                
                # Add to journey index
                self.redis_client.sadd("journeys:active", journey_id)
            
            # Log metrics
            self.log_metrics("journeys_created", 1)
            
            result = {
                'journey_id': journey_id,
                'name': name,
                'steps_count': len(journey_steps),
                'estimated_total_duration': sum(step.estimated_duration for step in journey_steps),
                'departments_involved': list(set(step.department for step in journey_steps)),
                'created_at': journey.created_at.isoformat()
            }
            
            logger.info(f"Created journey {journey_id}: {name}")
            
            return {
                'success': True,
                'agent': self.name,
                'data': result
            }
            
        except Exception as e:
            logger.error(f"Journey creation failed: {str(e)}")
            return {
                'success': False,
                'agent': self.name,
                'error': str(e)
            }
    
    def start_journey(self,
                     customer_id: str,
                     customer_email: str,
                     journey_id: str,
                     context_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Start a journey for a customer
        
        Args:
            customer_id: Customer identifier
            customer_email: Customer email
            journey_id: Journey to execute
            context_data: Additional context data
            
        Returns:
            Dict with journey execution response
        """
        try:
            logger.info(f"Starting journey {journey_id} for customer {customer_id}")
            
            # Load journey definition
            journey = self._load_journey(journey_id)
            if not journey:
                return {
                    'success': False,
                    'error': f'Journey {journey_id} not found'
                }
            
            # Create journey execution
            execution_id = str(uuid.uuid4())
            first_step = journey.steps[0] if journey.steps else None
            
            if not first_step:
                return {
                    'success': False,
                    'error': 'Journey has no steps defined'
                }
            
            # Calculate estimated completion time
            total_duration = sum(step.estimated_duration for step in journey.steps)
            estimated_completion = datetime.utcnow() + timedelta(minutes=total_duration)
            
            execution = JourneyExecution(
                id=execution_id,
                journey_id=journey_id,
                customer_id=customer_id,
                customer_email=customer_email,
                current_step=first_step.id,
                status=JourneyStatus.ACTIVE,
                started_at=datetime.utcnow(),
                current_step_started_at=datetime.utcnow(),
                completed_steps=[],
                failed_steps=[],
                context_data=context_data or {},
                metrics={
                    'steps_completed': 0,
                    'steps_failed': 0,
                    'total_steps': len(journey.steps)
                },
                estimated_completion=estimated_completion
            )
            
            # Store journey execution
            if self.redis_client:
                execution_key = f"journey_execution:{execution_id}"
                self.redis_client.setex(
                    execution_key,
                    timedelta(days=90),  # Store executions for 90 days
                    json.dumps(execution.to_dict())
                )
                
                # Add to customer's journey history
                customer_journeys_key = f"customer_journeys:{customer_id}"
                self.redis_client.sadd(customer_journeys_key, execution_id)
                
                # Add to active executions
                self.redis_client.sadd("executions:active", execution_id)
            
            # Execute first step
            first_step_result = self._execute_journey_step(execution, journey, first_step)
            
            # Log metrics
            self.log_metrics("journeys_started", 1)
            self.log_metrics("journey_executions_active", 1)
            
            result = {
                'execution_id': execution_id,
                'journey_id': journey_id,
                'customer_id': customer_id,
                'current_step': first_step.name,
                'estimated_completion': estimated_completion.isoformat(),
                'first_step_result': first_step_result,
                'total_steps': len(journey.steps)
            }
            
            return {
                'success': True,
                'agent': self.name,
                'data': result
            }
            
        except Exception as e:
            logger.error(f"Journey start failed: {str(e)}")
            return {
                'success': False,
                'agent': self.name,
                'error': str(e)
            }
    
    def continue_journey(self, execution_id: str, step_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Continue a journey to the next step
        
        Args:
            execution_id: Journey execution ID
            step_result: Result from the current step
            
        Returns:
            Dict with continuation response
        """
        try:
            logger.info(f"Continuing journey execution {execution_id}")
            
            # Load execution
            execution = self._load_execution(execution_id)
            if not execution:
                return {
                    'success': False,
                    'error': f'Journey execution {execution_id} not found'
                }
            
            # Load journey
            journey = self._load_journey(execution.journey_id)
            if not journey:
                return {
                    'success': False,
                    'error': f'Journey {execution.journey_id} not found'
                }
            
            # Find current step
            current_step = None
            for step in journey.steps:
                if step.id == execution.current_step:
                    current_step = step
                    break
            
            if not current_step:
                return {
                    'success': False,
                    'error': f'Current step {execution.current_step} not found'
                }
            
            # Process step result
            if step_result.get('success', False):
                # Step succeeded
                execution.completed_steps.append(current_step.id)
                execution.metrics['steps_completed'] += 1
                
                # Update context with step results
                execution.context_data.update(step_result.get('context_updates', {}))
                
                # Find next step
                next_step = self._find_next_step(journey, execution, current_step)
                
                if next_step:
                    # Continue to next step
                    execution.current_step = next_step.id
                    execution.current_step_started_at = datetime.utcnow()
                    
                    # Execute next step
                    next_step_result = self._execute_journey_step(execution, journey, next_step)
                    
                    # Update execution
                    self._update_execution(execution)
                    
                    return {
                        'success': True,
                        'status': 'continued',
                        'current_step': next_step.name,
                        'progress': f"{execution.metrics['steps_completed']}/{execution.metrics['total_steps']}",
                        'next_step_result': next_step_result
                    }
                else:
                    # Journey completed
                    execution.status = JourneyStatus.COMPLETED
                    execution.completed_at = datetime.utcnow()
                    
                    # Calculate final metrics
                    total_duration = execution.completed_at - execution.started_at
                    execution.metrics['total_duration_minutes'] = total_duration.total_seconds() / 60
                    execution.metrics['completion_rate'] = (
                        execution.metrics['steps_completed'] / execution.metrics['total_steps'] * 100
                    )
                    
                    # Update execution
                    self._update_execution(execution)
                    
                    # Remove from active executions
                    if self.redis_client:
                        self.redis_client.srem("executions:active", execution_id)
                    
                    # Log metrics
                    self.log_metrics("journeys_completed", 1)
                    self.log_metrics("journey_executions_active", -1)
                    
                    return {
                        'success': True,
                        'status': 'completed',
                        'completion_rate': execution.metrics['completion_rate'],
                        'total_duration': execution.metrics['total_duration_minutes'],
                        'completed_at': execution.completed_at.isoformat()
                    }
            else:
                # Step failed
                execution.failed_steps.append(current_step.id)
                execution.metrics['steps_failed'] += 1
                
                # Execute failure actions
                failure_results = []
                for failure_action in current_step.failure_actions:
                    failure_result = self._execute_failure_action(
                        execution, journey, current_step, failure_action, step_result
                    )
                    failure_results.append(failure_result)
                
                # Update execution
                self._update_execution(execution)
                
                return {
                    'success': True,
                    'status': 'step_failed',
                    'failed_step': current_step.name,
                    'failure_reason': step_result.get('error', 'Unknown error'),
                    'failure_actions': failure_results,
                    'can_retry': 'retry' in current_step.failure_actions
                }
            
        except Exception as e:
            logger.error(f"Journey continuation failed: {str(e)}")
            return {
                'success': False,
                'agent': self.name,
                'error': str(e)
            }
    
    def get_journey_status(self, execution_id: str) -> Dict[str, Any]:
        """
        Get current status of a journey execution
        
        Args:
            execution_id: Journey execution ID
            
        Returns:
            Dict with journey status
        """
        try:
            execution = self._load_execution(execution_id)
            if not execution:
                return {
                    'success': False,
                    'error': f'Journey execution {execution_id} not found'
                }
            
            journey = self._load_journey(execution.journey_id)
            if not journey:
                return {
                    'success': False,
                    'error': f'Journey {execution.journey_id} not found'
                }
            
            # Calculate progress
            progress_percentage = (execution.metrics['steps_completed'] / execution.metrics['total_steps']) * 100
            
            # Calculate time metrics
            now = datetime.utcnow()
            elapsed_time = now - execution.started_at
            
            # Find current step details
            current_step_name = ""
            current_step_department = ""
            for step in journey.steps:
                if step.id == execution.current_step:
                    current_step_name = step.name
                    current_step_department = step.department
                    break
            
            # Estimate remaining time
            remaining_steps = execution.metrics['total_steps'] - execution.metrics['steps_completed']
            avg_step_duration = 60  # Default 1 hour per step
            if execution.metrics['steps_completed'] > 0:
                avg_step_duration = elapsed_time.total_seconds() / 60 / execution.metrics['steps_completed']
            
            estimated_remaining = remaining_steps * avg_step_duration
            
            result = {
                'execution_id': execution_id,
                'journey_name': journey.name,
                'customer_id': execution.customer_id,
                'status': execution.status.value,
                'progress': {
                    'completed_steps': execution.metrics['steps_completed'],
                    'total_steps': execution.metrics['total_steps'],
                    'percentage': round(progress_percentage, 1),
                    'failed_steps': execution.metrics['steps_failed']
                },
                'current_step': {
                    'name': current_step_name,
                    'department': current_step_department,
                    'started_at': execution.current_step_started_at.isoformat()
                },
                'timing': {
                    'started_at': execution.started_at.isoformat(),
                    'elapsed_minutes': round(elapsed_time.total_seconds() / 60, 1),
                    'estimated_remaining_minutes': round(estimated_remaining, 1),
                    'estimated_completion': execution.estimated_completion.isoformat() if execution.estimated_completion else None
                },
                'context_data': execution.context_data,
                'metrics': execution.metrics
            }
            
            if execution.status == JourneyStatus.COMPLETED:
                result['completed_at'] = execution.completed_at.isoformat()
                result['total_duration'] = execution.metrics.get('total_duration_minutes', 0)
                result['completion_rate'] = execution.metrics.get('completion_rate', 0)
            
            return {
                'success': True,
                'agent': self.name,
                'data': result
            }
            
        except Exception as e:
            logger.error(f"Get journey status failed: {str(e)}")
            return {
                'success': False,
                'agent': self.name,
                'error': str(e)
            }
    
    def get_customer_journey_analytics(self, customer_id: str) -> Dict[str, Any]:
        """
        Get comprehensive journey analytics for a customer
        
        Args:
            customer_id: Customer identifier
            
        Returns:
            Dict with customer journey analytics
        """
        try:
            if not self.redis_client:
                return {
                    'success': False,
                    'error': 'Redis not available for analytics'
                }
            
            # Get customer's journey history
            customer_journeys_key = f"customer_journeys:{customer_id}"
            execution_ids = self.redis_client.smembers(customer_journeys_key)
            
            if not execution_ids:
                return {
                    'success': True,
                    'data': {
                        'customer_id': customer_id,
                        'total_journeys': 0,
                        'message': 'No journeys found for this customer'
                    }
                }
            
            # Load all executions
            executions = []
            for execution_id in execution_ids:
                execution = self._load_execution(execution_id)
                if execution:
                    executions.append(execution)
            
            # Calculate analytics
            total_journeys = len(executions)
            completed_journeys = len([e for e in executions if e.status == JourneyStatus.COMPLETED])
            active_journeys = len([e for e in executions if e.status == JourneyStatus.ACTIVE])
            failed_journeys = len([e for e in executions if e.status == JourneyStatus.FAILED])
            
            # Calculate timing metrics
            total_duration = 0
            completion_rates = []
            
            for execution in executions:
                if execution.status == JourneyStatus.COMPLETED:
                    duration = execution.completed_at - execution.started_at
                    total_duration += duration.total_seconds() / 60
                    completion_rates.append(execution.metrics.get('completion_rate', 0))
            
            avg_completion_time = total_duration / completed_journeys if completed_journeys > 0 else 0
            avg_completion_rate = sum(completion_rates) / len(completion_rates) if completion_rates else 0
            
            # Journey stage analysis
            current_stages = []
            for execution in executions:
                if execution.status == JourneyStatus.ACTIVE:
                    journey = self._load_journey(execution.journey_id)
                    if journey:
                        for step in journey.steps:
                            if step.id == execution.current_step:
                                current_stages.append(step.department)
                                break
            
            # Department interaction analysis
            department_interactions = {}
            for execution in executions:
                journey = self._load_journey(execution.journey_id)
                if journey:
                    for step_id in execution.completed_steps:
                        for step in journey.steps:
                            if step.id == step_id:
                                dept = step.department
                                department_interactions[dept] = department_interactions.get(dept, 0) + 1
                                break
            
            result = {
                'customer_id': customer_id,
                'summary': {
                    'total_journeys': total_journeys,
                    'completed_journeys': completed_journeys,
                    'active_journeys': active_journeys,
                    'failed_journeys': failed_journeys,
                    'success_rate': round((completed_journeys / total_journeys) * 100, 1) if total_journeys > 0 else 0
                },
                'timing_metrics': {
                    'avg_completion_time_minutes': round(avg_completion_time, 1),
                    'avg_completion_rate': round(avg_completion_rate, 1),
                    'fastest_completion': min([
                        (e.completed_at - e.started_at).total_seconds() / 60
                        for e in executions if e.status == JourneyStatus.COMPLETED
                    ]) if completed_journeys > 0 else 0
                },
                'current_status': {
                    'active_journeys': active_journeys,
                    'current_stages': current_stages
                },
                'department_interactions': department_interactions,
                'journey_history': [
                    {
                        'execution_id': e.id,
                        'journey_id': e.journey_id,
                        'status': e.status.value,
                        'started_at': e.started_at.isoformat(),
                        'completed_at': e.completed_at.isoformat() if e.completed_at else None,
                        'steps_completed': e.metrics['steps_completed'],
                        'completion_rate': e.metrics.get('completion_rate', 0)
                    }
                    for e in sorted(executions, key=lambda x: x.started_at, reverse=True)
                ],
                'recommendations': self._generate_customer_recommendations(executions)
            }
            
            return {
                'success': True,
                'agent': self.name,
                'data': result
            }
            
        except Exception as e:
            logger.error(f"Customer journey analytics failed: {str(e)}")
            return {
                'success': False,
                'agent': self.name,
                'error': str(e)
            }
    
    def get_journey_performance_analytics(self, journey_id: str = None) -> Dict[str, Any]:
        """
        Get journey performance analytics across all customers
        
        Args:
            journey_id: Specific journey ID (optional, analyzes all if None)
            
        Returns:
            Dict with journey performance analytics
        """
        try:
            if not self.redis_client:
                return {
                    'success': False,
                    'error': 'Redis not available for analytics'
                }
            
            # Get all active journeys if no specific journey requested
            if journey_id:
                journey_ids = [journey_id]
            else:
                journey_ids = list(self.redis_client.smembers("journeys:active"))
            
            analytics_data = {}
            
            for jid in journey_ids:
                journey = self._load_journey(jid)
                if not journey:
                    continue
                
                # Get all executions for this journey
                all_executions = list(self.redis_client.smembers("executions:active"))
                all_executions.extend(self._get_completed_executions(jid))
                
                journey_executions = []
                for execution_id in all_executions:
                    execution = self._load_execution(execution_id)
                    if execution and execution.journey_id == jid:
                        journey_executions.append(execution)
                
                if not journey_executions:
                    analytics_data[jid] = {
                        'journey_name': journey.name,
                        'total_executions': 0,
                        'message': 'No executions found for this journey'
                    }
                    continue
                
                # Calculate journey-specific analytics
                total_executions = len(journey_executions)
                completed = len([e for e in journey_executions if e.status == JourneyStatus.COMPLETED])
                active = len([e for e in journey_executions if e.status == JourneyStatus.ACTIVE])
                failed = len([e for e in journey_executions if e.status == JourneyStatus.FAILED])
                
                # Performance metrics
                completion_rates = [e.metrics.get('completion_rate', 0) for e in journey_executions if e.status == JourneyStatus.COMPLETED]
                avg_completion_rate = sum(completion_rates) / len(completion_rates) if completion_rates else 0
                
                # Timing analysis
                completion_times = []
                for execution in journey_executions:
                    if execution.status == JourneyStatus.COMPLETED:
                        duration = execution.completed_at - execution.started_at
                        completion_times.append(duration.total_seconds() / 60)
                
                avg_completion_time = sum(completion_times) / len(completion_times) if completion_times else 0
                
                # Bottleneck analysis
                step_performance = {}
                for execution in journey_executions:
                    for failed_step in execution.failed_steps:
                        step_performance[failed_step] = step_performance.get(failed_step, 0) + 1
                
                analytics_data[jid] = {
                    'journey_name': journey.name,
                    'journey_description': journey.description,
                    'total_executions': total_executions,
                    'status_breakdown': {
                        'completed': completed,
                        'active': active,
                        'failed': failed,
                        'success_rate': round((completed / total_executions) * 100, 1) if total_executions > 0 else 0
                    },
                    'performance_metrics': {
                        'avg_completion_rate': round(avg_completion_rate, 1),
                        'avg_completion_time_minutes': round(avg_completion_time, 1),
                        'fastest_completion_minutes': min(completion_times) if completion_times else 0,
                        'slowest_completion_minutes': max(completion_times) if completion_times else 0
                    },
                    'bottlenecks': step_performance,
                    'departments_involved': list(set(step.department for step in journey.steps)),
                    'total_steps': len(journey.steps),
                    'created_at': journey.created_at.isoformat()
                }
            
            # Generate overall insights
            if len(analytics_data) > 1:
                # Cross-journey insights
                all_success_rates = [data['status_breakdown']['success_rate'] for data in analytics_data.values()]
                all_completion_times = [data['performance_metrics']['avg_completion_time_minutes'] for data in analytics_data.values()]
                
                overall_insights = {
                    'total_journeys_analyzed': len(analytics_data),
                    'avg_success_rate_across_journeys': round(sum(all_success_rates) / len(all_success_rates), 1),
                    'avg_completion_time_across_journeys': round(sum(all_completion_times) / len(all_completion_times), 1),
                    'best_performing_journey': max(analytics_data.items(), key=lambda x: x[1]['status_breakdown']['success_rate'])[0],
                    'recommendations': self._generate_journey_optimization_recommendations(analytics_data)
                }
            else:
                overall_insights = {}
            
            result = {
                'journey_analytics': analytics_data,
                'overall_insights': overall_insights,
                'generated_at': datetime.utcnow().isoformat()
            }
            
            return {
                'success': True,
                'agent': self.name,
                'data': result
            }
            
        except Exception as e:
            logger.error(f"Journey performance analytics failed: {str(e)}")
            return {
                'success': False,
                'agent': self.name,
                'error': str(e)
            }
    
    # Helper methods
    
    def _load_journey_templates(self) -> Dict[str, Journey]:
        """Load pre-built journey templates"""
        templates = {}
        
        # B2B Sales Journey Template
        b2b_sales_steps = [
            JourneyStep(
                id="lead_qualification",
                name="Lead Qualification",
                department="sales",
                agent="phase1_prospect_agent",
                action="qualify_lead",
                conditions={"min_score": 70},
                success_criteria={"qualification_status": "qualified"},
                failure_actions=["nurture_sequence"],
                estimated_duration=30
            ),
            JourneyStep(
                id="sales_pitch",
                name="Personalized Sales Pitch",
                department="sales",
                agent="phase2_sales_pitch_agent",
                action="generate_pitch",
                conditions={"qualification_status": "qualified"},
                success_criteria={"engagement_score": ">= 8"},
                failure_actions=["revise_pitch", "human_escalation"],
                estimated_duration=60
            ),
            JourneyStep(
                id="demo_scheduling",
                name="Demo Scheduling",
                department="sales",
                agent="phase3_sales_strategist_agent",
                action="schedule_demo",
                conditions={"engagement_score": ">= 8"},
                success_criteria={"demo_scheduled": True},
                failure_actions=["follow_up_sequence"],
                estimated_duration=120
            ),
            JourneyStep(
                id="proposal_generation",
                name="Proposal Generation",
                department="sales",
                agent="phase3_sales_strategist_agent",
                action="generate_proposal",
                conditions={"demo_completed": True},
                success_criteria={"proposal_sent": True},
                failure_actions=["refine_requirements"],
                estimated_duration=240
            ),
            JourneyStep(
                id="onboarding",
                name="Customer Onboarding",
                department="customer_success",
                agent="phase3_customer_success_agent",
                action="initiate_onboarding",
                conditions={"deal_closed": True},
                success_criteria={"onboarding_completed": True},
                failure_actions=["escalate_onboarding"],
                estimated_duration=2880  # 48 hours
            )
        ]
        
        templates["b2b_sales"] = Journey(
            id="b2b_sales_template",
            name="B2B Sales Journey",
            description="Complete B2B sales process from lead to customer",
            trigger_conditions={"lead_source": "any", "lead_type": "b2b"},
            steps=b2b_sales_steps,
            success_metrics={"conversion_rate": 0.15, "avg_deal_size": 25000},
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Content Marketing Journey Template
        content_marketing_steps = [
            JourneyStep(
                id="content_creation",
                name="Content Creation",
                department="marketing",
                agent="phase2_content_writer_agent",
                action="create_content",
                conditions={"topic_approved": True},
                success_criteria={"content_quality_score": ">= 8"},
                failure_actions=["revise_content"],
                estimated_duration=240
            ),
            JourneyStep(
                id="seo_optimization",
                name="SEO Optimization",
                department="marketing",
                agent="phase2_seo_optimizer_agent",
                action="optimize_content",
                conditions={"content_created": True},
                success_criteria={"seo_score": ">= 80"},
                failure_actions=["re_optimize"],
                estimated_duration=60
            ),
            JourneyStep(
                id="social_distribution",
                name="Social Media Distribution",
                department="marketing",
                agent="phase2_social_media_agent",
                action="distribute_content",
                conditions={"content_optimized": True},
                success_criteria={"posts_published": True},
                failure_actions=["schedule_retry"],
                estimated_duration=30,
                parallel=True
            ),
            JourneyStep(
                id="performance_tracking",
                name="Performance Tracking",
                department="analytics",
                agent="phase3_analytics_agent",
                action="track_content_performance",
                conditions={"content_published": True},
                success_criteria={"analytics_setup": True},
                failure_actions=["setup_tracking"],
                estimated_duration=15
            )
        ]
        
        templates["content_marketing"] = Journey(
            id="content_marketing_template",
            name="Content Marketing Journey",
            description="End-to-end content creation, optimization, and distribution",
            trigger_conditions={"content_request": True},
            steps=content_marketing_steps,
            success_metrics={"engagement_rate": 0.05, "conversion_rate": 0.02},
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        return templates
    
    def _load_journey(self, journey_id: str) -> Optional[Journey]:
        """Load journey from storage"""
        if not self.redis_client:
            # Check templates
            for template in self.journey_templates.values():
                if template.id == journey_id:
                    return template
            return None
        
        try:
            journey_key = f"journey:{journey_id}"
            journey_data = self.redis_client.get(journey_key)
            
            if journey_data:
                data = json.loads(journey_data)
                
                # Convert steps back to JourneyStep objects
                steps = []
                for step_data in data['steps']:
                    step = JourneyStep(**step_data)
                    steps.append(step)
                
                data['steps'] = steps
                data['created_at'] = datetime.fromisoformat(data['created_at'])
                data['updated_at'] = datetime.fromisoformat(data['updated_at'])
                
                return Journey(**data)
            
            # Check templates if not found in Redis
            for template in self.journey_templates.values():
                if template.id == journey_id:
                    return template
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to load journey {journey_id}: {e}")
            return None
    
    def _load_execution(self, execution_id: str) -> Optional[JourneyExecution]:
        """Load journey execution from storage"""
        if not self.redis_client:
            return None
        
        try:
            execution_key = f"journey_execution:{execution_id}"
            execution_data = self.redis_client.get(execution_key)
            
            if execution_data:
                data = json.loads(execution_data)
                
                # Convert datetime strings back to datetime objects
                data['status'] = JourneyStatus(data['status'])
                data['started_at'] = datetime.fromisoformat(data['started_at'])
                data['current_step_started_at'] = datetime.fromisoformat(data['current_step_started_at'])
                
                if data['estimated_completion']:
                    data['estimated_completion'] = datetime.fromisoformat(data['estimated_completion'])
                if data['completed_at']:
                    data['completed_at'] = datetime.fromisoformat(data['completed_at'])
                
                return JourneyExecution(**data)
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to load execution {execution_id}: {e}")
            return None
    
    def _update_execution(self, execution: JourneyExecution):
        """Update journey execution in storage"""
        if not self.redis_client:
            return
        
        try:
            execution_key = f"journey_execution:{execution.id}"
            self.redis_client.setex(
                execution_key,
                timedelta(days=90),
                json.dumps(execution.to_dict())
            )
        except Exception as e:
            logger.error(f"Failed to update execution {execution.id}: {e}")
    
    def _execute_journey_step(self, execution: JourneyExecution, journey: Journey, step: JourneyStep) -> Dict[str, Any]:
        """Execute a single journey step"""
        try:
            logger.info(f"Executing step {step.name} for execution {execution.id}")
            
            # Check step conditions
            if not self._check_step_conditions(step, execution):
                return {
                    'success': False,
                    'error': 'Step conditions not met',
                    'conditions': step.conditions
                }
            
            # Find agent in department
            if step.agent not in self.department_agents.get(step.department, []):
                logger.warning(f"Agent {step.agent} not found in department {step.department}")
            
            # Simulate agent execution (in real implementation, this would call the actual agent)
            agent_result = self._simulate_agent_execution(step, execution)
            
            # Update step timing
            execution.current_step_started_at = datetime.utcnow()
            
            return agent_result
            
        except Exception as e:
            logger.error(f"Step execution failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _simulate_agent_execution(self, step: JourneyStep, execution: JourneyExecution) -> Dict[str, Any]:
        """Simulate agent execution (replace with real agent calls in production)"""
        
        # Simulate different success rates based on step type
        import random
        
        success_rates = {
            'qualify_lead': 0.8,
            'generate_pitch': 0.9,
            'schedule_demo': 0.7,
            'generate_proposal': 0.85,
            'initiate_onboarding': 0.95,
            'create_content': 0.9,
            'optimize_content': 0.95,
            'distribute_content': 0.85,
            'track_content_performance': 0.98
        }
        
        success_rate = success_rates.get(step.action, 0.8)
        is_success = random.random() < success_rate
        
        if is_success:
            # Generate realistic context updates based on action
            context_updates = {}
            
            if step.action == 'qualify_lead':
                context_updates = {
                    'qualification_score': random.randint(70, 95),
                    'qualification_status': 'qualified',
                    'lead_temperature': 'hot'
                }
            elif step.action == 'generate_pitch':
                context_updates = {
                    'pitch_sent': True,
                    'engagement_score': random.randint(8, 10),
                    'pitch_type': 'personalized'
                }
            elif step.action == 'schedule_demo':
                context_updates = {
                    'demo_scheduled': True,
                    'demo_date': (datetime.utcnow() + timedelta(days=random.randint(1, 7))).isoformat()
                }
            
            return {
                'success': True,
                'step_id': step.id,
                'step_name': step.name,
                'agent': step.agent,
                'execution_time_minutes': random.randint(15, step.estimated_duration),
                'context_updates': context_updates,
                'message': f'Step {step.name} completed successfully'
            }
        else:
            return {
                'success': False,
                'step_id': step.id,
                'step_name': step.name,
                'agent': step.agent,
                'error': f'Step {step.name} failed during execution',
                'error_code': 'EXECUTION_FAILED'
            }
    
    def _check_step_conditions(self, step: JourneyStep, execution: JourneyExecution) -> bool:
        """Check if step conditions are met"""
        for condition_key, condition_value in step.conditions.items():
            context_value = execution.context_data.get(condition_key)
            
            if isinstance(condition_value, str):
                if context_value != condition_value:
                    return False
            elif isinstance(condition_value, (int, float)):
                if context_value is None or context_value < condition_value:
                    return False
        
        return True
    
    def _find_next_step(self, journey: Journey, execution: JourneyExecution, current_step: JourneyStep) -> Optional[JourneyStep]:
        """Find the next step in the journey"""
        # Simple sequential execution (can be enhanced with complex routing logic)
        current_index = -1
        for i, step in enumerate(journey.steps):
            if step.id == current_step.id:
                current_index = i
                break
        
        if current_index >= 0 and current_index + 1 < len(journey.steps):
            return journey.steps[current_index + 1]
        
        return None
    
    def _execute_failure_action(self, execution: JourneyExecution, journey: Journey, 
                              failed_step: JourneyStep, action: str, step_result: Dict[str, Any]) -> Dict[str, Any]:
        """Execute failure action for a failed step"""
        try:
            if action == 'retry':
                # Schedule retry
                return {
                    'action': 'retry',
                    'scheduled_at': (datetime.utcnow() + timedelta(minutes=30)).isoformat(),
                    'message': 'Step scheduled for retry in 30 minutes'
                }
            elif action == 'human_escalation':
                # Trigger human escalation
                return {
                    'action': 'human_escalation',
                    'escalated_at': datetime.utcnow().isoformat(),
                    'escalation_reason': step_result.get('error', 'Step failed'),
                    'message': 'Case escalated to human agent'
                }
            elif action == 'nurture_sequence':
                # Start nurture sequence
                return {
                    'action': 'nurture_sequence',
                    'sequence_started': True,
                    'message': 'Customer added to nurture sequence'
                }
            elif action == 'alternative_path':
                # Take alternative path
                return {
                    'action': 'alternative_path',
                    'path_taken': True,
                    'message': 'Alternative workflow path initiated'
                }
            else:
                return {
                    'action': action,
                    'message': f'Failure action {action} executed'
                }
                
        except Exception as e:
            return {
                'action': action,
                'error': str(e),
                'message': f'Failure action {action} failed to execute'
            }
    
    def _get_completed_executions(self, journey_id: str) -> List[str]:
        """Get completed execution IDs for a journey (simplified implementation)"""
        # In a real implementation, this would query a database or search Redis keys
        if not self.redis_client:
            return []
        
        try:
            # This is a simplified approach - in production, you'd have better indexing
            all_keys = self.redis_client.keys("journey_execution:*")
            execution_ids = []
            
            for key in all_keys:
                execution_data = self.redis_client.get(key)
                if execution_data:
                    data = json.loads(execution_data)
                    if (data.get('journey_id') == journey_id and 
                        data.get('status') in ['completed', 'failed']):
                        execution_ids.append(data['id'])
            
            return execution_ids
            
        except Exception as e:
            logger.error(f"Failed to get completed executions: {e}")
            return []
    
    def _generate_customer_recommendations(self, executions: List[JourneyExecution]) -> List[str]:
        """Generate recommendations based on customer journey history"""
        recommendations = []
        
        # Analyze failure patterns
        failed_steps = []
        for execution in executions:
            failed_steps.extend(execution.failed_steps)
        
        if failed_steps:
            from collections import Counter
            most_common_failures = Counter(failed_steps).most_common(3)
            for step, count in most_common_failures:
                recommendations.append(f"Address recurring failure in step '{step}' (failed {count} times)")
        
        # Analyze completion rates
        completion_rates = [e.metrics.get('completion_rate', 0) for e in executions if e.status == JourneyStatus.COMPLETED]
        if completion_rates:
            avg_completion = sum(completion_rates) / len(completion_rates)
            if avg_completion < 80:
                recommendations.append("Consider journey optimization - completion rate below 80%")
        
        # Analyze timing
        active_executions = [e for e in executions if e.status == JourneyStatus.ACTIVE]
        for execution in active_executions:
            elapsed = datetime.utcnow() - execution.started_at
            if elapsed.total_seconds() > 7 * 24 * 60 * 60:  # 7 days
                recommendations.append("Long-running journey detected - consider intervention")
        
        return recommendations[:5]  # Top 5 recommendations
    
    def _generate_journey_optimization_recommendations(self, analytics_data: Dict[str, Any]) -> List[str]:
        """Generate journey optimization recommendations"""
        recommendations = []
        
        # Analyze success rates across journeys
        success_rates = [data['status_breakdown']['success_rate'] for data in analytics_data.values()]
        if success_rates:
            avg_success_rate = sum(success_rates) / len(success_rates)
            if avg_success_rate < 70:
                recommendations.append("Overall journey success rate is below 70% - review journey design")
        
        # Find bottlenecks
        all_bottlenecks = {}
        for journey_data in analytics_data.values():
            for step, failure_count in journey_data.get('bottlenecks', {}).items():
                all_bottlenecks[step] = all_bottlenecks.get(step, 0) + failure_count
        
        if all_bottlenecks:
            worst_bottleneck = max(all_bottlenecks.items(), key=lambda x: x[1])
            recommendations.append(f"Address major bottleneck in step '{worst_bottleneck[0]}' ({worst_bottleneck[1]} failures)")
        
        # Analyze completion times
        completion_times = [data['performance_metrics']['avg_completion_time_minutes'] for data in analytics_data.values()]
        if completion_times:
            avg_time = sum(completion_times) / len(completion_times)
            max_time = max(completion_times)
            if max_time > avg_time * 2:
                recommendations.append("Some journeys take significantly longer than others - investigate delays")
        
        return recommendations[:5]  # Top 5 recommendations


def test_journey_automation():
    """Test the Journey Automation Agent"""
    print("Testing Journey Automation Agent...")
    
    # Initialize agent
    agent = JourneyAutomationAgent()
    
    # Test journey creation
    print("\n1. Testing journey creation...")
    
    test_journey_steps = [
        {
            'name': 'Lead Qualification',
            'department': 'sales',
            'agent': 'phase1_prospect_agent',
            'action': 'qualify_lead',
            'conditions': {'lead_source': 'website'},
            'success_criteria': {'qualification_score': '>= 70'},
            'failure_actions': ['nurture_sequence'],
            'estimated_duration': 30
        },
        {
            'name': 'Sales Outreach',
            'department': 'sales',
            'agent': 'phase2_sales_pitch_agent',
            'action': 'generate_pitch',
            'conditions': {'qualification_score': '>= 70'},
            'success_criteria': {'engagement_score': '>= 8'},
            'failure_actions': ['human_escalation'],
            'estimated_duration': 60
        }
    ]
    
    journey_result = agent.create_journey(
        name="Test B2B Journey",
        description="Test journey for validation",
        trigger_conditions={"lead_type": "b2b"},
        steps=test_journey_steps,
        success_metrics={"conversion_rate": 0.2}
    )
    
    print(f"Journey creation: {'✅' if journey_result['success'] else '❌'}")
    if journey_result['success']:
        journey_id = journey_result['data']['journey_id']
        print(f"Created journey: {journey_id}")
        
        # Test journey start
        print("\n2. Testing journey execution...")
        start_result = agent.start_journey(
            customer_id="test_customer_123",
            customer_email="test@example.com",
            journey_id=journey_id,
            context_data={"lead_source": "website", "company": "Test Corp"}
        )
        
        print(f"Journey start: {'✅' if start_result['success'] else '❌'}")
        if start_result['success']:
            execution_id = start_result['data']['execution_id']
            print(f"Started execution: {execution_id}")
            
            # Test journey status
            print("\n3. Testing journey status...")
            status_result = agent.get_journey_status(execution_id)
            print(f"Status check: {'✅' if status_result['success'] else '❌'}")
            if status_result['success']:
                print(f"Current step: {status_result['data']['current_step']['name']}")
                print(f"Progress: {status_result['data']['progress']['percentage']}%")
    
    # Test journey templates
    print("\n4. Testing journey templates...")
    b2b_template = agent.journey_templates.get('b2b_sales')
    if b2b_template:
        print(f"✅ B2B template loaded: {len(b2b_template.steps)} steps")
    
    content_template = agent.journey_templates.get('content_marketing')
    if content_template:
        print(f"✅ Content template loaded: {len(content_template.steps)} steps")
    
    print("\nJourney Automation Agent testing completed!")


if __name__ == "__main__":
    test_journey_automation()