import pandas as pd
import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import json
import os
from typing import List, Dict, Any, Union, Tuple

class PostCategorizer:
    """
    Categorize NLP-related Stack Overflow posts based on various criteria.
    """
    
    def __init__(self, data_path: str):
        """
        Initialize the categorizer with preprocessed dataset.
        
        Args:
            data_path (str): Path to the preprocessed dataset.
        """
        self.data_path = data_path
        self.df = pd.read_csv(data_path)
        self.categories = {}
        
        # Create categories directory
        os.makedirs("../data/categories", exist_ok=True)
    
    def keyword_based_categorization(self, column: str = 'processed_title', 
                                    min_posts_per_category: int = 10) -> Dict[str, List[int]]:
        """
        Categorize posts based on keywords in the title.
        
        Args:
            column (str, optional): Column to search for keywords. Defaults to 'processed_title'.
            min_posts_per_category (int, optional): Minimum posts required for a category. Defaults to 10.
            
        Returns:
            Dict[str, List[int]]: Dictionary mapping category names to list of post indices.
        """
        print(f"Performing keyword-based categorization on {column}...")
        
        # Define categories and their keywords
        category_keywords = {
            "Text Classification": ["classification", "classifier", "classify", "categorization", "categorize"],
            "Named Entity Recognition": ["ner", "named entity", "entity recognition", "entity extraction"],
            "Sentiment Analysis": ["sentiment", "emotion", "polarity", "opinion"],
            "Text Summarization": ["summary", "summarization", "summarize", "summarizing"],
            "Machine Translation": ["translation", "translate", "translator", "machine translation", "mt"],
            "Question Answering": ["question answering", "qa system", "answer questions"],
            "Topic Modeling": ["topic", "lda", "topic model", "latent dirichlet"],
            "Word Embeddings": ["word2vec", "glove", "embedding", "word embedding", "vector"],
            "Text Preprocessing": ["preprocessing", "preprocess", "tokenization", "tokenize", "lemmatization", "stemming"],
            "Language Identification": ["language identification", "language detection", "detect language", "identify language"],
            "Text Similarity": ["similarity", "similar text", "document similarity", "semantic similarity"],
            "Part-of-Speech Tagging": ["pos", "part of speech", "tagging", "tagger"],
            "Implementation Issues": ["how to", "how do i", "implementation", "code", "example"],
            "Understanding Concepts": ["what is", "explain", "understand", "concept", "difference between", "why"],
            "Performance Issues": ["slow", "performance", "speed", "memory", "efficient", "optimization"],
            "Error Troubleshooting": ["error", "problem", "issue", "bug", "fix", "solve", "exception", "failed"],
            "Library Usage": ["spacy", "nltk", "huggingface", "transformers", "gensim", "pytorch", "tensorflow", "bert"],
            "Data Collection": ["corpus", "dataset", "data collection", "scraping", "crawling"],
            "Evaluation Metrics": ["accuracy", "precision", "recall", "f1", "bleu", "rouge", "evaluation", "metric"]
        }
        
        # Initialize categories
        categories = {category: [] for category in category_keywords}
        
        # Check if column exists
        if column not in self.df.columns:
            print(f"Column '{column}' not found in the dataset.")
            return categories
        
        # Iterate through posts and categorize
        for i, post_text in enumerate(self.df[column]):
            if not isinstance(post_text, str):
                continue
                
            post_text = post_text.lower()
            
            # Check each category
            for category, keywords in category_keywords.items():
                for keyword in keywords:
                    if keyword in post_text:
                        categories[category].append(i)
                        break
        
        # Remove categories with fewer than min_posts_per_category posts
        categories = {k: v for k, v in categories.items() if len(v) >= min_posts_per_category}
        
        # Save categorized indices
        self.categories["keyword_based"] = categories
        
        # Print statistics
        print("\nKeyword-based categorization results:")
        for category, indices in categories.items():
            print(f"{category}: {len(indices)} posts")
            
        return categories
    
    def task_based_categorization(self, column: str = 'processed_title', 
                                min_posts_per_category: int = 10) -> Dict[str, List[int]]:
        """
        Categorize posts based on NLP tasks in the title.
        
        Args:
            column (str, optional): Column to search for task keywords. Defaults to 'processed_title'.
            min_posts_per_category (int, optional): Minimum posts required for a category. Defaults to 10.
            
        Returns:
            Dict[str, List[int]]: Dictionary mapping category names to list of post indices.
        """
        print(f"Performing task-based categorization on {column}...")
        
        # Define NLP tasks and their keywords
        task_keywords = {
            "Text Classification": ["classification", "classifier", "classify", "categorization", "categorize"],
            "Named Entity Recognition": ["ner", "named entity", "entity recognition", "entity extraction"],
            "Sentiment Analysis": ["sentiment", "emotion", "polarity", "opinion"],
            "Text Summarization": ["summary", "summarization", "summarize", "summarizing"],
            "Machine Translation": ["translation", "translate", "translator", "machine translation", "mt"],
            "Question Answering": ["question answering", "qa system", "answer questions"],
            "Topic Modeling": ["topic", "lda", "topic model", "latent dirichlet"],
            "Word Embeddings": ["word2vec", "glove", "embedding", "word embedding", "vector"],
            "Tokenization": ["tokenization", "tokenize", "tokenizer", "tokens"],
            "Lemmatization": ["lemmatization", "lemmatize", "lemmatizer", "lemma"],
            "Stemming": ["stemming", "stem", "stemmer", "porter"],
            "Language Identification": ["language identification", "language detection", "detect language", "identify language"],
            "Text Similarity": ["similarity", "similar text", "document similarity", "semantic similarity"],
            "Part-of-Speech Tagging": ["pos", "part of speech", "tagging", "tagger"],
            "Dependency Parsing": ["dependency parsing", "dependency parser", "syntactic parsing"],
            "Coreference Resolution": ["coreference", "coreference resolution", "anaphora"],
            "Text Generation": ["text generation", "generate text", "text generator", "gpt"]
        }
        
        # Initialize categories
        categories = {task: [] for task in task_keywords}
        
        # Check if column exists
        if column not in self.df.columns:
            print(f"Column '{column}' not found in the dataset.")
            return categories
        
        # Iterate through posts and categorize
        for i, post_text in enumerate(self.df[column]):
            if not isinstance(post_text, str):
                continue
                
            post_text = post_text.lower()
            
            # Check each task
            for task, keywords in task_keywords.items():
                for keyword in keywords:
                    if keyword in post_text:
                        categories[task].append(i)
                        break
        
        # Remove tasks with fewer than min_posts_per_category posts
        categories = {k: v for k, v in categories.items() if len(v) >= min_posts_per_category}
        
        # Save categorized indices
        self.categories["task_based"] = categories
        
        # Print statistics
        print("\nTask-based categorization results:")
        for task, indices in categories.items():
            print(f"{task}: {len(indices)} posts")
            
        return categories
    
    def question_type_categorization(self):
        """
        Categorize posts based on question type (What, Why, How).
        """
        print("Performing question type categorization...")
        
        # Create patterns for different question types
        patterns = {
            "what": r'\bwhat\b|\bwhich\b',
            "why": r'\bwhy\b',
            "how": r'\bhow\b',
            "when": r'\bwhen\b',
            "where": r'\bwhere\b'
        }
        
        # Initialize categories
        question_categories = {cat: [] for cat in patterns.keys()}
        
        # Iterate through posts and categorize them
        for idx, row in self.df.iterrows():
            # Make sure we're checking the original title, not processed_title
            if 'title' not in row:
                continue
            
            title = row['title'].lower() if isinstance(row['title'], str) else ""
            
            # Check each pattern and assign to appropriate category
            for qtype, pattern in patterns.items():
                if re.search(pattern, title):
                    question_categories[qtype].append(idx)
                    break  # Assign to first matching category only
        
        # Save categorization results
        self._save_categorization("question_type", question_categories)
        
        # Print results
        print("\nQuestion Type categorization results:")
        for qtype, indices in question_categories.items():
            print(f"{qtype.capitalize()}: {len(indices)} posts")
        
        return question_categories
    
    def library_based_categorization(self, column: str = 'processed_title', 
                                  min_posts_per_category: int = 10) -> Dict[str, List[int]]:
        """
        Categorize posts based on NLP libraries mentioned.
        
        Args:
            column (str, optional): Column to search for library mentions. Defaults to 'processed_title'.
            min_posts_per_category (int, optional): Minimum posts required for a category. Defaults to 10.
            
        Returns:
            Dict[str, List[int]]: Dictionary mapping category names to list of post indices.
        """
        print(f"Performing library-based categorization on {column}...")
        
        # Define NLP libraries and their aliases
        library_keywords = {
            "NLTK": ["nltk", "natural language toolkit"],
            "spaCy": ["spacy", "spacy nlp"],
            "Hugging Face": ["huggingface", "hugging face", "transformers", "🤗"],
            "BERT": ["bert", "distilbert", "roberta", "albert"],
            "Word2Vec": ["word2vec", "word vectors", "word embedding"],
            "GloVe": ["glove", "global vectors"],
            "fastText": ["fasttext"],
            "Gensim": ["gensim"],
            "Stanford NLP": ["stanford nlp", "stanford core nlp", "stanfordnlp", "stanza"],
            "OpenNLP": ["opennlp"],
            "TextBlob": ["textblob"],
            "GPT": ["gpt", "gpt-2", "gpt-3", "gpt-4", "chatgpt"],
            "WordNet": ["wordnet"],
            "TensorFlow": ["tensorflow", "tf"],
            "PyTorch": ["pytorch", "torch"],
            "scikit-learn": ["scikit learn", "sklearn"]
        }
        
        # Initialize categories
        categories = {library: [] for library in library_keywords}
        
        # Check if column exists
        if column not in self.df.columns:
            print(f"Column '{column}' not found in the dataset.")
            return categories
        
        # Check tags column as well if available
        tags_available = 'tags' in self.df.columns
        
        # Iterate through posts and categorize
        for i, post_text in enumerate(self.df[column]):
            if not isinstance(post_text, str):
                continue
                
            post_text = post_text.lower()
            
            # Get tags for this post if available
            post_tags = []
            if tags_available:
                tags = self.df.iloc[i]['tags']
                if isinstance(tags, str):
                    try:
                        # Try to convert string representation of list to actual list
                        if tags.startswith('[') and tags.endswith(']'):
                            post_tags = eval(tags)
                        else:
                            post_tags = tags.split()
                    except:
                        post_tags = []
                elif isinstance(tags, list):
                    post_tags = tags
            
            # Convert tags to lowercase for matching
            post_tags = [tag.lower() for tag in post_tags]
            
            # Check each library in title and tags
            for library, keywords in library_keywords.items():
                # Check in title
                for keyword in keywords:
                    if keyword in post_text:
                        categories[library].append(i)
                        break
                
                # Check in tags if not already categorized
                if i not in categories[library] and tags_available:
                    for keyword in keywords:
                        if any(keyword in tag for tag in post_tags):
                            categories[library].append(i)
                            break
        
        # Remove libraries with fewer than min_posts_per_category posts
        categories = {k: v for k, v in categories.items() if len(v) >= min_posts_per_category}
        
        # Save categorized indices
        self.categories["library_based"] = categories
        
        # Print statistics
        print("\nLibrary-based categorization results:")
        for library, indices in categories.items():
            print(f"{library}: {len(indices)} posts")
            
        return categories
    
    def save_categories_to_files(self):
        """
        Save categorized posts to CSV files.
        """
        print("Saving categorized posts to files...")
        
        # Create summary file
        summary = {
            "categorization_methods": {},
            "total_categorized_posts": 0,
            "unique_categorized_posts": set()
        }
        
        # Process each categorization method
        for method, categories in self.categories.items():
            print(f"\nSaving {method} categories...")
            
            method_dir = f"../data/categories/{method}"
            os.makedirs(method_dir, exist_ok=True)
            
            # Create summary entry for this method
            summary["categorization_methods"][method] = {
                "categories": {},
                "total_posts": 0
            }
            
            # Save each category to a file
            for category, indices in categories.items():
                # Create a subset of the dataframe with these posts
                category_df = self.df.iloc[indices].copy()
                
                # Add indices to unique categorized posts set
                summary["unique_categorized_posts"].update(indices)
                
                # Update summary counts
                summary["categorization_methods"][method]["categories"][category] = len(indices)
                summary["categorization_methods"][method]["total_posts"] += len(indices)
                
                # Clean category name for filename
                clean_category = category.replace(' ', '_').replace('/', '_')
                
                # Save to CSV
                output_path = f"{method_dir}/{clean_category}.csv"
                category_df.to_csv(output_path, index=False)
                print(f"Saved {len(indices)} posts to {output_path}")
        
        # Calculate total unique categorized posts
        summary["total_categorized_posts"] = len(summary["unique_categorized_posts"])
        
        # Convert set to list for JSON serialization
        summary["unique_categorized_posts"] = list(summary["unique_categorized_posts"])
        
        # Save summary to JSON
        with open("../data/categories/categorization_summary.json", "w") as f:
            json.dump({
                "categorization_methods": summary["categorization_methods"],
                "total_categorized_posts": summary["total_categorized_posts"],
                "total_unique_posts": len(summary["unique_categorized_posts"])
            }, f, indent=2)
        
        print(f"\nCategorization complete. Total unique categorized posts: {summary['total_categorized_posts']}")
    
    def categorize_all(self):
        """
        Perform all categorization methods.
        """
        # Perform keyword-based categorization
        self.keyword_based_categorization()
        
        # Perform task-based categorization
        self.task_based_categorization()
        
        # Perform question type categorization
        self.question_type_categorization()
        
        # Perform library-based categorization
        self.library_based_categorization()
        
        # Save categories to files
        self.save_categories_to_files()

    def _save_categorization(self, category_type, categories):
        """
        Save categorization results to JSON files.
        
        Args:
            category_type (str): The type of categorization (e.g., 'keyword_based', 'task_based').
            categories (dict): Dictionary mapping category names to lists of post indices.
        """
        print(f"\n{category_type.replace('_', ' ').title()} categorization results:")
        category_dir = os.path.join("../data/categories", category_type)
        os.makedirs(category_dir, exist_ok=True)
        
        # Create a CSV lookup file for this category type
        lookup_file = os.path.join("../data/categories", f"{category_type}_categories.csv")
        with open(lookup_file, 'w') as f:
            f.write("category,count,file_path\n")
            
            for category, post_indices in categories.items():
                if len(post_indices) > 0:
                    # Print summary
                    print(f"{category.replace('_', ' ').title()}: {len(post_indices)} posts")
                    
                    # Save to CSV lookup
                    category_filename = f"{category.lower().replace(' ', '_')}.json"
                    file_path = os.path.join(category_type, category_filename)
                    f.write(f"{category},{len(post_indices)},{file_path}\n")
                    
                    # Save category data
                    category_data = {
                        "category": category,
                        "post_count": len(post_indices),
                        "posts": self.df.iloc[post_indices].to_dict(orient='records')
                    }
                    with open(os.path.join(category_dir, category_filename), 'w') as cat_file:
                        json.dump(category_data, cat_file, indent=2)


if __name__ == "__main__":
    try:
        # Path to preprocessed dataset
        data_path = "../data/preprocessed_nlp_dataset.csv"
        
        # Create categorizer
        categorizer = PostCategorizer(data_path)
        
        # Perform all categorizations
        categorizer.categorize_all()
        
    except Exception as e:
        print(f"Error: {e}") 