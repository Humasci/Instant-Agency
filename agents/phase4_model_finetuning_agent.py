#!/usr/bin/env python3
"""
Model Fine-Tuning Agent with LoRA for SIX3 Agency
Handles training data collection, LoRA fine-tuning, and A/B testing of custom models.
"""

import os
import sys
import json
import logging
import torch
import numpy as np
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import uuid
import asyncio
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.base_agent import BaseAgent

# Import fine-tuning libraries
try:
    from transformers import (
        AutoTokenizer, 
        AutoModelForCausalLM,
        TrainingArguments,
        Trainer,
        DataCollatorForLanguageModeling
    )
    from peft import LoraConfig, get_peft_model, TaskType, PeftModel
    from datasets import Dataset
    import wandb
    FINETUNING_AVAILABLE = True
except ImportError:
    logging.warning("Fine-tuning libraries not installed. Install with: pip install transformers peft datasets wandb")
    FINETUNING_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TrainingData:
    """Training data sample"""
    input_text: str
    target_text: str
    category: str
    source: str
    quality_score: float = 1.0
    created_at: datetime = None

@dataclass
class FineTuningConfig:
    """Fine-tuning configuration"""
    model_name: str
    task_type: str
    lora_rank: int = 16
    lora_alpha: int = 32
    lora_dropout: float = 0.1
    target_modules: List[str] = None
    learning_rate: float = 1e-4
    num_epochs: int = 3
    batch_size: int = 4
    gradient_accumulation_steps: int = 4
    warmup_steps: int = 100
    max_length: int = 512

@dataclass
class FineTuningJob:
    """Fine-tuning job tracking"""
    job_id: str
    model_name: str
    config: FineTuningConfig
    status: str  # pending, running, completed, failed
    training_data_count: int
    started_at: datetime = None
    completed_at: datetime = None
    metrics: Dict[str, float] = None
    model_path: str = None
    error_message: str = None

@dataclass
class ModelEvaluation:
    """Model evaluation results"""
    model_id: str
    evaluation_type: str
    metrics: Dict[str, float]
    test_samples: List[Dict]
    comparison_baseline: str = None
    evaluation_date: datetime = None

@dataclass
class ABTestResult:
    """A/B test results for model comparison"""
    test_id: str
    model_a: str
    model_b: str
    metric: str
    winner: str
    confidence: float
    sample_size: int
    results: Dict[str, Any]

class ModelFineTuningAgent(BaseAgent):
    """
    Advanced model fine-tuning agent with LoRA and A/B testing capabilities.
    Handles the complete lifecycle from data collection to model deployment.
    """
    
    def __init__(self):
        super().__init__("ModelFineTuning")
        
        # Setup directories
        self.models_dir = Path("models")
        self.data_dir = Path("training_data")
        self.experiments_dir = Path("experiments")
        
        for directory in [self.models_dir, self.data_dir, self.experiments_dir]:
            directory.mkdir(exist_ok=True)
        
        # Training data storage
        self.training_data: List[TrainingData] = []
        self.fine_tuning_jobs: Dict[str, FineTuningJob] = {}
        self.model_evaluations: Dict[str, ModelEvaluation] = {}
        self.ab_tests: Dict[str, ABTestResult] = {}
        
        # Supported model configurations
        self.model_configs = {
            "sales_agent": {
                "base_model": "microsoft/DialoGPT-medium",
                "task_type": TaskType.CAUSAL_LM if FINETUNING_AVAILABLE else "causal_lm",
                "target_modules": ["c_attn", "c_proj"],
                "categories": ["sales_pitch", "objection_handling", "discovery_questions"]
            },
            "content_writer": {
                "base_model": "gpt2-medium",
                "task_type": TaskType.CAUSAL_LM if FINETUNING_AVAILABLE else "causal_lm",
                "target_modules": ["c_attn", "c_proj"],
                "categories": ["blog_content", "social_media", "email_copy"]
            },
            "customer_support": {
                "base_model": "microsoft/DialoGPT-small",
                "task_type": TaskType.CAUSAL_LM if FINETUNING_AVAILABLE else "causal_lm",
                "target_modules": ["c_attn", "c_proj"],
                "categories": ["support_responses", "troubleshooting", "escalation"]
            }
        }
        
        logger.info(f"Model Fine-Tuning Agent initialized. LoRA available: {FINETUNING_AVAILABLE}")
    
    def collect_training_data(self, agent_logs: List[Dict], 
                            quality_threshold: float = 0.7) -> Dict[str, Any]:
        """
        Collect and process training data from agent interactions.
        
        Args:
            agent_logs: List of agent interaction logs
            quality_threshold: Minimum quality score for inclusion
            
        Returns:
            Dict with data collection results
        """
        try:
            collected_data = []
            
            for log in agent_logs:
                # Extract relevant data
                if (log.get('status') == 'success' and 
                    log.get('user_feedback', {}).get('rating', 0) >= quality_threshold * 5):
                    
                    training_sample = TrainingData(
                        input_text=log.get('input_message', ''),
                        target_text=log.get('agent_response', ''),
                        category=log.get('agent_name', 'general'),
                        source='agent_logs',
                        quality_score=log.get('user_feedback', {}).get('rating', 0) / 5.0,
                        created_at=datetime.fromisoformat(log.get('created_at', datetime.now().isoformat()))
                    )
                    
                    collected_data.append(training_sample)
            
            # Add to training data collection
            self.training_data.extend(collected_data)
            
            # Save to file
            self._save_training_data(collected_data)
            
            # Generate statistics
            stats = self._generate_data_stats(collected_data)
            
            result = {
                "collected_samples": len(collected_data),
                "total_samples": len(self.training_data),
                "categories": stats["categories"],
                "quality_distribution": stats["quality_distribution"],
                "data_sources": stats["sources"]
            }
            
            self.log_interaction("data_collection", {
                "samples_collected": len(collected_data),
                "quality_threshold": quality_threshold
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Error collecting training data: {e}")
            return {"error": f"Data collection failed: {e}"}
    
    def create_fine_tuning_job(self, model_type: str, 
                             custom_config: Dict = None) -> Dict[str, Any]:
        """
        Create a fine-tuning job with LoRA configuration.
        
        Args:
            model_type: Type of model to fine-tune (sales_agent, content_writer, etc.)
            custom_config: Custom configuration overrides
            
        Returns:
            Dict with job creation results
        """
        try:
            if model_type not in self.model_configs:
                raise ValueError(f"Unsupported model type: {model_type}")
            
            # Generate job ID
            job_id = f"ft_{model_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}"
            
            # Get base configuration
            base_config = self.model_configs[model_type]
            
            # Create LoRA configuration
            lora_config = FineTuningConfig(
                model_name=base_config["base_model"],
                task_type=base_config["task_type"],
                target_modules=base_config["target_modules"]
            )
            
            # Apply custom overrides
            if custom_config:
                for key, value in custom_config.items():
                    if hasattr(lora_config, key):
                        setattr(lora_config, key, value)
            
            # Filter training data for this model type
            relevant_categories = base_config["categories"]
            training_data = [
                data for data in self.training_data 
                if any(cat in data.category.lower() for cat in relevant_categories)
            ]
            
            if len(training_data) < 50:
                raise ValueError(f"Insufficient training data: {len(training_data)} samples (minimum: 50)")
            
            # Create job
            job = FineTuningJob(
                job_id=job_id,
                model_name=model_type,
                config=lora_config,
                status="pending",
                training_data_count=len(training_data)
            )
            
            self.fine_tuning_jobs[job_id] = job
            
            # Save job configuration
            self._save_job_config(job)
            
            result = {
                "job_id": job_id,
                "model_type": model_type,
                "training_samples": len(training_data),
                "config": asdict(lora_config),
                "status": "created",
                "estimated_duration_hours": self._estimate_training_time(len(training_data))
            }
            
            self.log_interaction("job_creation", {
                "job_id": job_id,
                "model_type": model_type,
                "training_samples": len(training_data)
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Error creating fine-tuning job: {e}")
            return {"error": f"Job creation failed: {e}"}
    
    async def execute_fine_tuning(self, job_id: str) -> Dict[str, Any]:
        """
        Execute fine-tuning with LoRA.
        
        Args:
            job_id: ID of the fine-tuning job
            
        Returns:
            Dict with execution results
        """
        try:
            if job_id not in self.fine_tuning_jobs:
                raise ValueError(f"Job not found: {job_id}")
            
            job = self.fine_tuning_jobs[job_id]
            
            if not FINETUNING_AVAILABLE:
                # Simulate fine-tuning
                return await self._simulate_fine_tuning(job)
            
            # Update job status
            job.status = "running"
            job.started_at = datetime.now()
            
            # Load base model and tokenizer
            logger.info(f"Loading base model: {job.config.model_name}")
            tokenizer = AutoTokenizer.from_pretrained(job.config.model_name)
            model = AutoModelForCausalLM.from_pretrained(job.config.model_name)
            
            # Setup LoRA configuration
            lora_config = LoraConfig(
                task_type=job.config.task_type,
                r=job.config.lora_rank,
                lora_alpha=job.config.lora_alpha,
                lora_dropout=job.config.lora_dropout,
                target_modules=job.config.target_modules
            )
            
            # Apply LoRA to model
            model = get_peft_model(model, lora_config)
            
            # Prepare training data
            train_dataset = self._prepare_training_dataset(job, tokenizer)
            
            # Training arguments
            training_args = TrainingArguments(
                output_dir=str(self.experiments_dir / job_id),
                overwrite_output_dir=True,
                num_train_epochs=job.config.num_epochs,
                per_device_train_batch_size=job.config.batch_size,
                gradient_accumulation_steps=job.config.gradient_accumulation_steps,
                warmup_steps=job.config.warmup_steps,
                learning_rate=job.config.learning_rate,
                logging_steps=10,
                save_steps=100,
                evaluation_strategy="steps",
                eval_steps=50,
                save_total_limit=2,
                prediction_loss_only=True,
                report_to="wandb" if os.getenv("WANDB_API_KEY") else None,
                run_name=f"six3_{job.model_name}_{job_id}"
            )
            
            # Data collator
            data_collator = DataCollatorForLanguageModeling(
                tokenizer=tokenizer,
                mlm=False
            )
            
            # Initialize trainer
            trainer = Trainer(
                model=model,
                args=training_args,
                train_dataset=train_dataset,
                data_collator=data_collator,
                tokenizer=tokenizer
            )
            
            # Start training
            logger.info(f"Starting fine-tuning for job: {job_id}")
            training_result = trainer.train()
            
            # Save model
            model_path = self.models_dir / f"{job.model_name}_{job_id}"
            model.save_pretrained(str(model_path))
            tokenizer.save_pretrained(str(model_path))
            
            # Update job
            job.status = "completed"
            job.completed_at = datetime.now()
            job.model_path = str(model_path)
            job.metrics = {
                "training_loss": float(training_result.training_loss),
                "train_runtime": training_result.metrics.get("train_runtime", 0),
                "train_samples_per_second": training_result.metrics.get("train_samples_per_second", 0)
            }
            
            result = {
                "job_id": job_id,
                "status": "completed",
                "model_path": str(model_path),
                "training_metrics": job.metrics,
                "duration_minutes": (job.completed_at - job.started_at).total_seconds() / 60
            }
            
            self.log_interaction("fine_tuning_completed", {
                "job_id": job_id,
                "duration_minutes": result["duration_minutes"],
                "training_loss": job.metrics["training_loss"]
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Error in fine-tuning execution: {e}")
            
            # Update job status
            if job_id in self.fine_tuning_jobs:
                job = self.fine_tuning_jobs[job_id]
                job.status = "failed"
                job.error_message = str(e)
            
            return {"error": f"Fine-tuning failed: {e}"}
    
    def evaluate_model(self, model_path: str, evaluation_type: str = "comprehensive") -> Dict[str, Any]:
        """
        Evaluate fine-tuned model performance.
        
        Args:
            model_path: Path to the fine-tuned model
            evaluation_type: Type of evaluation to perform
            
        Returns:
            Dict with evaluation results
        """
        try:
            evaluation_id = f"eval_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}"
            
            if not FINETUNING_AVAILABLE:
                # Simulate evaluation
                return self._simulate_model_evaluation(model_path, evaluation_type)
            
            # Load model and tokenizer
            tokenizer = AutoTokenizer.from_pretrained(model_path)
            model = PeftModel.from_pretrained(AutoModelForCausalLM.from_pretrained(model_path), model_path)
            
            # Prepare test data
            test_samples = self._prepare_test_data(evaluation_type)
            
            # Run evaluation
            metrics = {}
            
            if evaluation_type in ["comprehensive", "perplexity"]:
                metrics["perplexity"] = self._calculate_perplexity(model, tokenizer, test_samples)
            
            if evaluation_type in ["comprehensive", "generation_quality"]:
                metrics.update(self._evaluate_generation_quality(model, tokenizer, test_samples))
            
            if evaluation_type in ["comprehensive", "task_specific"]:
                metrics.update(self._evaluate_task_specific(model, tokenizer, test_samples))
            
            # Create evaluation record
            evaluation = ModelEvaluation(
                model_id=evaluation_id,
                evaluation_type=evaluation_type,
                metrics=metrics,
                test_samples=test_samples[:10],  # Store sample for review
                evaluation_date=datetime.now()
            )
            
            self.model_evaluations[evaluation_id] = evaluation
            
            result = {
                "evaluation_id": evaluation_id,
                "model_path": model_path,
                "metrics": metrics,
                "sample_outputs": test_samples[:3],
                "overall_score": self._calculate_overall_score(metrics)
            }
            
            self.log_interaction("model_evaluation", {
                "evaluation_id": evaluation_id,
                "evaluation_type": evaluation_type,
                "overall_score": result["overall_score"]
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Error evaluating model: {e}")
            return {"error": f"Model evaluation failed: {e}"}
    
    def create_ab_test(self, model_a_path: str, model_b_path: str, 
                      test_metric: str = "user_preference") -> Dict[str, Any]:
        """
        Create A/B test between two models.
        
        Args:
            model_a_path: Path to first model
            model_b_path: Path to second model
            test_metric: Metric to test (user_preference, response_quality, etc.)
            
        Returns:
            Dict with A/B test setup
        """
        try:
            test_id = f"abtest_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}"
            
            # Generate test cases
            test_cases = self._generate_ab_test_cases(test_metric)
            
            # Create test configuration
            ab_test = ABTestResult(
                test_id=test_id,
                model_a=model_a_path,
                model_b=model_b_path,
                metric=test_metric,
                winner="",
                confidence=0.0,
                sample_size=len(test_cases),
                results={
                    "test_cases": test_cases,
                    "model_a_responses": [],
                    "model_b_responses": [],
                    "comparisons": [],
                    "status": "created"
                }
            )
            
            self.ab_tests[test_id] = ab_test
            
            result = {
                "test_id": test_id,
                "model_a": model_a_path,
                "model_b": model_b_path,
                "test_metric": test_metric,
                "sample_size": len(test_cases),
                "status": "created",
                "next_step": "Execute A/B test comparison"
            }
            
            self.log_interaction("ab_test_creation", {
                "test_id": test_id,
                "metric": test_metric,
                "sample_size": len(test_cases)
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Error creating A/B test: {e}")
            return {"error": f"A/B test creation failed: {e}"}
    
    async def execute_ab_test(self, test_id: str) -> Dict[str, Any]:
        """
        Execute A/B test comparison.
        
        Args:
            test_id: ID of the A/B test
            
        Returns:
            Dict with test results
        """
        try:
            if test_id not in self.ab_tests:
                raise ValueError(f"A/B test not found: {test_id}")
            
            ab_test = self.ab_tests[test_id]
            
            if not FINETUNING_AVAILABLE:
                # Simulate A/B test
                return await self._simulate_ab_test(ab_test)
            
            # Load both models
            model_a = self._load_model_for_testing(ab_test.model_a)
            model_b = self._load_model_for_testing(ab_test.model_b)
            
            test_cases = ab_test.results["test_cases"]
            model_a_responses = []
            model_b_responses = []
            
            # Generate responses from both models
            for test_case in test_cases:
                response_a = self._generate_model_response(model_a, test_case)
                response_b = self._generate_model_response(model_b, test_case)
                
                model_a_responses.append(response_a)
                model_b_responses.append(response_b)
            
            # Compare responses
            comparisons = self._compare_responses(test_cases, model_a_responses, model_b_responses, ab_test.metric)
            
            # Calculate results
            winner, confidence = self._calculate_ab_test_winner(comparisons)
            
            # Update test results
            ab_test.results.update({
                "model_a_responses": model_a_responses,
                "model_b_responses": model_b_responses,
                "comparisons": comparisons,
                "status": "completed"
            })
            ab_test.winner = winner
            ab_test.confidence = confidence
            
            result = {
                "test_id": test_id,
                "winner": winner,
                "confidence": confidence,
                "sample_size": len(test_cases),
                "detailed_results": {
                    "model_a_wins": sum(1 for c in comparisons if c["winner"] == "model_a"),
                    "model_b_wins": sum(1 for c in comparisons if c["winner"] == "model_b"),
                    "ties": sum(1 for c in comparisons if c["winner"] == "tie")
                },
                "recommendation": self._generate_ab_test_recommendation(ab_test)
            }
            
            self.log_interaction("ab_test_completed", {
                "test_id": test_id,
                "winner": winner,
                "confidence": confidence
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Error executing A/B test: {e}")
            return {"error": f"A/B test execution failed: {e}"}
    
    def get_model_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive model performance report"""
        try:
            report = {
                "summary": {
                    "total_models_trained": len([job for job in self.fine_tuning_jobs.values() if job.status == "completed"]),
                    "total_evaluations": len(self.model_evaluations),
                    "total_ab_tests": len(self.ab_tests),
                    "training_data_samples": len(self.training_data)
                },
                "training_jobs": [],
                "model_evaluations": [],
                "ab_test_results": [],
                "recommendations": []
            }
            
            # Add job summaries
            for job in self.fine_tuning_jobs.values():
                report["training_jobs"].append({
                    "job_id": job.job_id,
                    "model_name": job.model_name,
                    "status": job.status,
                    "training_samples": job.training_data_count,
                    "metrics": job.metrics
                })
            
            # Add evaluation summaries
            for evaluation in self.model_evaluations.values():
                report["model_evaluations"].append({
                    "evaluation_id": evaluation.model_id,
                    "type": evaluation.evaluation_type,
                    "metrics": evaluation.metrics
                })
            
            # Add A/B test summaries
            for test in self.ab_tests.values():
                if test.winner:
                    report["ab_test_results"].append({
                        "test_id": test.test_id,
                        "winner": test.winner,
                        "confidence": test.confidence,
                        "metric": test.metric
                    })
            
            # Generate recommendations
            report["recommendations"] = self._generate_performance_recommendations()
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating performance report: {e}")
            return {"error": f"Report generation failed: {e}"}
    
    # Private helper methods
    
    def _save_training_data(self, data: List[TrainingData]):
        """Save training data to file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = self.data_dir / f"training_data_{timestamp}.jsonl"
        
        with open(filename, 'w') as f:
            for sample in data:
                f.write(json.dumps(asdict(sample), default=str) + '\n')
    
    def _save_job_config(self, job: FineTuningJob):
        """Save job configuration"""
        filename = self.experiments_dir / f"{job.job_id}_config.json"
        with open(filename, 'w') as f:
            json.dump(asdict(job), f, default=str, indent=2)
    
    def _generate_data_stats(self, data: List[TrainingData]) -> Dict[str, Any]:
        """Generate statistics for training data"""
        categories = {}
        sources = {}
        quality_scores = []
        
        for sample in data:
            categories[sample.category] = categories.get(sample.category, 0) + 1
            sources[sample.source] = sources.get(sample.source, 0) + 1
            quality_scores.append(sample.quality_score)
        
        return {
            "categories": categories,
            "sources": sources,
            "quality_distribution": {
                "mean": np.mean(quality_scores),
                "median": np.median(quality_scores),
                "min": np.min(quality_scores),
                "max": np.max(quality_scores)
            }
        }
    
    def _estimate_training_time(self, sample_count: int) -> float:
        """Estimate training time in hours"""
        # Rough estimation: 1 hour per 1000 samples
        base_time = sample_count / 1000
        return max(0.5, base_time * 2)  # Minimum 30 minutes
    
    async def _simulate_fine_tuning(self, job: FineTuningJob) -> Dict[str, Any]:
        """Simulate fine-tuning when libraries are not available"""
        logger.info(f"Simulating fine-tuning for job: {job.job_id}")
        
        # Simulate training time
        await asyncio.sleep(2)
        
        # Update job
        job.status = "completed"
        job.started_at = datetime.now() - timedelta(minutes=30)
        job.completed_at = datetime.now()
        job.model_path = str(self.models_dir / f"{job.model_name}_{job.job_id}_simulated")
        job.metrics = {
            "training_loss": 2.45 - (job.training_data_count / 1000) * 0.5,
            "train_runtime": 1800,
            "train_samples_per_second": job.training_data_count / 1800
        }
        
        # Create simulated model directory
        model_dir = Path(job.model_path)
        model_dir.mkdir(exist_ok=True)
        (model_dir / "config.json").write_text('{"model_type": "simulated"}')
        
        return {
            "job_id": job.job_id,
            "status": "completed",
            "model_path": job.model_path,
            "training_metrics": job.metrics,
            "duration_minutes": 30,
            "note": "Simulated fine-tuning (libraries not available)"
        }
    
    def _simulate_model_evaluation(self, model_path: str, evaluation_type: str) -> Dict[str, Any]:
        """Simulate model evaluation"""
        metrics = {
            "perplexity": np.random.uniform(15, 25),
            "bleu_score": np.random.uniform(0.6, 0.85),
            "rouge_l": np.random.uniform(0.55, 0.8),
            "coherence": np.random.uniform(0.7, 0.9),
            "relevance": np.random.uniform(0.75, 0.95)
        }
        
        return {
            "evaluation_id": f"eval_simulated_{str(uuid.uuid4())[:8]}",
            "model_path": model_path,
            "metrics": metrics,
            "sample_outputs": [
                {"input": "How can I help you today?", "output": "I'd be happy to assist you with any questions or concerns you might have."},
                {"input": "What are your pricing options?", "output": "We offer flexible pricing plans to meet your business needs..."}
            ],
            "overall_score": np.mean(list(metrics.values())),
            "note": "Simulated evaluation (libraries not available)"
        }
    
    async def _simulate_ab_test(self, ab_test: ABTestResult) -> Dict[str, Any]:
        """Simulate A/B test execution"""
        await asyncio.sleep(1)
        
        # Simulate test results
        model_a_wins = np.random.randint(8, 15)
        model_b_wins = np.random.randint(5, 12)
        ties = ab_test.sample_size - model_a_wins - model_b_wins
        
        if model_a_wins > model_b_wins:
            winner = "model_a"
            confidence = min(0.95, (model_a_wins - model_b_wins) / ab_test.sample_size + 0.5)
        elif model_b_wins > model_a_wins:
            winner = "model_b"
            confidence = min(0.95, (model_b_wins - model_a_wins) / ab_test.sample_size + 0.5)
        else:
            winner = "tie"
            confidence = 0.1
        
        ab_test.winner = winner
        ab_test.confidence = confidence
        
        return {
            "test_id": ab_test.test_id,
            "winner": winner,
            "confidence": confidence,
            "sample_size": ab_test.sample_size,
            "detailed_results": {
                "model_a_wins": model_a_wins,
                "model_b_wins": model_b_wins,
                "ties": ties
            },
            "recommendation": f"Deploy {winner} model" if winner != "tie" else "Continue testing with larger sample",
            "note": "Simulated A/B test (libraries not available)"
        }
    
    def _prepare_test_data(self, evaluation_type: str) -> List[Dict]:
        """Prepare test data for evaluation"""
        # Return sample test data
        return [
            {"input": "Hello, how can I help you today?", "expected": "greeting"},
            {"input": "I'm interested in your pricing", "expected": "pricing_inquiry"},
            {"input": "Can you tell me about your features?", "expected": "feature_inquiry"}
        ]
    
    def _calculate_overall_score(self, metrics: Dict[str, float]) -> float:
        """Calculate overall performance score"""
        if not metrics:
            return 0.0
        
        # Weight different metrics
        weights = {
            "perplexity": -0.3,  # Lower is better
            "bleu_score": 0.25,
            "rouge_l": 0.25,
            "coherence": 0.2,
            "relevance": 0.3
        }
        
        score = 0.0
        total_weight = 0.0
        
        for metric, value in metrics.items():
            if metric in weights:
                weight = weights[metric]
                if metric == "perplexity":
                    # Normalize perplexity (lower is better)
                    normalized_value = max(0, (50 - value) / 50)
                else:
                    normalized_value = value
                
                score += normalized_value * abs(weight)
                total_weight += abs(weight)
        
        return score / total_weight if total_weight > 0 else 0.0
    
    def _generate_ab_test_cases(self, metric: str) -> List[Dict]:
        """Generate test cases for A/B testing"""
        test_cases = [
            {"input": "What services do you offer?", "category": "service_inquiry"},
            {"input": "How much does it cost?", "category": "pricing"},
            {"input": "I need help with my account", "category": "support"},
            {"input": "Tell me about your company", "category": "company_info"},
            {"input": "I'm interested in a demo", "category": "demo_request"}
        ]
        
        # Add more test cases based on metric
        if metric == "user_preference":
            test_cases.extend([
                {"input": "Can you explain this feature?", "category": "feature_explanation"},
                {"input": "I have a technical question", "category": "technical_support"}
            ])
        
        return test_cases
    
    def _generate_performance_recommendations(self) -> List[str]:
        """Generate performance improvement recommendations"""
        recommendations = []
        
        if len(self.training_data) < 1000:
            recommendations.append("Collect more training data to improve model performance")
        
        completed_jobs = [job for job in self.fine_tuning_jobs.values() if job.status == "completed"]
        if len(completed_jobs) > 0:
            avg_loss = np.mean([job.metrics.get("training_loss", 3.0) for job in completed_jobs if job.metrics])
            if avg_loss > 2.0:
                recommendations.append("Consider increasing training epochs or adjusting learning rate")
        
        if len(self.ab_tests) < 3:
            recommendations.append("Conduct more A/B tests to validate model improvements")
        
        return recommendations

def main():
    """Test the model fine-tuning agent"""
    agent = ModelFineTuningAgent()
    
    print("🧠 SIX3 Agency Model Fine-Tuning Agent")
    print("=" * 50)
    
    # Test data collection
    print("\n📊 Testing Training Data Collection...")
    sample_logs = [
        {
            "input_message": "Hello, how are you?",
            "agent_response": "Hello! I'm doing well, thank you for asking. How can I assist you today?",
            "agent_name": "customer_support",
            "status": "success",
            "user_feedback": {"rating": 4},
            "created_at": datetime.now().isoformat()
        }
    ]
    
    data_result = agent.collect_training_data(sample_logs)
    print(f"Collected samples: {data_result.get('collected_samples', 0)}")
    
    # Test job creation
    print("\n🔧 Testing Fine-Tuning Job Creation...")
    job_result = agent.create_fine_tuning_job("sales_agent")
    print(f"Job ID: {job_result.get('job_id', 'N/A')}")
    print(f"Status: {job_result.get('status', 'N/A')}")
    
    # Test model evaluation
    print("\n📈 Testing Model Evaluation...")
    eval_result = agent.evaluate_model("test_model_path", "comprehensive")
    print(f"Overall Score: {eval_result.get('overall_score', 0):.2f}")
    
    # Test A/B test creation
    print("\n🧪 Testing A/B Test Creation...")
    ab_result = agent.create_ab_test("model_a", "model_b")
    print(f"Test ID: {ab_result.get('test_id', 'N/A')}")
    
    # Generate performance report
    print("\n📊 Generating Performance Report...")
    report = agent.get_model_performance_report()
    print(f"Total Models Trained: {report['summary']['total_models_trained']}")
    print(f"Recommendations: {len(report['recommendations'])}")
    
    print("\n✅ Model Fine-Tuning Agent testing completed!")

if __name__ == "__main__":
    main()