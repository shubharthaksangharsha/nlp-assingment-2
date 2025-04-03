# NLP Knowledge Base Web Application

The web interface for the NLP Knowledge Base project. This Flask application provides a modern, responsive interface for exploring NLP-related content organized by various categorization schemes.

▲ Web Demo: [https://nlp-knowledge-base-2ay6q43v3-shubharthaks-projects.vercel.app/](https://nlp-knowledge-base-2ay6q43v3-shubharthaks-projects.vercel.app/)

## Features

- **Clean, Modern UI**:
  - Responsive design that works on all devices
  - Dark/Light mode toggle
  - Intuitive navigation
  - Category-based browsing

- **Content Organization**:
  - Multiple category views
  - Post listings with tags
  - Code syntax highlighting
  - Markdown rendering

- **Search Functionality**:
  - Full-text search across all posts
  - Category-specific search
  - Tag-based filtering

## Directory Structure

```
web-app/
├── app.py              # Main Flask application
├── static/            
│   ├── css/           # Stylesheets
│   ├── js/            # JavaScript files
│   └── img/           # Images and icons
├── templates/
│   ├── base.html      # Base template
│   ├── index.html     # Home page
│   ├── category.html  # Category view
│   └── search.html    # Search results
└── vercel_setup.py    # Vercel deployment configuration
```

## Local Development

1. **Set Up Environment**
   ```bash
   # Create and activate virtual environment (optional)
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or
   venv\Scripts\activate     # Windows
   
   # Install dependencies
   pip install -r ../requirements.txt
   ```

2. **Run Development Server**
   ```bash
   python app.py
   ```

3. **Access the Application**
   - Open browser and go to `http://localhost:5000`
   - Changes to templates and static files will auto-reload

## Deployment

This application is configured for deployment on Vercel:

1. **Vercel Configuration**
   - `vercel.json` in the root directory handles routing and builds
   - `vercel_setup.py` manages data file copying and environment setup

2. **Deploy to Vercel**
   ```bash
   # From the project root
   vercel
   ```

3. **Environment Variables**
   Required environment variables:
   - `VERCEL=1` (set automatically)
   - Any additional API keys or configurations

## Template Structure

- **base.html**: Base template with common elements
  - Navigation bar
  - Dark/Light mode toggle
  - Footer
  
- **category.html**: Category view template
  - Category header
  - Post listings
  - Tag display
  
- **index.html**: Home page template
  - Category type navigation
  - Statistics display
  - Quick links

## Static Assets

- **CSS**:
  - `style.css`: Main stylesheet
  - `dark-mode.css`: Dark theme styles
  - `syntax-highlight.css`: Code highlighting

- **JavaScript**:
  - `script.js`: Main functionality
  - `dark-mode.js`: Theme switching
  - `search.js`: Search functionality

## Contributing

1. Fork the repository
2. Create your feature branch
3. Make your changes
4. Test locally
5. Submit a pull request

## Troubleshooting

- **Static Files Not Loading**:
  - Check file permissions
  - Verify paths in `vercel.json`
  - Clear browser cache

- **Data Not Displaying**:
  - Check data file paths
  - Verify file permissions
  - Check deployment logs

- **Deployment Issues**:
  - Verify Vercel configuration
  - Check environment variables
  - Review build logs 