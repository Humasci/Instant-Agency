# Agent Prompt Templates

This directory contains reusable prompt templates for all AI agents in the Instant Agency system.

## Directory Structure

```
prompts/
├── marketing/          # Marketing agent prompts
│   ├── prospecting.py
│   ├── engagement.py
│   └── nurture.py
├── sales/             # Sales agent prompts
│   ├── qualification.py
│   ├── pitch_generation.py
│   ├── objection_handling.py
│   └── discovery.py
├── content/           # Content creation prompts
│   ├── blog_writing.py
│   ├── social_media.py
│   └── seo_optimization.py
├── support/           # Customer support prompts
│   ├── triage.py
│   ├── resolution.py
│   └── escalation.py
├── avatar/            # Digital avatar prompts
│   ├── sarah_sales.py
│   ├── marcus_technical.py
│   └── priya_success.py
└── common/            # Shared utilities
    ├── base_prompts.py
    └── prompt_builder.py
```

## Usage

```python
from agents.prompts.sales import SALES_PITCH_PROMPT

prompt = SALES_PITCH_PROMPT.format(
    prospect_name="John Doe",
    company="Acme Corp",
    industry="SaaS",
    pain_points="Manual lead qualification"
)
```

## Prompt Engineering Best Practices

1. **Be Specific**: Clearly define the agent's role and task
2. **Provide Context**: Include relevant background information
3. **Use Examples**: Show desired output format
4. **Set Constraints**: Define length, tone, style requirements
5. **Include Error Handling**: Guide behavior for edge cases
6. **Version Control**: Track prompt changes and performance

## Prompt Template Format

All prompts should follow this structure:

```python
PROMPT_NAME = """
[System Role and Context]

[Task Description]

[Input Variables]
{variable_1}
{variable_2}

[Output Requirements]

[Output Format]
"""
```
