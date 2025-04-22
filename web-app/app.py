import os
import pandas as pd
import json
from flask import Flask, render_template, request, jsonify, redirect, url_for
from datetime import datetime
import logging
import urllib.parse

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuration
APP_ROOT = os.path.dirname(os.path.abspath(__file__))  # web-app directory

# In Vercel, we need to use the current working directory
if os.environ.get('VERCEL', False):
    DATA_DIR = os.path.join(os.getcwd(), 'data')
else:
    PARENT_DIR = os.path.dirname(APP_ROOT)  # parent directory
    DATA_DIR = os.path.join(PARENT_DIR, 'data')  # data directory in parent

CATEGORIES_DIR = os.path.join(DATA_DIR, 'categories')
VISUALIZATIONS_DIR = os.path.join(DATA_DIR, 'visualizations')
API_KEY = os.environ.get('STACK_API_KEY', "rl_QSELmsmpZPK2JvKfEHYZ8Pa9e")

# Run setup script in deployment environments
if os.environ.get('VERCEL', False):
    try:
        import vercel_setup
        vercel_setup.setup_for_vercel()
        print(f"Vercel setup complete. Data directory: {DATA_DIR}")
        print(f"Categories directory exists: {os.path.exists(CATEGORIES_DIR)}")
        if os.path.exists(CATEGORIES_DIR):
            print("Categories directory contents:", os.listdir(CATEGORIES_DIR))
    except Exception as e:
        print(f"Warning: Vercel setup error: {e}")
        import traceback
        print(traceback.format_exc())

# Ensure the static directories exist
# Use Flask's app.static_folder which defaults correctly if 'static' is alongside app.py
os.makedirs(os.path.join(app.static_folder, 'img'), exist_ok=True)
os.makedirs(os.path.join(app.static_folder, 'css'), exist_ok=True)
os.makedirs(os.path.join(app.static_folder, 'js'), exist_ok=True)

# Helper functions
def load_category_types():
    """Load all category types."""
    print(f"Looking for categories in: {CATEGORIES_DIR}")  # Debug print
    if os.path.exists(CATEGORIES_DIR):
        types = [d for d in os.listdir(CATEGORIES_DIR) 
                if os.path.isdir(os.path.join(CATEGORIES_DIR, d))]
        print(f"Found category types: {types}")  # Debug print
        return types
    print(f"Categories directory not found at: {CATEGORIES_DIR}")  # Debug print
    return []

def load_categories(category_type):
    """Load categories for a specific type."""
    categories_path = os.path.join(CATEGORIES_DIR, category_type)
    print(f"Loading categories from: {categories_path}")  # Debug print
    
    if os.path.exists(categories_path):
        categories = []
        for filename in os.listdir(categories_path):
            if filename.endswith(('.csv', '.json')):  # Handle both CSV and JSON
                category_name = filename.replace('.csv', '').replace('.json', '').replace('_', ' ')
                file_path = os.path.join(categories_path, filename)
                
                # Count items in the file
                try:
                    if filename.endswith('.csv'):
                        df = pd.read_csv(file_path)
                        count = len(df)
                    else:  # JSON file
                        with open(file_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            count = len(data if isinstance(data, list) else data.get('posts', []))
                except Exception as e:
                    print(f"Error loading {filename}: {e}")
                    count = 0
                
                categories.append({
                    'name': category_name,
                    'count': count,
                    'file': filename
                })
        
        print(f"Found categories: {categories}")  # Debug print
        return sorted(categories, key=lambda x: x['count'], reverse=True)
    
    print(f"Category path not found: {categories_path}")  # Debug print
    return []

def load_posts(category_type, category_name):
    logger.debug(f"Loading posts for {category_type}/{category_name}")
    
    try:
        # URL decode the category name first
        category_name = urllib.parse.unquote(category_name)
        
        # Normalize category_type and category_name
        normalized_type = category_type.lower().replace(' ', '_')
        normalized_name = category_name.lower().replace(' ', '_')
        normalized_name = normalized_name.replace('%20', '_')  # Handle URL encoding
        
        # Remove extensions and suffixes
        normalized_name = normalized_name.replace('.csv', '').replace('.json', '')
        normalized_name = normalized_name.replace('_questions', '').replace('_question', '')
        
        logger.debug(f"Normalized type: {normalized_type}")
        logger.debug(f"Normalized name: {normalized_name}")
        
        # Get the correct base path for Vercel
        if os.environ.get('VERCEL', False):
            base_path = os.path.join('/var/task/data/categories', normalized_type)
            logger.debug(f"Using Vercel path: {base_path}")
        else:
            base_path = os.path.join(CATEGORIES_DIR, normalized_type)
            logger.debug(f"Using local path: {base_path}")
            
        # List all files in the directory
        files = os.listdir(base_path)
        logger.debug(f"Files in directory: {files}")
        
        # Try all possible filename variations
        possible_names = [
            f"{category_name}.csv",  # Original name
            f"{category_name}.json",
            f"{normalized_name}.csv",  # Normalized name
            f"{normalized_name}.json",
            f"{category_name}_Questions.csv",  # With Questions suffix
            f"{normalized_name}_questions.csv",
            f"{category_name.replace(' ', '_')}.csv",  # Space to underscore
            f"{category_name.replace(' ', '_')}.json"
        ]
        
        # Also try uppercase variations
        possible_names.extend([name.upper() for name in possible_names])
        possible_names.extend([name.title() for name in possible_names])
        
        logger.debug(f"Trying file variations: {possible_names}")
        
        for filename in files:
            if filename in possible_names:
                file_path = os.path.join(base_path, filename)
                logger.debug(f"Found matching file: {file_path}")
                
                try:
                    if filename.endswith('.csv'):
                        posts_df = pd.read_csv(file_path)
                        # Convert DataFrame to list of dictionaries with proper tag handling
                        posts = []
                        for _, row in posts_df.iterrows():
                            post = {}
                            for col in row.index:
                                if col == 'tags':
                                    # Handle tags field specifically
                                    tags_value = row[col]
                                    if pd.isna(tags_value) or tags_value == '':
                                        post[col] = []
                                    elif isinstance(tags_value, str):
                                        # Try to parse as list if it looks like one
                                        if tags_value.startswith('[') and tags_value.endswith(']'):
                                            try:
                                                tags = eval(tags_value)
                                                post[col] = tags if isinstance(tags, list) else [tags_value]
                                            except:
                                                post[col] = [tag.strip() for tag in tags_value.strip('[]').split(',') if tag.strip()]
                                        else:
                                            post[col] = [tag.strip() for tag in tags_value.split(',') if tag.strip()]
                                    else:
                                        post[col] = []
                                else:
                                    # Handle other fields
                                    post[col] = '' if pd.isna(row[col]) else str(row[col])
                            posts.append(post)
                        logger.debug(f"Loaded {len(posts)} posts from CSV")
                        return posts, None
                    elif filename.endswith('.json'):
                        with open(file_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            posts = data if isinstance(data, list) else data.get('posts', [])
                            # Ensure tags is always a list
                            for post in posts:
                                if 'tags' not in post:
                                    post['tags'] = []
                                elif not isinstance(post['tags'], list):
                                    post['tags'] = [str(post['tags'])] if post['tags'] else []
                            logger.debug(f"Loaded {len(posts)} posts from JSON")
                            return posts, None
                except Exception as e:
                    logger.error(f"Error reading file {filename}: {str(e)}")
                    continue
        
        # If we get here, no matching file was found
        logger.warning(f"No matching file found in {base_path}")
        logger.warning(f"Tried variations: {possible_names}")
        return [], f"No data file found for category '{category_name}'"
            
    except Exception as e:
        import traceback
        logger.error(f"Error loading posts: {str(e)}")
        logger.error(traceback.format_exc())
        return [], f"Error loading posts: {str(e)}"

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

@app.route('/categories/<category_type>/<category_name>')
def category_posts(category_type, category_name):
    # URL decode the parameters
    category_type = urllib.parse.unquote(category_type)
    category_name = urllib.parse.unquote(category_name)
    
    posts, error = load_posts(category_type, category_name)
    
    if error:
        logger.error(f"Error loading posts: {error}")
        return render_template('category.html',
                             category_type=category_type,
                             category_name=category_name,
                             posts=[],
                             error_message=error)
    
    logger.debug(f"Loaded {len(posts)} posts")
    return render_template('category.html',
                         category_type=category_type,
                         category_name=category_name,
                         posts=posts)

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

@app.route('/debug/check_category/<category_type>/<category_name>')
def debug_check_category(category_type, category_name):
    """Debug endpoint to check category file existence and content"""
    try:
        # Get the base path
        base_path = os.path.join(CATEGORIES_DIR, category_type)
        
        # Check if base path exists
        base_path_exists = os.path.exists(base_path)
        
        # Get list of files if base path exists
        files = os.listdir(base_path) if base_path_exists else []
        
        # Try different file name variations
        exact_csv = f"{category_name}.csv"
        exact_json = f"{category_name}.json"
        normalized_name = category_name.lower().replace(' ', '_')
        normalized_csv = f"{normalized_name}.csv"
        normalized_json = f"{normalized_name}.json"
        
        # Check which files exist
        file_exists = {
            'exact_csv': exact_csv in files,
            'exact_json': exact_json in files,
            'normalized_csv': normalized_csv in files,
            'normalized_json': normalized_json in files
        }
        
        # Try to read the first existing file
        file_content = None
        error = None
        
        if file_exists['exact_csv'] or file_exists['normalized_csv']:
            try:
                file_name = exact_csv if file_exists['exact_csv'] else normalized_csv
                file_path = os.path.join(base_path, file_name)
                df = pd.read_csv(file_path)
                file_content = {
                    'num_rows': len(df),
                    'columns': list(df.columns),
                    'first_row': df.iloc[0].to_dict() if len(df) > 0 else None
                }
            except Exception as e:
                error = str(e)
        elif file_exists['exact_json'] or file_exists['normalized_json']:
            try:
                file_name = exact_json if file_exists['exact_json'] else normalized_json
                file_path = os.path.join(base_path, file_name)
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    file_content = {
                        'type': 'list' if isinstance(data, list) else 'dict',
                        'length': len(data if isinstance(data, list) else data.get('posts', [])),
                        'first_item': (data[0] if isinstance(data, list) else data.get('posts', [])[0]) if data else None
                    }
            except Exception as e:
                error = str(e)
        
        return jsonify({
            'category_type': category_type,
            'category_name': category_name,
            'base_path': base_path,
            'base_path_exists': base_path_exists,
            'files_in_directory': files,
            'file_exists': file_exists,
            'file_content': file_content,
            'error': error
        })
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

if __name__ == "__main__":
    # This is used when running locally
    app.run(host='0.0.0.0', debug=True) 