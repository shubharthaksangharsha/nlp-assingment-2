# NLP Knowledge Base

A comprehensive repository of NLP-related questions, answers, and insights from the Stack Exchange network, organized for easy discovery and learning.

## Overview

The NLP Knowledge Base project collects and categorizes Natural Language Processing (NLP) questions and answers from Stack Overflow and other Stack Exchange sites. It provides a searchable database with multiple categorization schemes, data visualizations, and a modern web interface for exploring the knowledge base.

![NLP Knowledge Base](web-app/static/img/title_wordcloud.png)

## Features

- **Data Collection Pipeline**: Fetches NLP-related posts from Stack Exchange API
- **Multi-faceted Categorization**: Organizes posts by keywords, tasks, question types, and libraries
- **Data Visualizations**: Generates visual insights about the NLP community and its interests
- **Interactive Web Interface**: Modern, responsive web application for exploring the knowledge base
- **Search Functionality**: Full-text search capabilities to find specific information
- **Code Syntax Highlighting**: Enhanced display of code snippets

## Project Structure

```
nlp_knowledge_base/
├── data/                      # Data storage directory
│   ├── nlp_stackoverflow_dataset.csv    # Raw dataset
│   ├── preprocessed_nlp_dataset.csv     # Processed dataset
│   ├── categories/            # Categorized posts
│   └── visualizations/        # Generated visualizations
├── src/                       # Source code for data pipeline
│   ├── data_collector.py      # Stack Exchange API integration
│   ├── preprocessor.py        # Data cleaning and preprocessing
│   ├── data_visualizer.py     # Visualization generation
│   └── categorizer.py         # Post categorization
├── web-app/                   # Web application
│   ├── app.py                 # Flask application
│   ├── templates/             # HTML templates
│   └── static/                # Static assets (CSS, JS, images)
├── run.sh                     # Main pipeline launcher (Linux/Mac)
├── run.bat                    # Main pipeline launcher (Windows)
└── README.md                  # This file
```

## Setup Instructions

### Prerequisites

- Python 3.6 or higher
- pip (Python package manager)
- Stack Exchange API key (optional, for data collection)

### Installation

1. Clone the repository or download the source code

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Register for the Stack Exchange API (optional, for data collection):
   - Go to https://stackapps.com/apps/oauth/register
   - Create a new application
   - Note your API key

### Running the Data Pipeline

To collect and process data from Stack Exchange:

**Linux/Mac:**
```bash
./run.sh YOUR_API_KEY
```

**Windows:**
```bat
run.bat YOUR_API_KEY
```

The pipeline performs the following steps:
1. Data collection from Stack Exchange API
2. Data preprocessing and cleaning
3. Data visualization generation
4. Post categorization

### Running the Web Application

To launch the web interface for exploring the knowledge base:

**Linux/Mac:**
```bash
cd web-app
./run_webapp.sh
```

**Windows:**
```bat
cd web-app
run_webapp.bat
```

Then open your browser and navigate to: http://localhost:5000

## Demo Mode

If you want to try the application without collecting data from Stack Exchange, you can use the demo mode:

```bash
cd web-app
python demo.py
./run_webapp.sh
```

This will set up a sample dataset with visualizations and categories for demonstration purposes.

## API Key

The current API key used in this project is: `rl_QSELmsmpZPK2JvKfEHYZ8Pa9e`

Note that API keys have usage limitations. If you experience issues with data collection, you may need to register for your own API key.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Stack Exchange for providing the API to access their data
- The NLP community for their valuable questions and answers
- All the open-source libraries used in this project 