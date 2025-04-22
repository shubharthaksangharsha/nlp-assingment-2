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

def run_data_collection(api_key: str = None, max_questions: int = 20000, tag: str = "nlp", force_collection: bool = False):
    """
    Run the data collection step.
    Collects questions for a specific tag and appends to a combined dataset file.

    Args:
        api_key (str, optional): Stack Exchange API key. Defaults to None.
        max_questions (int, optional): Maximum number of questions to retrieve. Defaults to 20000.
        tag (str, optional): Tag to filter questions. Defaults to "nlp".
        force_collection (bool, optional): Whether to force initial data collection for this tag even if intermediate files exist. Defaults to False.

    Returns:
        str: Path to the *combined* dataset file where data was appended.
    """
    print(f"\n=== Step 1: Data Collection for tag [{tag}] ===")

    # Define the path for the intermediate file for this specific tag
    # This file stores the initial question metadata collected by get_questions
    tag_specific_intermediate_file = f"../data/{tag}_questions_initial_collection.csv"

    # Define the path for the *combined* dataset file where all tags' data will be appended
    combined_output_file = "../data/nlp_stackoverflow_dataset.csv"

    questions_list = []

    # Check if the intermediate collection file for this tag already exists
    # We only skip the initial collection for this tag if the intermediate file exists and force_collection is False
    if os.path.exists(tag_specific_intermediate_file) and not force_collection:
        print(f"Intermediate dataset for tag [{tag}] already exists at {tag_specific_intermediate_file}. Skipping initial collection for this tag.")
        # Load questions from the intermediate file to proceed to create_dataset
        try:
            # Ensure correct dtypes if loading from CSV
            questions_df = pd.read_csv(tag_specific_intermediate_file)
            questions_list = questions_df.to_dict('records')
            print(f"Loaded {len(questions_list)} questions from intermediate file.")
        except Exception as e:
            print(f"Error loading intermediate file {tag_specific_intermediate_file}: {e}")
            questions_list = [] # Proceed with empty list if loading fails or file is corrupt

    else:
        # Create collector for the initial question list collection
        collector = StackOverflowDataCollector(api_key=api_key)

        # Collect questions for the current tag
        start_time = time.time()
        questions_list = collector.get_questions(tag=tag, max_questions=max_questions)

        # Save the intermediate result for this tag if any questions were collected
        if questions_list:
             intermediate_df = pd.DataFrame(questions_list)
             intermediate_df.to_csv(tag_specific_intermediate_file, index=False)
             print(f"Saved intermediate dataset for tag [{tag}] to {tag_specific_intermediate_file}")

        elapsed_time = time.time() - start_time
        print(f"Initial data collection for tag [{tag}] completed in {elapsed_time:.2f} seconds.")

    # Now, process the collected questions (fetch answers) and append to the *combined* dataset file
    # This step uses the create_dataset function which appends to the specified filename
    if questions_list: # Only run create_dataset if there are questions to process
        # Create a new collector instance for this phase if needed,
        # ensuring it has the API key for answer fetching
        collector = StackOverflowDataCollector(api_key=api_key)
        # Use the combined_output_file name for the create_dataset function
        collector.create_dataset(questions_list, filename=os.path.basename(combined_output_file))

    # Return the path to the combined dataset file for subsequent steps
    return combined_output_file

def run_preprocessing(input_file: str, remove_code: bool = True, force_collection: bool = False):
    """
    Run the preprocessing step.
    Processes the combined dataset file.

    Args:
        input_file (str): Path to the input dataset (should be the combined file).
        remove_code (bool, optional): Whether to remove code blocks from text. Defaults to True.
        force_collection (bool, optional): Whether the previous collection step was forced for *any* tag.
                                           This is used to decide if reprocessing is needed. Defaults to False.

    Returns:
        str: Path to the preprocessed dataset file.
    """
    print("\n=== Step 2: Data Preprocessing ===")

    # Define the output filename for the preprocessed combined dataset
    output_file = input_file.replace(".csv", "_preprocessed.csv")

    # Check if preprocessed dataset already exists
    # Reprocess only if the input file is newer than the output file,
    # or if force_collection was true (meaning new data was likely added),
    # or if the output file doesn't exist.
    reprocess_needed = True
    if os.path.exists(output_file) and os.path.exists(input_file):
        if not force_collection and os.path.getmtime(output_file) >= os.path.getmtime(input_file):
            print(f"Preprocessed dataset already exists and is up-to-date at {output_file}. Skipping preprocessing step.")
            reprocess_needed = False


    if reprocess_needed:
        # Check if input file exists
        if not os.path.exists(input_file):
            # This could happen if collection was skipped and the combined file doesn't exist yet
            print(f"Input file for preprocessing not found: {input_file}. Skipping preprocessing.")
            return None # Or raise an error

        print(f"Loading data from {input_file} for preprocessing...")
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
        print(f"Preprocessing completed in {elapsed_time:.2f} seconds. Output saved to {output_file}")
    else:
        print(f"Preprocessing skipped. Using existing file: {output_file}")


    return output_file


def run_visualization(input_file: str):
    """
    Run the data visualization step.
    Uses the preprocessed combined dataset file.

    Args:
        input_file (str): Path to the preprocessed dataset.
    """
    print("\n=== Step 3: Data Visualization ===")

    # Check if input file exists
    if not os.path.exists(input_file) or input_file is None:
        print(f"Input file for visualization not found or is None: {input_file}. Skipping visualization step.")
        return

    print(f"Using preprocessed data from {input_file} for visualization...")
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
    Uses the preprocessed combined dataset file.

    Args:
        input_file (str): Path to the preprocessed dataset.
    """
    print("\n=== Step 4: Post Categorization ===")

    # Check if input file exists
    if not os.path.exists(input_file) or input_file is None:
        print(f"Input file for categorization not found or is None: {input_file}. Skipping categorization step.")
        return

    print(f"Using preprocessed data from {input_file} for categorization...")
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
    parser.add_argument("--max-questions", type=int, default=20000, help="Maximum number of questions to retrieve per tag collection run") # Clarified help text
    parser.add_argument("--tag", type=str, default="nlp", help="Tag to filter questions for the current collection run") # Clarified help text
    parser.add_argument("--skip-collection", action="store_true", help="Skip initial data collection for the specified tag")
    parser.add_argument("--skip-preprocessing", action="store_true", help="Skip preprocessing step on the combined dataset")
    parser.add_argument("--skip-visualization", action="store_true", help="Skip visualization step")
    parser.add_argument("--skip-categorization", action="store_true", help="Skip categorization step")
    parser.add_argument("--remove-code", action="store_true", help="Remove code blocks from text during preprocessing")
    parser.add_argument("--force-collection", action="store_true", help="Force initial data collection for the specified tag, overwriting intermediate files")


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

    # Define the fixed path for the combined raw dataset file
    combined_raw_dataset_file = "../data/nlp_stackoverflow_dataset.csv"
    # Define the path for the preprocessed combined dataset file
    preprocessed_combined_dataset_file = combined_raw_dataset_file.replace(".csv", "_preprocessed.csv")


    # Step 1: Data Collection
    # run_data_collection will collect for the specified tag and append to the combined raw dataset file
    if not args.skip_collection:
        # run_data_collection now returns the path to the combined file
        run_data_collection(
            api_key=args.api_key,
            max_questions=args.max_questions,
            tag=args.tag,
            force_collection=args.force_collection
        )
        # After collection, the combined_raw_dataset_file is the one to use for subsequent steps
        input_file_for_subsequent_steps = combined_raw_dataset_file
    else:
        print(f"\n=== Step 1: Data Collection for tag [{args.tag}] [SKIPPED] ===")
        # If skipping collection, the input file for subsequent steps is the existing combined file
        input_file_for_subsequent_steps = combined_raw_dataset_file


    # Step 2: Data Preprocessing
    if not args.skip_preprocessing:
        # Preprocess the combined dataset file
        # Pass force_collection so preprocessing reruns if new data was collected
        preprocessed_file_output = run_preprocessing(
            input_file=input_file_for_subsequent_steps, # Use the combined file as input
            remove_code=args.remove_code,
            force_collection=args.force_collection # Rerun preprocessing if collection was forced
        )
    else:
        print("\n=== Step 2: Data Preprocessing [SKIPPED] ===")
        # If skipping preprocessing, the preprocessed file is the standard output name
        preprocessed_file_output = preprocessed_combined_dataset_file


    # Step 3: Data Visualization
    if not args.skip_visualization:
        # Visualize the preprocessed combined dataset
        run_visualization(input_file=preprocessed_file_output)
    else:
        print("\n=== Step 3: Data Visualization [SKIPPED] ===")

    # Step 4: Post Categorization
    if not args.skip_categorization:
        # Categorize the preprocessed combined dataset
        run_categorization(input_file=preprocessed_file_output)
    else:
        print("\n=== Step 4: Post Categorization [SKIPPED] ===")

    # Display completion message
    print("\n" + "=" * 80)
    print(" NLP Knowledge Base Generation Complete ".center(80, "="))
    print("=" * 80)
    print("\nResults:")
    print(f"- Combined raw dataset: {combined_raw_dataset_file}") # Updated message
    # Ensure preprocessed_file_output is not None if a step was skipped
    if preprocessed_file_output and os.path.exists(preprocessed_file_output):
         print(f"- Preprocessed dataset: {preprocessed_combined_dataset_file}")
    else:
         print("- Preprocessed dataset: Not generated in this run or file not found.")

    print(f"- Visualizations: ../data/visualizations/")
    print(f"- Categorized posts: ../data/categories/")
    print("\nThank you for using the NLP Knowledge Base Generator!")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")

