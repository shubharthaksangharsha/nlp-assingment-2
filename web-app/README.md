# 🌐 NLP Knowledge Base Web Application

> 💫 A modern, responsive web interface for exploring NLP knowledge, built with Flask and powered by curated Stack Exchange content.

[![Demo](https://img.shields.io/badge/demo-live-success.svg)](https://nlp-knowledge-base-2ay6q43v3-shubharthaks-projects.vercel.app/)
[![Flask](https://img.shields.io/badge/flask-2.0+-blue.svg)](https://flask.palletsprojects.com/)

## ✨ Features

### 🎨 Modern Interface
- 📱 Responsive design for all devices
- 🌓 Dark/Light mode toggle
- 🧭 Intuitive navigation
- 📂 Category-based browsing

### 📚 Content Organization
- 🗂️ Multiple category views
- 🏷️ Post listings with tags
- 💻 Code syntax highlighting
- 📝 Markdown rendering

### 🔍 Search Capabilities
- 📄 Full-text search across posts
- 🎯 Category-specific filtering
- 🏷️ Tag-based navigation
- ⚡ Fast search results

## 📁 Directory Structure

```
web-app/
├── 🚀 app.py              # Main Flask application
├── 📂 static/            
│   ├── 🎨 css/           # Stylesheets
│   ├── ⚡ js/            # JavaScript files
│   └── 🖼️ img/           # Images and icons
├── 📝 templates/
│   ├── 📄 base.html      # Base template
│   ├── 🏠 index.html     # Home page
│   ├── 📂 category.html  # Category view
│   └── 🔍 search.html    # Search results
└── ⚙️ vercel_setup.py    # Vercel deployment config
```

## 💻 Local Development

### 1. 🔧 Set Up Environment
```bash
# Create and activate virtual environment
python -m venv venv

# Linux/Mac
source venv/bin/activate

# Windows
venv\Scripts\activate

# Install dependencies
pip install -r ../requirements.txt
```

### 2. 🚀 Run Development Server
```bash
python app.py
```

### 3. 🌐 Access Application
- 🔗 Open `http://localhost:5000`
- 🔄 Auto-reload enabled for development
- 🛠️ Debug mode active

## 🚀 Deployment

### 1. ⚙️ Vercel Configuration
```json
{
  "version": 2,
  "builds": [
    { "src": "app.py", "use": "@vercel/python" }
  ],
  "routes": [
    { "src": "/(.*)", "dest": "app.py" }
  ]
}
```

### 2. 📤 Deploy
```bash
vercel
```

### 3. 🔐 Environment Setup
Required variables:
- `VERCEL=1`
- `FLASK_ENV=production`
- `SECRET_KEY=your-secret-key`

## 🎨 Template Structure

### 📄 Base Template (`base.html`)
- 🧭 Navigation bar
- 🌓 Theme toggle
- 📱 Responsive menu
- 👣 Footer

### 📂 Category View (`category.html`)
- 📑 Category header
- 📝 Post listings
- 🏷️ Tag cloud
- 🔍 Search bar

### 🏠 Home Page (`index.html`)
- 📊 Statistics dashboard
- 🔗 Quick links
- 📂 Category navigation
- 📈 Trending topics

## 🎨 Static Assets

### CSS Files
```css
/* Main styling */
@import 'style.css';       /* Core styles */
@import 'dark-mode.css';   /* Dark theme */
@import 'responsive.css';  /* Mobile-first design */
```

### JavaScript Modules
```javascript
// Core functionality
import { initApp } from './script.js';
import { setupTheme } from './dark-mode.js';
import { initSearch } from './search.js';
```

## 🤝 Contributing

1. 🍴 Fork repository
2. 🌿 Create feature branch
3. 💻 Make changes
4. 🧪 Test thoroughly
5. 📤 Submit pull request

## ❓ Troubleshooting

### 🔍 Common Issues

#### 📁 Static Files
- ✅ Check file permissions
- 🔄 Clear browser cache
- 📋 Verify paths in config

#### 📊 Data Display
- 📂 Verify data file locations
- 🔒 Check file permissions
- 📝 Review error logs

#### 🚀 Deployment
- ⚙️ Validate Vercel config
- 🔐 Check environment vars
- 📋 Review build logs

## 📚 Resources

- 📖 [Flask Documentation](https://flask.palletsprojects.com/)
- 🚀 [Vercel Docs](https://vercel.com/docs)
- 💻 [Contributing Guide](../CONTRIBUTING.md)
- 📝 [Change Log](../CHANGELOG.md) 