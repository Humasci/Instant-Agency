"""
Phase 2 - Social Media Manager Agent

Transforms content into platform-specific social media posts.

Models used:
- EleutherAI/gpt-neo-2.7B (text generation and adaptation)
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from base_agent import BaseAgent
from typing import Dict, Any, List
import requests
from datetime import datetime, timedelta
from loguru import logger


class Phase2SocialMediaAgent(BaseAgent):
    """
    Phase 2 Social Media Manager Agent

    Transforms content into platform-specific posts for:
    - LinkedIn (professional, B2B focus)
    - Twitter/X (concise, engaging)
    - Facebook (casual, community-focused)

    Includes hashtag generation, optimal posting times, and engagement hooks.
    """

    def __init__(self):
        config_path = os.path.join(
            os.path.dirname(__file__),
            'social/manager_config.yaml'
        )

        if not os.path.exists(os.path.dirname(config_path)):
            os.makedirs(os.path.dirname(config_path), exist_ok=True)

        if not os.path.exists(config_path):
            self._create_default_config(config_path)

        super().__init__(config_path)

        # Hugging Face configuration
        self.hf_api_url = "https://api-inference.huggingface.co/models"
        self.hf_api_key = os.getenv('HUGGINGFACE_API_KEY')
        self.model = "EleutherAI/gpt-neo-2.7B"

        # Platform specifications
        self.platform_specs = {
            'linkedin': {
                'max_length': 3000,
                'optimal_length': '150-300 words',
                'tone': 'professional, insightful',
                'best_times': ['Tuesday 10-11 AM', 'Wednesday 12 PM', 'Thursday 9-10 AM'],
                'hashtag_count': '3-5',
                'emoji_use': 'minimal, professional'
            },
            'twitter': {
                'max_length': 280,
                'optimal_length': '120-180 characters',
                'tone': 'concise, engaging, conversational',
                'best_times': ['Monday-Friday 8-10 AM', '12-1 PM', '5-6 PM'],
                'hashtag_count': '1-2',
                'emoji_use': 'moderate'
            },
            'facebook': {
                'max_length': 63206,
                'optimal_length': '40-80 words',
                'tone': 'friendly, community-focused',
                'best_times': ['Thursday-Friday 1-4 PM', 'Saturday 12-1 PM'],
                'hashtag_count': '2-3',
                'emoji_use': 'moderate to high'
            }
        }

    def _create_default_config(self, config_path: str):
        """Create default configuration"""
        config = {
            'agent': {
                'name': 'Social Media Manager Agent',
                'version': '2.0',
                'department': 'marketing',
                'description': 'Creates platform-specific social media posts'
            },
            'model': {
                'provider': 'huggingface',
                'model_name': 'EleutherAI/gpt-neo-2.7B',
                'temperature': 0.85,
                'max_tokens': 300
            },
            'memory': {
                'type': 'conversation',
                'ttl': 7200
            },
            'monitoring': {
                'log_level': 'INFO',
                'track_metrics': ['generation_time', 'engagement_score', 'posts_created']
            }
        }

        with open(config_path, 'w') as f:
            import yaml
            yaml.dump(config, f)

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate social media posts

        Args:
            input_data: Dict with keys:
                - content: Source content (blog post, article, etc.)
                - platforms: List of platforms ['linkedin', 'twitter', 'facebook']
                - topic: Main topic/theme
                - target_audience: Target audience description
                - cta: Optional call-to-action
                - link: Optional link to include

        Returns:
            Dict with posts for each platform
        """
        start_time = datetime.now()

        try:
            content = input_data.get('content', input_data.get('topic', ''))
            if not content:
                return {'error': 'content or topic is required', 'success': False}

            platforms = input_data.get('platforms', ['linkedin', 'twitter', 'facebook'])
            topic = input_data.get('topic', 'AI and Automation')
            target_audience = input_data.get('target_audience', 'business professionals')
            cta = input_data.get('cta', '')
            link = input_data.get('link', '')

            logger.info(f"Generating social posts for {len(platforms)} platforms")

            # Check cache
            cache_key = f"social:{topic.lower().replace(' ', '_')[:50]}:{','.join(sorted(platforms))}"
            cached_result = self.cache_get(cache_key)
            if cached_result:
                logger.info(f"Returning cached social posts")
                return cached_result

            # Generate posts for each platform
            platform_posts = {}
            for platform in platforms:
                if platform not in self.platform_specs:
                    logger.warning(f"Unknown platform: {platform}, skipping")
                    continue

                post = self._generate_platform_post(
                    content=content,
                    platform=platform,
                    topic=topic,
                    target_audience=target_audience,
                    cta=cta,
                    link=link
                )

                platform_posts[platform] = post

            if not platform_posts:
                return {'error': 'No valid platforms specified', 'success': False}

            # Calculate overall engagement score
            avg_engagement_score = sum(p['engagement_score'] for p in platform_posts.values()) / len(platform_posts)

            # Compile result
            result = {
                'success': True,
                'topic': topic,
                'platforms': platform_posts,
                'average_engagement_score': round(avg_engagement_score, 2),
                'generated_at': datetime.now().isoformat(),
                'agent_version': self.version
            }

            # Cache result
            self.cache_set(cache_key, result, ttl=7200)

            # Log interaction
            self.log_interaction(input_data, result, {
                'platforms': list(platforms),
                'engagement_score': avg_engagement_score
            })

            # Track metrics
            generation_time = (datetime.now() - start_time).total_seconds()
            self.track_metric('generation_time', generation_time)
            self.track_metric('engagement_score', avg_engagement_score)
            self.track_metric('posts_created', len(platform_posts))

            logger.info(f"Social posts generated for {len(platform_posts)} platforms")

            return result

        except Exception as e:
            logger.error(f"Social post generation failed: {e}")
            return {'error': str(e), 'success': False}

    def _generate_platform_post(
        self,
        content: str,
        platform: str,
        topic: str,
        target_audience: str,
        cta: str,
        link: str
    ) -> Dict[str, Any]:
        """Generate post for specific platform"""

        specs = self.platform_specs[platform]

        # Build prompt
        prompt = self._build_platform_prompt(
            content=content,
            platform=platform,
            topic=topic,
            target_audience=target_audience,
            cta=cta,
            link=link,
            specs=specs
        )

        # Generate post
        generated = self._generate_post(prompt, platform)

        if not generated['success']:
            # Fallback to template
            generated = self._template_based_post(content, platform, topic, link)

        # Parse and enhance post
        post_text = generated['text']
        hashtags = self._generate_hashtags(topic, platform)
        post_with_hashtags = self._add_hashtags(post_text, hashtags, platform)

        # Get optimal posting time
        best_time = self._get_next_optimal_time(platform)

        # Calculate engagement score
        engagement_score = self._calculate_engagement_score(post_with_hashtags, platform)

        return {
            'platform': platform,
            'post_text': post_with_hashtags,
            'character_count': len(post_with_hashtags),
            'hashtags': hashtags,
            'optimal_posting_time': best_time,
            'engagement_score': engagement_score,
            'link': link
        }

    def _build_platform_prompt(
        self,
        content: str,
        platform: str,
        topic: str,
        target_audience: str,
        cta: str,
        link: str,
        specs: Dict[str, Any]
    ) -> str:
        """Build prompt for platform-specific post generation"""

        # Truncate content if too long
        content_preview = content[:500] if len(content) > 500 else content

        prompt = f"""Transform the following content into a {platform} post:

Source Content:
{content_preview}

Platform: {platform}
Topic: {topic}
Target Audience: {target_audience}
Tone: {specs['tone']}
Optimal Length: {specs['optimal_length']}
Emoji Usage: {specs['emoji_use']}

Requirements:
1. {specs['tone']} tone
2. Length: {specs['optimal_length']}
3. Engaging hook in first line
4. Platform-appropriate formatting
"""

        if platform == 'linkedin':
            prompt += """5. Professional insights or takeaway
6. Thought-provoking question or discussion prompt
7. Maximum 1-2 emojis if at all
"""
        elif platform == 'twitter':
            prompt += """5. Concise and punchy
6. Strong hook in first 120 characters
7. 1-2 relevant emojis
8. Thread-starter if complex topic
"""
        elif platform == 'facebook':
            prompt += """5. Community-focused language
6. Personal or relatable angle
7. Encourage comments and sharing
8. 2-3 relevant emojis
"""

        if cta:
            prompt += f"9. Include CTA: {cta}\n"

        if link:
            prompt += f"10. Include link: {link}\n"

        prompt += "\nWrite the post now (without hashtags, those will be added separately):\n"

        return prompt

    def _generate_post(self, prompt: str, platform: str) -> Dict[str, Any]:
        """Generate post using Hugging Face API"""

        try:
            url = f"{self.hf_api_url}/{self.model}"
            headers = {"Authorization": f"Bearer {self.hf_api_key}"}

            max_tokens = 150 if platform == 'twitter' else 300

            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": max_tokens,
                    "temperature": 0.85,
                    "top_p": 0.95,
                    "do_sample": True,
                    "return_full_text": False
                }
            }

            response = requests.post(url, headers=headers, json=payload, timeout=20)

            if response.status_code == 200:
                result = response.json()

                if isinstance(result, list) and len(result) > 0:
                    text = result[0].get('generated_text', '').strip()

                    # Clean up the text
                    text = self._clean_post_text(text, platform)

                    return {'success': True, 'text': text}

            return {'success': False}

        except Exception as e:
            logger.error(f"Post generation failed: {e}")
            return {'success': False}

    def _template_based_post(self, content: str, platform: str, topic: str, link: str) -> Dict[str, str]:
        """Generate post using templates (fallback)"""

        templates = {
            'linkedin': f"""The future of {topic} is here, and it's transforming how businesses operate.

{content[:200] if len(content) > 200 else content}...

What's your take on this? How is your organization approaching {topic}?

{link}""",

            'twitter': f"""The {topic} revolution is here 🚀

Companies leveraging these tools are seeing incredible results.

What's your experience?

{link}""",

            'facebook': f"""Exciting developments in {topic}!

{content[:150] if len(content) > 150 else content}...

Have you tried any of these tools? Share your experience in the comments! 👇

{link}"""
        }

        text = templates.get(platform, content[:280])

        return {'success': True, 'text': text}

    def _clean_post_text(self, text: str, platform: str) -> str:
        """Clean and format post text"""

        # Remove common artifacts
        text = text.replace('Post:', '').replace(f'{platform}:', '').strip()

        # Ensure proper length
        specs = self.platform_specs[platform]
        max_len = specs['max_length']

        if len(text) > max_len:
            # Truncate and add ellipsis
            text = text[:max_len-3] + '...'

        return text

    def _generate_hashtags(self, topic: str, platform: str) -> List[str]:
        """Generate relevant hashtags"""

        specs = self.platform_specs[platform]
        hashtag_range = specs['hashtag_count'].split('-')
        max_hashtags = int(hashtag_range[-1])

        # Base hashtags from topic
        hashtags = []

        # Split topic into words and create hashtags
        words = topic.split()
        for word in words:
            if len(word) > 3:
                hashtags.append(f"#{word.capitalize()}")

        # Add common industry hashtags
        industry_tags = ['#AI', '#Automation', '#Technology', '#Innovation', '#DigitalTransformation']

        if platform == 'linkedin':
            industry_tags.extend(['#Business', '#Leadership', '#B2B'])
        elif platform == 'twitter':
            industry_tags.extend(['#Tech', '#Startup', '#SaaS'])
        elif platform == 'facebook':
            industry_tags.extend(['#SmallBusiness', '#Entrepreneur'])

        # Combine and limit
        all_tags = list(set(hashtags + industry_tags))
        return all_tags[:max_hashtags]

    def _add_hashtags(self, post_text: str, hashtags: List[str], platform: str) -> str:
        """Add hashtags to post"""

        if platform == 'twitter':
            # Twitter: hashtags inline or at end
            return f"{post_text}\n\n{' '.join(hashtags[:2])}"
        else:
            # LinkedIn/Facebook: hashtags at end
            return f"{post_text}\n\n{' '.join(hashtags)}"

    def _get_next_optimal_time(self, platform: str) -> str:
        """Get next optimal posting time for platform"""

        specs = self.platform_specs[platform]
        best_times = specs['best_times']

        # For demo, just return the first option with "tomorrow"
        tomorrow = (datetime.now() + timedelta(days=1)).strftime('%A')

        return f"{tomorrow} {best_times[0]}"

    def _calculate_engagement_score(self, post_text: str, platform: str) -> float:
        """Calculate predicted engagement score (0-100)"""

        score = 0.0

        # 1. Length appropriateness (30 points)
        specs = self.platform_specs[platform]
        char_count = len(post_text)

        if platform == 'twitter':
            if 120 <= char_count <= 200:
                score += 30
            elif 100 <= char_count <= 280:
                score += 20
        elif platform == 'linkedin':
            word_count = len(post_text.split())
            if 150 <= word_count <= 300:
                score += 30
            elif 100 <= word_count <= 400:
                score += 20
        else:  # facebook
            word_count = len(post_text.split())
            if 40 <= word_count <= 80:
                score += 30
            elif 30 <= word_count <= 100:
                score += 20

        # 2. Engagement hooks (25 points)
        hooks = ['?', '!', 'you', 'your', 'how', 'what', 'why']
        hook_count = sum(1 for hook in hooks if hook in post_text.lower())
        score += min(25, hook_count * 5)

        # 3. Hashtags (20 points)
        hashtag_count = post_text.count('#')
        if hashtag_count >= 3:
            score += 20
        elif hashtag_count >= 2:
            score += 15
        elif hashtag_count >= 1:
            score += 10

        # 4. Emojis (15 points)
        # Simple check for emoji presence
        has_emoji = any(ord(c) > 127 for c in post_text)
        if has_emoji:
            score += 15

        # 5. CTA (10 points)
        cta_words = ['learn', 'discover', 'read', 'check', 'click', 'share', 'comment', 'join']
        if any(word in post_text.lower() for word in cta_words):
            score += 10

        return round(min(100, score), 2)


if __name__ == "__main__":
    """Test the Social Media Manager Agent"""

    agent = Phase2SocialMediaAgent()

    test_content = """
    AI-powered automation is revolutionizing how businesses operate. Companies using AI agents
    are seeing 70% reduction in manual tasks and 3x faster response times.

    The key is starting small - focus on one repetitive process, automate it with AI, measure
    results, then scale. Digital avatars and intelligent agents can handle everything from lead
    qualification to customer support.

    Ready to transform your business with AI?
    """

    test_cases = [
        {
            'content': test_content,
            'topic': 'AI Automation for Business',
            'platforms': ['linkedin'],
            'target_audience': 'B2B decision makers',
            'cta': 'Learn more about AI agents',
            'link': 'https://instant-agency.ai/blog/ai-automation'
        },
        {
            'content': test_content,
            'topic': 'Digital Avatars in Sales',
            'platforms': ['twitter', 'facebook'],
            'target_audience': 'sales professionals',
            'link': 'https://instant-agency.ai/avatars'
        }
    ]

    print("=" * 80)
    print("PHASE 2 - SOCIAL MEDIA MANAGER AGENT TEST")
    print("=" * 80)

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'─'*80}")
        print(f"Test {i}: {test_case['topic']}")
        print(f"Platforms: {', '.join(test_case['platforms'])}")
        print(f"{'─'*80}")

        result = agent.process(test_case)

        if result.get('success'):
            for platform, post_data in result['platforms'].items():
                print(f"\n📱 {platform.upper()}:")
                print(f"{'─'*60}")
                print(post_data['post_text'])
                print(f"\n📊 Stats:")
                print(f"  - Characters: {post_data['character_count']}")
                print(f"  - Hashtags: {', '.join(post_data['hashtags'])}")
                print(f"  - Engagement Score: {post_data['engagement_score']}/100")
                print(f"  - Best time: {post_data['optimal_posting_time']}")
        else:
            print(f"❌ Error: {result.get('error')}")

    print(f"\n{'='*80}")
    print("Testing complete!")
    print("=" * 80)
