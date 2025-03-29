import requests
import pandas as pd
import time
import os
from typing import List, Dict, Any

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
                'sort': 'votes',
                'tagged': tag,
                'site': 'stackoverflow',
                'filter': '!-*jbN-o8P3E5',  # Default filter with some enhancements
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
                    backoff_time = data['backoff']
                    print(f"API backoff requested. Waiting for {backoff_time} seconds...")
                    time.sleep(backoff_time)
                else:
                    time.sleep(1)  # Be nice to the API
                
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
                    intermediate_df.to_csv(f"../data/nlp_questions_intermediate_{len(questions)}.csv", index=False)
                
            except requests.exceptions.RequestException as e:
                print(f"Error making request: {e}")
                time.sleep(5)  # Wait before retrying
            
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
            'filter': '!-*jbN-o8P3E5',  # Default filter with some enhancements
        }
        
        if self.api_key:
            params['key'] = self.api_key
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            return data.get('items', [])
        except Exception as e:
            print(f"Error getting answers for question {question_id}: {e}")
            return []
    
    def create_dataset(self, questions: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Create a DataFrame with questions and their accepted answers.
        
        Args:
            questions (List[Dict[str, Any]]): List of question data dictionaries.
        
        Returns:
            pd.DataFrame: DataFrame with questions and answers.
        """
        dataset = []
        
        total_questions = len(questions)
        for i, question in enumerate(questions):
            question_id = question.get('question_id')
            title = question.get('title', '')
            body = question.get('body', '')
            tags = question.get('tags', [])
            
            print(f"Processing question {i+1}/{total_questions}: {question_id}")
            
            # Get answers for this question
            answers = self.get_answers_for_question(question_id)
            
            # Find accepted answer
            accepted_answer = None
            other_answers = []
            
            for answer in answers:
                if answer.get('is_accepted', False):
                    accepted_answer = answer.get('body', '')
                else:
                    other_answers.append(answer.get('body', ''))
            
            # Add to dataset
            dataset.append({
                'title': title,
                'description': body,
                'tags': tags,
                'accepted_answer': accepted_answer,
                'other_answers': other_answers[:5] if other_answers else []  # Include up to 5 additional answers
            })
            
            # Be nice to the API
            time.sleep(1)
        
        return pd.DataFrame(dataset)
    
    def save_dataset(self, df: pd.DataFrame, filename: str = "nlp_dataset.csv"):
        """
        Save the dataset to a CSV file.
        
        Args:
            df (pd.DataFrame): DataFrame to save.
            filename (str, optional): Output filename. Defaults to "nlp_dataset.csv".
        """
        df.to_csv(f"../data/{filename}", index=False)
        print(f"Dataset saved to ../data/{filename}")


if __name__ == "__main__":
    # You should get an API key from Stack Exchange for better rate limits
    # https://stackapps.com/apps/oauth/register
    API_KEY = ""  # Add your API key here
    
    collector = StackOverflowDataCollector(api_key=API_KEY)
    
    # Collect questions
    questions = collector.get_questions(tag="nlp", max_questions=20000)
    
    # Create dataset
    dataset = collector.create_dataset(questions)
    
    # Save dataset
    collector.save_dataset(dataset, filename="nlp_stackoverflow_dataset.csv") 