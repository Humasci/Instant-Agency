#!/usr/bin/env python3
"""
SIX3 Agency Service Configuration
Defines the three core services and their workflows
"""

SERVICES = {
    "search_marketing": {
        "name": "Search Marketing & Paid Media",
        "description": "AI-driven search marketing with advanced algorithm optimization",
        "approach": [
            "Data-driven keyword research using ML models",
            "Automated bid optimization across platforms",
            "Real-time performance monitoring and adjustment",
            "Cross-platform campaign orchestration"
        ],
        "expertise": [
            "Google Ads optimization algorithms",
            "Meta Ads AI bidding strategies", 
            "LinkedIn campaign automation",
            "TikTok Ads machine learning"
        ],
        "technology_stack": [
            "Custom ML models for bid optimization",
            "Real-time API integrations",
            "Automated reporting dashboards",
            "Performance prediction algorithms"
        ],
        "workflows": [
            "SIX3 Search Campaign Optimization",
            "SIX3 Multi-Platform Bid Management", 
            "SIX3 Performance Analytics Pipeline"
        ],
        "agents": [
            "Campaign Strategy Agent",
            "Bid Optimization Agent",
            "Performance Analytics Agent",
            "Competitor Analysis Agent"
        ]
    },
    "generative_ai_media": {
        "name": "Generative AI Video/Audio",
        "description": "AI avatars and generative models for unique multimedia content",
        "approach": [
            "Custom AI avatar creation for brand consistency",
            "Voice cloning for authentic brand voices",
            "Automated video content generation",
            "Multi-language content localization"
        ],
        "expertise": [
            "Digital avatar development and animation",
            "Voice synthesis and cloning technology",
            "Video generation using diffusion models",
            "UGC campaign automation"
        ],
        "technology_stack": [
            "Stable Diffusion video models",
            "Custom voice cloning neural networks",
            "Real-time avatar rendering engines",
            "Content moderation AI systems"
        ],
        "workflows": [
            "SIX3 Avatar Content Creation",
            "SIX3 Voice Clone Production",
            "SIX3 UGC Campaign Generator"
        ],
        "agents": [
            "Digital Avatar Agent",
            "Voice Conversation Agent", 
            "Video Content Generator",
            "UGC Campaign Manager"
        ]
    },
    "ml_model_tuning": {
        "name": "Fine-Tuning ML Models",
        "description": "Custom AI models tailored to client data and objectives",
        "approach": [
            "Secure data ingestion and preprocessing",
            "Domain-specific model architecture selection",
            "Iterative fine-tuning with client feedback",
            "Production deployment with monitoring"
        ],
        "expertise": [
            "Large Language Model fine-tuning",
            "Computer vision model adaptation",
            "Recommendation system optimization",
            "Predictive analytics model training"
        ],
        "technology_stack": [
            "Transformer-based language models",
            "PyTorch and TensorFlow frameworks",
            "Distributed training infrastructure",
            "MLOps pipeline automation"
        ],
        "workflows": [
            "SIX3 Model Fine-Tuning Pipeline",
            "SIX3 Data Processing Automation",
            "SIX3 Model Deployment Manager"
        ],
        "agents": [
            "Data Processing Agent",
            "Model Training Agent",
            "Performance Evaluation Agent",
            "Deployment Orchestrator"
        ]
    }
}

# Industry-specific use cases
INDUSTRY_USE_CASES = {
    "e_commerce": {
        "search_marketing": [
            "Product-specific keyword optimization",
            "Shopping campaign automation",
            "Dynamic product ad generation"
        ],
        "generative_ai_media": [
            "Product demo video generation",
            "Customer testimonial avatars",
            "Multi-language product videos"
        ],
        "ml_model_tuning": [
            "Recommendation engine fine-tuning",
            "Price optimization models",
            "Churn prediction systems"
        ]
    },
    "saas": {
        "search_marketing": [
            "Feature-based campaign targeting",
            "Trial-to-paid conversion optimization",
            "Competitive keyword positioning"
        ],
        "generative_ai_media": [
            "Product walkthrough avatars",
            "Onboarding video sequences",
            "Customer success story videos"
        ],
        "ml_model_tuning": [
            "User behavior prediction models",
            "Feature usage optimization",
            "Support ticket classification"
        ]
    },
    "local_services": {
        "search_marketing": [
            "Local SEO optimization",
            "Location-based ad targeting",
            "Review response automation"
        ],
        "generative_ai_media": [
            "Service demonstration videos",
            "Local testimonial content",
            "Multi-location brand messaging"
        ],
        "ml_model_tuning": [
            "Lead scoring models",
            "Service demand prediction",
            "Customer lifetime value models"
        ]
    }
}

# FAQ content for each service
SERVICE_FAQS = {
    "search_marketing": [
        {
            "question": "How do your AI algorithms optimize ad spend better than platform defaults?",
            "answer": "Our proprietary ML models analyze thousands of data points in real-time, including competitor behavior, seasonal trends, and audience signals that platform algorithms miss. This results in 23% better ROAS on average."
        },
        {
            "question": "Which ad platforms do you integrate with?",
            "answer": "We integrate with Google Ads, Meta (Facebook/Instagram), LinkedIn, TikTok, Twitter, Pinterest, and Snapchat. Our unified dashboard manages campaigns across all platforms simultaneously."
        },
        {
            "question": "How transparent is your reporting and attribution?",
            "answer": "Complete transparency with real-time dashboards, custom attribution models, and detailed performance breakdowns. You own all data and can export reports anytime."
        }
    ],
    "generative_ai_media": [
        {
            "question": "Are AI-generated avatars safe for brand use?",
            "answer": "Yes, our avatars are trained on licensed content and include brand safety filters. We also provide legal indemnification for avatar-generated content within usage guidelines."
        },
        {
            "question": "Can you clone specific voices for our brand?",
            "answer": "We can clone any voice with proper consent and legal documentation. The process takes 2-3 hours of source audio and delivers production-ready voice models in 48 hours."
        },
        {
            "question": "How do you handle deepfake concerns and ethical use?",
            "answer": "We follow strict ethical guidelines, require explicit consent for all voice/likeness cloning, include watermarking in generated content, and maintain audit trails for all creations."
        }
    ],
    "ml_model_tuning": [
        {
            "question": "How do you ensure data security during model training?",
            "answer": "All data is encrypted in transit and at rest, processed in isolated environments, and automatically purged after training. We're SOC 2 compliant with enterprise-grade security."
        },
        {
            "question": "What's the typical timeline for custom model delivery?",
            "answer": "Initial models are delivered in 2-3 weeks, with iterative improvements over 6-8 weeks. Production deployment and monitoring setup adds another 1-2 weeks."
        },
        {
            "question": "Do you provide ongoing model maintenance and updates?",
            "answer": "Yes, we provide continuous monitoring, performance optimization, and model retraining as your data evolves. Maintenance packages include monthly performance reviews."
        }
    ]
}

if __name__ == "__main__":
    print("SIX3 Agency Services Configuration")
    print("="*50)
    
    for service_key, service in SERVICES.items():
        print(f"\n🚀 {service['name']}")
        print(f"   Workflows: {len(service['workflows'])}")
        print(f"   Agents: {len(service['agents'])}")
        print(f"   Technologies: {len(service['technology_stack'])}")
    
    print(f"\n📊 Total Industry Use Cases: {sum(len(cases) for cases in INDUSTRY_USE_CASES.values())}")
    print(f"📋 Total FAQ Items: {sum(len(faqs) for faqs in SERVICE_FAQS.values())}")