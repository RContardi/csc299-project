# Tasks 4: OpenAI Chat Completions API Experiment

This is a standalone experiment using the OpenAI Chat Completions API to summarize paragraph-length task descriptions into short phrases, as required by the [2025-11-10 Mon] milestone.

## Requirements
- Python 3.13+
- `openai` package (installed via `uv`)
- `OPENAI_API_KEY` environment variable

## Setup

1. Set your OpenAI API key:
   ```powershell
   # Windows PowerShell (current session)
   $env:OPENAI_API_KEY = 'sk-...'
   
   # or persist for new sessions
   setx OPENAI_API_KEY "sk-..."
   ```

2. Install dependencies (if not already done):
   ```bash
   cd tasks4
   uv sync
   ```

## Usage

Run the summarizer:
```bash
uv run tasks4
```

or

```bash
python -m tasks4.src
```

The program will summarize two sample paragraph-length task descriptions and print the short-phrase summaries.

## Features
- Summarizes multiple paragraph-length descriptions independently
- Uses the OpenAI Chat Completions API (currently `gpt-3.5-turbo`)
- Gracefully handles missing API keys and quota errors
- Portable across Windows, macOS, and Linux

## Notes
- If you encounter a 429 (quota exceeded) error, check your OpenAI billing and usage at https://platform.openai.com/account/billing
- The code is designed to work with or without an API key (see error messages for guidance).
