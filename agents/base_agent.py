"""
Base Agent Class for Instant Agency
Provides common functionality for all AI agents
"""

import os
import json
import yaml
from typing import Dict, List, Any, Optional
from datetime import datetime
from abc import ABC, abstractmethod

from langchain.llms import HuggingFaceHub
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.memory import ConversationBufferMemory
from langchain.vectorstores import Chroma
from langchain.chains import ConversationalRetrievalChain

import redis
import psycopg2
from psycopg2.extras import RealDictCursor

from loguru import logger


class BaseAgent(ABC):
    """
    Base class for all Instant Agency AI agents
    """

    def __init__(self, config_path: str):
        """
        Initialize the base agent

        Args:
            config_path: Path to agent configuration YAML file
        """
        self.config = self._load_config(config_path)
        self.agent_name = self.config['agent']['name']
        self.version = self.config['agent']['version']

        # Initialize components
        self._init_logger()
        self._init_llm()
        self._init_memory()
        self._init_database()
        self._init_cache()
        self._init_vector_store()

        logger.info(f"{self.agent_name} v{self.version} initialized")

    def _load_config(self, config_path: str) -> Dict:
        """Load agent configuration from YAML file"""
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)

    def _init_logger(self):
        """Initialize logging"""
        log_level = self.config.get('monitoring', {}).get('log_level', 'INFO')
        logger.add(
            f"logs/{self.agent_name.lower().replace(' ', '_')}.log",
            rotation="500 MB",
            retention="10 days",
            level=log_level.upper()
        )

    def _init_llm(self):
        """Initialize the Language Model"""
        model_config = self.config['model']

        self.llm = HuggingFaceHub(
            repo_id=model_config['model_name'],
            model_kwargs={
                'temperature': model_config.get('temperature', 0.7),
                'max_length': model_config.get('max_tokens', 2048),
            },
            huggingfacehub_api_token=os.getenv('HUGGINGFACE_API_KEY')
        )

        logger.info(f"LLM initialized: {model_config['model_name']}")

    def _init_memory(self):
        """Initialize conversation memory"""
        memory_config = self.config.get('memory', {})

        if memory_config.get('type') == 'conversation':
            self.memory = ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True,
                output_key="answer"
            )
        else:
            self.memory = None

        logger.info("Memory initialized")

    def _init_database(self):
        """Initialize PostgreSQL database connection"""
        try:
            self.db = psycopg2.connect(
                host=os.getenv('POSTGRES_HOST', 'postgres'),
                port=os.getenv('POSTGRES_PORT', '5432'),
                database=os.getenv('POSTGRES_DB', 'instant_agency'),
                user=os.getenv('POSTGRES_USER', 'instant_agency'),
                password=os.getenv('POSTGRES_PASSWORD'),
                cursor_factory=RealDictCursor
            )
            logger.info("Database connection established")
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            self.db = None

    def _init_cache(self):
        """Initialize Redis cache"""
        try:
            self.cache = redis.Redis(
                host=os.getenv('REDIS_HOST', 'redis'),
                port=int(os.getenv('REDIS_PORT', 6379)),
                password=os.getenv('REDIS_PASSWORD'),
                decode_responses=True
            )
            self.cache.ping()
            logger.info("Redis cache connected")
        except Exception as e:
            logger.error(f"Redis connection failed: {e}")
            self.cache = None

    def _init_vector_store(self):
        """Initialize vector database for RAG"""
        memory_config = self.config.get('memory', {})
        vector_config = memory_config.get('vector_store', {})

        if not vector_config.get('enabled', False):
            self.vector_store = None
            return

        try:
            embeddings = HuggingFaceEmbeddings(
                model_name=os.getenv(
                    'HUGGINGFACE_EMBEDDING_MODEL',
                    'sentence-transformers/all-MiniLM-L6-v2'
                )
            )

            self.vector_store = Chroma(
                collection_name=vector_config.get('collection', 'default'),
                embedding_function=embeddings,
                persist_directory=f"./chroma_data/{self.agent_name}"
            )

            logger.info("Vector store initialized")
        except Exception as e:
            logger.error(f"Vector store initialization failed: {e}")
            self.vector_store = None

    @abstractmethod
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main processing method - must be implemented by each agent

        Args:
            input_data: Input data for the agent to process

        Returns:
            Dict containing the agent's response
        """
        pass

    def get_system_prompt(self) -> str:
        """Get the system prompt for this agent"""
        return self.config.get('system_prompt', '')

    def should_escalate(self, data: Dict[str, Any]) -> Optional[Dict[str, str]]:
        """
        Check if the current situation requires escalation

        Args:
            data: Context data to evaluate

        Returns:
            Escalation action if needed, None otherwise
        """
        escalation_rules = self.config.get('escalation', {}).get('rules', [])

        for rule in escalation_rules:
            condition = rule['condition']

            # Simple condition evaluation
            if self._evaluate_condition(condition, data):
                return {
                    'action': rule['action'],
                    'notify': rule.get('notify', False)
                }

        return None

    def _evaluate_condition(self, condition: str, data: Dict[str, Any]) -> bool:
        """
        Evaluate a simple condition string

        Args:
            condition: Condition string (e.g., "score < 5")
            data: Data to evaluate against

        Returns:
            True if condition is met, False otherwise
        """
        # This is a simplified evaluation - in production, use a safer method
        try:
            # Replace variables with actual values
            for key, value in data.items():
                condition = condition.replace(key, str(value))

            # Evaluate the condition
            return eval(condition)
        except Exception as e:
            logger.warning(f"Condition evaluation failed: {e}")
            return False

    def cache_get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.cache:
            return None

        try:
            value = self.cache.get(key)
            if value:
                return json.loads(value)
        except Exception as e:
            logger.warning(f"Cache get failed: {e}")

        return None

    def cache_set(self, key: str, value: Any, ttl: int = None):
        """Set value in cache"""
        if not self.cache:
            return

        try:
            cache_config = self.config.get('performance', {})
            default_ttl = cache_config.get('cache_ttl', 3600)

            self.cache.setex(
                key,
                ttl or default_ttl,
                json.dumps(value)
            )
        except Exception as e:
            logger.warning(f"Cache set failed: {e}")

    def db_query(self, query: str, params: tuple = None) -> List[Dict]:
        """Execute database query"""
        if not self.db:
            return []

        try:
            cursor = self.db.cursor()
            cursor.execute(query, params)
            results = cursor.fetchall()
            cursor.close()
            return results
        except Exception as e:
            logger.error(f"Database query failed: {e}")
            return []

    def db_execute(self, query: str, params: tuple = None) -> bool:
        """Execute database command (INSERT, UPDATE, DELETE)"""
        if not self.db:
            return False

        try:
            cursor = self.db.cursor()
            cursor.execute(query, params)
            self.db.commit()
            cursor.close()
            return True
        except Exception as e:
            logger.error(f"Database execute failed: {e}")
            self.db.rollback()
            return False

    def log_interaction(self, input_data: Dict, output_data: Dict, metadata: Dict = None):
        """Log agent interaction to database"""
        try:
            query = """
                INSERT INTO agent_interactions
                (agent_name, input_data, output_data, metadata, created_at)
                VALUES (%s, %s, %s, %s, %s)
            """

            self.db_execute(
                query,
                (
                    self.agent_name,
                    json.dumps(input_data),
                    json.dumps(output_data),
                    json.dumps(metadata or {}),
                    datetime.now()
                )
            )
        except Exception as e:
            logger.warning(f"Failed to log interaction: {e}")

    def track_metric(self, metric_name: str, value: float):
        """Track agent performance metric"""
        metrics_to_track = self.config.get('monitoring', {}).get('track_metrics', [])

        if metric_name not in metrics_to_track:
            return

        try:
            # Store in Redis for real-time metrics
            key = f"metrics:{self.agent_name}:{metric_name}"
            self.cache.lpush(key, f"{datetime.now().isoformat()}:{value}")
            self.cache.ltrim(key, 0, 999)  # Keep last 1000 values

            # Also store in database for historical analysis
            query = """
                INSERT INTO agent_metrics
                (agent_name, metric_name, value, timestamp)
                VALUES (%s, %s, %s, %s)
            """

            self.db_execute(
                query,
                (self.agent_name, metric_name, value, datetime.now())
            )
        except Exception as e:
            logger.warning(f"Failed to track metric: {e}")

    def __del__(self):
        """Cleanup on agent destruction"""
        if hasattr(self, 'db') and self.db:
            self.db.close()

        if hasattr(self, 'cache') and self.cache:
            self.cache.close()
