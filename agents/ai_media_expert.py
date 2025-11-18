"""
AI Media Production Expert Agent
Creative Director with 15+ years in video/audio production and AI technology
Handles creative consultation, production strategy, and client creative direction
"""

import os
import sys
from typing import Dict, Any, List
from datetime import datetime, timedelta
from dataclasses import dataclass

sys.path.append(os.path.dirname(__file__))
from base_agent import BaseAgent

@dataclass
class CreativeBrief:
    project_name: str
    brand: str
    industry: str
    campaign_objectives: List[str]
    target_audience: Dict[str, Any]
    creative_requirements: Dict[str, Any]
    brand_guidelines: Dict[str, Any]
    distribution_channels: List[str]
    timeline: str
    budget_range: str
    success_metrics: List[str]

@dataclass
class ProductionStrategy:
    creative_concept: str
    visual_direction: Dict[str, Any]
    production_approach: Dict[str, Any]
    technical_specifications: Dict[str, Any]
    asset_deliverables: List[Dict[str, Any]]
    production_timeline: List[Dict[str, Any]]
    quality_framework: Dict[str, Any]
    risk_mitigation: Dict[str, Any]

class AIMediaExpert(BaseAgent):
    """
    Senior AI Media Production Expert Agent
    
    Capabilities:
    - Creative consultation and concept development
    - AI technology assessment and recommendation
    - Production strategy and creative direction
    - Brand alignment and creative compliance
    - Multi-platform content optimization
    - Client creative presentation and communication
    - Production quality management and oversight
    """
    
    def __init__(self):
        super().__init__(
            agent_name="ai_media_expert",
            agent_type="expert_consultant",
            model_name="gpt-4"
        )
        
        # Creative expertise database
        self.content_type_expertise = {
            'ai_avatar_videos': {
                'best_for': ['Product demos', 'Explainer videos', 'Customer testimonials', 'Training content'],
                'production_time': '2-4 hours per video',
                'typical_length': '30s-3min',
                'platforms': ['website', 'linkedin', 'youtube', 'sales_presentations'],
                'cost_range': '$500-3000',
                'key_considerations': ['Avatar realism', 'Voice quality', 'Brand alignment', 'Lip-sync accuracy']
            },
            'voice_synthesis': {
                'best_for': ['Narration', 'Podcast content', 'Audio ads', 'IVR systems'],
                'production_time': '30min-2 hours',
                'typical_length': '15s-10min',
                'platforms': ['podcasts', 'radio', 'phone_systems', 'audio_ads'],
                'cost_range': '$200-1500',
                'key_considerations': ['Voice naturalness', 'Emotion consistency', 'Brand voice match', 'Audio quality']
            },
            'ugc_campaigns': {
                'best_for': ['Social proof', 'Testimonials', 'Product reviews', 'Brand advocacy'],
                'production_time': '1-3 days',
                'typical_length': '15s-60s',
                'platforms': ['tiktok', 'instagram', 'facebook', 'youtube_shorts'],
                'cost_range': '$1000-5000',
                'key_considerations': ['Authenticity', 'Diversity', 'Platform optimization', 'Compliance']
            },
            'product_demonstrations': {
                'best_for': ['Feature showcases', 'How-to guides', 'Comparison videos', 'Onboarding'],
                'production_time': '2-5 hours',
                'typical_length': '1min-5min',
                'platforms': ['website', 'youtube', 'sales_tools', 'support_docs'],
                'cost_range': '$800-4000',
                'key_considerations': ['Clarity', 'Technical accuracy', 'Visual hierarchy', 'Call-to-action']
            }
        }
        
        self.ai_technology_stack = {
            'avatar_generation': {
                'technologies': ['D-ID', 'Synthesia', 'HeyGen', 'Custom Stable Diffusion'],
                'strengths': ['Photorealism', 'Custom branding', 'Multi-language', 'Gesture control'],
                'limitations': ['Uncanny valley', 'Limited emotions', 'Setup complexity'],
                'best_use_cases': ['Corporate communications', 'Training videos', 'Product demos']
            },
            'voice_cloning': {
                'technologies': ['ElevenLabs', 'Murf', 'Respeecher', 'Custom models'],
                'strengths': ['Voice consistency', 'Emotion control', 'Multi-language', 'Real-time generation'],
                'limitations': ['Training data required', 'Ethical considerations', 'Quality variance'],
                'best_use_cases': ['Brand voice consistency', 'Multilingual content', 'Scalable narration']
            },
            'video_generation': {
                'technologies': ['Runway ML', 'Pika Labs', 'Stable Video Diffusion', 'Custom pipelines'],
                'strengths': ['Creative flexibility', 'Style consistency', 'Rapid iteration', 'Cost effectiveness'],
                'limitations': ['Quality inconsistency', 'Limited control', 'Brand alignment challenges'],
                'best_use_cases': ['Abstract concepts', 'Motion graphics', 'Style experimentation']
            }
        }
        
        self.brand_alignment_framework = {
            'visual_consistency': [
                'Color palette adherence',
                'Typography consistency',
                'Logo placement and usage',
                'Visual style alignment',
                'Imagery style matching'
            ],
            'voice_and_tone': [
                'Brand personality expression',
                'Tone consistency',
                'Language style matching',
                'Emotional alignment',
                'Value proposition clarity'
            ],
            'content_strategy': [
                'Message hierarchy',
                'Call-to-action alignment',
                'Content pillar adherence',
                'Audience appropriateness',
                'Platform optimization'
            ]
        }
        
        self.creative_process_stages = {
            'discovery': {
                'objectives': 'Understand brand, audience, and creative goals',
                'deliverables': ['Creative brief', 'Audience analysis', 'Competitive review'],
                'timeline': '2-3 days',
                'client_involvement': 'High - interviews and briefing sessions'
            },
            'concept_development': {
                'objectives': 'Develop creative concepts and visual direction',
                'deliverables': ['Concept presentations', 'Mood boards', 'Storyboards'],
                'timeline': '3-5 days',
                'client_involvement': 'Medium - concept review and feedback'
            },
            'pre_production': {
                'objectives': 'Finalize creative approach and technical specifications',
                'deliverables': ['Final scripts', 'Technical specs', 'Production timeline'],
                'timeline': '2-3 days',
                'client_involvement': 'Low - approvals and asset provision'
            },
            'production': {
                'objectives': 'Execute AI-powered content creation',
                'deliverables': ['Raw assets', 'Initial cuts', 'Quality reviews'],
                'timeline': '2-5 days',
                'client_involvement': 'Low - progress updates only'
            },
            'post_production': {
                'objectives': 'Refine, optimize, and finalize content',
                'deliverables': ['Final assets', 'Platform versions', 'Usage guidelines'],
                'timeline': '1-3 days',
                'client_involvement': 'Medium - final review and approval'
            }
        }
        
        print(f"✓ AI Media Expert initialized with expertise in {len(self.content_type_expertise)} content types")

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process creative engagement based on stage and requirements
        
        Args:
            input_data: {
                'action': 'creative_consultation' | 'concept_development' | 'production_planning' | 'quality_review' | 'client_presentation',
                'creative_brief': dict,
                'project_context': dict,
                'client_feedback': dict,
                'production_stage': str
            }
        """
        try:
            action = input_data.get('action', 'creative_consultation')
            
            if action == 'creative_consultation':
                return self._conduct_creative_consultation(input_data)
            elif action == 'concept_development':
                return self._develop_creative_concepts(input_data)
            elif action == 'production_planning':
                return self._plan_production_strategy(input_data)
            elif action == 'quality_review':
                return self._conduct_quality_review(input_data)
            elif action == 'client_presentation':
                return self._prepare_client_presentation(input_data)
            elif action == 'creative_direction':
                return self._provide_creative_direction(input_data)
            else:
                return {'success': False, 'error': f'Unknown action: {action}'}
                
        except Exception as e:
            self.logger.error(f"AI media expert processing error: {e}")
            return {'success': False, 'error': str(e)}

    def _conduct_creative_consultation(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Conduct comprehensive creative consultation"""
        try:
            creative_brief_data = input_data.get('creative_brief', {})
            consultation_type = input_data.get('consultation_type', 'discovery')
            
            # Parse creative brief
            creative_brief = self._parse_creative_brief(creative_brief_data)
            
            # Analyze creative requirements
            creative_analysis = self._analyze_creative_requirements(creative_brief)
            
            # Technology assessment
            technology_assessment = self._assess_ai_technology_options(creative_brief)
            
            # Creative strategy framework
            creative_strategy = self._develop_initial_creative_strategy(creative_brief, creative_analysis)
            
            # Production feasibility
            production_feasibility = self._assess_production_feasibility(creative_brief, technology_assessment)
            
            # Creative recommendations
            creative_recommendations = self._generate_creative_recommendations(
                creative_brief, creative_analysis, technology_assessment
            )
            
            # Risk assessment
            creative_risks = self._assess_creative_risks(creative_brief, technology_assessment)
            
            return {
                'success': True,
                'consultation_overview': {
                    'project': creative_brief.project_name,
                    'brand': creative_brief.brand,
                    'content_type': creative_analysis.get('recommended_content_type'),
                    'production_approach': creative_strategy.get('production_approach'),
                    'estimated_timeline': production_feasibility.get('timeline_estimate'),
                    'budget_assessment': production_feasibility.get('budget_assessment')
                },
                'creative_analysis': creative_analysis,
                'technology_assessment': technology_assessment,
                'creative_strategy': creative_strategy,
                'production_feasibility': production_feasibility,
                'creative_recommendations': creative_recommendations,
                'creative_risks': creative_risks,
                'consultation_materials': self._prepare_consultation_materials(creative_brief),
                'next_steps': self._define_consultation_next_steps(creative_brief, creative_recommendations),
                'creative_inspiration': self._provide_creative_inspiration(creative_brief, creative_analysis)
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Creative consultation failed: {str(e)}'}

    def _develop_creative_concepts(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Develop comprehensive creative concepts"""
        try:
            creative_brief = self._parse_creative_brief(input_data.get('creative_brief', {}))
            consultation_insights = input_data.get('consultation_insights', {})
            
            # Generate multiple creative concepts
            creative_concepts = self._generate_creative_concepts(creative_brief, consultation_insights)
            
            # Develop visual direction
            visual_direction = self._develop_visual_direction(creative_brief, creative_concepts)
            
            # Create mood boards and references
            mood_boards = self._create_mood_boards(creative_brief, visual_direction)
            
            # Develop storytelling framework
            storytelling_framework = self._develop_storytelling_framework(creative_brief, creative_concepts)
            
            # Technical specifications
            technical_specs = self._define_technical_specifications(creative_brief, creative_concepts)
            
            # Production requirements
            production_requirements = self._detail_production_requirements(creative_brief, creative_concepts)
            
            # Concept presentations
            concept_presentations = self._create_concept_presentations(
                creative_concepts, visual_direction, storytelling_framework
            )
            
            return {
                'success': True,
                'concept_overview': {
                    'total_concepts': len(creative_concepts),
                    'recommended_concept': creative_concepts[0]['concept_id'] if creative_concepts else None,
                    'visual_styles': [concept.get('visual_style') for concept in creative_concepts],
                    'production_complexity': self._assess_production_complexity(creative_concepts)
                },
                'creative_concepts': creative_concepts,
                'visual_direction': visual_direction,
                'mood_boards': mood_boards,
                'storytelling_framework': storytelling_framework,
                'technical_specifications': technical_specs,
                'production_requirements': production_requirements,
                'concept_presentations': concept_presentations,
                'selection_criteria': self._define_concept_selection_criteria(creative_brief),
                'client_decision_framework': self._create_client_decision_framework(creative_concepts)
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Concept development failed: {str(e)}'}

    def _analyze_creative_requirements(self, creative_brief: CreativeBrief) -> Dict[str, Any]:
        """Analyze creative requirements and constraints"""
        
        # Determine optimal content type
        content_type_scores = {}
        for content_type, specs in self.content_type_expertise.items():
            score = self._score_content_type_fit(creative_brief, content_type, specs)
            content_type_scores[content_type] = score
        
        recommended_content_type = max(content_type_scores, key=content_type_scores.get)
        
        return {
            'content_type_analysis': {
                'recommended_type': recommended_content_type,
                'type_scores': content_type_scores,
                'rationale': self._explain_content_type_recommendation(
                    creative_brief, recommended_content_type
                )
            },
            'audience_analysis': {
                'demographic_insights': self._analyze_audience_demographics(creative_brief.target_audience),
                'content_preferences': self._identify_audience_content_preferences(creative_brief.target_audience),
                'platform_behavior': self._analyze_platform_behavior(creative_brief.distribution_channels),
                'engagement_patterns': self._predict_engagement_patterns(creative_brief.target_audience)
            },
            'brand_analysis': {
                'visual_identity_assessment': self._assess_visual_identity(creative_brief.brand_guidelines),
                'voice_and_tone_analysis': self._analyze_brand_voice(creative_brief.brand_guidelines),
                'content_strategy_alignment': self._assess_content_strategy_alignment(creative_brief),
                'brand_differentiation': self._identify_brand_differentiation_opportunities(creative_brief)
            },
            'creative_constraints': {
                'technical_limitations': self._identify_technical_constraints(creative_brief),
                'budget_constraints': self._analyze_budget_constraints(creative_brief.budget_range),
                'timeline_constraints': self._analyze_timeline_constraints(creative_brief.timeline),
                'compliance_requirements': self._identify_compliance_requirements(creative_brief)
            },
            'creative_opportunities': {
                'innovation_opportunities': self._identify_innovation_opportunities(creative_brief),
                'competitive_advantages': self._identify_creative_competitive_advantages(creative_brief),
                'trend_alignment': self._assess_trend_alignment(creative_brief),
                'scalability_potential': self._assess_scalability_potential(creative_brief)
            }
        }

    def _assess_ai_technology_options(self, creative_brief: CreativeBrief) -> Dict[str, Any]:
        """Assess optimal AI technology stack for project"""
        
        technology_recommendations = {}
        
        for tech_category, tech_details in self.ai_technology_stack.items():
            suitability_score = self._score_technology_suitability(creative_brief, tech_category, tech_details)
            technology_recommendations[tech_category] = {
                'suitability_score': suitability_score,
                'recommended_tools': self._recommend_specific_tools(creative_brief, tech_category, tech_details),
                'implementation_complexity': self._assess_implementation_complexity(tech_category, creative_brief),
                'quality_expectations': self._set_quality_expectations(tech_category, creative_brief),
                'cost_implications': self._analyze_cost_implications(tech_category, creative_brief)
            }
        
        return {
            'technology_recommendations': technology_recommendations,
            'recommended_stack': self._select_optimal_technology_stack(technology_recommendations, creative_brief),
            'innovation_opportunities': self._identify_technology_innovation_opportunities(creative_brief),
            'risk_mitigation': self._plan_technology_risk_mitigation(technology_recommendations),
            'quality_assurance': self._design_technology_qa_framework(technology_recommendations),
            'scalability_considerations': self._assess_technology_scalability(technology_recommendations),
            'future_proofing': self._plan_technology_future_proofing(technology_recommendations)
        }

    def _generate_creative_concepts(self, creative_brief: CreativeBrief, consultation_insights: Dict) -> List[Dict[str, Any]]:
        """Generate multiple creative concepts for client consideration"""
        
        concepts = []
        
        # Concept 1: Direct and Professional
        concepts.append({
            'concept_id': 'concept_direct',
            'concept_name': 'Direct Professional Approach',
            'concept_description': 'Clean, professional presentation focused on clear value communication',
            'visual_style': 'Minimalist corporate',
            'tone': 'Professional and authoritative',
            'key_elements': ['Clear messaging', 'Professional avatar', 'Brand-consistent visuals', 'Direct CTAs'],
            'target_outcome': 'Build trust and credibility',
            'production_complexity': 'Low',
            'estimated_cost': '$1,500-2,500',
            'unique_selling_points': ['Quick production', 'High conversion potential', 'Brand safe'],
            'considerations': ['May lack emotional connection', 'Could be perceived as generic']
        })
        
        # Concept 2: Story-Driven
        concepts.append({
            'concept_id': 'concept_story',
            'concept_name': 'Story-Driven Engagement',
            'concept_description': 'Narrative approach using customer journey and emotional connection',
            'visual_style': 'Cinematic and engaging',
            'tone': 'Conversational and relatable',
            'key_elements': ['Customer story arc', 'Emotional hooks', 'Visual storytelling', 'Problem-solution narrative'],
            'target_outcome': 'Create emotional engagement and memorability',
            'production_complexity': 'Medium',
            'estimated_cost': '$2,500-4,000',
            'unique_selling_points': ['High engagement', 'Memorable messaging', 'Emotional connection'],
            'considerations': ['Longer production time', 'Higher complexity', 'Cultural sensitivity needed']
        })
        
        # Concept 3: Interactive and Innovative
        concepts.append({
            'concept_id': 'concept_interactive',
            'concept_name': 'Interactive Innovation',
            'concept_description': 'Cutting-edge AI features with interactive elements and personalization',
            'visual_style': 'Modern and tech-forward',
            'tone': 'Innovative and forward-thinking',
            'key_elements': ['Personalized avatars', 'Interactive elements', 'Dynamic content', 'Tech showcase'],
            'target_outcome': 'Position as innovation leader and create buzz',
            'production_complexity': 'High',
            'estimated_cost': '$4,000-7,000',
            'unique_selling_points': ['Cutting-edge tech', 'Viral potential', 'Competitive differentiation'],
            'considerations': ['Higher risk', 'Longer timeline', 'Technical dependencies']
        })
        
        return concepts

    def _prepare_client_presentation(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare comprehensive client presentation materials"""
        
        presentation_type = input_data.get('presentation_type', 'concept_review')
        
        if presentation_type == 'concept_review':
            return self._prepare_concept_review_presentation(input_data)
        elif presentation_type == 'production_kickoff':
            return self._prepare_production_kickoff_presentation(input_data)
        elif presentation_type == 'final_delivery':
            return self._prepare_final_delivery_presentation(input_data)
        else:
            return self._prepare_general_creative_presentation(input_data)

    def _prepare_concept_review_presentation(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare concept review presentation for client decision"""
        
        return {
            'presentation_structure': {
                'opening': {
                    'duration': '5 minutes',
                    'content': ['Project recap', 'Creative objectives', 'Presentation agenda'],
                    'key_message': 'Collaborative creative partnership'
                },
                'concept_presentations': {
                    'duration': '20 minutes',
                    'content': ['3 distinct concepts', 'Visual mockups', 'Production approach'],
                    'key_message': 'Tailored solutions for your brand'
                },
                'technical_overview': {
                    'duration': '10 minutes',
                    'content': ['AI technology explanation', 'Quality assurance', 'Timeline details'],
                    'key_message': 'Professional execution and quality'
                },
                'decision_framework': {
                    'duration': '10 minutes',
                    'content': ['Selection criteria', 'Next steps', 'Investment details'],
                    'key_message': 'Clear path forward'
                }
            },
            'supporting_materials': {
                'concept_boards': 'Visual representation of each concept',
                'mood_boards': 'Style and tone references',
                'technical_specs': 'Detailed production specifications',
                'timeline_overview': 'Production schedule and milestones',
                'budget_breakdown': 'Transparent cost structure'
            },
            'interactive_elements': {
                'concept_comparison': 'Side-by-side concept analysis',
                'roi_calculator': 'Projected performance metrics',
                'customization_options': 'Available modifications and add-ons',
                'reference_portfolio': 'Similar successful projects'
            },
            'decision_support': {
                'recommendation': 'Expert-recommended concept with rationale',
                'risk_assessment': 'Honest evaluation of challenges and mitigation',
                'success_metrics': 'How we will measure project success',
                'approval_process': 'Clear next steps and timeline'
            }
        }

    # Helper methods for creative analysis
    def _parse_creative_brief(self, brief_data: Dict[str, Any]) -> CreativeBrief:
        """Parse creative brief data into structured format"""
        return CreativeBrief(
            project_name=brief_data.get('project_name', 'Untitled Project'),
            brand=brief_data.get('brand', 'Unknown Brand'),
            industry=brief_data.get('industry', 'General'),
            campaign_objectives=brief_data.get('campaign_objectives', []),
            target_audience=brief_data.get('target_audience', {}),
            creative_requirements=brief_data.get('creative_requirements', {}),
            brand_guidelines=brief_data.get('brand_guidelines', {}),
            distribution_channels=brief_data.get('distribution_channels', []),
            timeline=brief_data.get('timeline', 'Not specified'),
            budget_range=brief_data.get('budget_range', 'Not specified'),
            success_metrics=brief_data.get('success_metrics', [])
        )

    def _score_content_type_fit(self, brief: CreativeBrief, content_type: str, specs: Dict) -> float:
        """Score how well a content type fits the brief requirements"""
        score = 0.0
        
        # Objective alignment (40% of score)
        objective_match = 0
        for objective in brief.campaign_objectives:
            if any(use_case.lower() in objective.lower() for use_case in specs['best_for']):
                objective_match += 1
        
        if brief.campaign_objectives:
            score += (objective_match / len(brief.campaign_objectives)) * 0.4
        
        # Platform alignment (30% of score)
        platform_match = 0
        for channel in brief.distribution_channels:
            if channel.lower() in [p.lower() for p in specs['platforms']]:
                platform_match += 1
        
        if brief.distribution_channels:
            score += (platform_match / len(brief.distribution_channels)) * 0.3
        
        # Budget alignment (20% of score)
        if brief.budget_range and brief.budget_range != 'Not specified':
            # Simple budget matching logic
            score += 0.2  # Assume budget is appropriate for now
        
        # Timeline alignment (10% of score)
        if brief.timeline and brief.timeline != 'Not specified':
            score += 0.1  # Assume timeline is workable for now
        
        return min(score, 1.0)

    # Additional helper methods would continue here...

if __name__ == "__main__":
    print("\n" + "="*80)
    print("Testing AI Media Expert Agent")
    print("="*80)
    
    expert = AIMediaExpert()
    
    # Test creative consultation
    result = expert.process({
        'action': 'creative_consultation',
        'consultation_type': 'discovery',
        'creative_brief': {
            'project_name': 'Product Launch Campaign',
            'brand': 'InnovateTech',
            'industry': 'SaaS',
            'campaign_objectives': ['Introduce new product', 'Generate leads', 'Build brand awareness'],
            'target_audience': {
                'demographics': 'B2B decision makers, 35-55',
                'job_roles': ['CTO', 'Product Manager', 'Engineering Lead'],
                'company_size': '100-1000 employees'
            },
            'creative_requirements': {
                'content_type': 'product_demonstration',
                'duration': '90 seconds',
                'style': 'professional yet engaging',
                'key_messages': ['Ease of use', 'Time savings', 'ROI benefits']
            },
            'brand_guidelines': {
                'colors': ['#1E40AF', '#059669'],
                'tone': 'Professional and trustworthy',
                'visual_style': 'Clean and modern'
            },
            'distribution_channels': ['website', 'linkedin', 'youtube', 'sales_presentations'],
            'timeline': '2 weeks',
            'budget_range': '$3,000-5,000',
            'success_metrics': ['Video completion rate > 70%', 'Lead generation increase', 'Sales team adoption']
        }
    })
    
    print(f"✅ Creative Consultation: {result.get('success')}")
    if result.get('success'):
        print(f"   Project: {result.get('consultation_overview', {}).get('project')}")
        print(f"   Content Type: {result.get('consultation_overview', {}).get('content_type')}")
        print(f"   Timeline: {result.get('consultation_overview', {}).get('estimated_timeline')}")
        print(f"   Creative Recommendations: {len(result.get('creative_recommendations', []))}")
    
    print("\n" + "="*80)
    print("AI Media Expert Tests Complete!")
    print("="*80)