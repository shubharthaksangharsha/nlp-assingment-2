# NLP Knowledge Base - Source Code

This directory contains the source code for data collection, processing, and categorization pipeline of the NLP Knowledge Base project.

▲ Web Demo: [https://nlp-knowledge-base-2ay6q43v3-shubharthaks-projects.vercel.app/](https://nlp-knowledge-base-2ay6q43v3-shubharthaks-projects.vercel.app/)

## Directory Structure

```
src/
├── data_collector.py    # Stack Exchange API integration and data fetching
├── preprocessor.py      # Data cleaning and text preprocessing
├── data_visualizer.py   # Visualization generation for insights
├── categorizer.py       # Post categorization logic
├── main.py             # Pipeline orchestration
└── __init__.py         # Package initialization
```

## Components

### 1. Data Collection (`data_collector.py`)
- Integrates with Stack Exchange API
- Fetches NLP-related questions and answers
- Handles API rate limiting and pagination

### 2. Data Preprocessing (`preprocessor.py`)
- Cleans and normalizes text data
- Handles HTML entities and code blocks
- Prepares data for categorization

### 3. Data Visualization (`data_visualizer.py`)
- Generates insights from the dataset
- Creates visualizations for web interface
- Analyzes trends and patterns

### 4. Categorization (`categorizer.py`)
- Implements post categorization logic
- Organizes content into multiple schemes
- Handles category assignment rules

### 5. Pipeline Orchestration (`main.py`)
- Coordinates data processing pipeline
- Manages workflow between components
- Handles error cases and logging

## Usage

1. **Run Complete Pipeline**
   ```bash
   python main.py
   ```

2. **Individual Component Usage**
   ```python
   from src.data_collector import StackExchangeCollector
   from src.preprocessor import DataPreprocessor
   from src.categorizer import PostCategorizer
   from src.data_visualizer import DataVisualizer

   # Example: Run data collection
   collector = StackExchangeCollector()
   data = collector.fetch_data()

   # Example: Preprocess data
   preprocessor = DataPreprocessor()
   cleaned_data = preprocessor.process(data)
   ```

## Data Flow

1. **Collection** → **Preprocessing** → **Categorization** → **Visualization**
   - Data is fetched from Stack Exchange
   - Raw data is cleaned and normalized
   - Posts are categorized into schemes
   - Visualizations are generated

## Configuration

- API keys and settings in environment variables
- Category rules in categorizer configuration
- Visualization parameters in visualizer settings

## Output

The pipeline generates:
- Categorized posts in JSON/CSV format
- Visualization images for web interface
- Statistics and metadata files 