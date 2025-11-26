"""
Twitter API Integration for SIX3 Agency

Handles:
- Publishing tweets and threads
- Scheduling tweets for optimal engagement
- Analytics and engagement tracking
- Hashtag research and trending topics
- Direct message automation
- Twitter Lists management

Requirements:
- Twitter API v2 access (Developer account)
- tweepy Python package
- Valid Twitter API credentials
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
import json
import re

try:
    import tweepy
    TWEEPY_AVAILABLE = True
except ImportError:
    TWEEPY_AVAILABLE = False

logger = logging.getLogger(__name__)


class TwitterIntegration:
    """Twitter API integration for automated posting and engagement"""
    
    def __init__(self, 
                 consumer_key: Optional[str] = None,
                 consumer_secret: Optional[str] = None,
                 access_token: Optional[str] = None,
                 access_token_secret: Optional[str] = None,
                 bearer_token: Optional[str] = None):
        """
        Initialize Twitter integration
        
        Args:
            consumer_key: Twitter API consumer key
            consumer_secret: Twitter API consumer secret
            access_token: Twitter access token
            access_token_secret: Twitter access token secret
            bearer_token: Twitter bearer token (for API v2)
        """
        if not TWEEPY_AVAILABLE:
            raise ImportError("Tweepy package not installed. Run: pip install tweepy")
        
        # Get credentials from environment if not provided
        self.consumer_key = consumer_key or os.getenv('TWITTER_CONSUMER_KEY')
        self.consumer_secret = consumer_secret or os.getenv('TWITTER_CONSUMER_SECRET')
        self.access_token = access_token or os.getenv('TWITTER_ACCESS_TOKEN')
        self.access_token_secret = access_token_secret or os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
        self.bearer_token = bearer_token or os.getenv('TWITTER_BEARER_TOKEN')
        
        # Check required credentials
        if not all([self.consumer_key, self.consumer_secret, self.access_token, self.access_token_secret]):
            raise ValueError("Missing Twitter API credentials. Set environment variables: TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET")
        
        # Initialize Twitter API clients
        try:
            # API v1.1 client (for posting, DMs, etc.)
            auth = tweepy.OAuthHandler(self.consumer_key, self.consumer_secret)
            auth.set_access_token(self.access_token, self.access_token_secret)
            self.api = tweepy.API(auth, wait_on_rate_limit=True)
            
            # API v2 client (for advanced features)
            if self.bearer_token:
                self.client = tweepy.Client(
                    bearer_token=self.bearer_token,
                    consumer_key=self.consumer_key,
                    consumer_secret=self.consumer_secret,
                    access_token=self.access_token,
                    access_token_secret=self.access_token_secret,
                    wait_on_rate_limit=True
                )
            else:
                self.client = None
                logger.warning("No bearer token provided - some v2 API features will be unavailable")
            
            # Get user info for validation
            self.user_info = self.api.verify_credentials()
            logger.info(f"Twitter integration initialized for user: @{self.user_info.screen_name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Twitter API: {str(e)}")
            raise
    
    def post_tweet(self, text: str, media_paths: List[str] = None, reply_to: str = None) -> Dict[str, Any]:
        """
        Post a tweet
        
        Args:
            text: Tweet content (max 280 characters)
            media_paths: List of file paths for images/videos to attach
            reply_to: Tweet ID to reply to
            
        Returns:
            Dict with tweet posting response
        """
        try:
            # Truncate text if too long
            if len(text) > 280:
                text = text[:277] + "..."
            
            # Upload media if provided
            media_ids = []
            if media_paths:
                for media_path in media_paths:
                    if os.path.exists(media_path):
                        media = self.api.media_upload(media_path)
                        media_ids.append(media.media_id)
                    else:
                        logger.warning(f"Media file not found: {media_path}")
            
            # Post tweet
            tweet_kwargs = {
                'status': text,
                'media_ids': media_ids if media_ids else None
            }
            
            if reply_to:
                tweet_kwargs['in_reply_to_status_id'] = reply_to
                tweet_kwargs['auto_populate_reply_metadata'] = True
            
            tweet = self.api.update_status(**{k: v for k, v in tweet_kwargs.items() if v is not None})
            
            return {
                'success': True,
                'tweet_id': str(tweet.id),
                'tweet_url': f"https://twitter.com/{tweet.user.screen_name}/status/{tweet.id}",
                'text': tweet.text,
                'created_at': tweet.created_at.isoformat(),
                'retweet_count': tweet.retweet_count,
                'favorite_count': tweet.favorite_count,
                'media_count': len(media_ids),
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to post tweet: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'text': text,
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def post_thread(self, texts: List[str], media_paths: List[str] = None) -> Dict[str, Any]:
        """
        Post a Twitter thread (multiple connected tweets)
        
        Args:
            texts: List of tweet texts for the thread
            media_paths: Optional list of media files (one per tweet)
            
        Returns:
            Dict with thread posting response
        """
        try:
            thread_tweets = []
            reply_to = None
            
            for i, text in enumerate(texts):
                # Get media for this tweet if provided
                tweet_media = [media_paths[i]] if media_paths and i < len(media_paths) else None
                
                # Add thread numbering if multiple tweets
                if len(texts) > 1:
                    text = f"{text}\n\n({i + 1}/{len(texts)})"
                
                result = self.post_tweet(text, tweet_media, reply_to)
                
                if result['success']:
                    thread_tweets.append(result)
                    reply_to = result['tweet_id']
                else:
                    # If any tweet fails, return the error
                    return {
                        'success': False,
                        'error': f"Failed at tweet {i + 1}: {result['error']}",
                        'completed_tweets': thread_tweets,
                        'timestamp': datetime.utcnow().isoformat()
                    }
            
            return {
                'success': True,
                'thread_length': len(thread_tweets),
                'tweets': thread_tweets,
                'first_tweet_url': thread_tweets[0]['tweet_url'] if thread_tweets else None,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to post thread: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def get_tweet_analytics(self, tweet_id: str) -> Dict[str, Any]:
        """
        Get analytics for a specific tweet
        
        Args:
            tweet_id: Twitter tweet ID
            
        Returns:
            Dict with tweet analytics
        """
        try:
            tweet = self.api.get_status(tweet_id, tweet_mode='extended')
            
            # Additional metrics via v2 API if available
            v2_metrics = {}
            if self.client:
                try:
                    v2_tweet = self.client.get_tweet(
                        tweet_id, 
                        tweet_fields=['public_metrics', 'created_at', 'context_annotations']
                    )
                    if v2_tweet.data:
                        v2_metrics = v2_tweet.data.public_metrics or {}
                except Exception as e:
                    logger.warning(f"Could not get v2 metrics: {str(e)}")
            
            return {
                'success': True,
                'tweet_id': tweet_id,
                'created_at': tweet.created_at.isoformat(),
                'text': tweet.full_text,
                'metrics': {
                    'retweets': v2_metrics.get('retweet_count', tweet.retweet_count),
                    'likes': v2_metrics.get('like_count', tweet.favorite_count),
                    'replies': v2_metrics.get('reply_count', 0),
                    'quotes': v2_metrics.get('quote_count', 0),
                    'impressions': v2_metrics.get('impression_count', 0)
                },
                'engagement_rate': self._calculate_engagement_rate(v2_metrics or {
                    'retweet_count': tweet.retweet_count,
                    'like_count': tweet.favorite_count,
                    'reply_count': 0,
                    'impression_count': 1  # Avoid division by zero
                }),
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get tweet analytics for {tweet_id}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'tweet_id': tweet_id,
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def search_tweets(self, query: str, count: int = 10, result_type: str = "recent") -> Dict[str, Any]:
        """
        Search for tweets matching a query
        
        Args:
            query: Search query
            count: Number of tweets to return
            result_type: Type of results ("recent", "popular", "mixed")
            
        Returns:
            Dict with search results
        """
        try:
            tweets = tweepy.Cursor(
                self.api.search_tweets,
                q=query,
                result_type=result_type,
                tweet_mode='extended',
                include_entities=True
            ).items(count)
            
            search_results = []
            for tweet in tweets:
                search_results.append({
                    'id': str(tweet.id),
                    'text': tweet.full_text,
                    'author': tweet.user.screen_name,
                    'author_name': tweet.user.name,
                    'created_at': tweet.created_at.isoformat(),
                    'retweets': tweet.retweet_count,
                    'likes': tweet.favorite_count,
                    'url': f"https://twitter.com/{tweet.user.screen_name}/status/{tweet.id}"
                })
            
            return {
                'success': True,
                'query': query,
                'count': len(search_results),
                'tweets': search_results,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to search tweets: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'query': query,
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def get_trending_hashtags(self, location_id: int = 1) -> Dict[str, Any]:
        """
        Get trending hashtags for a location
        
        Args:
            location_id: WOEID for location (1 = Worldwide, 23424977 = USA)
            
        Returns:
            Dict with trending hashtags
        """
        try:
            trends = self.api.get_place_trends(location_id)
            
            if trends:
                trend_data = trends[0]
                hashtags = []
                
                for trend in trend_data['trends']:
                    if trend['name'].startswith('#'):
                        hashtags.append({
                            'hashtag': trend['name'],
                            'url': trend['url'],
                            'tweet_volume': trend.get('tweet_volume'),
                            'promoted': trend.get('promoted_content', False)
                        })
                
                return {
                    'success': True,
                    'location': trend_data['locations'][0]['name'],
                    'as_of': trend_data['as_of'],
                    'hashtags': hashtags[:10],  # Top 10 hashtags
                    'total_trends': len(trend_data['trends']),
                    'timestamp': datetime.utcnow().isoformat()
                }
            else:
                return {
                    'success': False,
                    'error': 'No trends data available',
                    'timestamp': datetime.utcnow().isoformat()
                }
            
        except Exception as e:
            logger.error(f"Failed to get trending hashtags: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def send_direct_message(self, recipient_screen_name: str, message: str) -> Dict[str, Any]:
        """
        Send a direct message to a user
        
        Args:
            recipient_screen_name: Recipient's Twitter handle (without @)
            message: Message content
            
        Returns:
            Dict with DM sending response
        """
        try:
            # Get recipient user ID
            recipient_user = self.api.get_user(screen_name=recipient_screen_name)
            recipient_id = recipient_user.id
            
            # Send DM
            dm = self.api.send_direct_message(recipient_id, message)
            
            return {
                'success': True,
                'message_id': str(dm.id),
                'recipient': recipient_screen_name,
                'message': message,
                'created_at': dm.created_at.isoformat(),
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to send DM to @{recipient_screen_name}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'recipient': recipient_screen_name,
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def get_user_timeline(self, screen_name: str = None, count: int = 10) -> Dict[str, Any]:
        """
        Get user's timeline tweets
        
        Args:
            screen_name: User's screen name (if None, gets own timeline)
            count: Number of tweets to return
            
        Returns:
            Dict with timeline tweets
        """
        try:
            if screen_name:
                tweets = self.api.user_timeline(
                    screen_name=screen_name,
                    count=count,
                    tweet_mode='extended',
                    exclude_replies=True,
                    include_rts=False
                )
            else:
                tweets = self.api.user_timeline(
                    count=count,
                    tweet_mode='extended',
                    exclude_replies=True,
                    include_rts=False
                )
            
            timeline = []
            for tweet in tweets:
                timeline.append({
                    'id': str(tweet.id),
                    'text': tweet.full_text,
                    'created_at': tweet.created_at.isoformat(),
                    'retweets': tweet.retweet_count,
                    'likes': tweet.favorite_count,
                    'url': f"https://twitter.com/{tweet.user.screen_name}/status/{tweet.id}",
                    'hashtags': [tag['text'] for tag in tweet.entities.get('hashtags', [])],
                    'mentions': [mention['screen_name'] for mention in tweet.entities.get('user_mentions', [])]
                })
            
            return {
                'success': True,
                'user': screen_name or self.user_info.screen_name,
                'count': len(timeline),
                'tweets': timeline,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get user timeline: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'user': screen_name,
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def _calculate_engagement_rate(self, metrics: Dict[str, int]) -> float:
        """Calculate engagement rate from metrics"""
        impressions = metrics.get('impression_count', 1)
        engagements = (
            metrics.get('like_count', 0) +
            metrics.get('retweet_count', 0) +
            metrics.get('reply_count', 0) +
            metrics.get('quote_count', 0)
        )
        return round((engagements / impressions) * 100, 2) if impressions > 0 else 0
    
    def test_connection(self) -> Dict[str, Any]:
        """
        Test the Twitter API connection
        
        Returns:
            Dict with connection test results
        """
        try:
            user = self.api.verify_credentials()
            
            return {
                'success': True,
                'connection_status': 'connected',
                'username': user.screen_name,
                'display_name': user.name,
                'user_id': str(user.id),
                'followers_count': user.followers_count,
                'following_count': user.friends_count,
                'tweets_count': user.statuses_count,
                'api_v1_access': True,
                'api_v2_access': self.client is not None,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Twitter connection test failed: {str(e)}")
            return {
                'success': False,
                'connection_status': 'failed',
                'error': str(e),
                'api_v1_access': False,
                'api_v2_access': False,
                'timestamp': datetime.utcnow().isoformat()
            }


class TwitterPostTemplates:
    """Pre-built Twitter post templates for common business use cases"""
    
    @staticmethod
    def product_launch(product_name: str, key_benefit: str, hashtags: List[str] = None) -> str:
        """Generate product launch tweet"""
        tags = ' '.join([f'#{tag}' for tag in (hashtags or ['ProductLaunch', 'Innovation', 'AI'])])
        return f"🚀 Introducing {product_name}!\n\n{key_benefit}\n\nReady to revolutionize how you work?\n\n{tags}"
    
    @staticmethod
    def thought_leadership(insight: str, hashtags: List[str] = None) -> str:
        """Generate thought leadership tweet"""
        tags = ' '.join([f'#{tag}' for tag in (hashtags or ['ThoughtLeadership', 'Business', 'Innovation'])])
        return f"💡 {insight}\n\n{tags}"
    
    @staticmethod
    def industry_news_comment(news_summary: str, opinion: str, hashtags: List[str] = None) -> str:
        """Generate industry news commentary tweet"""
        tags = ' '.join([f'#{tag}' for tag in (hashtags or ['Industry', 'News', 'Analysis'])])
        return f"📰 {news_summary}\n\n🤔 My take: {opinion}\n\n{tags}"
    
    @staticmethod
    def customer_success_story(customer_result: str, hashtags: List[str] = None) -> str:
        """Generate customer success story tweet"""
        tags = ' '.join([f'#{tag}' for tag in (hashtags or ['CustomerSuccess', 'Results', 'AI'])])
        return f"🎉 Customer Success Story:\n\n{customer_result}\n\nLove seeing our clients achieve amazing results!\n\n{tags}"
    
    @staticmethod
    def educational_thread_starter(topic: str, thread_length: int = 5) -> str:
        """Generate educational thread starter"""
        return f"🧵 THREAD: Everything you need to know about {topic}\n\nA {thread_length}-part breakdown 👇\n\n(1/{thread_length})"
    
    @staticmethod
    def engagement_question(question: str, context: str = None) -> str:
        """Generate engagement-focused question tweet"""
        context_text = f"{context}\n\n" if context else ""
        return f"{context_text}❓ {question}\n\nDrop your thoughts in the replies! 👇\n\n#Community #Discussion"


# Usage example
if __name__ == "__main__":
    # Example usage (requires Twitter API credentials in environment variables)
    import os
    
    if all([
        os.getenv('TWITTER_CONSUMER_KEY'),
        os.getenv('TWITTER_CONSUMER_SECRET'),
        os.getenv('TWITTER_ACCESS_TOKEN'),
        os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
    ]):
        twitter = TwitterIntegration()
        
        # Test connection
        test_result = twitter.test_connection()
        print("Connection test:", test_result)
        
        # Create a test tweet
        if test_result.get('success'):
            tweet_content = TwitterPostTemplates.thought_leadership(
                "The future of business lies in AI that augments human creativity, not replaces it.",
                ['AI', 'Future', 'Business']
            )
            
            result = twitter.post_tweet(tweet_content)
            print("Tweet posting result:", result)
    else:
        print("Set Twitter API credentials in environment variables to test integration")