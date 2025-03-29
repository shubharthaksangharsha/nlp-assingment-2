import os
import pandas as pd
import json
from flask import Flask, render_template, request, jsonify, redirect, url_for
from datetime import datetime

app = Flask(__name__)

# Configuration
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
CATEGORIES_DIR = os.path.join(DATA_DIR, 'categories')
VISUALIZATIONS_DIR = os.path.join(DATA_DIR, 'visualizations')
API_KEY = "rl_QSELmsmpZPK2JvKfEHYZ8Pa9e"  # Store your API key

# Ensure the static directories exist
os.makedirs(os.path.join(app.static_folder, 'img'), exist_ok=True)
os.makedirs(os.path.join(app.static_folder, 'css'), exist_ok=True)
os.makedirs(os.path.join(app.static_folder, 'js'), exist_ok=True)

# Helper functions
def load_category_types():
    """Load all category types."""
    if os.path.exists(CATEGORIES_DIR):
        return [d for d in os.listdir(CATEGORIES_DIR) if os.path.isdir(os.path.join(CATEGORIES_DIR, d))]
    return []

def load_categories(category_type):
    """Load categories for a specific type."""
    categories_path = os.path.join(CATEGORIES_DIR, category_type)
    if os.path.exists(categories_path):
        categories = []
        for filename in os.listdir(categories_path):
            if filename.endswith('.csv'):
                category_name = filename.replace('.csv', '').replace('_', ' ')
                # Count the number of rows in the CSV
                try:
                    df = pd.read_csv(os.path.join(categories_path, filename))
                    count = len(df)
                except:
                    count = 0
                categories.append({
                    'name': category_name,
                    'count': count,
                    'file': filename
                })
        return sorted(categories, key=lambda x: x['count'], reverse=True)
    return []

def load_category_posts(category_type, category_name):
    """Load posts for a specific category."""
    try:
        file_path = os.path.join(CATEGORIES_DIR, category_type, f"{category_name.replace(' ', '_')}.csv")
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            # Convert any float columns that should be strings to strings
            for col in ['title', 'description', 'accepted_answer', 'other_answers', 'tags']:
                if col in df.columns:
                    df[col] = df[col].fillna('').astype(str)
            
            posts = []
            for _, row in df.iterrows():
                post = {
                    'title': row['title'],
                    'description': row['description'] if 'description' in df.columns else '',
                    'accepted_answer': row['accepted_answer'] if 'accepted_answer' in df.columns else '',
                    'other_answers': row['other_answers'] if 'other_answers' in df.columns else '',
                    'tags': row['tags'].split() if 'tags' in df.columns and isinstance(row['tags'], str) else []
                }
                posts.append(post)
            return posts
        return []
    except Exception as e:
        print(f"Error loading category: {e}")
        return []

def load_visualizations():
    """Load available visualizations."""
    if os.path.exists(VISUALIZATIONS_DIR):
        return [f for f in os.listdir(VISUALIZATIONS_DIR) if f.endswith(('.png', '.jpg', '.jpeg'))]
    return []

def search_posts(query):
    """Search for posts containing the query string."""
    try:
        if not query:
            return []
            
        dataset_path = os.path.join(DATA_DIR, 'preprocessed_nlp_dataset.csv')
        if not os.path.exists(dataset_path):
            dataset_path = os.path.join(DATA_DIR, 'nlp_stackoverflow_dataset.csv')
            
        if os.path.exists(dataset_path):
            df = pd.read_csv(dataset_path)
            
            # Convert any float columns that should be strings to strings
            for col in ['title', 'description', 'accepted_answer', 'other_answers', 'tags']:
                if col in df.columns:
                    df[col] = df[col].fillna('').astype(str)
            
            # Search in multiple columns
            search_cols = ['title', 'description', 'tags']
            
            # Create a combined condition for searching
            mask = df.apply(lambda row: any(query.lower() in str(row[col]).lower() 
                                          for col in search_cols 
                                          if col in df.columns), axis=1)
            
            results = df[mask]
            
            # Convert to list of dictionaries
            posts = []
            for _, row in results.iterrows():
                post = {
                    'title': row['title'],
                    'description': row['description'] if 'description' in df.columns else '',
                    'accepted_answer': row['accepted_answer'] if 'accepted_answer' in df.columns else '',
                    'other_answers': row['other_answers'] if 'other_answers' in df.columns else '',
                    'tags': row['tags'].split() if 'tags' in df.columns and isinstance(row['tags'], str) else []
                }
                posts.append(post)
            
            return posts
        return []
    except Exception as e:
        print(f"Error searching: {e}")
        return []

def load_top_tags():
    """Extract top tags from the visualization data"""
    try:
        dataset_path = os.path.join(DATA_DIR, 'preprocessed_nlp_dataset.csv')
        if not os.path.exists(dataset_path):
            dataset_path = os.path.join(DATA_DIR, 'nlp_stackoverflow_dataset.csv')
            
        if os.path.exists(dataset_path):
            df = pd.read_csv(dataset_path)
            
            if 'tags' in df.columns:
                # Extract tags and count them
                all_tags = []
                for tags_str in df['tags'].fillna(''):
                    if isinstance(tags_str, str):
                        tags = tags_str.strip("[]'").replace("'", "").split(', ')
                        all_tags.extend(tags)
                
                # Count occurrences of each tag
                tag_counts = {}
                for tag in all_tags:
                    if tag:
                        tag_counts[tag] = tag_counts.get(tag, 0) + 1
                
                # Sort by count and take top 10
                top_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10]
                return top_tags
        return []
    except Exception as e:
        print(f"Error loading top tags: {e}")
        return []

def get_dataset_stats():
    """Get statistics about the dataset"""
    try:
        dataset_path = os.path.join(DATA_DIR, 'preprocessed_nlp_dataset.csv')
        if not os.path.exists(dataset_path):
            dataset_path = os.path.join(DATA_DIR, 'nlp_stackoverflow_dataset.csv')
            
        if os.path.exists(dataset_path):
            df = pd.read_csv(dataset_path)
            
            stats = {
                'total_posts': len(df),
                'categories': {}
            }
            
            # Count posts in each category type
            for category_type in load_category_types():
                stats['categories'][category_type] = sum(c['count'] for c in load_categories(category_type))
            
            return stats
        return None
    except Exception as e:
        print(f"Error getting dataset stats: {e}")
        return None

# Routes
@app.route('/')
def index():
    stats = get_dataset_stats()
    top_tags = load_top_tags()
    return render_template('index.html', 
                           stats=stats, 
                           top_tags=top_tags, 
                           current_year=datetime.now().year,
                           api_key=API_KEY)

@app.route('/categories')
def categories():
    category_types = load_category_types()
    all_categories = {}
    
    for category_type in category_types:
        all_categories[category_type] = load_categories(category_type)
    
    return render_template('categories.html', 
                           category_types=category_types, 
                           all_categories=all_categories,
                           current_year=datetime.now().year)

@app.route('/category/<category_type>/<category_name>')
def category(category_type, category_name):
    posts = load_category_posts(category_type, category_name)
    return render_template('category.html', 
                           category_type=category_type, 
                           category_name=category_name, 
                           posts=posts,
                           current_year=datetime.now().year)

@app.route('/visualizations')
def visualizations():
    viz_files = load_visualizations()
    visualizations = []
    
    for viz_file in viz_files:
        name = viz_file.replace('.png', '').replace('_', ' ').title()
        visualizations.append({
            'name': name,
            'file': viz_file
        })
    
    return render_template('visualizations.html', 
                           visualizations=visualizations,
                           current_year=datetime.now().year)

@app.route('/search')
def search():
    query = request.args.get('query', '')
    results = search_posts(query) if query else []
    return render_template('search.html', 
                           query=query, 
                           results=results,
                           current_year=datetime.now().year)

@app.route('/api/categories')
def api_categories():
    category_types = load_category_types()
    all_categories = {}
    
    for category_type in category_types:
        all_categories[category_type] = load_categories(category_type)
    
    return jsonify(all_categories)

@app.route('/api/category/<category_type>/<category_name>')
def api_category(category_type, category_name):
    posts = load_category_posts(category_type, category_name)
    return jsonify(posts)

@app.route('/api/search')
def api_search():
    query = request.args.get('query', '')
    results = search_posts(query) if query else []
    return jsonify(results)

@app.route('/api/stats')
def api_stats():
    stats = get_dataset_stats()
    return jsonify(stats)

@app.route('/about')
def about():
    return render_template('about.html', current_year=datetime.now().year)

@app.route('/admin/reprocess_categories')
def reprocess_categories():
    """Admin endpoint to reprocess categories."""
    try:
        from src.categorizer import PostCategorizer
        
        # Get path to the processed dataset
        data_path = os.path.join(DATA_DIR, 'preprocessed_nlp_dataset.csv')
        
        # Check if file exists
        if not os.path.exists(data_path):
            return jsonify({"error": "Processed dataset not found"}), 404
            
        # Initialize categorizer and reprocess categories
        categorizer = PostCategorizer(data_path)
        categorizer.keyword_based_categorization()
        categorizer.task_based_categorization()
        categorizer.question_type_categorization()
        categorizer.library_based_categorization()
        
        return jsonify({"success": "Categories reprocessed successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000) 