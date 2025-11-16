"""
Phase 2 - Content Writing Agent

Generates high-quality blog posts, articles, and marketing content.

Models used:
- EleutherAI/gpt-neo-2.7B or mistralai/Mistral-7B-v0.1 (content generation)
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from base_agent import BaseAgent
from typing import Dict, Any, List, Optional
import json
import requests
from datetime import datetime
from loguru import logger


class Phase2ContentWriterAgent(BaseAgent):
    """
    Phase 2 Content Writing Agent

    Generates professional content including:
    - Blog posts
    - Articles
    - Social media posts
    - Marketing copy
    - Case studies

    Uses GPT-Neo-2.7B or Mistral-7B for generation.
    """

    def __init__(self):
        config_path = os.path.join(
            os.path.dirname(__file__),
            'content/writer_config.yaml'
        )

        if not os.path.exists(os.path.dirname(config_path)):
            os.makedirs(os.path.dirname(config_path), exist_ok=True)

        if not os.path.exists(config_path):
            self._create_default_config(config_path)

        super().__init__(config_path)

        # Hugging Face configuration
        self.hf_api_url = "https://api-inference.huggingface.co/models"
        self.hf_api_key = os.getenv('HUGGINGFACE_API_KEY')
        self.model = "EleutherAI/gpt-neo-2.7B"  # Good for content generation

    def _create_default_config(self, config_path: str):
        """Create default configuration"""
        config = {
            'agent': {
                'name': 'Content Writing Agent',
                'version': '2.0',
                'department': 'content',
                'description': 'Generates blog posts and marketing content'
            },
            'model': {
                'provider': 'huggingface',
                'model_name': 'EleutherAI/gpt-neo-2.7B',
                'temperature': 0.8,
                'max_tokens': 1000
            },
            'memory': {
                'type': 'conversation',
                'ttl': 7200
            },
            'monitoring': {
                'log_level': 'INFO',
                'track_metrics': ['generation_time', 'content_length', 'content_quality']
            }
        }

        with open(config_path, 'w') as f:
            import yaml
            yaml.dump(config, f)

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate content

        Args:
            input_data: Dict with keys:
                - topic: Main topic/title
                - content_type: 'blog_post', 'article', 'social_post', 'case_study'
                - audience: Target audience
                - tone: 'professional', 'casual', 'technical', 'conversational'
                - word_count: Target word count (optional)
                - keywords: List of keywords to include (optional)
                - key_points: List of key points to cover (optional)

        Returns:
            Dict with generated content and metadata
        """
        start_time = datetime.now()

        try:
            # Validate inputs
            topic = input_data.get('topic')
            if not topic:
                return {'error': 'topic is required', 'success': False}

            content_type = input_data.get('content_type', 'blog_post')
            audience = input_data.get('audience', 'business professionals')
            tone = input_data.get('tone', 'professional')
            word_count = input_data.get('word_count', 600)
            keywords = input_data.get('keywords', [])
            key_points = input_data.get('key_points', [])

            logger.info(f"Generating {content_type} on topic: {topic}")

            # Check cache
            cache_key = f"content:{content_type}:{topic.lower().replace(' ', '_')[:50]}"
            cached_result = self.cache_get(cache_key)
            if cached_result:
                logger.info(f"Returning cached content for {topic}")
                return cached_result

            # Build prompt
            prompt = self._build_content_prompt(
                topic=topic,
                content_type=content_type,
                audience=audience,
                tone=tone,
                word_count=word_count,
                keywords=keywords,
                key_points=key_points
            )

            # Generate content
            generated = self._generate_content(prompt, word_count)

            if not generated['success']:
                return generated

            # Parse the content
            parsed = self._parse_content(generated['text'], content_type)

            # Generate SEO metadata
            seo_metadata = self._generate_seo_metadata(topic, parsed['body'], keywords)

            # Calculate quality score
            quality_score = self._calculate_quality_score(parsed, input_data)

            # Compile result
            result = {
                'success': True,
                'content_type': content_type,
                'headline': parsed['headline'],
                'body': parsed['body'],
                'meta_description': seo_metadata['meta_description'],
                'keywords': seo_metadata['keywords'],
                'tags': seo_metadata['tags'],
                'estimated_reading_time': self._estimate_reading_time(parsed['body']),
                'word_count': len(parsed['body'].split()),
                'quality_score': quality_score,
                'timestamp': datetime.now().isoformat(),
                'agent_version': self.version
            }

            # Cache result
            self.cache_set(cache_key, result, ttl=7200)

            # Log interaction
            self.log_interaction(input_data, result, {
                'quality_score': quality_score,
                'word_count': result['word_count']
            })

            # Track metrics
            generation_time = (datetime.now() - start_time).total_seconds()
            self.track_metric('generation_time', generation_time)
            self.track_metric('content_length', result['word_count'])
            self.track_metric('content_quality', quality_score)

            logger.info(f"Content generated: {result['word_count']} words, quality={quality_score:.2f}")

            return result

        except Exception as e:
            logger.error(f"Content generation failed: {e}")
            return {'error': str(e), 'success': False}

    def _build_content_prompt(
        self,
        topic: str,
        content_type: str,
        audience: str,
        tone: str,
        word_count: int,
        keywords: List[str],
        key_points: List[str]
    ) -> str:
        """Build prompt for content generation"""

        prompt = f"""You are a professional content writer specializing in B2B SaaS and AI technology.

Write a {content_type} on the following topic:

Topic: {topic}
Target Audience: {audience}
Tone: {tone}
Target Length: {word_count} words
"""

        if keywords:
            prompt += f"Keywords to include: {', '.join(keywords)}\n"

        if key_points:
            prompt += f"\nKey points to cover:\n"
            for i, point in enumerate(key_points, 1):
                prompt += f"{i}. {point}\n"

        prompt += f"""
Requirements:
1. Engaging headline with target keyword
2. Clear introduction with hook
3. Well-structured body with subheadings
4. Actionable insights and examples
5. Strong conclusion with CTA
6. {tone} tone throughout

Output format:
Headline: [headline]

Body:
[full content with subheadings]

Write the complete {content_type} now:
"""

        return prompt

    def _generate_content(self, prompt: str, target_length: int) -> Dict[str, Any]:
        """Generate content using Hugging Face API"""

        try:
            url = f"{self.hf_api_url}/{self.model}"
            headers = {"Authorization": f"Bearer {self.hf_api_key}"}

            # Estimate tokens needed (rough: 1 word ≈ 1.3 tokens)
            max_tokens = min(2048, int(target_length * 1.5))

            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": max_tokens,
                    "temperature": 0.8,
                    "top_p": 0.9,
                    "do_sample": True,
                    "return_full_text": False
                }
            }

            logger.debug(f"Calling HF API: {self.model}")

            response = requests.post(url, headers=headers, json=payload, timeout=45)

            if response.status_code == 200:
                result = response.json()

                if isinstance(result, list) and len(result) > 0:
                    generated_text = result[0].get('generated_text', '')

                    return {
                        'success': True,
                        'text': generated_text
                    }

            logger.warning(f"HF API error: {response.status_code}")
            return self._fallback_content(prompt)

        except Exception as e:
            logger.error(f"Content generation failed: {e}")
            return self._fallback_content(prompt)

    def _fallback_content(self, prompt: str) -> Dict[str, Any]:
        """Generate simple content using templates (fallback)"""

        # Extract topic from prompt
        lines = prompt.split('\n')
        topic = "AI and Automation"
        for line in lines:
            if line.startswith('Topic:'):
                topic = line.split(':', 1)[1].strip()
                break

        content = f"""Headline: The Future of {topic}: What You Need to Know

Body:

## Introduction

{topic} is transforming how businesses operate in today's digital landscape. Companies that embrace these technologies early gain significant competitive advantages.

## Why {topic} Matters

In an increasingly competitive market, organizations need every advantage they can get. {topic} offers several key benefits:

- **Increased Efficiency**: Automate repetitive tasks and free your team for strategic work
- **Cost Savings**: Reduce operational costs while maintaining or improving quality
- **Scalability**: Handle growing workloads without proportional increases in resources
- **Better Insights**: Leverage data to make informed decisions faster

## Key Considerations

When implementing {topic}, keep these factors in mind:

1. **Start Small**: Begin with a pilot project to prove value before scaling
2. **Team Training**: Ensure your team understands and embraces the new technology
3. **Measure Results**: Track KPIs to demonstrate ROI and identify areas for improvement
4. **Stay Flexible**: Be ready to adapt as you learn what works best for your organization

## Real-World Applications

Leading companies are already seeing results with {topic}. From streamlining customer service to optimizing supply chains, the applications are virtually limitless.

## Conclusion

{topic} represents a significant opportunity for forward-thinking organizations. By starting today, you position your company for success in an increasingly automated future.

Ready to explore how {topic} can transform your business? Let's talk about your specific needs and goals.
"""

        return {
            'success': True,
            'text': content
        }

    def _parse_content(self, generated_text: str, content_type: str) -> Dict[str, str]:
        """Parse generated content into components"""

        parsed = {
            'headline': '',
            'body': ''
        }

        # Try to find headline
        lines = generated_text.split('\n')

        for i, line in enumerate(lines):
            if 'headline:' in line.lower():
                parsed['headline'] = line.split(':', 1)[1].strip()
                # Rest is body
                parsed['body'] = '\n'.join(lines[i+1:]).strip()
                break

        # If no explicit headline found, use first substantial line
        if not parsed['headline']:
            for line in lines:
                if len(line.strip()) > 20 and not line.strip().startswith('#'):
                    parsed['headline'] = line.strip()
                    # Find where body starts
                    body_start = lines.index(line) + 1
                    parsed['body'] = '\n'.join(lines[body_start:]).strip()
                    break

        # If still no body, use everything except headline
        if not parsed['body']:
            parsed['body'] = generated_text.replace(parsed['headline'], '').strip()

        # Clean up
        parsed['body'] = parsed['body'].replace('Body:', '').strip()

        return parsed

    def _generate_seo_metadata(
        self,
        topic: str,
        content: str,
        provided_keywords: List[str]
    ) -> Dict[str, Any]:
        """Generate SEO metadata"""

        # Meta description (first ~150 chars of content, cleaned)
        content_words = content.split()
        meta_desc = ' '.join(content_words[:25])
        if len(meta_desc) > 155:
            meta_desc = meta_desc[:152] + '...'

        # Extract keywords (combine provided + auto-extracted)
        keywords = list(provided_keywords) if provided_keywords else []

        # Simple keyword extraction: find capitalized words/phrases
        words = content.split()
        for i, word in enumerate(words):
            if word[0].isupper() and len(word) > 3:
                if word not in keywords and word.lower() not in ['the', 'this', 'that']:
                    keywords.append(word.lower())
                    if len(keywords) >= 10:
                        break

        # Generate tags (simplified)
        tags = [topic.lower()]
        if 'AI' in content or 'artificial intelligence' in content.lower():
            tags.append('artificial-intelligence')
        if 'automation' in content.lower():
            tags.append('automation')
        if 'business' in content.lower():
            tags.append('business')

        return {
            'meta_description': meta_desc,
            'keywords': keywords[:10],
            'tags': tags[:5]
        }

    def _estimate_reading_time(self, content: str) -> str:
        """Estimate reading time (assuming 200 words/minute)"""
        word_count = len(content.split())
        minutes = max(1, round(word_count / 200))

        return f"{minutes} min read"

    def _calculate_quality_score(
        self,
        parsed: Dict[str, str],
        input_data: Dict[str, Any]
    ) -> float:
        """Calculate content quality score (0-100)"""

        score = 0.0

        # 1. Has headline (15 points)
        if parsed['headline'] and len(parsed['headline']) > 20:
            score += 15

        # 2. Body length appropriate (30 points)
        word_count = len(parsed['body'].split())
        target = input_data.get('word_count', 600)

        if target * 0.8 <= word_count <= target * 1.2:
            score += 30
        elif target * 0.6 <= word_count <= target * 1.5:
            score += 20
        else:
            score += 10

        # 3. Structure (25 points)
        has_subheadings = '##' in parsed['body'] or '**' in parsed['body']
        has_paragraphs = parsed['body'].count('\n\n') >= 3

        if has_subheadings:
            score += 15
        if has_paragraphs:
            score += 10

        # 4. Keywords included (20 points)
        keywords = input_data.get('keywords', [])
        if keywords:
            content_lower = parsed['body'].lower()
            keyword_count = sum(1 for kw in keywords if kw.lower() in content_lower)
            score += min(20, keyword_count * 5)
        else:
            score += 10  # No keywords required

        # 5. Professional quality indicators (10 points)
        quality_indicators = [
            'however', 'therefore', 'additionally', 'furthermore',
            'key', 'important', 'significant', 'essential'
        ]
        body_lower = parsed['body'].lower()
        indicator_count = sum(1 for ind in quality_indicators if ind in body_lower)
        score += min(10, indicator_count * 2)

        return round(min(100, score), 2)


if __name__ == "__main__":
    """Test the Content Writing Agent"""

    agent = Phase2ContentWriterAgent()

    test_cases = [
        {
            'topic': 'AI Automation for Small Businesses',
            'content_type': 'blog_post',
            'audience': 'small business owners',
            'tone': 'conversational',
            'word_count': 600,
            'keywords': ['AI', 'automation', 'small business', 'productivity'],
            'key_points': [
                'Benefits of AI for small teams',
                'Common automation use cases',
                'Getting started with AI tools'
            ]
        },
        {
            'topic': 'Digital Avatars in Sales',
            'content_type': 'article',
            'audience': 'sales professionals',
            'tone': 'professional',
            'word_count': 800,
            'keywords': ['digital avatars', 'sales automation', 'AI agents']
        }
    ]

    print("=" * 80)
    print("PHASE 2 - CONTENT WRITING AGENT TEST")
    print("=" * 80)

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'─'*80}")
        print(f"Test {i}: {test_case['topic']}")
        print(f"Type: {test_case['content_type']} | Target: {test_case['word_count']} words")
        print(f"{'─'*80}")

        result = agent.process(test_case)

        if result.get('success'):
            print(f"\n📰 HEADLINE: {result['headline']}")
            print(f"\n📝 CONTENT:\n{result['body'][:500]}...")
            print(f"\n📊 Stats:")
            print(f"  - Word Count: {result['word_count']}")
            print(f"  - Reading Time: {result['estimated_reading_time']}")
            print(f"  - Quality Score: {result['quality_score']}/100")
            print(f"  - Keywords: {', '.join(result['keywords'][:5])}")
            print(f"  - Meta Description: {result['meta_description']}")
        else:
            print(f"❌ Error: {result.get('error')}")

    print(f"\n{'='*80}")
    print("Testing complete!")
    print("=" * 80)
