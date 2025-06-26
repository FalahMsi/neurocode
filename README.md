# NeuroCode – Modular Cognitive AI for Code Understanding

This repository contains the core implementation of the **NeuroCode initiative** — an open intellectual project aimed at rethinking how artificial intelligence understands and interacts with programming code.

## About the Project

NeuroCode simulates a human-like memory system within AI by extracting lightweight "code neurons" from source code, documentation, and patterns. These neurons are:
- Activated only when relevant
- Forgotten when unused
- Adaptively weighted based on frequency and context
- Organized to mimic human cognitive structures (contextual recall, associative memory)

The goal is to reduce reliance on large-scale inference from LLMs by using selective memory activation — similar to how the human brain recalls only relevant neural pathways depending on the task or context.

You can read the full open initiative (in PDF format) here:  
👉 [initiative.pdf](./initiative.pdf)

## What's Included

- Core extraction logic and analyzers
- Tools to link code patterns to semantic concepts
- Modular design for extensibility across languages/domains
- Main entry point (`main.py`) for running custom experiments

## What's Not Included

This repository **excludes** heavy data files and intermediate artifacts to maintain performance and simplicity. Notably:
- `example_bank.json`, `example_bank_advanced.json`
- Full training datasets (`python100k_train.json`)
- SQLite databases
- Large log files

You can generate your own data using the included scripts or contact the author for instructions on creating a minimal test environment.

## Quick Start

```bash
# Assuming dependencies are installed
python main.py
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
