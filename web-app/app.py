import os
import pandas as pd
import json
from flask import Flask, render_template, request, jsonify, redirect, url_for
from datetime import datetime
import logging
import urllib.parse
import functools
import gc
import time

# Handle different cache implementations
try:
    from werkzeug.contrib.cache import SimpleCache
except ImportError:
    try:
        from cachelib import SimpleCache
    except ImportError:
        # Create a simple in-memory cache implementation if dependencies not available
        class SimpleCache:
            def __init__(self, threshold=500, default_timeout=300):
                self._cache = {}
                self.default_timeout = default_timeout
                self.threshold = threshold
            
            def get(self, key):
                return self._cache.get(key)
                
            def set(self, key, value, timeout=None):
                self._cache[key] = value
                
            def clear(self):
                self._cache.clear()

logging.basicConfig(level=logging.INFO)  # Changed from DEBUG to INFO to reduce log volume
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

# Memory management settings
MAX_SEARCH_RESULTS = 100     # Limit search results
CACHE_TIMEOUT = 3600         # Cache expiration in seconds (1 hour)
CHUNK_SIZE = 1000            # Number of rows to process at a time
cache = SimpleCache(threshold=10, default_timeout=CACHE_TIMEOUT)  # In-memory cache limited to 10 items

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
def cached(key_prefix, timeout=None):
    """Function decorator for caching results"""
    def decorator(f):
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            cache_key = f"{key_prefix}:{':'.join(str(arg) for arg in args)}:{':'.join(f'{k}={v}' for k, v in kwargs.items())}"
            rv = cache.get(cache_key)
            if rv is not None:
                return rv
            rv = f(*args, **kwargs)
            cache.set(cache_key, rv, timeout=timeout)
            return rv
        return decorated_function
    return decorator

@cached('category_types', timeout=3600)
def load_category_types():
    """Load all category types."""
    logger.info(f"Looking for categories in: {CATEGORIES_DIR}")
    if os.path.exists(CATEGORIES_DIR):
        types = [d for d in os.listdir(CATEGORIES_DIR) 
                if os.path.isdir(os.path.join(CATEGORIES_DIR, d))]
        logger.info(f"Found category types: {types}")
        return types
    logger.info(f"Categories directory not found at: {CATEGORIES_DIR}")
    return []

@cached('categories', timeout=3600)
def load_categories(category_type):
    """Load categories for a specific type."""
    categories_path = os.path.join(CATEGORIES_DIR, category_type)
    logger.info(f"Loading categories from: {categories_path}")
    
    if os.path.exists(categories_path):
        categories = []
        for filename in os.listdir(categories_path):
            if filename.endswith(('.csv', '.json')):  # Handle both CSV and JSON
                category_name = filename.replace('.csv', '').replace('.json', '').replace('_', ' ')
                file_path = os.path.join(categories_path, filename)
                
                # Count items in the file - more efficiently
                try:
                    count = 0
                    if filename.endswith('.csv'):
                        # Get count without loading entire file
                        with open(file_path, 'r', encoding='utf-8') as f:
                            # Count header + lines
                            for i, _ in enumerate(f):
                                pass
                            count = i  # i will be the last line index
                    else:  # JSON file
                        with open(file_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            count = len(data if isinstance(data, list) else data.get('posts', []))
                except Exception as e:
                    logger.error(f"Error loading {filename}: {e}")
                    count = 0
                
                categories.append({
                    'name': category_name,
                    'count': count,
                    'file': filename
                })
        
        logger.info(f"Found {len(categories)} categories")
        return sorted(categories, key=lambda x: x['count'], reverse=True)
    
    logger.info(f"Category path not found: {categories_path}")
    return []

def get_file_path_for_category(category_type, category_name):
    """Helper to find the correct file path for a category with different naming variations."""
    normalized_type = category_type.lower().replace(' ', '_')
    normalized_name = category_name.lower().replace(' ', '_')
    normalized_name = normalized_name.replace('%20', '_')  # Handle URL encoding
    normalized_name = normalized_name.replace('.csv', '').replace('.json', '')
    
    # Get the base path
    base_path = os.path.join(CATEGORIES_DIR, normalized_type)
    if not os.path.exists(base_path):
        return None, f"Category type directory not found: {normalized_type}"
    
    # Try common file name variations
    possible_names = [
        f"{category_name}.csv", f"{category_name}.json",
        f"{normalized_name}.csv", f"{normalized_name}.json",
        f"{category_name}_Questions.csv", f"{normalized_name}_questions.csv",
        f"{category_name.replace(' ', '_')}.csv", f"{category_name.replace(' ', '_')}.json"
    ]
    possible_names.extend([name.upper() for name in possible_names])
    possible_names.extend([name.title() for name in possible_names])
    
    for filename in os.listdir(base_path):
        if filename in possible_names:
            return os.path.join(base_path, filename), None
    
    return None, f"No matching file found for category: {category_name}"

def load_posts(category_type, category_name, page=1, per_page=50):
    """Load posts with pagination to reduce memory usage."""
    logger.info(f"Loading posts for {category_type}/{category_name} (page {page})")
    
    try:
        # URL decode the category name
        category_name = urllib.parse.unquote(category_name)
        
        # Find the file path
        file_path, error = get_file_path_for_category(category_type, category_name)
        if error:
            return [], 0, error
        
        logger.info(f"Found file: {file_path}")
        
        # Calculate pagination offsets
        offset = (page - 1) * per_page
        
        # Process based on file type
        if file_path.endswith('.csv'):
            # Get total row count first
            total_count = 0
            with open(file_path, 'r', encoding='utf-8') as f:
                for i, _ in enumerate(f):
                    pass
                total_count = i  # i will be the last line index
            
            # Read only the necessary chunk
            if offset >= total_count:
                return [], total_count, None
                
            # Read only the needed chunk of data using skiprows and nrows
            posts_df = pd.read_csv(file_path, skiprows=range(1, offset+1), nrows=per_page)
            
            # Convert DataFrame to list of dictionaries
            posts = []
            for _, row in posts_df.iterrows():
                post = {}
                for col in row.index:
                    if col == 'tags':
                        # Handle tags field
                        tags_value = row[col]
                        if pd.isna(tags_value) or tags_value == '':
                            post[col] = []
                        elif isinstance(tags_value, str):
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
            
            return posts, total_count, None
            
        elif file_path.endswith('.json'):
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                all_posts = data if isinstance(data, list) else data.get('posts', [])
                total_count = len(all_posts)
                
                # Apply pagination
                posts = all_posts[offset:offset+per_page]
                
                # Ensure tags is always a list
                for post in posts:
                    if 'tags' not in post:
                        post['tags'] = []
                    elif not isinstance(post['tags'], list):
                        post['tags'] = [str(post['tags'])] if post['tags'] else []
                
                return posts, total_count, None
        
        return [], 0, "Unsupported file format"
            
    except Exception as e:
        import traceback
        logger.error(f"Error loading posts: {str(e)}")
        logger.error(traceback.format_exc())
        return [], 0, f"Error loading posts: {str(e)}"

@cached('visualizations', timeout=7200)
def load_visualizations():
    """Load available visualizations."""
    if os.path.exists(VISUALIZATIONS_DIR):
        return [f for f in os.listdir(VISUALIZATIONS_DIR) if f.endswith(('.png', '.jpg', '.jpeg'))]
    return []

def search_posts(query, page=1, per_page=50):
    """Search for posts containing the query string with pagination."""
    try:
        if not query:
            return [], 0
            
        start_time = time.time()
        dataset_path = os.path.join(DATA_DIR, 'preprocessed_nlp_dataset.csv')
        if not os.path.exists(dataset_path):
            dataset_path = os.path.join(DATA_DIR, 'nlp_stackoverflow_dataset.csv')
        
        if not os.path.exists(dataset_path):
            return [], 0
        
        # Search columns to check
        search_cols = ['title', 'description', 'tags']
        query_lower = query.lower()
        
        # Process file in chunks to reduce memory usage
        posts = []
        total_matching = 0
        offset = (page - 1) * per_page
        matching_needed = offset + per_page
        
        # Iteratively read chunks of the CSV
        reader = pd.read_csv(dataset_path, chunksize=CHUNK_SIZE)
        for chunk in reader:
            # Convert columns to strings for searching
            for col in search_cols:
                if col in chunk.columns:
                    chunk[col] = chunk[col].fillna('').astype(str)
            
            # Filter matching rows in this chunk
            matching_mask = chunk.apply(
                lambda row: any(query_lower in str(row[col]).lower() for col in search_cols if col in chunk.columns), 
                axis=1
            )
            matching_rows = chunk[matching_mask]
            
            total_matching += len(matching_rows)
            
            # If we've collected enough matches before this chunk, skip
            if total_matching <= offset:
                continue
                
            # If we're in the relevant page range, collect these results
            if total_matching > offset:
                # Calculate how many from this chunk we need
                start_idx = max(0, offset - (total_matching - len(matching_rows)))
                end_idx = min(len(matching_rows), start_idx + (matching_needed - len(posts)))
                
                # Extract needed rows from this chunk
                for _, row in matching_rows.iloc[start_idx:end_idx].iterrows():
                    post = {
                        'title': row['title'],
                        'description': row['description'] if 'description' in chunk.columns else '',
                        'accepted_answer': row['accepted_answer'] if 'accepted_answer' in chunk.columns else '',
                        'other_answers': row['other_answers'] if 'other_answers' in chunk.columns else '',
                        'tags': row['tags'].split() if 'tags' in chunk.columns and isinstance(row['tags'], str) else []
                    }
                    posts.append(post)
            
            # If we have enough results, break
            if len(posts) >= per_page:
                break
        
        # Clean up
        del reader
        gc.collect()
        
        logger.info(f"Search for '{query}' found {total_matching} results in {time.time() - start_time:.2f}s")
        return posts, total_matching
            
    except Exception as e:
        logger.error(f"Error searching: {e}")
        return [], 0

@cached('top_tags', timeout=86400)  # Cache for 24 hours
def load_top_tags():
    """Extract top tags from the visualization data"""
    try:
        # Check if we already have this data cached in a file
        tags_cache_file = os.path.join(DATA_DIR, 'top_tags_cache.json')
        if os.path.exists(tags_cache_file):
            with open(tags_cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        dataset_path = os.path.join(DATA_DIR, 'preprocessed_nlp_dataset.csv')
        if not os.path.exists(dataset_path):
            dataset_path = os.path.join(DATA_DIR, 'nlp_stackoverflow_dataset.csv')
            
        if os.path.exists(dataset_path):
            tag_counts = {}
            
            # Process in chunks to save memory
            for chunk in pd.read_csv(dataset_path, chunksize=CHUNK_SIZE):
                if 'tags' in chunk.columns:
                    for tags_str in chunk['tags'].fillna(''):
                        if isinstance(tags_str, str):
                            tags = tags_str.strip("[]'").replace("'", "").split(', ')
                            for tag in tags:
                                if tag:
                                    tag_counts[tag] = tag_counts.get(tag, 0) + 1
            
            # Sort by count and take top 10
            top_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            
            # Save to cache file
            with open(tags_cache_file, 'w', encoding='utf-8') as f:
                json.dump(top_tags, f)
                
            return top_tags
        return []
    except Exception as e:
        logger.error(f"Error loading top tags: {e}")
        return []

@cached('dataset_stats', timeout=86400)  # Cache for 24 hours
def get_dataset_stats():
    """Get statistics about the dataset"""
    try:
        # Check for cached stats
        stats_cache_file = os.path.join(DATA_DIR, 'dataset_stats_cache.json')
        if os.path.exists(stats_cache_file):
            with open(stats_cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        dataset_path = os.path.join(DATA_DIR, 'preprocessed_nlp_dataset.csv')
        if not os.path.exists(dataset_path):
            dataset_path = os.path.join(DATA_DIR, 'nlp_stackoverflow_dataset.csv')
            
        if os.path.exists(dataset_path):
            # Count rows without loading entire file
            total_posts = 0
            with open(dataset_path, 'r', encoding='utf-8') as f:
                for i, _ in enumerate(f):
                    pass
                total_posts = i  # Last line index
            
            stats = {
                'total_posts': total_posts,
                'categories': {}
            }
            
            # Count posts in each category type
            for category_type in load_category_types():
                stats['categories'][category_type] = sum(c['count'] for c in load_categories(category_type))
            
            # Save stats to cache
            with open(stats_cache_file, 'w', encoding='utf-8') as f:
                json.dump(stats, f)
                
            return stats
        return None
    except Exception as e:
        logger.error(f"Error getting dataset stats: {e}")
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
    
    # Get pagination parameters
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    
    # Load posts with pagination
    posts, total_count, error = load_posts(category_type, category_name, page=page, per_page=per_page)
    
    # Calculate pagination info
    total_pages = (total_count + per_page - 1) // per_page if total_count > 0 else 1
    
    if error:
        logger.error(f"Error loading posts: {error}")
        return render_template('category.html',
                             category_type=category_type,
                             category_name=category_name,
                             posts=[],
                             page=page,
                             total_pages=0,
                             total_count=0,
                             per_page=per_page,
                             error_message=error)
    
    logger.info(f"Loaded {len(posts)} posts (page {page}/{total_pages})")
    return render_template('category.html',
                         category_type=category_type,
                         category_name=category_name,
                         posts=posts,
                         page=page,
                         total_pages=total_pages,
                         total_count=total_count,
                         per_page=per_page)

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
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    
    results, total_count = search_posts(query, page=page, per_page=per_page) if query else ([], 0)
    
    total_pages = (total_count + per_page - 1) // per_page if total_count > 0 else 1
    
    return render_template('search.html', 
                           query=query, 
                           results=results,
                           page=page,
                           total_pages=total_pages,
                           total_count=total_count,
                           per_page=per_page,
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
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    posts, total_count, _ = load_posts(category_type, category_name, page=page, per_page=per_page)
    return jsonify({
        'posts': posts, 
        'total': total_count,
        'page': page,
        'per_page': per_page
    })

@app.route('/api/search')
def api_search():
    query = request.args.get('query', '')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    
    results, total_count = search_posts(query, page=page, per_page=per_page) if query else ([], 0)
    
    return jsonify({
        'results': results, 
        'total': total_count,
        'page': page,
        'per_page': per_page
    })

@app.route('/api/stats')
def api_stats():
    stats = get_dataset_stats()
    return jsonify(stats)

@app.route('/about')
def about():
    return render_template('about.html', current_year=datetime.now().year)

@app.route('/clear-cache')
def clear_cache():
    """Admin endpoint to clear the application cache."""
    try:
        # Clear in-memory cache
        cache.clear()
        
        # Clear file caches
        cache_files = [
            os.path.join(DATA_DIR, 'top_tags_cache.json'),
            os.path.join(DATA_DIR, 'dataset_stats_cache.json')
        ]
        
        for file_path in cache_files:
            if os.path.exists(file_path):
                os.remove(file_path)
        
        # Force garbage collection
        gc.collect()
        
        return jsonify({"success": "Cache cleared successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

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
        
        # Clear cache after reprocessing
        cache.clear()
        
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
                # Read only first 10 rows to save memory
                df = pd.read_csv(file_path, nrows=10)
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

@app.route('/memory')
def memory_usage():
    """Debug endpoint to check memory usage"""
    import psutil
    import sys
    
    process = psutil.Process(os.getpid())
    memory_info = {
        'rss': process.memory_info().rss / 1024 / 1024,  # MB
        'vms': process.memory_info().vms / 1024 / 1024,  # MB
        'percent': process.memory_percent(),
        'cache_size': len(cache._cache) if hasattr(cache, '_cache') else 'Unknown'
    }
    
    return jsonify(memory_info)

@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', 
                          error_code=500,
                          error_message="Server Error: The application encountered an internal error.",
                          current_year=datetime.now().year), 500

@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', 
                          error_code=404,
                          error_message="Page Not Found: The requested resource could not be found.",
                          current_year=datetime.now().year), 404

if __name__ == "__main__":
    # This is used when running locally
    app.run(host='0.0.0.0', debug=True) 