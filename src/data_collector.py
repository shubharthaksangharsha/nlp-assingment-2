import requests
import pandas as pd
import time
import os
from typing import List, Dict, Any
import csv # Import the csv library

class StackOverflowDataCollector:
    """
    A class to collect NLP-related posts from Stack Overflow using the Stack Exchange API.
    """

    def __init__(self, api_key: str = None):
        """
        Initialize the collector with an API key.
        Args:
            api_key (str, optional): Stack Exchange API key. Defaults to None.
        """
        self.base_url = "https://api.stackexchange.com/2.3"
        self.api_key = api_key
        self.backoff_time = 1 # Initial backoff time

    def get_questions(self, tag: str = "nlp", page_size: int = 100, max_questions: int = 20000) -> List[Dict[str, Any]]:
        """
        Collect questions with specified tag from Stack Overflow.
        Args:
            tag (str, optional): Tag to filter questions. Defaults to "nlp".
            page_size (int, optional): Number of items per page. Defaults to 100.
            max_questions (int, optional): Maximum number of questions to retrieve. Defaults to 20000.

        Returns:
            List[Dict[str, Any]]: List of question data dictionaries.
        """
        questions = []
        page = 1
        has_more = True

        # Create data directory if it doesn't exist
        os.makedirs("../data", exist_ok=True)

        print(f"Collecting questions with tag [{tag}]...")

        while has_more and len(questions) < max_questions:
            # Construct API URL
            url = f"{self.base_url}/questions"

            # Define parameters
            params = {
                'page': page,
                'pagesize': page_size,
                'order': 'desc',
                'sort': 'creation', # Changed to 'creation'
                'tagged': tag,
                'site': 'stackoverflow',
                'filter': '!-*jbN-o8P3E5', # Default filter with some enhancements
            }

            if self.api_key:
                params['key'] = self.api_key

            # Make API request
            try:
                response = requests.get(url, params=params)
                response.raise_for_status()
                data = response.json()

                # Extract questions
                items = data.get('items', [])
                questions.extend(items)

                print(f"Collected {len(questions)} questions so far...")

                # Check if there are more pages
                has_more = data.get('has_more', False)

                # Update page number
                page += 1

                # Respect API quota and avoid throttling
                if 'backoff' in data:
                    self.backoff_time = data['backoff']
                    print(f"API backoff requested. Waiting for {self.backoff_time} seconds...")
                    time.sleep(self.backoff_time)
                else:
                    time.sleep(1) # Be nice to the API

                # Save intermediate results every 1000 questions
                if len(questions) % 1000 == 0:
                    print(f"Saving intermediate result with {len(questions)} questions...")
                    intermediate_df = pd.DataFrame({
                        'question_id': [q.get('question_id') for q in questions],
                        'title': [q.get('title') for q in questions],
                        'body': [q.get('body') for q in questions],
                        'tags': [q.get('tags') for q in questions],
                        'creation_date': [q.get('creation_date') for q in questions],
                        'view_count': [q.get('view_count') for q in questions],
                        'score': [q.get('score') for q in questions],
                        'answer_count': [q.get('answer_count') for q in questions],
                        'is_answered': [q.get('is_answered') for q in questions],
                    })
                    intermediate_df.to_csv(f"../data/{tag}_questions_intermediate_{len(questions)}.csv", index=False) # Added tag to intermediate filename


            except requests.exceptions.RequestException as e:
                print(f"Error making request: {e}")
                time.sleep(5) # Wait before retrying

            except Exception as e:
                print(f"Unexpected error: {e}")
                break


        print(f"Collected a total of {len(questions)} questions.")
        return questions

    def get_answers_for_question(self, question_id: int) -> List[Dict[str, Any]]:
        """
        Get all answers for a specific question.
        Args:
            question_id (int): ID of the question.
        Returns:
            List[Dict[str, Any]]: List of answer data dictionaries.
        """
        url = f"{self.base_url}/questions/{question_id}/answers"

        params = {
            'order': 'desc',
            'sort': 'votes',
            'site': 'stackoverflow',
            'filter': '!-*jbN-o8P3E5', # Default filter with some enhancements
        }

        if self.api_key:
            params['key'] = self.api_key

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            # Check for backoff in answer requests and wait
            if 'backoff' in data:
                self.backoff_time = data['backoff']
                print(f"API backoff requested during answer fetching. Waiting for {self.backoff_time} seconds...")
                time.sleep(self.backoff_time)
            else:
                time.sleep(1) # Be nice to the API between answer calls


            return data.get('items', [])

        except requests.exceptions.RequestException as e:
            print(f"Error getting answers for question {question_id}: {e}")
            # Implement retry logic or return empty list on failure
            return []

        except Exception as e:
            print(f"Unexpected error getting answers for question {question_id}: {e}")
            return []


    # Modified create_dataset to accept filename and save incrementally
    def create_dataset(self, questions: List[Dict[str, Any]], filename: str = "nlp_stackoverflow_dataset.csv"):
        """
        Create a DataFrame with questions and their accepted answers and save incrementally to a CSV file.
        Args:
            questions (List[Dict[str, Any]]): List of question data dictionaries.
            filename (str, optional): Output filename to save the dataset. Defaults to "nlp_stackoverflow_dataset.csv".
        """
        output_path = f"../data/{filename}"
        total_questions = len(questions)
        # Define the fieldnames for the CSV, including the new fields from API
        fieldnames = ['question_id', 'title', 'description', 'tags', 'creation_date', 'view_count', 'score', 'answer_count', 'is_answered', 'accepted_answer', 'other_answers']


        # Check if file exists to decide whether to write header
        # Write header if the file does not exist or is empty
        write_header = not os.path.exists(output_path) or os.path.getsize(output_path) == 0

        # Open the file in append mode ('a')
        # use newline='' to prevent extra blank rows in CSV
        # use encoding='utf-8' to handle various characters
        with open(output_path, 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            if write_header:
                writer.writeheader()
                print(f"Created new dataset file: {output_path}")
            else:
                print(f"Appending to existing dataset file: {output_path}")


            print(f"Starting to process questions and save incrementally to {output_path}")

            # Optional: Add logic here to skip questions already in the file if rerunning
            # This is more complex as it requires reading the existing file's IDs first.
            # For now, it will process all questions and append, which might create duplicates
            # if you rerun after an interruption without clearing the file.

            for i, question in enumerate(questions):
                question_id = question.get('question_id')
                # You could add a check here if question_id is already in the CSV
                # For example, load existing IDs into a set before the loop.

                print(f"Processing question {i+1}/{total_questions}: {question_id}")

                # Get answers for this question
                answers = self.get_answers_for_question(question_id)

                accepted_answer = None
                other_answers_list = []

                for answer in answers:
                    if answer.get('is_accepted', False):
                        accepted_answer = answer.get('body', '')
                    else:
                        other_answers_list.append(answer.get('body', ''))

                # Prepare the data row as a dictionary
                row_data = {
                    'question_id': question_id,
                    'title': question.get('title', ''),
                    'description': question.get('body', ''),
                    'tags': question.get('tags', []),
                    'creation_date': question.get('creation_date'),
                    'view_count': question.get('view_count'),
                    'score': question.get('score'),
                    'answer_count': question.get('answer_count'),
                    'is_answered': question.get('is_answered'),
                    'accepted_answer': accepted_answer,
                    'other_answers': other_answers_list[:5] # Include up to 5 additional answers
                }

                # Write the row to the CSV
                try:
                    writer.writerow(row_data)
                    # Optional: Flush the buffer to ensure data is written to disk more frequently
                    # This can be useful if you are worried about losing data on sudden interruption
                    # csvfile.flush()
                except Exception as e:
                    print(f"Error writing row for question {question_id}: {e}")


        print(f"Finished processing questions. Data saved to {output_path}")


    def save_dataset(self, df: pd.DataFrame, filename: str = "nlp_dataset.csv"):
        """
        Save a full DataFrame to a CSV file.
        This method is less relevant now if create_dataset is used for primary incremental saving.
        It's kept for potential compatibility or other uses.

        Args:
            df (pd.DataFrame): DataFrame to save.
            filename (str, optional): Output filename. Defaults to "nlp_dataset.csv".
        """
        # With incremental saving in create_dataset, this method might not be the primary way
        # the dataset is saved in the main pipeline anymore.
        print(f"Dataset saving handled by create_dataset function for incremental writes.")
        # If you still need to save a DataFrame (e.g., after loading the full CSV), uncomment the line below:
        # df.to_csv(f"../data/{filename}", index=False)
        # print(f"Dataset saved to ../data/{filename} using save_dataset.")


if __name__ == "__main__":
    # Example usage of the data collector
    # You should get an API key from Stack Exchange for better rate limits
    # https://stackapps.com/apps/oauth/register
    API_KEY = "rl_QSELmsmpZPK2JvKfEHYZ8Pa9e" # Add your API key here

    collector = StackOverflowDataCollector(api_key=API_KEY)

    # Example of collecting questions for a tag (initial metadata)
    # This will save intermediate files but does not include answer bodies yet
    # questions_metadata = collector.get_questions(tag="nlp", max_questions=100)
    # print(f"Collected initial metadata for {len(questions_metadata)} questions.")

    # Example of processing collected questions and saving incrementally with answers
    # This is the primary method for building the full dataset now
    # Assuming 'questions_metadata' list is populated from a previous get_questions call or intermediate file load
    # For a standalone test, you might need to call get_questions first:
    test_questions = collector.get_questions(tag="nlp", max_questions=50) # Collect a small number for testing
    if test_questions:
        collector.create_dataset(test_questions, filename="test_nlp_dataset.csv")
        print("Test dataset created with incremental saving.")
    else:
        print("No questions collected for test dataset creation.")

    # The preprocess, visualize, and categorize steps would typically load the completed CSV file
    # e.g., pd.read_csv("../data/test_nlp_dataset.csv")
