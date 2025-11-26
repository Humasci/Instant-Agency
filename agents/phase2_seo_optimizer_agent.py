"""
Phase 2 SEO Optimization Agent

Capabilities:
- Keyword research and analysis
- Content SEO optimization
- Competitor analysis
- Technical SEO audit
- SERP analysis and tracking
- Content gap identification
- Meta tag optimization
- Schema markup suggestions

This agent helps optimize content for search engines and improve organic visibility.
"""

import os
import sys
import logging
import json
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
import re
import requests
from urllib.parse import urljoin, urlparse
import time

# Add the project root to the path so we can import from other directories
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from base_agent import BaseAgent

try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False
    print("Warning: BeautifulSoup4 not available. Install with: pip install beautifulsoup4")

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("Warning: requests not available. Install with: pip install requests")

try:
    from urllib.parse import urlparse, quote_plus
    import xml.etree.ElementTree as ET
    from collections import Counter
    import hashlib
    EXTENDED_LIBS_AVAILABLE = True
except ImportError:
    EXTENDED_LIBS_AVAILABLE = False


class SEOOptimizerAgent(BaseAgent):
    """
    Phase 2 SEO Optimization Agent
    
    Provides comprehensive SEO analysis and optimization recommendations
    for content and websites.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """Initialize the SEO Optimizer Agent"""
        
        agent_config = {
            "name": "SEO Optimizer Agent",
            "description": "Optimizes content and websites for search engine visibility",
            "version": "2.0",
            "capabilities": [
                "keyword_research",
                "content_optimization",
                "technical_seo_audit",
                "competitor_analysis",
                "serp_analysis",
                "meta_optimization",
                "schema_markup",
                "content_gap_analysis"
            ]
        }
        
        if config:
            agent_config.update(config)
            
        super().__init__(agent_config)
        
        # SEO configuration
        self.max_title_length = 60
        self.max_meta_description_length = 160
        self.max_h1_length = 70
        self.optimal_keyword_density = 0.02  # 2%
        self.max_keyword_density = 0.04  # 4%
        
        # Common stop words for keyword analysis
        self.stop_words = {
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
            'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
            'to', 'was', 'will', 'with', 'the', 'this', 'but', 'they', 'have',
            'had', 'what', 'said', 'each', 'which', 'their', 'time', 'if',
            'up', 'out', 'many', 'then', 'them', 'can', 'would'
        }
        
        # Initialize API configurations for free services
        self.google_trends_url = "https://trends.google.com/trends/api"
        self.serp_user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0"
        ]
        
        self.logger.info(f"SEO Optimizer Agent initialized with enhanced APIs")
    
    def research_keywords(self, 
                         seed_keyword: str, 
                         industry: str = None,
                         target_audience: str = None,
                         competition_level: str = "medium") -> Dict[str, Any]:
        """
        Research keywords related to a seed keyword
        
        Args:
            seed_keyword: Main keyword to research
            industry: Target industry context
            target_audience: Audience description
            competition_level: "low", "medium", "high"
            
        Returns:
            Dict with keyword research results
        """
        try:
            self.logger.info(f"Researching keywords for: {seed_keyword}")
            
            # Generate keyword variations and suggestions
            keyword_variations = self._generate_keyword_variations(seed_keyword, industry)
            long_tail_keywords = self._generate_long_tail_keywords(seed_keyword, target_audience)
            related_keywords = self._generate_related_keywords(seed_keyword, industry)
            
            # Analyze keyword metrics (simulated for now - in production, would use real SEO APIs)
            keyword_analysis = []
            
            all_keywords = keyword_variations + long_tail_keywords + related_keywords
            for keyword in all_keywords[:20]:  # Limit to top 20 keywords
                analysis = self._analyze_keyword_metrics(keyword, competition_level)
                keyword_analysis.append(analysis)
            
            # Sort by potential value (volume / difficulty ratio)
            keyword_analysis.sort(key=lambda x: x.get('potential_score', 0), reverse=True)
            
            # Generate keyword strategy
            strategy = self._generate_keyword_strategy(keyword_analysis, target_audience)
            
            result = {
                'seed_keyword': seed_keyword,
                'industry': industry,
                'target_audience': target_audience,
                'total_keywords_found': len(keyword_analysis),
                'primary_keywords': keyword_analysis[:5],
                'secondary_keywords': keyword_analysis[5:15],
                'long_tail_opportunities': [k for k in keyword_analysis if k.get('word_count', 0) >= 3][:10],
                'strategy': strategy,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Log metrics
            self.log_metrics("keywords_researched", len(keyword_analysis))
            self.log_metrics("research_requests", 1)
            
            return {
                'success': True,
                'agent': self.name,
                'data': result
            }
            
        except Exception as e:
            self.logger.error(f"Keyword research failed: {str(e)}")
            return {
                'success': False,
                'agent': self.name,
                'error': str(e),
                'seed_keyword': seed_keyword
            }
    
    def optimize_content(self, 
                        content: str, 
                        target_keyword: str,
                        content_type: str = "blog_post",
                        target_audience: str = None) -> Dict[str, Any]:
        """
        Optimize content for SEO
        
        Args:
            content: Content to optimize
            target_keyword: Primary keyword to optimize for
            content_type: "blog_post", "product_page", "landing_page"
            target_audience: Target audience description
            
        Returns:
            Dict with optimization recommendations
        """
        try:
            self.logger.info(f"Optimizing content for keyword: {target_keyword}")
            
            # Analyze current content
            content_analysis = self._analyze_content_structure(content)
            keyword_analysis = self._analyze_keyword_usage(content, target_keyword)
            readability_analysis = self._analyze_readability(content)
            
            # Generate optimization recommendations
            recommendations = self._generate_seo_recommendations(
                content, target_keyword, content_analysis, keyword_analysis, content_type
            )
            
            # Generate optimized versions
            optimized_title = self._optimize_title(content, target_keyword)
            optimized_meta_description = self._optimize_meta_description(content, target_keyword)
            optimized_headings = self._optimize_headings(content, target_keyword)
            
            # Calculate SEO score
            seo_score = self._calculate_seo_score(
                content_analysis, keyword_analysis, readability_analysis
            )
            
            result = {
                'target_keyword': target_keyword,
                'content_type': content_type,
                'current_analysis': {
                    'word_count': content_analysis['word_count'],
                    'keyword_density': keyword_analysis['density'],
                    'readability_score': readability_analysis['score'],
                    'seo_score': seo_score
                },
                'recommendations': recommendations,
                'optimized_elements': {
                    'title': optimized_title,
                    'meta_description': optimized_meta_description,
                    'headings': optimized_headings
                },
                'keyword_analysis': keyword_analysis,
                'improvement_potential': self._calculate_improvement_potential(seo_score),
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Log metrics
            self.log_metrics("content_optimizations", 1)
            self.log_metrics("seo_score_generated", seo_score)
            
            return {
                'success': True,
                'agent': self.name,
                'data': result
            }
            
        except Exception as e:
            self.logger.error(f"Content optimization failed: {str(e)}")
            return {
                'success': False,
                'agent': self.name,
                'error': str(e),
                'target_keyword': target_keyword
            }
    
    def audit_technical_seo(self, url: str) -> Dict[str, Any]:
        """
        Perform technical SEO audit of a webpage
        
        Args:
            url: URL to audit
            
        Returns:
            Dict with technical SEO audit results
        """
        try:
            self.logger.info(f"Performing technical SEO audit for: {url}")
            
            if not REQUESTS_AVAILABLE or not BS4_AVAILABLE:
                return {
                    'success': False,
                    'error': 'Required packages not available. Install requests and beautifulsoup4',
                    'url': url
                }
            
            # Fetch page content
            page_data = self._fetch_page_data(url)
            if not page_data['success']:
                return page_data
            
            soup = BeautifulSoup(page_data['content'], 'html.parser')
            
            # Perform various technical checks
            audit_results = {
                'url': url,
                'response_code': page_data['status_code'],
                'load_time': page_data['load_time'],
                'page_size': len(page_data['content']),
                'meta_tags': self._audit_meta_tags(soup),
                'headings': self._audit_heading_structure(soup),
                'images': self._audit_images(soup),
                'links': self._audit_links(soup, url),
                'schema_markup': self._audit_schema_markup(soup),
                'performance': self._audit_performance(page_data),
                'mobile_friendly': self._check_mobile_friendly(soup),
                'security': self._audit_security(url, page_data),
                'overall_score': 0  # Will be calculated
            }
            
            # Calculate overall technical SEO score
            audit_results['overall_score'] = self._calculate_technical_seo_score(audit_results)
            
            # Generate recommendations
            recommendations = self._generate_technical_recommendations(audit_results)
            
            result = {
                'audit_results': audit_results,
                'recommendations': recommendations,
                'priority_issues': [r for r in recommendations if r.get('priority') == 'high'],
                'audit_timestamp': datetime.utcnow().isoformat()
            }
            
            # Log metrics
            self.log_metrics("technical_audits", 1)
            self.log_metrics("technical_seo_score", audit_results['overall_score'])
            
            return {
                'success': True,
                'agent': self.name,
                'data': result
            }
            
        except Exception as e:
            self.logger.error(f"Technical SEO audit failed: {str(e)}")
            return {
                'success': False,
                'agent': self.name,
                'error': str(e),
                'url': url
            }
    
    def analyze_competitors(self, 
                          target_keywords: List[str], 
                          competitor_urls: List[str]) -> Dict[str, Any]:
        """
        Analyze competitor SEO strategies
        
        Args:
            target_keywords: Keywords to analyze competition for
            competitor_urls: List of competitor website URLs
            
        Returns:
            Dict with competitor analysis
        """
        try:
            self.logger.info(f"Analyzing competitors for keywords: {target_keywords}")
            
            competitor_analysis = []
            
            for url in competitor_urls[:5]:  # Limit to 5 competitors
                try:
                    analysis = self._analyze_competitor(url, target_keywords)
                    if analysis:
                        competitor_analysis.append(analysis)
                except Exception as e:
                    self.logger.warning(f"Failed to analyze competitor {url}: {str(e)}")
                    continue
            
            # Identify content gaps and opportunities
            content_gaps = self._identify_content_gaps(competitor_analysis, target_keywords)
            keyword_opportunities = self._identify_keyword_opportunities(competitor_analysis)
            
            # Generate competitive insights
            insights = self._generate_competitive_insights(competitor_analysis, content_gaps)
            
            result = {
                'target_keywords': target_keywords,
                'competitors_analyzed': len(competitor_analysis),
                'competitor_data': competitor_analysis,
                'content_gaps': content_gaps,
                'keyword_opportunities': keyword_opportunities,
                'competitive_insights': insights,
                'recommendations': self._generate_competitive_recommendations(
                    competitor_analysis, content_gaps, keyword_opportunities
                ),
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Log metrics
            self.log_metrics("competitor_analyses", len(competitor_analysis))
            self.log_metrics("content_gaps_found", len(content_gaps))
            
            return {
                'success': True,
                'agent': self.name,
                'data': result
            }
            
        except Exception as e:
            self.logger.error(f"Competitor analysis failed: {str(e)}")
            return {
                'success': False,
                'agent': self.name,
                'error': str(e),
                'target_keywords': target_keywords
            }
    
    def analyze_serp_results(self, 
                            keyword: str, 
                            location: str = "us",
                            language: str = "en",
                            num_results: int = 10) -> Dict[str, Any]:
        """
        Analyze Search Engine Results Page (SERP) for a keyword
        
        Args:
            keyword: Target keyword to analyze
            location: Search location ("us", "uk", "ca", etc.)
            language: Search language ("en", "es", "fr", etc.)
            num_results: Number of results to analyze
            
        Returns:
            Dict with SERP analysis results
        """
        try:
            self.logger.info(f"Analyzing SERP results for keyword: {keyword}")
            
            if not REQUESTS_AVAILABLE or not BS4_AVAILABLE:
                return {
                    'success': False,
                    'error': 'Required packages not available. Install requests and beautifulsoup4',
                    'keyword': keyword
                }
            
            # Fetch SERP results
            serp_data = self._fetch_google_serp(keyword, location, language, num_results)
            
            if not serp_data['success']:
                return serp_data
            
            # Analyze the results
            results = serp_data['results']
            
            # Extract competitor analysis
            competitors = []
            for i, result in enumerate(results[:10]):
                competitor = self._analyze_serp_competitor(result, keyword, i + 1)
                competitors.append(competitor)
            
            # Analyze SERP features
            serp_features = self._identify_serp_features(serp_data['raw_html'])
            
            # Keyword difficulty estimation
            difficulty_score = self._estimate_keyword_difficulty(competitors, serp_features)
            
            # Content gap analysis
            content_gaps = self._analyze_serp_content_gaps(competitors, keyword)
            
            # Generate insights
            insights = self._generate_serp_insights(competitors, serp_features, difficulty_score)
            
            result_data = {
                'keyword': keyword,
                'location': location,
                'language': language,
                'total_results': len(competitors),
                'competitors': competitors,
                'serp_features': serp_features,
                'keyword_difficulty': {
                    'score': difficulty_score,
                    'level': self._get_difficulty_level(difficulty_score)
                },
                'content_gaps': content_gaps,
                'insights': insights,
                'ranking_factors': self._analyze_ranking_factors(competitors),
                'opportunities': self._identify_ranking_opportunities(competitors, keyword),
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Log metrics
            self.log_metrics("serp_analyses", 1)
            self.log_metrics("keywords_analyzed", 1)
            
            return {
                'success': True,
                'agent': self.name,
                'data': result_data
            }
            
        except Exception as e:
            self.logger.error(f"SERP analysis failed: {str(e)}")
            return {
                'success': False,
                'agent': self.name,
                'error': str(e),
                'keyword': keyword
            }
    
    def get_trending_keywords(self, 
                             category: str = "",
                             geo: str = "US",
                             timeframe: str = "today 3-m") -> Dict[str, Any]:
        """
        Get trending keywords from Google Trends (free API)
        
        Args:
            category: Trend category (e.g., "business", "technology")
            geo: Geographic location (e.g., "US", "GB", "CA")
            timeframe: Time period ("today 3-m", "today 12-m", "today 5-y")
            
        Returns:
            Dict with trending keywords
        """
        try:
            self.logger.info(f"Fetching trending keywords for category: {category}")
            
            # Use pytrends unofficial library if available, otherwise simulate
            try:
                from pytrends.request import TrendReq
                
                pytrend = TrendReq(hl='en-US', tz=360)
                
                # Get trending searches
                trending_df = pytrend.trending_searches(pn='united_states')
                trending_keywords = trending_df[0].tolist()[:20]  # Top 20
                
                # Get related queries for top trending keyword if available
                related_queries = {}
                if trending_keywords:
                    pytrend.build_payload([trending_keywords[0]], cat=0, timeframe=timeframe, geo=geo)
                    related_queries = pytrend.related_queries()
                
                return {
                    'success': True,
                    'trending_keywords': trending_keywords,
                    'related_queries': related_queries,
                    'category': category,
                    'geo': geo,
                    'timeframe': timeframe,
                    'timestamp': datetime.utcnow().isoformat()
                }
                
            except ImportError:
                # Fallback: simulate trending keywords based on common patterns
                self.logger.warning("pytrends not available, using simulated trending keywords")
                
                # Generate simulated trending keywords based on category
                trending_keywords = self._generate_simulated_trending_keywords(category)
                
                return {
                    'success': True,
                    'trending_keywords': trending_keywords,
                    'source': 'simulated',
                    'category': category,
                    'geo': geo,
                    'note': 'Install pytrends for real Google Trends data: pip install pytrends',
                    'timestamp': datetime.utcnow().isoformat()
                }
            
        except Exception as e:
            self.logger.error(f"Trending keywords fetch failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'category': category
            }
    
    def analyze_page_speed(self, url: str) -> Dict[str, Any]:
        """
        Analyze page speed using Google PageSpeed Insights API (free)
        
        Args:
            url: URL to analyze
            
        Returns:
            Dict with page speed analysis
        """
        try:
            self.logger.info(f"Analyzing page speed for: {url}")
            
            # Google PageSpeed Insights API (free, but requires API key)
            api_key = os.getenv('GOOGLE_PAGESPEED_API_KEY')
            
            if api_key and REQUESTS_AVAILABLE:
                return self._analyze_with_pagespeed_api(url, api_key)
            else:
                # Fallback: basic performance analysis
                return self._analyze_basic_performance(url)
            
        except Exception as e:
            self.logger.error(f"Page speed analysis failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'url': url
            }

    def generate_meta_tags(self, 
                          content: str, 
                          target_keyword: str,
                          page_type: str = "article") -> Dict[str, Any]:
        """
        Generate optimized meta tags for content
        
        Args:
            content: Page content
            target_keyword: Primary target keyword
            page_type: Type of page ("article", "product", "homepage", "category")
            
        Returns:
            Dict with generated meta tags
        """
        try:
            self.logger.info(f"Generating meta tags for keyword: {target_keyword}")
            
            # Extract key information from content
            content_summary = self._extract_content_summary(content)
            
            # Generate various meta tag options
            title_options = self._generate_title_options(content_summary, target_keyword, page_type)
            description_options = self._generate_description_options(content_summary, target_keyword)
            
            # Generate additional meta tags
            additional_tags = self._generate_additional_meta_tags(
                content_summary, target_keyword, page_type
            )
            
            # Generate Open Graph tags
            og_tags = self._generate_og_tags(content_summary, target_keyword, page_type)
            
            # Generate Twitter Card tags
            twitter_tags = self._generate_twitter_tags(content_summary, target_keyword)
            
            result = {
                'target_keyword': target_keyword,
                'page_type': page_type,
                'recommended_tags': {
                    'title': title_options[0] if title_options else "",
                    'meta_description': description_options[0] if description_options else "",
                    'meta_keywords': self._generate_meta_keywords(content, target_keyword),
                    'canonical_url': "<!-- Set your canonical URL -->",
                    'robots': "index, follow"
                },
                'alternative_options': {
                    'titles': title_options,
                    'descriptions': description_options
                },
                'social_media_tags': {
                    'open_graph': og_tags,
                    'twitter_card': twitter_tags
                },
                'additional_tags': additional_tags,
                'schema_suggestions': self._suggest_schema_markup(content_summary, page_type),
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Log metrics
            self.log_metrics("meta_tags_generated", 1)
            
            return {
                'success': True,
                'agent': self.name,
                'data': result
            }
            
        except Exception as e:
            self.logger.error(f"Meta tag generation failed: {str(e)}")
            return {
                'success': False,
                'agent': self.name,
                'error': str(e),
                'target_keyword': target_keyword
            }
    
    # Helper methods
    
    def _generate_keyword_variations(self, seed_keyword: str, industry: str = None) -> List[str]:
        """Generate keyword variations"""
        variations = []
        
        # Add industry context if provided
        if industry:
            variations.extend([
                f"{seed_keyword} {industry}",
                f"{industry} {seed_keyword}",
                f"best {seed_keyword} {industry}",
                f"{seed_keyword} for {industry}"
            ])
        
        # Common modifiers
        modifiers = [
            "best", "top", "professional", "enterprise", "small business",
            "affordable", "cheap", "premium", "advanced", "simple",
            "free", "paid", "online", "software", "tools", "services",
            "solution", "platform", "system", "guide", "tutorial"
        ]
        
        for modifier in modifiers[:10]:  # Limit variations
            variations.append(f"{modifier} {seed_keyword}")
            if len(seed_keyword.split()) == 1:
                variations.append(f"{seed_keyword} {modifier}")
        
        return variations
    
    def _generate_long_tail_keywords(self, seed_keyword: str, target_audience: str = None) -> List[str]:
        """Generate long-tail keyword suggestions"""
        long_tail = []
        
        # Question-based keywords
        question_starters = [
            "what is", "how to", "why", "when", "where", "who",
            "how much", "how many", "which", "can you", "should i",
            "what are the best", "how do i choose"
        ]
        
        for starter in question_starters[:8]:
            long_tail.append(f"{starter} {seed_keyword}")
        
        # Audience-specific keywords
        if target_audience:
            long_tail.extend([
                f"{seed_keyword} for {target_audience}",
                f"best {seed_keyword} for {target_audience}",
                f"how {target_audience} use {seed_keyword}"
            ])
        
        # Intent-based keywords
        intents = [
            "review", "comparison", "vs", "alternative", "pricing",
            "features", "benefits", "tutorial", "guide", "tips"
        ]
        
        for intent in intents[:6]:
            long_tail.append(f"{seed_keyword} {intent}")
        
        return long_tail
    
    def _generate_related_keywords(self, seed_keyword: str, industry: str = None) -> List[str]:
        """Generate semantically related keywords"""
        # This would typically use an API like LSIGraph, SEMrush, or Ahrefs
        # For now, generating based on common semantic relationships
        
        related = []
        
        # Common related terms for AI/automation (example)
        if any(term in seed_keyword.lower() for term in ['ai', 'automation', 'agent']):
            related.extend([
                "machine learning", "artificial intelligence", "chatbot",
                "workflow automation", "process automation", "intelligent automation",
                "robotic process automation", "digital transformation"
            ])
        
        # Add industry-specific related terms
        if industry:
            if "marketing" in industry.lower():
                related.extend([
                    "digital marketing", "content marketing", "social media marketing",
                    "email marketing", "lead generation", "marketing automation"
                ])
            elif "sales" in industry.lower():
                related.extend([
                    "sales automation", "crm", "lead qualification",
                    "sales funnel", "conversion optimization", "sales process"
                ])
        
        return related[:15]  # Limit to 15 related keywords
    
    def _analyze_keyword_metrics(self, keyword: str, competition_level: str) -> Dict[str, Any]:
        """Analyze keyword metrics (simulated - would use real SEO tools in production)"""
        import hashlib
        
        # Generate consistent "metrics" based on keyword hash
        keyword_hash = int(hashlib.md5(keyword.encode()).hexdigest()[:8], 16)
        
        # Simulate search volume (100-10000)
        search_volume = (keyword_hash % 9900) + 100
        
        # Simulate difficulty (1-100)
        if competition_level == "low":
            difficulty = (keyword_hash % 30) + 1
        elif competition_level == "high":
            difficulty = (keyword_hash % 30) + 70
        else:  # medium
            difficulty = (keyword_hash % 40) + 30
        
        # Calculate potential score
        potential_score = search_volume / (difficulty + 1)
        
        return {
            'keyword': keyword,
            'search_volume': search_volume,
            'keyword_difficulty': difficulty,
            'competition_level': competition_level,
            'potential_score': round(potential_score, 2),
            'word_count': len(keyword.split()),
            'cpc_estimate': round((keyword_hash % 500) / 100, 2),
            'trend': 'stable'  # Would be calculated from real data
        }
    
    def _generate_keyword_strategy(self, keyword_analysis: List[Dict], target_audience: str = None) -> Dict[str, Any]:
        """Generate a keyword strategy based on analysis"""
        primary_keywords = [k for k in keyword_analysis[:5]]
        long_tail_keywords = [k for k in keyword_analysis if k.get('word_count', 0) >= 3]
        
        return {
            'primary_focus': primary_keywords[0]['keyword'] if primary_keywords else "",
            'secondary_targets': [k['keyword'] for k in primary_keywords[1:4]],
            'long_tail_strategy': [k['keyword'] for k in long_tail_keywords[:5]],
            'content_themes': self._extract_content_themes(keyword_analysis),
            'recommended_approach': self._recommend_keyword_approach(keyword_analysis, target_audience)
        }
    
    def _extract_content_themes(self, keyword_analysis: List[Dict]) -> List[str]:
        """Extract content themes from keywords"""
        themes = set()
        
        for keyword_data in keyword_analysis:
            keyword = keyword_data['keyword']
            words = keyword.lower().split()
            
            # Extract meaningful terms (not stop words)
            meaningful_words = [w for w in words if w not in self.stop_words and len(w) > 2]
            themes.update(meaningful_words)
        
        return list(themes)[:10]  # Top 10 themes
    
    def _recommend_keyword_approach(self, keyword_analysis: List[Dict], target_audience: str = None) -> str:
        """Recommend keyword approach based on analysis"""
        if not keyword_analysis:
            return "Focus on creating high-quality content around your main topic."
        
        avg_difficulty = sum(k.get('keyword_difficulty', 50) for k in keyword_analysis) / len(keyword_analysis)
        
        if avg_difficulty < 30:
            return "Target high-volume keywords aggressively - competition is manageable."
        elif avg_difficulty > 70:
            return "Focus on long-tail keywords and build authority gradually."
        else:
            return "Mix of primary and long-tail keywords with content clusters."
    
    def _analyze_content_structure(self, content: str) -> Dict[str, Any]:
        """Analyze content structure"""
        lines = content.split('\n')
        
        # Count different elements
        word_count = len(content.split())
        paragraph_count = len([line for line in lines if line.strip() and not line.startswith('#')])
        
        # Find headings (markdown style)
        h1_count = len([line for line in lines if line.startswith('# ')])
        h2_count = len([line for line in lines if line.startswith('## ')])
        h3_count = len([line for line in lines if line.startswith('### ')])
        
        return {
            'word_count': word_count,
            'paragraph_count': paragraph_count,
            'heading_structure': {
                'h1_count': h1_count,
                'h2_count': h2_count,
                'h3_count': h3_count,
                'total_headings': h1_count + h2_count + h3_count
            },
            'average_paragraph_length': word_count / max(paragraph_count, 1),
            'content_length_category': self._categorize_content_length(word_count)
        }
    
    def _analyze_keyword_usage(self, content: str, target_keyword: str) -> Dict[str, Any]:
        """Analyze keyword usage in content"""
        content_lower = content.lower()
        keyword_lower = target_keyword.lower()
        
        # Count exact matches
        exact_matches = content_lower.count(keyword_lower)
        
        # Count partial matches (individual words from keyword)
        keyword_words = keyword_lower.split()
        partial_matches = sum(content_lower.count(word) for word in keyword_words)
        
        # Calculate density
        total_words = len(content.split())
        density = (exact_matches + (partial_matches * 0.5)) / max(total_words, 1)
        
        # Check placement
        in_title = any(keyword_lower in line.lower() for line in content.split('\n')[:3])
        in_first_paragraph = keyword_lower in content_lower[:300]
        in_last_paragraph = keyword_lower in content_lower[-300:]
        
        return {
            'exact_matches': exact_matches,
            'partial_matches': partial_matches,
            'density': round(density, 4),
            'density_percentage': round(density * 100, 2),
            'placement': {
                'in_title': in_title,
                'in_first_paragraph': in_first_paragraph,
                'in_last_paragraph': in_last_paragraph
            },
            'optimization_status': self._evaluate_keyword_optimization(density, exact_matches)
        }
    
    def _analyze_readability(self, content: str) -> Dict[str, Any]:
        """Analyze content readability"""
        sentences = content.split('.')
        words = content.split()
        
        # Calculate basic metrics
        avg_sentence_length = len(words) / max(len(sentences), 1)
        
        # Simple readability score (approximation)
        # Real implementation would use Flesch-Kincaid or similar
        complex_words = len([w for w in words if len(w) > 6])
        readability_score = max(0, 100 - (avg_sentence_length * 1.5) - (complex_words / len(words) * 100))
        
        return {
            'score': round(readability_score, 1),
            'grade_level': self._calculate_grade_level(readability_score),
            'avg_sentence_length': round(avg_sentence_length, 1),
            'complex_word_percentage': round((complex_words / len(words)) * 100, 1),
            'recommendations': self._get_readability_recommendations(readability_score)
        }
    
    def _generate_seo_recommendations(self, content: str, target_keyword: str, 
                                    content_analysis: Dict, keyword_analysis: Dict, 
                                    content_type: str) -> List[Dict[str, Any]]:
        """Generate SEO recommendations"""
        recommendations = []
        
        # Keyword density recommendations
        density = keyword_analysis['density']
        if density < self.optimal_keyword_density:
            recommendations.append({
                'type': 'keyword_usage',
                'priority': 'high',
                'issue': 'Low keyword density',
                'recommendation': f"Increase keyword usage. Current density: {density:.2%}, target: {self.optimal_keyword_density:.2%}",
                'action': 'Add the target keyword naturally throughout the content'
            })
        elif density > self.max_keyword_density:
            recommendations.append({
                'type': 'keyword_usage',
                'priority': 'high',
                'issue': 'Keyword stuffing detected',
                'recommendation': f"Reduce keyword usage. Current density: {density:.2%}, maximum: {self.max_keyword_density:.2%}",
                'action': 'Replace some keyword instances with synonyms or related terms'
            })
        
        # Content length recommendations
        word_count = content_analysis['word_count']
        if content_type == "blog_post" and word_count < 1000:
            recommendations.append({
                'type': 'content_length',
                'priority': 'medium',
                'issue': 'Content too short for blog post',
                'recommendation': f"Increase content length to at least 1000 words (current: {word_count})",
                'action': 'Add more detailed sections, examples, or supporting information'
            })
        
        # Heading structure recommendations
        headings = content_analysis['heading_structure']
        if headings['h1_count'] == 0:
            recommendations.append({
                'type': 'content_structure',
                'priority': 'high',
                'issue': 'Missing H1 tag',
                'recommendation': 'Add an H1 heading with the target keyword',
                'action': 'Create a compelling H1 that includes the target keyword'
            })
        
        if headings['h2_count'] < 3 and word_count > 800:
            recommendations.append({
                'type': 'content_structure',
                'priority': 'medium',
                'issue': 'Insufficient heading structure',
                'recommendation': 'Add more H2 subheadings to improve content organization',
                'action': 'Break content into logical sections with descriptive H2 headings'
            })
        
        # Keyword placement recommendations
        placement = keyword_analysis['placement']
        if not placement['in_first_paragraph']:
            recommendations.append({
                'type': 'keyword_placement',
                'priority': 'high',
                'issue': 'Keyword missing from introduction',
                'recommendation': 'Include target keyword in the first paragraph',
                'action': 'Naturally incorporate the keyword within the first 100 words'
            })
        
        return recommendations
    
    def _optimize_title(self, content: str, target_keyword: str) -> Dict[str, Any]:
        """Generate optimized title options"""
        # Extract potential title from content
        lines = content.split('\n')
        current_title = ""
        
        # Look for existing title (H1 or first line)
        for line in lines:
            if line.strip():
                if line.startswith('# '):
                    current_title = line[2:].strip()
                else:
                    current_title = line.strip()
                break
        
        # Generate title options
        title_options = [
            f"The Complete Guide to {target_keyword}",
            f"How to Master {target_keyword}: Expert Tips and Strategies",
            f"{target_keyword}: Everything You Need to Know in 2024",
            f"Ultimate {target_keyword} Guide for Professionals",
            f"Best Practices for {target_keyword} Implementation"
        ]
        
        # If we have current content, try to incorporate it
        if current_title and target_keyword.lower() not in current_title.lower():
            title_options.insert(0, f"{current_title} - {target_keyword}")
        
        # Ensure titles are within optimal length
        optimized_titles = []
        for title in title_options:
            if len(title) > self.max_title_length:
                title = title[:self.max_title_length-3] + "..."
            optimized_titles.append(title)
        
        return {
            'current_title': current_title,
            'recommended_title': optimized_titles[0],
            'alternative_titles': optimized_titles[1:4],
            'title_length': len(optimized_titles[0]),
            'includes_keyword': target_keyword.lower() in optimized_titles[0].lower()
        }
    
    def _optimize_meta_description(self, content: str, target_keyword: str) -> Dict[str, Any]:
        """Generate optimized meta description"""
        # Extract key points from content
        sentences = content.split('.')[:5]  # First 5 sentences
        
        # Create description templates
        descriptions = [
            f"Learn everything about {target_keyword} with our comprehensive guide. Discover best practices, expert tips, and proven strategies.",
            f"Master {target_keyword} with our detailed tutorial. Step-by-step instructions and professional insights included.",
            f"Comprehensive {target_keyword} guide covering fundamentals, advanced techniques, and real-world applications.",
            f"Expert insights on {target_keyword}. Learn the latest strategies and best practices from industry professionals."
        ]
        
        # Ensure descriptions are within optimal length
        optimized_descriptions = []
        for desc in descriptions:
            if len(desc) > self.max_meta_description_length:
                desc = desc[:self.max_meta_description_length-3] + "..."
            optimized_descriptions.append(desc)
        
        return {
            'recommended_description': optimized_descriptions[0],
            'alternative_descriptions': optimized_descriptions[1:],
            'description_length': len(optimized_descriptions[0]),
            'includes_keyword': target_keyword.lower() in optimized_descriptions[0].lower()
        }
    
    def _optimize_headings(self, content: str, target_keyword: str) -> List[Dict[str, Any]]:
        """Generate optimized heading suggestions"""
        optimized_headings = []
        
        # H1 suggestions
        h1_options = [
            f"The Ultimate {target_keyword} Guide",
            f"Mastering {target_keyword}: A Complete Overview",
            f"Everything You Need to Know About {target_keyword}"
        ]
        
        optimized_headings.append({
            'level': 'H1',
            'suggestions': h1_options,
            'recommended': h1_options[0]
        })
        
        # H2 suggestions
        h2_options = [
            f"What is {target_keyword}?",
            f"Benefits of {target_keyword}",
            f"How to Implement {target_keyword}",
            f"Best Practices for {target_keyword}",
            f"Common {target_keyword} Mistakes to Avoid",
            f"Future of {target_keyword}"
        ]
        
        optimized_headings.append({
            'level': 'H2',
            'suggestions': h2_options,
            'recommended': h2_options[:3]
        })
        
        return optimized_headings
    
    def _calculate_seo_score(self, content_analysis: Dict, keyword_analysis: Dict, readability_analysis: Dict) -> int:
        """Calculate overall SEO score"""
        score = 0
        
        # Keyword optimization (30 points)
        density = keyword_analysis['density']
        if self.optimal_keyword_density <= density <= self.max_keyword_density:
            score += 30
        elif density > 0:
            score += 15
        
        # Content length (20 points)
        word_count = content_analysis['word_count']
        if word_count >= 1000:
            score += 20
        elif word_count >= 500:
            score += 10
        
        # Heading structure (20 points)
        headings = content_analysis['heading_structure']
        if headings['h1_count'] >= 1:
            score += 10
        if headings['h2_count'] >= 2:
            score += 10
        
        # Keyword placement (20 points)
        placement = keyword_analysis['placement']
        if placement['in_title']:
            score += 7
        if placement['in_first_paragraph']:
            score += 7
        if placement['in_last_paragraph']:
            score += 6
        
        # Readability (10 points)
        readability_score = readability_analysis['score']
        if readability_score >= 70:
            score += 10
        elif readability_score >= 50:
            score += 5
        
        return min(score, 100)
    
    def _calculate_improvement_potential(self, current_score: int) -> Dict[str, Any]:
        """Calculate improvement potential"""
        if current_score >= 90:
            return {
                'level': 'excellent',
                'potential': 'minimal',
                'focus_areas': ['maintain current quality', 'minor optimizations']
            }
        elif current_score >= 70:
            return {
                'level': 'good',
                'potential': 'moderate',
                'focus_areas': ['keyword placement', 'content structure', 'internal linking']
            }
        elif current_score >= 50:
            return {
                'level': 'needs_improvement',
                'potential': 'high',
                'focus_areas': ['keyword optimization', 'content length', 'heading structure']
            }
        else:
            return {
                'level': 'poor',
                'potential': 'very_high',
                'focus_areas': ['complete content overhaul', 'keyword strategy', 'basic SEO principles']
            }
    
    def _categorize_content_length(self, word_count: int) -> str:
        """Categorize content length"""
        if word_count < 300:
            return "short"
        elif word_count < 800:
            return "medium"
        elif word_count < 2000:
            return "long"
        else:
            return "very_long"
    
    def _evaluate_keyword_optimization(self, density: float, exact_matches: int) -> str:
        """Evaluate keyword optimization status"""
        if density < 0.005:  # Less than 0.5%
            return "under_optimized"
        elif density > self.max_keyword_density:
            return "over_optimized"
        elif self.optimal_keyword_density <= density <= self.max_keyword_density:
            return "well_optimized"
        else:
            return "needs_adjustment"
    
    def _calculate_grade_level(self, readability_score: float) -> str:
        """Calculate grade level from readability score"""
        if readability_score >= 90:
            return "5th grade"
        elif readability_score >= 80:
            return "6th grade"
        elif readability_score >= 70:
            return "7th grade"
        elif readability_score >= 60:
            return "8th-9th grade"
        elif readability_score >= 50:
            return "10th-12th grade"
        else:
            return "college level"
    
    def _get_readability_recommendations(self, score: float) -> List[str]:
        """Get readability improvement recommendations"""
        recommendations = []
        
        if score < 50:
            recommendations.extend([
                "Use shorter sentences",
                "Replace complex words with simpler alternatives",
                "Break up long paragraphs"
            ])
        elif score < 70:
            recommendations.extend([
                "Simplify sentence structure where possible",
                "Use more common vocabulary",
                "Add transition words"
            ])
        else:
            recommendations.append("Content readability is good")
        
        return recommendations
    
    def _fetch_page_data(self, url: str) -> Dict[str, Any]:
        """Fetch page data for analysis"""
        try:
            start_time = time.time()
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            load_time = time.time() - start_time
            
            return {
                'success': True,
                'content': response.text,
                'status_code': response.status_code,
                'load_time': round(load_time, 2),
                'headers': dict(response.headers)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'url': url
            }
    
    def _audit_meta_tags(self, soup) -> Dict[str, Any]:
        """Audit meta tags"""
        meta_audit = {}
        
        # Title tag
        title_tag = soup.find('title')
        meta_audit['title'] = {
            'exists': title_tag is not None,
            'content': title_tag.text.strip() if title_tag else "",
            'length': len(title_tag.text.strip()) if title_tag else 0,
            'optimal_length': 30 <= len(title_tag.text.strip()) <= 60 if title_tag else False
        }
        
        # Meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        meta_audit['description'] = {
            'exists': meta_desc is not None,
            'content': meta_desc.get('content', '') if meta_desc else "",
            'length': len(meta_desc.get('content', '')) if meta_desc else 0,
            'optimal_length': 120 <= len(meta_desc.get('content', '')) <= 160 if meta_desc else False
        }
        
        # Meta keywords
        meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
        meta_audit['keywords'] = {
            'exists': meta_keywords is not None,
            'content': meta_keywords.get('content', '') if meta_keywords else ""
        }
        
        # Viewport
        viewport = soup.find('meta', attrs={'name': 'viewport'})
        meta_audit['viewport'] = {
            'exists': viewport is not None,
            'content': viewport.get('content', '') if viewport else ""
        }
        
        return meta_audit
    
    def _audit_heading_structure(self, soup) -> Dict[str, Any]:
        """Audit heading structure"""
        heading_audit = {}
        
        for i in range(1, 7):  # H1-H6
            headings = soup.find_all(f'h{i}')
            heading_audit[f'h{i}'] = {
                'count': len(headings),
                'content': [h.text.strip() for h in headings[:5]]  # First 5 headings
            }
        
        return heading_audit
    
    def _audit_images(self, soup) -> Dict[str, Any]:
        """Audit images for SEO"""
        images = soup.find_all('img')
        
        missing_alt = 0
        missing_title = 0
        large_images = 0
        
        for img in images:
            if not img.get('alt'):
                missing_alt += 1
            if not img.get('title'):
                missing_title += 1
            # Would check image size in real implementation
        
        return {
            'total_images': len(images),
            'missing_alt_text': missing_alt,
            'missing_title': missing_title,
            'alt_text_optimization': round((len(images) - missing_alt) / max(len(images), 1) * 100, 1)
        }
    
    def _audit_links(self, soup, base_url: str) -> Dict[str, Any]:
        """Audit internal and external links"""
        links = soup.find_all('a', href=True)
        
        internal_links = 0
        external_links = 0
        nofollow_links = 0
        
        for link in links:
            href = link['href']
            if href.startswith('http'):
                if urlparse(base_url).netloc in href:
                    internal_links += 1
                else:
                    external_links += 1
                    if 'nofollow' in link.get('rel', []):
                        nofollow_links += 1
            elif href.startswith('/') or not href.startswith('#'):
                internal_links += 1
        
        return {
            'total_links': len(links),
            'internal_links': internal_links,
            'external_links': external_links,
            'nofollow_external': nofollow_links,
            'internal_to_external_ratio': round(internal_links / max(external_links, 1), 2)
        }
    
    def _audit_schema_markup(self, soup) -> Dict[str, Any]:
        """Audit schema markup"""
        # Look for JSON-LD
        json_ld = soup.find_all('script', type='application/ld+json')
        
        # Look for microdata
        microdata = soup.find_all(attrs={'itemtype': True})
        
        return {
            'json_ld_count': len(json_ld),
            'microdata_count': len(microdata),
            'has_schema': len(json_ld) > 0 or len(microdata) > 0
        }
    
    def _audit_performance(self, page_data: Dict) -> Dict[str, Any]:
        """Audit performance indicators"""
        return {
            'load_time': page_data.get('load_time', 0),
            'page_size_kb': len(page_data.get('content', '')) / 1024,
            'gzip_enabled': 'gzip' in page_data.get('headers', {}).get('content-encoding', ''),
            'cache_control': page_data.get('headers', {}).get('cache-control', '')
        }
    
    def _check_mobile_friendly(self, soup) -> Dict[str, Any]:
        """Check mobile friendliness"""
        viewport = soup.find('meta', attrs={'name': 'viewport'})
        
        return {
            'has_viewport_meta': viewport is not None,
            'viewport_content': viewport.get('content', '') if viewport else "",
            'mobile_optimized': 'width=device-width' in viewport.get('content', '') if viewport else False
        }
    
    def _audit_security(self, url: str, page_data: Dict) -> Dict[str, Any]:
        """Audit security aspects"""
        return {
            'https_enabled': url.startswith('https://'),
            'has_hsts': 'strict-transport-security' in page_data.get('headers', {}),
            'x_frame_options': page_data.get('headers', {}).get('x-frame-options', ''),
            'content_security_policy': 'content-security-policy' in page_data.get('headers', {})
        }
    
    def _calculate_technical_seo_score(self, audit_results: Dict) -> int:
        """Calculate technical SEO score"""
        score = 0
        
        # Meta tags (25 points)
        if audit_results['meta_tags']['title']['exists']:
            score += 10
        if audit_results['meta_tags']['title']['optimal_length']:
            score += 5
        if audit_results['meta_tags']['description']['exists']:
            score += 10
        
        # Performance (25 points)
        load_time = audit_results['performance']['load_time']
        if load_time < 2:
            score += 15
        elif load_time < 4:
            score += 10
        elif load_time < 6:
            score += 5
        
        if audit_results['performance']['gzip_enabled']:
            score += 5
        if audit_results['performance']['page_size_kb'] < 1000:
            score += 5
        
        # Mobile friendly (15 points)
        if audit_results['mobile_friendly']['mobile_optimized']:
            score += 15
        
        # Security (15 points)
        if audit_results['security']['https_enabled']:
            score += 10
        if audit_results['security']['has_hsts']:
            score += 5
        
        # Structure (20 points)
        if audit_results['headings']['h1']['count'] == 1:
            score += 10
        if audit_results['images']['alt_text_optimization'] > 80:
            score += 5
        if audit_results['schema_markup']['has_schema']:
            score += 5
        
        return min(score, 100)
    
    def _generate_technical_recommendations(self, audit_results: Dict) -> List[Dict[str, Any]]:
        """Generate technical SEO recommendations"""
        recommendations = []
        
        # Meta tag recommendations
        if not audit_results['meta_tags']['title']['exists']:
            recommendations.append({
                'type': 'meta_tags',
                'priority': 'high',
                'issue': 'Missing title tag',
                'recommendation': 'Add a unique, descriptive title tag to every page'
            })
        
        if not audit_results['meta_tags']['description']['exists']:
            recommendations.append({
                'type': 'meta_tags',
                'priority': 'high',
                'issue': 'Missing meta description',
                'recommendation': 'Add meta descriptions to improve click-through rates'
            })
        
        # Performance recommendations
        if audit_results['performance']['load_time'] > 3:
            recommendations.append({
                'type': 'performance',
                'priority': 'high',
                'issue': 'Slow page load time',
                'recommendation': f"Improve page speed (current: {audit_results['performance']['load_time']}s)"
            })
        
        # Security recommendations
        if not audit_results['security']['https_enabled']:
            recommendations.append({
                'type': 'security',
                'priority': 'high',
                'issue': 'No HTTPS',
                'recommendation': 'Implement SSL certificate and redirect HTTP to HTTPS'
            })
        
        return recommendations
    
    def _analyze_competitor(self, url: str, target_keywords: List[str]) -> Dict[str, Any]:
        """Analyze a competitor website"""
        # Simplified competitor analysis
        page_data = self._fetch_page_data(url)
        if not page_data['success']:
            return None
        
        soup = BeautifulSoup(page_data['content'], 'html.parser')
        content = soup.get_text()
        
        # Analyze keyword usage
        keyword_presence = {}
        for keyword in target_keywords:
            keyword_presence[keyword] = content.lower().count(keyword.lower())
        
        return {
            'url': url,
            'domain': urlparse(url).netloc,
            'title': soup.find('title').text.strip() if soup.find('title') else "",
            'word_count': len(content.split()),
            'keyword_presence': keyword_presence,
            'meta_description': soup.find('meta', attrs={'name': 'description'}).get('content', '') if soup.find('meta', attrs={'name': 'description'}) else "",
            'headings': {
                'h1': [h.text.strip() for h in soup.find_all('h1')],
                'h2': [h.text.strip() for h in soup.find_all('h2')][:5]
            }
        }
    
    def _identify_content_gaps(self, competitor_analysis: List[Dict], target_keywords: List[str]) -> List[Dict[str, Any]]:
        """Identify content gaps compared to competitors"""
        gaps = []
        
        # Analyze common topics among competitors
        all_headings = []
        for competitor in competitor_analysis:
            all_headings.extend(competitor.get('headings', {}).get('h2', []))
        
        # Find common themes
        from collections import Counter
        heading_words = []
        for heading in all_headings:
            words = [w.lower() for w in heading.split() if len(w) > 3 and w.lower() not in self.stop_words]
            heading_words.extend(words)
        
        common_themes = Counter(heading_words).most_common(10)
        
        for theme, count in common_themes:
            if count >= 2:  # Appears in at least 2 competitors
                gaps.append({
                    'topic': theme,
                    'competitor_coverage': count,
                    'opportunity_score': count * 10,
                    'content_type': 'blog_post'
                })
        
        return gaps
    
    def _identify_keyword_opportunities(self, competitor_analysis: List[Dict]) -> List[Dict[str, Any]]:
        """Identify keyword opportunities from competitor analysis"""
        opportunities = []
        
        # Analyze competitor titles for keyword patterns
        titles = [comp.get('title', '') for comp in competitor_analysis]
        
        # Extract common patterns
        for title in titles:
            words = title.lower().split()
            meaningful_words = [w for w in words if len(w) > 3 and w not in self.stop_words]
            
            for word in meaningful_words:
                opportunities.append({
                    'keyword': word,
                    'source': 'competitor_title',
                    'competition_level': 'medium'
                })
        
        return opportunities[:10]  # Top 10 opportunities
    
    def _generate_competitive_insights(self, competitor_analysis: List[Dict], content_gaps: List[Dict]) -> List[str]:
        """Generate competitive insights"""
        insights = []
        
        if competitor_analysis:
            avg_word_count = sum(comp.get('word_count', 0) for comp in competitor_analysis) / len(competitor_analysis)
            insights.append(f"Competitors average {int(avg_word_count)} words per page")
        
        if content_gaps:
            top_gap = content_gaps[0]
            insights.append(f"Major content gap opportunity: {top_gap['topic']}")
        
        return insights
    
    def _generate_competitive_recommendations(self, competitor_analysis: List[Dict], 
                                            content_gaps: List[Dict], 
                                            keyword_opportunities: List[Dict]) -> List[Dict[str, Any]]:
        """Generate competitive SEO recommendations"""
        recommendations = []
        
        if content_gaps:
            recommendations.append({
                'type': 'content_gap',
                'priority': 'high',
                'recommendation': f"Create content around '{content_gaps[0]['topic']}' - high competitor coverage",
                'action': 'Develop comprehensive content covering this topic'
            })
        
        if keyword_opportunities:
            recommendations.append({
                'type': 'keyword_opportunity',
                'priority': 'medium',
                'recommendation': f"Target keyword opportunity: '{keyword_opportunities[0]['keyword']}'",
                'action': 'Create content optimized for this keyword'
            })
        
        return recommendations
    
    def _extract_content_summary(self, content: str) -> Dict[str, Any]:
        """Extract key information from content"""
        lines = content.split('\n')
        first_paragraph = ""
        
        # Find first substantial paragraph
        for line in lines:
            if line.strip() and len(line) > 50 and not line.startswith('#'):
                first_paragraph = line.strip()
                break
        
        # Extract key phrases (simplified)
        words = content.lower().split()
        meaningful_words = [w for w in words if len(w) > 4 and w not in self.stop_words]
        
        from collections import Counter
        key_phrases = Counter(meaningful_words).most_common(5)
        
        return {
            'first_paragraph': first_paragraph,
            'key_phrases': [phrase for phrase, count in key_phrases],
            'word_count': len(words),
            'main_topics': self._extract_main_topics(content)
        }
    
    def _extract_main_topics(self, content: str) -> List[str]:
        """Extract main topics from content"""
        lines = content.split('\n')
        topics = []
        
        # Extract headings as topics
        for line in lines:
            if line.startswith('#'):
                topic = line.strip('#').strip()
                if topic:
                    topics.append(topic)
        
        return topics[:5]  # Top 5 topics
    
    def _generate_title_options(self, content_summary: Dict, target_keyword: str, page_type: str) -> List[str]:
        """Generate title options"""
        key_phrases = content_summary.get('key_phrases', [])
        main_topic = key_phrases[0] if key_phrases else target_keyword
        
        templates = {
            'article': [
                f"The Complete Guide to {target_keyword}",
                f"How to Master {target_keyword}: Expert Tips",
                f"{target_keyword}: Everything You Need to Know",
                f"Ultimate {target_keyword} Guide for 2024"
            ],
            'product': [
                f"Best {target_keyword} Software - {main_topic}",
                f"{target_keyword} Solutions | Professional Tools",
                f"Advanced {target_keyword} Platform",
                f"{target_keyword} - Enterprise Solution"
            ],
            'homepage': [
                f"Professional {target_keyword} Services",
                f"{target_keyword} Experts | Your Company",
                f"Leading {target_keyword} Solutions",
                f"{target_keyword} Consulting & Services"
            ]
        }
        
        return templates.get(page_type, templates['article'])
    
    def _generate_description_options(self, content_summary: Dict, target_keyword: str) -> List[str]:
        """Generate meta description options"""
        first_paragraph = content_summary.get('first_paragraph', '')
        
        descriptions = [
            f"Learn everything about {target_keyword} with our comprehensive guide. Expert tips, best practices, and proven strategies included.",
            f"Master {target_keyword} with our detailed tutorial. Step-by-step instructions and professional insights to help you succeed.",
            f"Discover the power of {target_keyword}. Complete guide covering fundamentals, advanced techniques, and real-world applications.",
            f"Professional {target_keyword} solutions and expert guidance. Transform your approach with proven strategies and industry insights."
        ]
        
        # If we have a good first paragraph, use it as base
        if first_paragraph and len(first_paragraph) <= 160:
            descriptions.insert(0, first_paragraph)
        
        return descriptions
    
    def _generate_meta_keywords(self, content: str, target_keyword: str) -> str:
        """Generate meta keywords (legacy but sometimes still used)"""
        words = content.lower().split()
        meaningful_words = [w for w in words if len(w) > 3 and w not in self.stop_words]
        
        from collections import Counter
        top_words = Counter(meaningful_words).most_common(8)
        
        keywords = [target_keyword]
        keywords.extend([word for word, count in top_words if word != target_keyword.lower()])
        
        return ', '.join(keywords[:10])
    
    def _generate_additional_meta_tags(self, content_summary: Dict, target_keyword: str, page_type: str) -> Dict[str, str]:
        """Generate additional meta tags"""
        return {
            'author': 'SIX3 Agency',
            'robots': 'index, follow',
            'language': 'en-US',
            'revisit-after': '7 days',
            'classification': 'business',
            'rating': 'general',
            'distribution': 'global'
        }
    
    def _generate_og_tags(self, content_summary: Dict, target_keyword: str, page_type: str) -> Dict[str, str]:
        """Generate Open Graph tags"""
        title = f"The Complete Guide to {target_keyword}"
        description = f"Learn everything about {target_keyword} with our comprehensive guide."
        
        return {
            'og:title': title,
            'og:description': description,
            'og:type': 'article' if page_type == 'article' else 'website',
            'og:url': '<!-- Set your page URL -->',
            'og:image': '<!-- Set your image URL -->',
            'og:site_name': 'SIX3 Agency',
            'og:locale': 'en_US'
        }
    
    def _generate_twitter_tags(self, content_summary: Dict, target_keyword: str) -> Dict[str, str]:
        """Generate Twitter Card tags"""
        title = f"The Complete Guide to {target_keyword}"
        description = f"Learn everything about {target_keyword} with our comprehensive guide."
        
        return {
            'twitter:card': 'summary_large_image',
            'twitter:title': title,
            'twitter:description': description,
            'twitter:image': '<!-- Set your image URL -->',
            'twitter:creator': '@six3agency',
            'twitter:site': '@six3agency'
        }
    
    def _suggest_schema_markup(self, content_summary: Dict, page_type: str) -> Dict[str, Any]:
        """Suggest appropriate schema markup"""
        schema_suggestions = []
        
        if page_type == 'article':
            schema_suggestions.append({
                'type': 'Article',
                'properties': ['headline', 'author', 'datePublished', 'dateModified', 'description', 'image'],
                'recommended': True
            })
        
        if page_type == 'product':
            schema_suggestions.append({
                'type': 'Product',
                'properties': ['name', 'description', 'brand', 'offers', 'aggregateRating'],
                'recommended': True
            })
        
        # Always suggest Organization schema
        schema_suggestions.append({
            'type': 'Organization',
            'properties': ['name', 'url', 'logo', 'contactPoint', 'address'],
            'recommended': False
        })
        
        return {
            'suggestions': schema_suggestions,
            'priority': 'high' if page_type in ['article', 'product'] else 'medium'
        }
    
    # New helper methods for enhanced SERP and API functionality
    
    def _fetch_google_serp(self, keyword: str, location: str, language: str, num_results: int) -> Dict[str, Any]:
        """Fetch Google SERP results for analysis"""
        try:
            import random
            
            # Construct Google search URL
            search_url = f"https://www.google.com/search"
            params = {
                'q': keyword,
                'num': min(num_results, 10),
                'hl': language,
                'gl': location.upper()
            }
            
            headers = {
                'User-Agent': random.choice(self.serp_user_agents),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': f'{language}-US,{language};q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            
            response = requests.get(search_url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract search results
            results = []
            result_divs = soup.find_all('div', class_='g')
            
            for div in result_divs[:num_results]:
                try:
                    link_elem = div.find('a')
                    title_elem = div.find('h3')
                    snippet_elem = div.find('span', {'data-ved': True}) or div.find('div', class_='s')
                    
                    if link_elem and title_elem:
                        result = {
                            'title': title_elem.get_text(strip=True),
                            'url': link_elem.get('href', ''),
                            'snippet': snippet_elem.get_text(strip=True) if snippet_elem else '',
                            'domain': urlparse(link_elem.get('href', '')).netloc
                        }
                        results.append(result)
                except Exception as e:
                    continue
            
            return {
                'success': True,
                'results': results,
                'raw_html': response.text,
                'keyword': keyword,
                'total_found': len(results)
            }
            
        except Exception as e:
            self.logger.warning(f"Failed to fetch SERP for {keyword}: {e}")
            # Return simulated results for testing
            return self._generate_simulated_serp(keyword, num_results)
    
    def _generate_simulated_serp(self, keyword: str, num_results: int) -> Dict[str, Any]:
        """Generate simulated SERP results for testing when real scraping fails"""
        simulated_domains = [
            'wikipedia.org', 'medium.com', 'linkedin.com', 'hubspot.com',
            'salesforce.com', 'forbes.com', 'techcrunch.com', 'entrepreneur.com'
        ]
        
        results = []
        for i in range(min(num_results, 8)):
            domain = simulated_domains[i % len(simulated_domains)]
            results.append({
                'title': f"{keyword.title()} - Complete Guide | {domain.split('.')[0].title()}",
                'url': f"https://{domain}/article/{keyword.replace(' ', '-').lower()}",
                'snippet': f"Learn everything about {keyword}. Comprehensive guide covering best practices, implementation strategies, and expert insights.",
                'domain': domain
            })
        
        return {
            'success': True,
            'results': results,
            'raw_html': '',
            'keyword': keyword,
            'total_found': len(results),
            'simulated': True
        }
    
    def _analyze_serp_competitor(self, result: Dict[str, Any], keyword: str, position: int) -> Dict[str, Any]:
        """Analyze a single SERP competitor result"""
        title = result.get('title', '')
        snippet = result.get('snippet', '')
        url = result.get('url', '')
        domain = result.get('domain', '')
        
        # Analyze title optimization
        title_analysis = {
            'contains_keyword': keyword.lower() in title.lower(),
            'length': len(title),
            'optimal_length': 30 <= len(title) <= 60,
            'keyword_position': title.lower().find(keyword.lower())
        }
        
        # Analyze snippet optimization
        snippet_analysis = {
            'contains_keyword': keyword.lower() in snippet.lower(),
            'length': len(snippet),
            'keyword_mentions': snippet.lower().count(keyword.lower())
        }
        
        # Domain authority estimation (simplified)
        domain_authority = self._estimate_domain_authority(domain)
        
        return {
            'position': position,
            'title': title,
            'url': url,
            'domain': domain,
            'snippet': snippet,
            'title_analysis': title_analysis,
            'snippet_analysis': snippet_analysis,
            'estimated_da': domain_authority,
            'content_type': self._identify_content_type(title, snippet),
            'optimization_score': self._calculate_optimization_score(title_analysis, snippet_analysis)
        }
    
    def _identify_serp_features(self, html: str) -> Dict[str, Any]:
        """Identify SERP features present in the search results"""
        features = {
            'featured_snippet': False,
            'people_also_ask': False,
            'related_searches': False,
            'image_pack': False,
            'video_results': False,
            'local_pack': False,
            'shopping_results': False,
            'knowledge_graph': False
        }
        
        if html:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Check for featured snippet
            if soup.find('div', {'data-attrid': 'FeaturedSnippet'}) or soup.find('div', class_='kp-blk'):
                features['featured_snippet'] = True
            
            # Check for People Also Ask
            if soup.find('div', class_='related-question-pair'):
                features['people_also_ask'] = True
            
            # Check for images
            if soup.find('div', {'data-attrid': 'images'}):
                features['image_pack'] = True
            
            # Check for videos
            if soup.find('div', {'data-attrid': 'video'}):
                features['video_results'] = True
        
        return features
    
    def _estimate_keyword_difficulty(self, competitors: List[Dict], serp_features: Dict) -> int:
        """Estimate keyword difficulty score (0-100)"""
        difficulty = 0
        
        # High authority domains increase difficulty
        high_da_count = sum(1 for comp in competitors if comp.get('estimated_da', 0) > 70)
        difficulty += high_da_count * 10
        
        # Well-optimized pages increase difficulty
        optimized_count = sum(1 for comp in competitors if comp.get('optimization_score', 0) > 80)
        difficulty += optimized_count * 8
        
        # SERP features increase difficulty
        feature_count = sum(1 for feature, present in serp_features.items() if present)
        difficulty += feature_count * 5
        
        # Wikipedia or other authority sites in top 3
        top_3_domains = [comp.get('domain', '') for comp in competitors[:3]]
        if any(domain in ['wikipedia.org', 'youtube.com', 'linkedin.com'] for domain in top_3_domains):
            difficulty += 15
        
        return min(difficulty, 100)
    
    def _analyze_serp_content_gaps(self, competitors: List[Dict], keyword: str) -> List[Dict[str, Any]]:
        """Analyze content gaps based on SERP analysis"""
        gaps = []
        
        # Analyze common content types
        content_types = [comp.get('content_type', 'unknown') for comp in competitors]
        type_counts = Counter(content_types)
        
        # Identify missing content types
        all_types = ['guide', 'tutorial', 'list', 'comparison', 'review', 'news']
        for content_type in all_types:
            if type_counts.get(content_type, 0) == 0:
                gaps.append({
                    'type': 'content_type',
                    'opportunity': f"No {content_type} content in top 10",
                    'suggested_title': f"{keyword.title()} {content_type.title()}",
                    'priority': 'medium'
                })
        
        # Analyze title patterns for gaps
        titles = [comp.get('title', '') for comp in competitors]
        common_words = []
        for title in titles:
            words = [w.lower() for w in title.split() if len(w) > 3]
            common_words.extend(words)
        
        word_counts = Counter(common_words)
        missing_modifiers = ['best', 'top', 'ultimate', 'complete', 'beginner', 'advanced']
        
        for modifier in missing_modifiers:
            if word_counts.get(modifier, 0) == 0:
                gaps.append({
                    'type': 'title_modifier',
                    'opportunity': f"No '{modifier}' modifier in top results",
                    'suggested_title': f"{modifier.title()} {keyword.title()} Guide",
                    'priority': 'low'
                })
        
        return gaps[:5]  # Return top 5 gaps
    
    def _generate_serp_insights(self, competitors: List[Dict], serp_features: Dict, difficulty: int) -> List[str]:
        """Generate insights based on SERP analysis"""
        insights = []
        
        # Difficulty insights
        if difficulty > 80:
            insights.append("High competition keyword - focus on long-tail variations")
        elif difficulty < 30:
            insights.append("Low competition keyword - good opportunity for quick ranking")
        
        # SERP feature insights
        if serp_features.get('featured_snippet'):
            insights.append("Featured snippet present - optimize for snippet targeting")
        
        if serp_features.get('people_also_ask'):
            insights.append("People Also Ask box present - create FAQ-style content")
        
        # Competitor insights
        avg_da = sum(comp.get('estimated_da', 0) for comp in competitors) / len(competitors)
        if avg_da > 60:
            insights.append("High authority domains dominate - build strong backlink profile")
        
        # Content type insights
        content_types = [comp.get('content_type', '') for comp in competitors]
        if content_types.count('guide') > 5:
            insights.append("Guide content dominates - consider alternative content angles")
        
        return insights
    
    def _analyze_ranking_factors(self, competitors: List[Dict]) -> Dict[str, Any]:
        """Analyze ranking factors from competitor data"""
        factors = {
            'title_optimization': 0,
            'keyword_in_url': 0,
            'high_authority': 0,
            'content_length_correlation': 'unknown'
        }
        
        total_competitors = len(competitors)
        if total_competitors == 0:
            return factors
        
        # Calculate percentages
        factors['title_optimization'] = sum(1 for comp in competitors if comp.get('title_analysis', {}).get('contains_keyword', False)) / total_competitors * 100
        factors['keyword_in_url'] = sum(1 for comp in competitors if comp.get('url', '').find(comp.get('title', '').lower().replace(' ', '-')) > -1) / total_competitors * 100
        factors['high_authority'] = sum(1 for comp in competitors if comp.get('estimated_da', 0) > 50) / total_competitors * 100
        
        return factors
    
    def _identify_ranking_opportunities(self, competitors: List[Dict], keyword: str) -> List[Dict[str, Any]]:
        """Identify ranking opportunities based on competitor weaknesses"""
        opportunities = []
        
        for i, comp in enumerate(competitors):
            title_analysis = comp.get('title_analysis', {})
            
            # Poor title optimization
            if not title_analysis.get('contains_keyword', False):
                opportunities.append({
                    'type': 'title_optimization',
                    'competitor_position': i + 1,
                    'competitor_domain': comp.get('domain', ''),
                    'opportunity': 'Competitor title lacks target keyword',
                    'action': 'Create title with target keyword for better relevance'
                })
            
            # Suboptimal title length
            if not title_analysis.get('optimal_length', False):
                opportunities.append({
                    'type': 'title_length',
                    'competitor_position': i + 1,
                    'competitor_domain': comp.get('domain', ''),
                    'opportunity': 'Competitor has suboptimal title length',
                    'action': 'Optimize title length for better click-through rates'
                })
        
        return opportunities[:3]  # Top 3 opportunities
    
    def _estimate_domain_authority(self, domain: str) -> int:
        """Estimate domain authority (simplified scoring)"""
        # High authority domains
        high_authority = {
            'wikipedia.org': 95, 'youtube.com': 90, 'linkedin.com': 85,
            'medium.com': 80, 'forbes.com': 85, 'techcrunch.com': 80,
            'hubspot.com': 85, 'salesforce.com': 80
        }
        
        if domain in high_authority:
            return high_authority[domain]
        
        # Estimate based on domain characteristics
        if domain.endswith('.edu'):
            return 70
        elif domain.endswith('.gov'):
            return 85
        elif domain.endswith('.org'):
            return 60
        elif '.' in domain and len(domain.split('.')[0]) < 5:
            return 40  # Short domains tend to be older
        else:
            return 30  # Default for unknown domains
    
    def _identify_content_type(self, title: str, snippet: str) -> str:
        """Identify content type based on title and snippet"""
        title_lower = title.lower()
        snippet_lower = snippet.lower()
        
        if any(word in title_lower for word in ['guide', 'how to', 'tutorial']):
            return 'guide'
        elif any(word in title_lower for word in ['list', 'best', 'top']):
            return 'list'
        elif any(word in title_lower for word in ['vs', 'versus', 'comparison']):
            return 'comparison'
        elif any(word in title_lower for word in ['review', 'rating']):
            return 'review'
        elif any(word in snippet_lower for word in ['news', 'announced', 'today']):
            return 'news'
        else:
            return 'informational'
    
    def _calculate_optimization_score(self, title_analysis: Dict, snippet_analysis: Dict) -> int:
        """Calculate optimization score for a competitor"""
        score = 0
        
        # Title optimization (40 points)
        if title_analysis.get('contains_keyword'):
            score += 20
        if title_analysis.get('optimal_length'):
            score += 15
        if title_analysis.get('keyword_position', -1) >= 0:
            # Earlier keyword position is better
            position = title_analysis.get('keyword_position', 50)
            score += max(0, 15 - (position // 5))
        
        # Snippet optimization (30 points)
        if snippet_analysis.get('contains_keyword'):
            score += 20
        keyword_mentions = snippet_analysis.get('keyword_mentions', 0)
        score += min(keyword_mentions * 3, 10)  # Max 10 points for keyword mentions
        
        return min(score, 100)
    
    def _get_difficulty_level(self, score: int) -> str:
        """Convert difficulty score to difficulty level"""
        if score >= 80:
            return "Very High"
        elif score >= 60:
            return "High"
        elif score >= 40:
            return "Medium"
        elif score >= 20:
            return "Low"
        else:
            return "Very Low"
    
    def _generate_simulated_trending_keywords(self, category: str) -> List[str]:
        """Generate simulated trending keywords when API is not available"""
        base_keywords = {
            'business': ['ai automation', 'digital transformation', 'remote work', 'productivity tools', 'saas platforms'],
            'technology': ['machine learning', 'cloud computing', 'cybersecurity', 'blockchain', 'iot devices'],
            'marketing': ['social media marketing', 'content marketing', 'email automation', 'seo optimization', 'ppc advertising'],
            '': ['artificial intelligence', 'automation', 'productivity', 'efficiency', 'optimization']
        }
        
        keywords = base_keywords.get(category.lower(), base_keywords[''])
        
        # Add trending modifiers
        modifiers = ['best', '2024', 'tools', 'software', 'solutions', 'platforms', 'services']
        trending = []
        
        for keyword in keywords:
            trending.append(keyword)
            for modifier in modifiers[:2]:
                trending.append(f"{keyword} {modifier}")
                trending.append(f"{modifier} {keyword}")
        
        return trending[:20]
    
    def _analyze_with_pagespeed_api(self, url: str, api_key: str) -> Dict[str, Any]:
        """Analyze page speed using Google PageSpeed Insights API"""
        try:
            api_url = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
            params = {
                'url': url,
                'key': api_key,
                'category': 'PERFORMANCE',
                'strategy': 'MOBILE'
            }
            
            response = requests.get(api_url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            lighthouse_result = data.get('lighthouseResult', {})
            audits = lighthouse_result.get('audits', {})
            
            # Extract key metrics
            metrics = {
                'performance_score': lighthouse_result.get('categories', {}).get('performance', {}).get('score', 0) * 100,
                'first_contentful_paint': audits.get('first-contentful-paint', {}).get('displayValue', 'N/A'),
                'largest_contentful_paint': audits.get('largest-contentful-paint', {}).get('displayValue', 'N/A'),
                'cumulative_layout_shift': audits.get('cumulative-layout-shift', {}).get('displayValue', 'N/A'),
                'total_blocking_time': audits.get('total-blocking-time', {}).get('displayValue', 'N/A')
            }
            
            return {
                'success': True,
                'url': url,
                'metrics': metrics,
                'api_source': 'google_pagespeed',
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'url': url
            }
    
    def _analyze_basic_performance(self, url: str) -> Dict[str, Any]:
        """Basic performance analysis without external API"""
        try:
            start_time = time.time()
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            load_time = time.time() - start_time
            
            # Basic analysis
            content_size = len(response.content)
            
            # Simple scoring
            load_score = 100 - min(load_time * 10, 50)  # Penalize slow loading
            size_score = 100 - min(content_size / 10000, 30)  # Penalize large pages
            performance_score = (load_score + size_score) / 2
            
            return {
                'success': True,
                'url': url,
                'metrics': {
                    'performance_score': round(performance_score, 1),
                    'load_time': f"{load_time:.2f}s",
                    'content_size': f"{content_size / 1024:.1f} KB",
                    'status_code': response.status_code
                },
                'api_source': 'basic_analysis',
                'note': 'Basic analysis - install Google PageSpeed API key for detailed metrics',
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'url': url
            }


def test_seo_optimizer():
    """Test the SEO Optimizer Agent"""
    print("Testing SEO Optimizer Agent...")
    
    # Initialize agent
    agent = SEOOptimizerAgent()
    
    # Test content
    test_content = """
    # AI Automation for Business
    
    Artificial intelligence automation is transforming how businesses operate. Companies are using AI agents to streamline processes, reduce costs, and improve efficiency.
    
    ## Benefits of AI Automation
    
    AI automation offers numerous advantages including cost reduction, improved accuracy, and 24/7 availability. Many businesses report significant ROI improvements after implementing AI solutions.
    
    ## Implementation Strategies
    
    To successfully implement AI automation, businesses should start with pilot projects, train their teams, and gradually scale their AI initiatives.
    """
    
    # Test keyword research
    print("\n1. Testing keyword research...")
    keyword_result = agent.research_keywords("AI automation", "technology", "business owners")
    print(f"Success: {keyword_result['success']}")
    if keyword_result['success']:
        print(f"Found {keyword_result['data']['total_keywords_found']} keywords")
        print(f"Primary keywords: {[k['keyword'] for k in keyword_result['data']['primary_keywords'][:3]]}")
    
    # Test content optimization
    print("\n2. Testing content optimization...")
    optimization_result = agent.optimize_content(test_content, "AI automation", "blog_post")
    print(f"Success: {optimization_result['success']}")
    if optimization_result['success']:
        print(f"SEO Score: {optimization_result['data']['current_analysis']['seo_score']}/100")
        print(f"Recommendations: {len(optimization_result['data']['recommendations'])}")
    
    # Test meta tag generation
    print("\n3. Testing meta tag generation...")
    meta_result = agent.generate_meta_tags(test_content, "AI automation", "article")
    print(f"Success: {meta_result['success']}")
    if meta_result['success']:
        print(f"Recommended title: {meta_result['data']['recommended_tags']['title']}")
        print(f"Meta description: {meta_result['data']['recommended_tags']['meta_description'][:100]}...")
    
    print("\nSEO Optimizer Agent testing completed!")


if __name__ == "__main__":
    test_seo_optimizer()