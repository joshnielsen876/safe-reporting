# Safe Reporting Analysis

This project analyzes news articles about suicide using OpenAI's GPT models to evaluate their adherence to safe reporting guidelines.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up your OpenAI API key:
```bash
export OPENAI_API_KEY='your-api-key-here'
```

## Project Structure

- `openai_utils.py`: Utility functions for OpenAI API interactions
- `headline_analysis.py`: Analyzes article headlines for safe reporting
- `tempos_analysis.py`: Performs detailed TEMPOS analysis on article content
- `fetch_urls.py`: Fetches article URLs from Google Search
- `extract_content.py`: Extracts content from articles using Jina AI

## Usage

1. First, fetch article URLs:
```bash
python fetch_urls.py
```

2. Extract article content:
```bash
python extract_content.py
```

3. Analyze headlines:
```bash
python headline_analysis.py
```

4. Perform TEMPOS analysis:
```bash
python tempos_analysis.py
```

## Database Schema

The SQLite database (`articles.db`) contains the following fields:
- `url`: Article URL
- `headline`: Article headline
- `article_text`: Full article text
- `name_of_deceased`: Name of the deceased person
- `date_of_death`: Date of death
- `protective`: Whether the headline is protective (headline analysis)
- `neutral`: Whether the headline is neutral (headline analysis)
- `sensational`: Whether the headline is sensational (headline analysis)
- `harmful`: Whether the headline is harmful (headline analysis)
- `reasoning`: Reasoning for headline classification
- `suicide_framing`: TEMPOS score for suicide framing
- `factual_information`: TEMPOS score for factual information
- `non_stigmatizing_language`: TEMPOS score for language use
- `method_and_scene`: TEMPOS score for method/scene description
- `suicide_note`: TEMPOS score for note description
- `factors_and_reasons`: TEMPOS score for factors/reasons discussion
- `sensational`: TEMPOS score for sensational language
- `glamorized`: TEMPOS score for glamorization
- `resources`: TEMPOS score for resource inclusion

## Requirements

- Python 3.8+
- OpenAI API key
- Jina AI API key (for content extraction)
- Google Custom Search API key (for URL fetching)
