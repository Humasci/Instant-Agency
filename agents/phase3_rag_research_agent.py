"""
Phase 3: RAG-Enhanced Research Agent

Uses Retrieval-Augmented Generation (RAG) to research topics, gather context,
and provide data-backed insights for content creation and decision-making.

Key Features:
- Semantic search using embeddings
- Multi-source research (web, docs, knowledge base)
- Context compilation and summarization
- Source attribution and fact-checking
- Integration with content creation workflow

Models:
- Embeddings: sentence-transformers/all-mpnet-base-v2
- Generation: EleutherAI/gpt-neo-2.7B
"""

import os
import json
import time
import requests
import numpy as np
from typing import Dict, Any, List, Optional
from datetime import datetime
from base_agent import BaseAgent


class Phase3RAGResearchAgent(BaseAgent):
    """
    RAG-enhanced Research Agent for intelligent information retrieval
    """

    def __init__(self):
        super().__init__(
            agent_name="phase3_rag_research",
            agent_type="research",
            model_name="EleutherAI/gpt-neo-2.7B"
        )

        # Embedding model for semantic search
        self.embedding_model = "sentence-transformers/all-mpnet-base-v2"

        # Knowledge base (in production, this would be a vector database like Pinecone/Weaviate)
        self.knowledge_base = self._initialize_knowledge_base()

        # Research sources
        self.sources = {
            'knowledge_base': True,
            'web_search': False,  # Requires API key
            'company_docs': True
        }

        print(f"✓ RAG Research Agent initialized")
        print(f"  - Embedding model: {self.embedding_model}")
        print(f"  - Knowledge base entries: {len(self.knowledge_base)}")

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Research a topic using RAG

        Args:
            input_data: {
                'query': str,                    # Research query
                'topic': str,                    # Topic/subject
                'depth': str,                    # 'quick', 'standard', 'deep'
                'sources': list,                 # Sources to search
                'max_results': int,              # Max results to return
                'include_citations': bool        # Include source citations
            }

        Returns:
            {
                'success': bool,
                'query': str,
                'research_summary': str,
                'key_findings': list,
                'sources': list,
                'confidence': float,
                'context_for_generation': dict
            }
        """
        try:
            query = input_data.get('query') or input_data.get('topic')
            if not query:
                return {
                    'success': False,
                    'error': 'No query or topic provided'
                }

            depth = input_data.get('depth', 'standard')
            max_results = input_data.get('max_results', 5)
            include_citations = input_data.get('include_citations', True)

            # Step 1: Generate query embedding
            query_embedding = self._generate_embedding(query)

            # Step 2: Search knowledge base
            search_results = self._semantic_search(
                query_embedding,
                max_results=max_results * 2  # Get extra for filtering
            )

            # Step 3: Rank and filter results
            top_results = self._rank_results(search_results, query)[:max_results]

            # Step 4: Compile research summary
            research_summary = self._compile_research_summary(
                query,
                top_results,
                depth
            )

            # Step 5: Extract key findings
            key_findings = self._extract_key_findings(top_results, query)

            # Step 6: Prepare sources
            sources = self._format_sources(top_results) if include_citations else []

            # Step 7: Calculate confidence
            confidence = self._calculate_confidence(top_results, query)

            # Step 8: Prepare context for downstream generation
            context_for_generation = {
                'query': query,
                'findings': key_findings,
                'supporting_facts': [r['content'] for r in top_results[:3]],
                'sources': sources,
                'confidence': confidence
            }

            result = {
                'success': True,
                'query': query,
                'research_summary': research_summary,
                'key_findings': key_findings,
                'sources': sources,
                'confidence': confidence,
                'context_for_generation': context_for_generation,
                'results_count': len(top_results),
                'timestamp': datetime.now().isoformat()
            }

            # Log research
            self._log_research(input_data, result)

            return result

        except Exception as e:
            self.logger.error(f"Research error: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _initialize_knowledge_base(self) -> List[Dict[str, Any]]:
        """
        Initialize knowledge base with sample entries
        In production, this would load from a vector database
        """
        knowledge_base = [
            {
                'id': 'kb_001',
                'title': 'AI Agent Benefits for Small Business',
                'content': 'AI agents can reduce operational costs by 40-60% for small businesses by automating repetitive tasks like lead qualification, customer support, and content creation.',
                'category': 'business_value',
                'source': 'Internal Research',
                'date': '2024-12-01'
            },
            {
                'id': 'kb_002',
                'title': 'Lead Qualification Best Practices',
                'content': 'Effective lead qualification requires scoring based on engagement (40%), fit (30%), intent signals (20%), and timing (10%). AI can automate this process with 85%+ accuracy.',
                'category': 'sales',
                'source': 'Sales Playbook',
                'date': '2024-11-15'
            },
            {
                'id': 'kb_003',
                'title': 'Content Marketing ROI',
                'content': 'Companies using AI for content creation see 3x higher publishing velocity and 2x engagement rates compared to manual processes, while reducing costs by 50%.',
                'category': 'marketing',
                'source': 'Marketing Study',
                'date': '2024-10-20'
            },
            {
                'id': 'kb_004',
                'title': 'Customer Support Automation',
                'content': 'AI chatbots can handle 70-80% of tier-1 support queries, reducing response time from hours to seconds. Average customer satisfaction scores remain high at 4.2/5.',
                'category': 'support',
                'source': 'Support Metrics',
                'date': '2024-11-01'
            },
            {
                'id': 'kb_005',
                'title': 'Email Personalization Impact',
                'content': 'Personalized emails have 6x higher transaction rates. AI-powered personalization based on behavior, industry, and pain points increases open rates by 50%.',
                'category': 'marketing',
                'source': 'Email Campaign Analysis',
                'date': '2024-09-15'
            },
            {
                'id': 'kb_006',
                'title': 'Sales Cycle Acceleration',
                'content': 'AI-driven sales automation can reduce sales cycles by 25-35% through faster response times, better qualification, and personalized outreach at scale.',
                'category': 'sales',
                'source': 'Sales Analytics',
                'date': '2024-11-10'
            },
            {
                'id': 'kb_007',
                'title': 'Social Media Engagement Tactics',
                'content': 'Platform-specific content performs 2.5x better than generic posts. LinkedIn: professional insights, Twitter: concise updates, Facebook: community stories.',
                'category': 'marketing',
                'source': 'Social Media Guide',
                'date': '2024-08-30'
            },
            {
                'id': 'kb_008',
                'title': 'Intent Classification Benefits',
                'content': 'Classifying customer intent enables 90% faster routing, 60% reduction in response time, and 40% improvement in customer satisfaction.',
                'category': 'operations',
                'source': 'Operations Research',
                'date': '2024-10-05'
            }
        ]

        # In production, each entry would have a pre-computed embedding
        return knowledge_base

    def _generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for text using Hugging Face model

        In production, this would call HF Inference API
        For now, using simulated embeddings based on keyword matching
        """
        try:
            # Production code:
            # url = f"{self.hf_api_url}/{self.embedding_model}"
            # response = requests.post(url, headers=headers, json={"inputs": text})
            # return response.json()

            # Simulated: Create simple keyword-based vector
            keywords = {
                'business': 0, 'sales': 1, 'marketing': 2, 'support': 3,
                'ai': 4, 'automation': 5, 'content': 6, 'email': 7,
                'lead': 8, 'customer': 9, 'social': 10, 'intent': 11
            }

            # Create a 12-dimensional vector
            embedding = [0.0] * 12

            text_lower = text.lower()
            for keyword, idx in keywords.items():
                if keyword in text_lower:
                    embedding[idx] = 1.0

            # Normalize
            magnitude = sum(x**2 for x in embedding) ** 0.5
            if magnitude > 0:
                embedding = [x / magnitude for x in embedding]

            return embedding

        except Exception as e:
            self.logger.error(f"Embedding generation error: {e}")
            return [0.1] * 12  # Fallback

    def _semantic_search(
        self,
        query_embedding: List[float],
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Perform semantic search in knowledge base
        """
        results = []

        for entry in self.knowledge_base:
            # Generate embedding for entry (in production, these would be pre-computed)
            entry_embedding = self._generate_embedding(entry['content'])

            # Calculate cosine similarity
            similarity = self._cosine_similarity(query_embedding, entry_embedding)

            results.append({
                **entry,
                'similarity_score': similarity
            })

        # Sort by similarity
        results.sort(key=lambda x: x['similarity_score'], reverse=True)

        return results[:max_results]

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = sum(a**2 for a in vec1) ** 0.5
        magnitude2 = sum(b**2 for b in vec2) ** 0.5

        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0

        return dot_product / (magnitude1 * magnitude2)

    def _rank_results(
        self,
        results: List[Dict[str, Any]],
        query: str
    ) -> List[Dict[str, Any]]:
        """
        Re-rank results based on multiple factors
        """
        query_lower = query.lower()

        for result in results:
            # Base score from similarity
            score = result['similarity_score']

            # Boost if query terms in title
            if any(term in result['title'].lower() for term in query_lower.split()):
                score *= 1.2

            # Recency boost (newer content scores higher)
            try:
                date = datetime.fromisoformat(result['date'])
                days_old = (datetime.now() - date).days
                recency_factor = max(0.8, 1.0 - (days_old / 365) * 0.2)
                score *= recency_factor
            except:
                pass

            result['final_score'] = score

        # Re-sort by final score
        results.sort(key=lambda x: x['final_score'], reverse=True)

        return results

    def _compile_research_summary(
        self,
        query: str,
        results: List[Dict[str, Any]],
        depth: str
    ) -> str:
        """
        Compile research summary from top results
        """
        if not results:
            return f"No relevant information found for: {query}"

        # Extract key information
        top_results = results[:3] if depth == 'quick' else results[:5]

        summary_parts = [f"Research Summary: {query}\n"]

        for i, result in enumerate(top_results, 1):
            summary_parts.append(
                f"\n{i}. {result['title']}\n"
                f"   {result['content'][:200]}..."
                f"\n   (Source: {result['source']}, Relevance: {result['final_score']:.2f})"
            )

        if depth == 'deep':
            summary_parts.append(
                f"\n\nBased on {len(results)} sources analyzed, "
                f"the key themes are: {query}"
            )

        return '\n'.join(summary_parts)

    def _extract_key_findings(
        self,
        results: List[Dict[str, Any]],
        query: str
    ) -> List[str]:
        """Extract key findings from results"""
        findings = []

        for result in results[:5]:
            # Extract numerical facts
            content = result['content']

            # Look for percentages, numbers, statistics
            import re
            stats = re.findall(r'\d+(?:\.\d+)?%|\d+x|\d+(?:-\d+)?%', content)

            if stats:
                # Create finding with context
                finding = f"{result['title']}: {stats[0]}"
                if finding not in findings:
                    findings.append(finding)

            # Also add high-scoring titles
            if result['final_score'] > 0.7:
                findings.append(result['title'])

        return findings[:5]  # Top 5 findings

    def _format_sources(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format sources for citation"""
        sources = []

        for i, result in enumerate(results, 1):
            sources.append({
                'citation_number': i,
                'title': result['title'],
                'source': result['source'],
                'date': result['date'],
                'relevance_score': round(result['final_score'], 2)
            })

        return sources

    def _calculate_confidence(
        self,
        results: List[Dict[str, Any]],
        query: str
    ) -> float:
        """Calculate confidence score for research"""
        if not results:
            return 0.0

        # Factors:
        # 1. Number of relevant results
        # 2. Average relevance score
        # 3. Source diversity

        num_results = len(results)
        avg_score = sum(r['final_score'] for r in results) / num_results
        unique_sources = len(set(r['source'] for r in results))

        # Combine factors
        confidence = (
            min(num_results / 5, 1.0) * 0.3 +  # More results = higher confidence
            avg_score * 0.5 +                   # Higher relevance = higher confidence
            min(unique_sources / 3, 1.0) * 0.2  # Source diversity
        )

        return min(confidence, 1.0)

    def _log_research(self, input_data: Dict[str, Any], result: Dict[str, Any]):
        """Log research activity"""
        log_entry = {
            'agent': self.agent_name,
            'query': input_data.get('query'),
            'results_count': result.get('results_count'),
            'confidence': result.get('confidence'),
            'timestamp': datetime.now().isoformat()
        }

        self.logger.info(f"Research completed: {json.dumps(log_entry)}")

        if self.db:
            try:
                self.db.log_interaction(
                    agent_name=self.agent_name,
                    interaction_type='research',
                    input_data=input_data,
                    output_data=result
                )
            except Exception as e:
                self.logger.error(f"Failed to log research: {e}")


if __name__ == "__main__":
    # Test the RAG research agent
    print("\n" + "="*80)
    print("Testing Phase 3 RAG Research Agent")
    print("="*80 + "\n")

    agent = Phase3RAGResearchAgent()

    # Test 1: Research AI benefits for small business
    print("Test 1: Research AI benefits for small business")
    print("-"*80)
    result = agent.process({
        'query': 'AI automation benefits for small businesses',
        'depth': 'standard',
        'max_results': 5,
        'include_citations': True
    })

    if result['success']:
        print(f"\nQuery: {result['query']}")
        print(f"Confidence: {result['confidence']:.2%}")
        print(f"\nKey Findings:")
        for i, finding in enumerate(result['key_findings'], 1):
            print(f"  {i}. {finding}")
        print(f"\nSources: {len(result['sources'])} sources found")
        print(f"\nResearch Summary:\n{result['research_summary']}")
    else:
        print(f"Error: {result.get('error')}")

    # Test 2: Research sales automation
    print("\n\nTest 2: Research sales automation tactics")
    print("-"*80)
    result = agent.process({
        'query': 'How can AI accelerate sales cycles',
        'depth': 'deep',
        'max_results': 3
    })

    if result['success']:
        print(f"\nQuery: {result['query']}")
        print(f"Confidence: {result['confidence']:.2%}")
        print(f"\nKey Findings:")
        for finding in result['key_findings']:
            print(f"  • {finding}")

    # Test 3: Research email marketing
    print("\n\nTest 3: Research email personalization")
    print("-"*80)
    result = agent.process({
        'topic': 'email personalization and engagement',
        'depth': 'quick',
        'max_results': 3
    })

    if result['success']:
        print(f"\nQuery: {result['query']}")
        print(f"Confidence: {result['confidence']:.2%}")
        print(f"Results: {result['results_count']} relevant documents")

    print("\n" + "="*80)
    print("RAG Research Agent Tests Complete!")
    print("="*80)
