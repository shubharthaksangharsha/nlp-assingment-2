import pandas as pd
import re
import string
import nltk
from bs4 import BeautifulSoup
import html
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from typing import List, Dict, Any, Union

# Download necessary NLTK resources
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)

class DataPreprocessor:
    """
    Preprocessor for Stack Overflow NLP dataset.
    """
    
    def __init__(self, remove_code: bool = False):
        """
        Initialize the preprocessor.
        
        Args:
            remove_code (bool, optional): Whether to remove code blocks from text. Defaults to False.
        """
        self.remove_code = remove_code
        self.stop_words = set(stopwords.words('english'))
        
    def clean_html(self, text: str) -> str:
        """
        Remove HTML tags and decode HTML entities.
        
        Args:
            text (str): Text containing HTML.
            
        Returns:
            str: Cleaned text.
        """
        if not isinstance(text, str):
            return ""
        
        # Decode HTML entities
        text = html.unescape(text)
        
        # Remove HTML tags
        soup = BeautifulSoup(text, "lxml")
        
        # Optionally remove code blocks
        if self.remove_code:
            for code in soup.find_all(['code', 'pre']):
                code.decompose()
        
        # Get text
        text = soup.get_text()
        
        return text
    
    def remove_urls(self, text: str) -> str:
        """
        Remove URLs from text.
        
        Args:
            text (str): Input text.
            
        Returns:
            str: Text with URLs removed.
        """
        if not isinstance(text, str):
            return ""
        
        url_pattern = re.compile(r'https?://\S+|www\.\S+')
        return url_pattern.sub('', text)
    
    def remove_punctuation(self, text: str) -> str:
        """
        Remove punctuation from text.
        
        Args:
            text (str): Input text.
            
        Returns:
            str: Text with punctuation removed.
        """
        if not isinstance(text, str):
            return ""
        
        translator = str.maketrans('', '', string.punctuation)
        return text.translate(translator)
    
    def tokenize(self, text: str) -> List[str]:
        """
        Tokenize text into words.
        
        Args:
            text (str): Input text.
            
        Returns:
            List[str]: List of tokens.
        """
        if not isinstance(text, str):
            return []
        
        return word_tokenize(text)
    
    def remove_stopwords(self, tokens: List[str]) -> List[str]:
        """
        Remove stopwords from a list of tokens.
        
        Args:
            tokens (List[str]): List of tokens.
            
        Returns:
            List[str]: Tokens with stopwords removed.
        """
        return [word for word in tokens if word.lower() not in self.stop_words]
    
    def preprocess_text(self, text: str, remove_stopwords: bool = True) -> str:
        """
        Apply full preprocessing pipeline to text.
        
        Args:
            text (str): Input text.
            remove_stopwords (bool, optional): Whether to remove stopwords. Defaults to True.
            
        Returns:
            str: Preprocessed text.
        """
        if not isinstance(text, str):
            return ""
        
        # Clean HTML
        text = self.clean_html(text)
        
        # Remove URLs
        text = self.remove_urls(text)
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove punctuation
        text = self.remove_punctuation(text)
        
        # Tokenize
        tokens = self.tokenize(text)
        
        # Remove stopwords if requested
        if remove_stopwords:
            tokens = self.remove_stopwords(tokens)
        
        # Join tokens back into text
        preprocessed_text = ' '.join(tokens)
        
        return preprocessed_text
    
    def preprocess_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Preprocess all text columns in the DataFrame.
        
        Args:
            df (pd.DataFrame): Input DataFrame.
            
        Returns:
            pd.DataFrame: Preprocessed DataFrame.
        """
        # Create a copy to avoid modifying the original
        processed_df = df.copy()
        
        # Process title column
        print("Preprocessing titles...")
        processed_df['processed_title'] = processed_df['title'].apply(
            lambda x: self.preprocess_text(x, remove_stopwords=False)
        )
        
        # Process description column
        print("Preprocessing descriptions...")
        processed_df['processed_description'] = processed_df['description'].apply(
            lambda x: self.preprocess_text(x)
        )
        
        # Process accepted_answer column
        print("Preprocessing accepted answers...")
        processed_df['processed_accepted_answer'] = processed_df['accepted_answer'].apply(
            lambda x: self.preprocess_text(x)
        )
        
        # Process other_answers column (if it's a list of strings)
        if 'other_answers' in processed_df.columns:
            print("Preprocessing other answers...")
            
            def process_answers(answers_list):
                if isinstance(answers_list, list):
                    return [self.preprocess_text(answer) for answer in answers_list]
                return []
            
            processed_df['processed_other_answers'] = processed_df['other_answers'].apply(process_answers)
        
        # Process tags column (if it's a list of strings)
        if 'tags' in processed_df.columns:
            print("Preprocessing tags...")
            
            def process_tags(tags_list):
                if isinstance(tags_list, list):
                    return [tag.lower() for tag in tags_list]
                return []
            
            processed_df['processed_tags'] = processed_df['tags'].apply(process_tags)
        
        print("Preprocessing complete.")
        return processed_df


if __name__ == "__main__":
    # Test the preprocessor
    try:
        # Load dataset
        dataset_path = "../data/nlp_stackoverflow_dataset.csv"
        df = pd.read_csv(dataset_path)
        
        # Create preprocessor
        preprocessor = DataPreprocessor(remove_code=True)
        
        # Preprocess data
        processed_df = preprocessor.preprocess_dataframe(df)
        
        # Save preprocessed data
        processed_df.to_csv("../data/preprocessed_nlp_dataset.csv", index=False)
        print(f"Preprocessed dataset saved to ../data/preprocessed_nlp_dataset.csv")
        
    except Exception as e:
        print(f"Error: {e}") 
