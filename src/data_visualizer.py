import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import seaborn as sns
from collections import Counter
from datetime import datetime
import os
from typing import List, Dict, Any, Union, Tuple

plt.style.use('ggplot')

class DataVisualizer:
    """
    Class for visualizing NLP Stack Overflow data.
    """
    
    def __init__(self, data_path: str):
        """
        Initialize the visualizer with dataset path.
        
        Args:
            data_path (str): Path to the preprocessed dataset.
        """
        self.data_path = data_path
        self.df = pd.read_csv(data_path)
        
        # Create output directory for visualizations
        os.makedirs("../data/visualizations", exist_ok=True)
        
    def generate_wordcloud(self, text_column: str, title: str, filename: str, 
                          width: int = 800, height: int = 400, 
                          max_words: int = 200, background_color: str = 'white'):
        """
        Generate a word cloud from text data.
        
        Args:
            text_column (str): Column name containing text data.
            title (str): Title for the word cloud.
            filename (str): Output filename.
            width (int, optional): Width of the word cloud image. Defaults to 800.
            height (int, optional): Height of the word cloud image. Defaults to 400.
            max_words (int, optional): Maximum number of words to include. Defaults to 200.
            background_color (str, optional): Background color. Defaults to 'white'.
        """
        print(f"Generating word cloud for {text_column}...")
        
        # Combine all text into a single string
        text_data = ' '.join(self.df[text_column].dropna().astype(str))
        
        # Generate word cloud
        wordcloud = WordCloud(
            width=width, 
            height=height,
            max_words=max_words,
            background_color=background_color,
            contour_width=1,
            contour_color='steelblue'
        ).generate(text_data)
        
        # Plot the word cloud
        plt.figure(figsize=(width/100, height/100))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.title(title)
        plt.tight_layout(pad=0)
        
        # Save the word cloud
        output_path = f"../data/visualizations/{filename}.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Word cloud saved to {output_path}")
    
    def plot_top_tags(self, n: int = 20, filename: str = "top_tags"):
        """
        Plot the most common tags associated with NLP questions.
        
        Args:
            n (int, optional): Number of top tags to show. Defaults to 20.
            filename (str, optional): Output filename. Defaults to "top_tags".
        """
        print(f"Plotting top {n} tags...")
        
        # Check if tags column is available and is a list
        if 'tags' not in self.df.columns:
            print("Tags column not found.")
            return
        
        # Get all tags and count them
        all_tags = []
        for tag_list in self.df['tags']:
            try:
                if isinstance(tag_list, str):
                    # Convert string representation of list to actual list
                    if tag_list.startswith('[') and tag_list.endswith(']'):
                        tag_list = eval(tag_list)
                    else:
                        tag_list = tag_list.split()
                
                if isinstance(tag_list, list):
                    all_tags.extend(tag_list)
            except:
                continue
        
        # Count tags
        tag_counts = Counter(all_tags)
        
        # Get top N tags
        top_tags = tag_counts.most_common(n)
        
        # Extract tags and counts
        tags, counts = zip(*top_tags)
        
        # Create horizontal bar chart
        plt.figure(figsize=(10, 8))
        bars = plt.barh(tags, counts, color='skyblue')
        
        # Add count labels to the bars
        for bar in bars:
            width = bar.get_width()
            label_position = width + (width * 0.01)
            plt.text(label_position, bar.get_y() + bar.get_height()/2, f'{int(width)}',
                    va='center', fontsize=8)
        
        plt.xlabel('Count')
        plt.ylabel('Tags')
        plt.title(f'Top {n} Tags Associated with NLP Questions')
        plt.gca().invert_yaxis()  # Invert to have highest count at the top
        plt.tight_layout()
        
        # Save the plot
        output_path = f"../data/visualizations/{filename}.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Top tags plot saved to {output_path}")
    
    def plot_question_frequency_over_time(self, filename: str = "question_frequency"):
        """
        Plot the frequency of NLP questions over time.
        
        Args:
            filename (str, optional): Output filename. Defaults to "question_frequency".
        """
        print("Plotting question frequency over time...")
        
        # Check if creation_date column is available
        if 'creation_date' not in self.df.columns:
            print("Creation date column not found.")
            return
        
        # Convert timestamp to datetime and extract year and month
        try:
            self.df['date'] = pd.to_datetime(self.df['creation_date'], unit='s')
            self.df['year_month'] = self.df['date'].dt.to_period('M')
            
            # Count questions by year and month
            question_counts = self.df.groupby('year_month').size()
            
            # Plot the trend
            plt.figure(figsize=(14, 6))
            question_counts.plot(kind='line', marker='o', linestyle='-', color='blue')
            
            plt.title('NLP Questions Frequency Over Time')
            plt.xlabel('Time (Year-Month)')
            plt.ylabel('Number of Questions')
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            
            # Save the plot
            output_path = f"../data/visualizations/{filename}.png"
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            print(f"Question frequency plot saved to {output_path}")
            
        except Exception as e:
            print(f"Error plotting question frequency: {e}")
    
    def plot_views_vs_answers(self, filename: str = "views_vs_answers"):
        """
        Plot the relationship between views and number of answers.
        
        Args:
            filename (str, optional): Output filename. Defaults to "views_vs_answers".
        """
        print("Plotting views vs. answers...")
        
        # Check if required columns are available
        if 'view_count' not in self.df.columns or 'answer_count' not in self.df.columns:
            print("View count or answer count columns not found.")
            return
        
        # Create scatter plot
        plt.figure(figsize=(10, 6))
        
        # Apply log transformation to handle skewed distributions
        sns.scatterplot(
            x=np.log1p(self.df['view_count']), 
            y=np.log1p(self.df['answer_count']),
            alpha=0.5
        )
        
        # Add regression line
        sns.regplot(
            x=np.log1p(self.df['view_count']), 
            y=np.log1p(self.df['answer_count']),
            scatter=False, 
            color='red'
        )
        
        plt.title('Relationship Between Views and Answers (Log Scale)')
        plt.xlabel('Log(View Count + 1)')
        plt.ylabel('Log(Answer Count + 1)')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        # Save the plot
        output_path = f"../data/visualizations/{filename}.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Views vs. answers plot saved to {output_path}")
    
    def generate_visualizations(self):
        """
        Generate all visualizations.
        """
        # Generate word cloud from processed titles
        if 'processed_title' in self.df.columns:
            self.generate_wordcloud(
                'processed_title',
                'Word Cloud of NLP Question Titles',
                'title_wordcloud'
            )
        
        # Generate word cloud from processed descriptions
        if 'processed_description' in self.df.columns:
            self.generate_wordcloud(
                'processed_description',
                'Word Cloud of NLP Question Descriptions',
                'description_wordcloud'
            )
        
        # Plot top tags
        self.plot_top_tags()
        
        # Plot question frequency over time
        self.plot_question_frequency_over_time()
        
        # Plot views vs. answers
        self.plot_views_vs_answers()


if __name__ == "__main__":
    try:
        # Path to preprocessed dataset
        data_path = "../data/preprocessed_nlp_dataset.csv"
        
        # Create visualizer
        visualizer = DataVisualizer(data_path)
        
        # Generate all visualizations
        visualizer.generate_visualizations()
        
    except Exception as e:
        print(f"Error: {e}") 