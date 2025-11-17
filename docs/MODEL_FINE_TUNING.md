# Model Fine-Tuning Guide

**Version**: 1.0
**Last Updated**: November 2025

## Table of Contents

1. [Overview](#overview)
2. [When to Fine-Tune](#when-to-fine-tune)
3. [Dataset Preparation](#dataset-preparation)
4. [Fine-Tuning LLMs](#fine-tuning-llms)
5. [Fine-Tuning Classification Models](#fine-tuning-classification-models)
6. [Evaluation & Testing](#evaluation--testing)
7. [Deployment](#deployment)
8. [Cost Analysis](#cost-analysis)

---

## Overview

Fine-tuning allows you to adapt pre-trained models to your specific use case, improving performance on domain-specific tasks like:

- **Sales pitch generation** in your company's voice
- **Lead qualification** based on your criteria
- **Customer support** with your product knowledge
- **Content creation** matching your brand style

---

## When to Fine-Tune

### Fine-Tune When:

✅ **You have quality training data** (500+ examples minimum, 5000+ ideal)
✅ **Base models don't perform well** on your specific task
✅ **You need consistent brand voice** or domain expertise
✅ **Cost of API calls is high** (fine-tuned models can be smaller/cheaper)
✅ **You need lower latency** (smaller fine-tuned models run faster)

### Don't Fine-Tune When:

❌ **You have < 100 examples** (few-shot prompting is better)
❌ **Base models already work well** (prompting is easier)
❌ **Requirements change frequently** (prompts are more flexible)
❌ **You lack GPU resources** (fine-tuning requires compute)

---

## Dataset Preparation

### Sales Pitch Dataset Example

```python
# data/sales_pitches_train.jsonl

{"text": "###Instruction: Generate a sales email pitch.\n\n###Input:\nProspect: John Smith\nCompany: Acme Corp\nIndustry: SaaS\nPain Point: Manual lead qualification taking too much time\n\n###Response:\nSubject: How Acme Corp could save 20 hours/week on lead qualification\n\nHi John,\n\nI noticed Acme Corp has been growing rapidly in the SaaS space. Congrats on the momentum!\n\nMany fast-growing SaaS companies we work with face the same challenge: as leads increase, manual qualification becomes a bottleneck. We recently helped a similar-sized company automate 80% of their qualification process, freeing up their sales team to focus on closing deals.\n\nWould a 15-minute conversation about how they did it be valuable?\n\nBest,\nSales Team"}

{"text": "###Instruction: Generate a sales email pitch.\n\n###Input:\nProspect: Sarah Johnson\nCompany: TechStartup Inc\nIndustry: FinTech\nPain Point: Difficulty nurturing leads at scale\n\n###Response:\nSubject: Re: TechStartup's lead nurturing challenge\n\nHi Sarah,\n\nFollowing up on your recent funding announcement - exciting times at TechStartup!\n\nAs you scale, personalized lead nurturing becomes increasingly challenging. We've helped several FinTech companies automate their nurturing sequences while maintaining personalization, resulting in 2-3x higher conversion rates.\n\nHappy to share how. Are you available for a quick call next week?\n\nBest,\nSales Team"}
```

### Dataset Format Guidelines

```python
# Standard instruction-tuning format
{
  "text": "###Instruction: {task_description}\n\n###Input:\n{input_data}\n\n###Response:\n{expected_output}"
}

# Alternative format (conversation)
{
  "text": "<|system|>You are a sales expert.</s>\n<|user|>{user_input}</s>\n<|assistant|>{assistant_response}</s>"
}
```

### Data Collection Script

```python
# scripts/prepare_training_data.py

import json
import pandas as pd
from datetime import datetime

def prepare_sales_pitch_dataset(crm_data_csv, output_file):
    """
    Convert historical sales emails into training dataset.

    Args:
        crm_data_csv: CSV file with columns: prospect_name, company, industry,
                      pain_points, email_subject, email_body, response_rate
        output_file: Output JSONL file path
    """

    df = pd.read_csv(crm_data_csv)

    # Filter for high-performing emails (response rate > 20%)
    df_filtered = df[df['response_rate'] > 0.20]

    training_examples = []

    for _, row in df_filtered.iterrows():
        example = {
            "text": f"""###Instruction: Generate a personalized sales email pitch.

###Input:
Prospect: {row['prospect_name']}
Company: {row['company']}
Industry: {row['industry']}
Pain Points: {row['pain_points']}
Company Size: {row['company_size']}

###Response:
Subject: {row['email_subject']}

{row['email_body']}"""
        }

        training_examples.append(example)

    # Write to JSONL
    with open(output_file, 'w') as f:
        for example in training_examples:
            f.write(json.dumps(example) + '\n')

    print(f"✅ Created {len(training_examples)} training examples")
    print(f"📁 Saved to {output_file}")

    return len(training_examples)

# Usage
if __name__ == "__main__":
    prepare_sales_pitch_dataset(
        crm_data_csv="data/raw/historical_sales_emails.csv",
        output_file="data/processed/sales_pitches_train.jsonl"
    )
```

### Data Quality Checks

```python
def validate_dataset(file_path):
    """Validate training dataset quality"""

    with open(file_path, 'r') as f:
        examples = [json.loads(line) for line in f]

    print(f"\n📊 Dataset Statistics:")
    print(f"Total examples: {len(examples)}")

    # Check for duplicates
    texts = [ex['text'] for ex in examples]
    duplicates = len(texts) - len(set(texts))
    print(f"Duplicate examples: {duplicates}")

    # Check length distribution
    lengths = [len(ex['text'].split()) for ex in examples]
    print(f"Average length: {sum(lengths)/len(lengths):.0f} words")
    print(f"Min length: {min(lengths)} words")
    print(f"Max length: {max(lengths)} words")

    # Check format consistency
    format_errors = 0
    for ex in examples:
        if "###Instruction:" not in ex['text']:
            format_errors += 1
        if "###Input:" not in ex['text']:
            format_errors += 1
        if "###Response:" not in ex['text']:
            format_errors += 1

    print(f"Format errors: {format_errors}")

    if format_errors == 0 and duplicates < len(examples) * 0.05:
        print("✅ Dataset validation passed!")
    else:
        print("⚠️ Dataset has issues - review before training")

# Usage
validate_dataset("data/processed/sales_pitches_train.jsonl")
```

---

## Fine-Tuning LLMs

### Full Fine-Tuning Example (GPT-Neo 2.7B)

```python
# scripts/finetune_sales_agent.py

from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    Trainer,
    TrainingArguments,
    DataCollatorForLanguageModeling
)
from datasets import load_dataset
import torch

# Configuration
MODEL_NAME = "EleutherAI/gpt-neo-2.7B"
OUTPUT_DIR = "./models/sales_agent_gpt_neo_2.7b"
TRAIN_DATA = "data/processed/sales_pitches_train.jsonl"
VAL_DATA = "data/processed/sales_pitches_val.jsonl"

def finetune_model():
    """Fine-tune GPT-Neo for sales pitch generation"""

    print("🚀 Starting fine-tuning process...")

    # 1. Load model and tokenizer
    print(f"📥 Loading base model: {MODEL_NAME}")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        torch_dtype=torch.float16,  # Use mixed precision
        device_map="auto"  # Automatically distribute across GPUs
    )

    # Set padding token
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    # 2. Load and tokenize dataset
    print(f"📚 Loading dataset...")
    dataset = load_dataset("json", data_files={
        "train": TRAIN_DATA,
        "validation": VAL_DATA
    })

    def tokenize_function(examples):
        """Tokenize training examples"""
        return tokenizer(
            examples["text"],
            truncation=True,
            max_length=512,
            padding="max_length"
        )

    print(f"🔧 Tokenizing dataset...")
    tokenized_dataset = dataset.map(
        tokenize_function,
        batched=True,
        remove_columns=dataset["train"].column_names
    )

    # 3. Configure training
    training_args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        num_train_epochs=3,
        per_device_train_batch_size=2,  # Adjust based on GPU memory
        per_device_eval_batch_size=2,
        gradient_accumulation_steps=4,  # Effective batch size = 2 * 4 = 8
        warmup_steps=500,
        weight_decay=0.01,
        logging_dir=f"{OUTPUT_DIR}/logs",
        logging_steps=100,
        save_steps=1000,
        save_total_limit=3,
        evaluation_strategy="steps",
        eval_steps=500,
        load_best_model_at_end=True,
        metric_for_best_model="eval_loss",
        fp16=True,  # Mixed precision training
        push_to_hub=False,
        report_to="tensorboard",
        learning_rate=5e-5,
        lr_scheduler_type="cosine",
    )

    # 4. Data collator
    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer,
        mlm=False  # Causal language modeling (not masked)
    )

    # 5. Initialize trainer
    print(f"👨‍🏫 Initializing trainer...")
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_dataset["train"],
        eval_dataset=tokenized_dataset["validation"],
        data_collator=data_collator,
    )

    # 6. Train!
    print(f"🏋️ Starting training...")
    trainer.train()

    # 7. Save model
    print(f"💾 Saving model to {OUTPUT_DIR}")
    trainer.save_model(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)

    print("✅ Fine-tuning complete!")

    # 8. Test generation
    print("\n🧪 Testing model generation...")
    test_prompt = """###Instruction: Generate a personalized sales email pitch.

###Input:
Prospect: Jane Doe
Company: StartupXYZ
Industry: E-commerce
Pain Points: Low email open rates, poor lead conversion

###Response:"""

    inputs = tokenizer(test_prompt, return_tensors="pt").to(model.device)
    outputs = model.generate(
        **inputs,
        max_new_tokens=300,
        temperature=0.7,
        top_p=0.9,
        do_sample=True
    )

    generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    print("\n📧 Generated Sales Pitch:")
    print(generated_text)

if __name__ == "__main__":
    finetune_model()
```

### LoRA Fine-Tuning (Efficient, Recommended)

LoRA (Low-Rank Adaptation) is much more efficient - fine-tune large models with minimal GPU memory:

```python
# scripts/finetune_sales_agent_lora.py

from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    TrainingArguments
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from trl import SFTTrainer
from datasets import load_dataset
import torch

MODEL_NAME = "mistralai/Mistral-7B-v0.1"
OUTPUT_DIR = "./models/sales_agent_mistral_7b_lora"

def finetune_with_lora():
    """Fine-tune Mistral-7B using LoRA for efficiency"""

    print("🚀 Starting LoRA fine-tuning...")

    # 1. Load model in 4-bit quantization (saves memory!)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        load_in_4bit=True,
        torch_dtype=torch.float16,
        device_map="auto"
    )

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    tokenizer.pad_token = tokenizer.eos_token

    # 2. Prepare model for LoRA training
    model = prepare_model_for_kbit_training(model)

    # 3. Configure LoRA
    lora_config = LoraConfig(
        r=16,  # LoRA rank
        lora_alpha=32,  # LoRA scaling factor
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],  # Which layers to adapt
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM"
    )

    # 4. Wrap model with LoRA
    model = get_peft_model(model, lora_config)

    # Print trainable parameters (should be ~1% of full model)
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    total_params = sum(p.numel() for p in model.parameters())
    print(f"Trainable params: {trainable_params:,} ({100 * trainable_params / total_params:.2f}%)")

    # 5. Load dataset
    dataset = load_dataset("json", data_files={
        "train": "data/processed/sales_pitches_train.jsonl"
    })

    # 6. Training arguments
    training_args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        num_train_epochs=3,
        per_device_train_batch_size=4,
        gradient_accumulation_steps=2,
        warmup_steps=100,
        logging_steps=50,
        save_steps=500,
        learning_rate=2e-4,
        fp16=True,
        optim="paged_adamw_8bit",  # Memory-efficient optimizer
        save_total_limit=3,
    )

    # 7. Initialize SFTTrainer (Supervised Fine-Tuning)
    trainer = SFTTrainer(
        model=model,
        train_dataset=dataset["train"],
        args=training_args,
        peft_config=lora_config,
        dataset_text_field="text",
        max_seq_length=512,
        tokenizer=tokenizer,
    )

    # 8. Train!
    print("🏋️ Starting LoRA training...")
    trainer.train()

    # 9. Save LoRA weights (tiny - only a few MB!)
    print(f"💾 Saving LoRA weights to {OUTPUT_DIR}")
    model.save_pretrained(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)

    print("✅ LoRA fine-tuning complete!")

if __name__ == "__main__":
    finetune_with_lora()
```

**LoRA Benefits:**
- ✅ **99% less memory** than full fine-tuning
- ✅ **Faster training** (fewer parameters to update)
- ✅ **Tiny checkpoints** (5-50 MB vs 5-10 GB)
- ✅ **Can train 7B models on consumer GPUs**

---

## Fine-Tuning Classification Models

### Lead Qualification Classifier

```python
# scripts/finetune_lead_classifier.py

from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    Trainer,
    TrainingArguments
)
from datasets import load_dataset
from sklearn.metrics import accuracy_score, f1_score
import numpy as np

MODEL_NAME = "distilbert-base-uncased"
OUTPUT_DIR = "./models/lead_classifier"

def finetune_classifier():
    """Fine-tune DistilBERT for lead qualification"""

    # 1. Load dataset
    # Format: {"text": "lead message", "label": 0/1/2 (unqualified/qualified/hot)}
    dataset = load_dataset("json", data_files={
        "train": "data/lead_qualification_train.jsonl",
        "validation": "data/lead_qualification_val.jsonl"
    })

    # 2. Load model
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSequenceClassification.from_pretrained(
        MODEL_NAME,
        num_labels=3  # 3 classes: unqualified, qualified, hot
    )

    # 3. Tokenize
    def tokenize_function(examples):
        return tokenizer(
            examples["text"],
            padding="max_length",
            truncation=True,
            max_length=128
        )

    tokenized_dataset = dataset.map(tokenize_function, batched=True)

    # 4. Evaluation metrics
    def compute_metrics(eval_pred):
        predictions, labels = eval_pred
        predictions = np.argmax(predictions, axis=1)

        accuracy = accuracy_score(labels, predictions)
        f1 = f1_score(labels, predictions, average='weighted')

        return {
            "accuracy": accuracy,
            "f1": f1
        }

    # 5. Training arguments
    training_args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        num_train_epochs=5,
        per_device_train_batch_size=16,
        per_device_eval_batch_size=16,
        evaluation_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="f1",
        learning_rate=2e-5,
        weight_decay=0.01,
    )

    # 6. Train
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_dataset["train"],
        eval_dataset=tokenized_dataset["validation"],
        compute_metrics=compute_metrics,
    )

    trainer.train()
    trainer.save_model(OUTPUT_DIR)

    print("✅ Classification model trained!")

if __name__ == "__main__":
    finetune_classifier()
```

---

## Evaluation & Testing

### Generate Test Predictions

```python
# scripts/evaluate_model.py

from transformers import AutoTokenizer, AutoModelForCausalLM
import json

def evaluate_sales_pitch_model(model_path, test_file):
    """Evaluate fine-tuned sales pitch model"""

    # Load model
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForCausalLM.from_pretrained(model_path)

    # Load test cases
    with open(test_file, 'r') as f:
        test_cases = [json.loads(line) for line in f]

    results = []

    for i, test_case in enumerate(test_cases):
        prompt = test_case['prompt']

        # Generate
        inputs = tokenizer(prompt, return_tensors="pt")
        outputs = model.generate(
            **inputs,
            max_new_tokens=300,
            temperature=0.7,
            top_p=0.9,
            do_sample=True
        )

        generated = tokenizer.decode(outputs[0], skip_special_tokens=True)

        results.append({
            "test_case": i + 1,
            "prompt": prompt,
            "generated": generated,
            "expected": test_case.get('expected', None)
        })

        print(f"\n{'='*60}")
        print(f"Test Case {i+1}")
        print(f"{'='*60}")
        print(f"GENERATED:\n{generated}")

    # Save results
    with open("evaluation_results.json", 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n✅ Evaluation complete! Results saved to evaluation_results.json")

if __name__ == "__main__":
    evaluate_sales_pitch_model(
        model_path="./models/sales_agent_gpt_neo_2.7b",
        test_file="data/test_cases.jsonl"
    )
```

### A/B Testing Framework

```python
def ab_test_models(model_a_path, model_b_path, test_prompts, n_iterations=5):
    """
    Compare two models on the same prompts.

    Args:
        model_a_path: Path to model A (e.g., base model)
        model_b_path: Path to model B (e.g., fine-tuned model)
        test_prompts: List of test prompts
        n_iterations: Number of generations per prompt

    Returns:
        Comparison results
    """

    from transformers import AutoTokenizer, AutoModelForCausalLM

    # Load models
    tokenizer_a = AutoTokenizer.from_pretrained(model_a_path)
    model_a = AutoModelForCausalLM.from_pretrained(model_a_path)

    tokenizer_b = AutoTokenizer.from_pretrained(model_b_path)
    model_b = AutoModelForCausalLM.from_pretrained(model_b_path)

    results = []

    for prompt in test_prompts:
        for iteration in range(n_iterations):
            # Generate with Model A
            inputs_a = tokenizer_a(prompt, return_tensors="pt")
            outputs_a = model_a.generate(**inputs_a, max_new_tokens=200)
            text_a = tokenizer_a.decode(outputs_a[0], skip_special_tokens=True)

            # Generate with Model B
            inputs_b = tokenizer_b(prompt, return_tensors="pt")
            outputs_b = model_b.generate(**inputs_b, max_new_tokens=200)
            text_b = tokenizer_b.decode(outputs_b[0], skip_special_tokens=True)

            results.append({
                "prompt": prompt,
                "iteration": iteration,
                "model_a_output": text_a,
                "model_b_output": text_b
            })

            print(f"\nPrompt: {prompt[:50]}...")
            print(f"Model A: {text_a[:100]}...")
            print(f"Model B: {text_b[:100]}...")

    return results
```

---

## Deployment

### Serve Fine-Tuned Model with FastAPI

```python
# services/model_server.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

app = FastAPI()

# Load model at startup
MODEL_PATH = "./models/sales_agent_mistral_7b_lora"
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_PATH,
    torch_dtype=torch.float16,
    device_map="auto"
)

class GenerationRequest(BaseModel):
    prospect_name: str
    company: str
    industry: str
    pain_points: str
    company_size: str = "Unknown"
    temperature: float = 0.7
    max_tokens: int = 300

class GenerationResponse(BaseModel):
    subject: str
    body: str
    model: str

@app.post("/generate/sales-pitch", response_model=GenerationResponse)
def generate_sales_pitch(request: GenerationRequest):
    """Generate a personalized sales pitch"""

    prompt = f"""###Instruction: Generate a personalized sales email pitch.

###Input:
Prospect: {request.prospect_name}
Company: {request.company}
Industry: {request.industry}
Pain Points: {request.pain_points}
Company Size: {request.company_size}

###Response:"""

    try:
        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
        outputs = model.generate(
            **inputs,
            max_new_tokens=request.max_tokens,
            temperature=request.temperature,
            top_p=0.9,
            do_sample=True
        )

        generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)

        # Parse response
        response_text = generated_text.split("###Response:")[-1].strip()

        # Extract subject and body
        lines = response_text.split('\n')
        subject = lines[0].replace("Subject:", "").strip()
        body = '\n'.join(lines[1:]).strip()

        return GenerationResponse(
            subject=subject,
            body=body,
            model=MODEL_PATH
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    return {"status": "healthy", "model": MODEL_PATH}

# Run with: uvicorn model_server:app --host 0.0.0.0 --port 8001
```

---

## Cost Analysis

### Training Costs

| Model Size | Method | GPU Required | Training Time | Cost (Cloud GPU) |
|------------|--------|--------------|---------------|------------------|
| 1B params | Full FT | 1x A100 (40GB) | ~4 hours | ~$12 |
| 1B params | LoRA | 1x T4 (16GB) | ~2 hours | ~$2 |
| 2.7B params | Full FT | 2x A100 (40GB) | ~12 hours | ~$70 |
| 2.7B params | LoRA | 1x A100 (40GB) | ~4 hours | ~$12 |
| 7B params | Full FT | 4x A100 (40GB) | ~24 hours | ~$280 |
| 7B params | LoRA | 1x A100 (40GB) | ~8 hours | ~$24 |

**Recommendation**: Use LoRA for 90% cost savings with similar performance!

### Inference Costs

**Fine-Tuned Model (Self-Hosted)**:
- GPU Server: $100-300/month
- Unlimited inference
- Cost per call: ~$0.001

**vs. API-Based (OpenAI GPT-4)**:
- No infrastructure cost
- Pay per token
- Cost per call: ~$0.10

**Break-Even**: ~1,000 calls/month

---

**Document Version**: 1.0
**Next Steps**: Start with LoRA fine-tuning on a small model (GPT-Neo 1.3B) with 500-1000 examples to validate approach before scaling up.
