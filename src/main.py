#!/usr/bin/env python3
import os
import argparse
import time
import pandas as pd
from typing import List, Dict, Any, Union, Tuple

# Import our modules
from data_collector import StackOverflowDataCollector
from preprocessor import DataPreprocessor
from data_visualizer import DataVisualizer
from categorizer import PostCategorizer

def ensure_directories():
    """Create necessary directories for the project."""
    os.makedirs("../data", exist_ok=True)
    os.makedirs("../data/visualizations", exist_ok=True)
    os.makedirs("../data/categories", exist_ok=True)

def run_data_collection(api_key: str = None, max_questions: int = 20000, tag: str = "nlp"):
    """
    Run the data collection step.
    
    Args:
        api_key (str, optional): Stack Exchange API key. Defaults to None.
        max_questions (int, optional): Maximum number of questions to retrieve. Defaults to 20000.
        tag (str, optional): Tag to filter questions. Defaults to "nlp".
    
    Returns:
        str: Path to the collected dataset file.
    """
    print("\n=== Step 1: Data Collection ===")
    
    output_file = "../data/nlp_stackoverflow_dataset.csv"
    
    # Check if dataset already exists
    if os.path.exists(output_file):
        print(f"Dataset already exists at {output_file}. Skipping collection step.")
        return output_file
    
    # Create collector
    collector = StackOverflowDataCollector(api_key=api_key)
    
    # Collect questions
    start_time = time.time()
    questions = collector.get_questions(tag=tag, max_questions=max_questions)
    
    # Create dataset
    dataset = collector.create_dataset(questions)
    
    # Save dataset
    collector.save_dataset(dataset, filename="nlp_stackoverflow_dataset.csv")
    
    elapsed_time = time.time() - start_time
    print(f"Data collection completed in {elapsed_time:.2f} seconds.")
    
    return output_file

def run_preprocessing(input_file: str, remove_code: bool = True):
    """
    Run the preprocessing step.
    
    Args:
        input_file (str): Path to the input dataset.
        remove_code (bool, optional): Whether to remove code blocks from text. Defaults to True.
    
    Returns:
        str: Path to the preprocessed dataset file.
    """
    print("\n=== Step 2: Data Preprocessing ===")
    
    output_file = "../data/preprocessed_nlp_dataset.csv"
    
    # Check if preprocessed dataset already exists
    if os.path.exists(output_file):
        print(f"Preprocessed dataset already exists at {output_file}. Skipping preprocessing step.")
        return output_file
    
    # Check if input file exists
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Input file {input_file} not found.")
    
    # Load dataset
    df = pd.read_csv(input_file)
    
    # Create preprocessor
    preprocessor = DataPreprocessor(remove_code=remove_code)
    
    # Preprocess data
    start_time = time.time()
    processed_df = preprocessor.preprocess_dataframe(df)
    
    # Save preprocessed data
    processed_df.to_csv(output_file, index=False)
    
    elapsed_time = time.time() - start_time
    print(f"Preprocessing completed in {elapsed_time:.2f} seconds.")
    
    return output_file

def run_visualization(input_file: str):
    """
    Run the data visualization step.
    
    Args:
        input_file (str): Path to the preprocessed dataset.
    """
    print("\n=== Step 3: Data Visualization ===")
    
    # Check if input file exists
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Input file {input_file} not found.")
    
    # Create visualizer
    visualizer = DataVisualizer(input_file)
    
    # Generate visualizations
    start_time = time.time()
    visualizer.generate_visualizations()
    
    elapsed_time = time.time() - start_time
    print(f"Visualization completed in {elapsed_time:.2f} seconds.")

def run_categorization(input_file: str):
    """
    Run the post categorization step.
    
    Args:
        input_file (str): Path to the preprocessed dataset.
    """
    print("\n=== Step 4: Post Categorization ===")
    
    # Check if input file exists
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Input file {input_file} not found.")
    
    # Create categorizer
    categorizer = PostCategorizer(input_file)
    
    # Perform categorization
    start_time = time.time()
    categorizer.categorize_all()
    
    elapsed_time = time.time() - start_time
    print(f"Categorization completed in {elapsed_time:.2f} seconds.")

def parse_arguments():
    """
    Parse command line arguments.
    
    Returns:
        argparse.Namespace: Parsed arguments.
    """
    parser = argparse.ArgumentParser(description="NLP Knowledge Base Generator")
    
    parser.add_argument("--api-key", type=str, help="Stack Exchange API key")
    parser.add_argument("--max-questions", type=int, default=20000, help="Maximum number of questions to retrieve")
    parser.add_argument("--tag", type=str, default="nlp", help="Tag to filter questions")
    parser.add_argument("--skip-collection", action="store_true", help="Skip data collection step")
    parser.add_argument("--skip-preprocessing", action="store_true", help="Skip preprocessing step")
    parser.add_argument("--skip-visualization", action="store_true", help="Skip visualization step")
    parser.add_argument("--skip-categorization", action="store_true", help="Skip categorization step")
    parser.add_argument("--remove-code", action="store_true", help="Remove code blocks from text during preprocessing")
    
    return parser.parse_args()

def main():
    """Main function to run the NLP knowledge base pipeline."""
    # Ensure necessary directories exist
    ensure_directories()
    
    # Parse command line arguments
    args = parse_arguments()
    
    # Display banner
    print("=" * 80)
    print(" NLP Knowledge Base Generator ".center(80, "="))
    print("=" * 80)
    
    dataset_file = "../data/nlp_stackoverflow_dataset.csv"
    preprocessed_file = "../data/preprocessed_nlp_dataset.csv"
    
    # Step 1: Data Collection
    if not args.skip_collection:
        dataset_file = run_data_collection(
            api_key=args.api_key,
            max_questions=args.max_questions,
            tag=args.tag
        )
    else:
        print("\n=== Step 1: Data Collection [SKIPPED] ===")
    
    # Step 2: Data Preprocessing
    if not args.skip_preprocessing:
        preprocessed_file = run_preprocessing(
            input_file=dataset_file,
            remove_code=args.remove_code
        )
    else:
        print("\n=== Step 2: Data Preprocessing [SKIPPED] ===")
    
    # Step 3: Data Visualization
    if not args.skip_visualization:
        run_visualization(input_file=preprocessed_file)
    else:
        print("\n=== Step 3: Data Visualization [SKIPPED] ===")
    
    # Step 4: Post Categorization
    if not args.skip_categorization:
        run_categorization(input_file=preprocessed_file)
    else:
        print("\n=== Step 4: Post Categorization [SKIPPED] ===")
    
    # Display completion message
    print("\n" + "=" * 80)
    print(" NLP Knowledge Base Generation Complete ".center(80, "="))
    print("=" * 80)
    print("\nResults:")
    print(f"- Raw dataset: {dataset_file}")
    print(f"- Preprocessed dataset: {preprocessed_file}")
    print(f"- Visualizations: ../data/visualizations/")
    print(f"- Categorized posts: ../data/categories/")
    print("\nThank you for using the NLP Knowledge Base Generator!")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}") 