# NLP Knowledge Base 📚

A comprehensive collection of NLP questions, answers, and insights organized by different categorization schemes. This project provides a web interface to explore and search through curated NLP-related content from Stack Exchange.

[![Web Demo](web-app/static/img/top_tags.png)](https://nlp-knowledge-base-2ay6q43v3-shubharthaks-projects.vercel.app/)

> 🔗 [**Live Demo**](https://nlp-knowledge-base-2ay6q43v3-shubharthaks-projects.vercel.app/) | [**Documentation**](src/README.md) | [**Web App**](web-app/README.md)

## ✨ Features

### 📊 Multiple Categorization Schemes
- **Task-based**: Text Classification, Sentiment Analysis, etc.
- **Keyword-based**: Implementation Issues, Library Usage, etc.
- **Library-based**: NLTK, spaCy, BERT, etc.
- **Question Type**: How, What, Why, etc.

### 📝 Rich Content
- 🔍 Curated questions and answers
- 💻 Code examples
- 🛠️ Implementation details
- ✅ Best practices
- ❗ Common issues and solutions

### 🌐 Modern Web Interface
- 🎨 Clean and responsive design
- 🧭 Easy navigation
- 📂 Category browsing
- 🔍 Search functionality
- 🌓 Dark/Light mode toggle

## 📊 Insights

<div align="center">
  <img src="web-app/static/img/description_wordcloud.png" alt="Description Word Cloud" width="400"/>
  <p><em>Word Cloud of NLP Topics</em></p>
</div>

## 🗂️ Project Structure

```
nlp_knowledge_base/
├── 📁 src/                
│   ├── 📜 data_collector.py   
│   ├── 📜 preprocessor.py     
│   ├── 📜 data_visualizer.py  
│   ├── 📜 categorizer.py      
│   └── 📜 main.py             
├── 📁 data/
│   └── 📁 categories/     # Processed data files
│       ├── 📁 keyword_based/
│       ├── 📁 task_based/
│       ├── 📁 library_based/
│       └── 📁 question_type/
├── 📁 web-app/           # Web application
│   ├── 📜 app.py         # Flask application
│   ├── 📁 static/        # Static assets
│   └── 📁 templates/     # HTML templates
├── 📜 vercel.json       # Vercel deployment config
└── 📜 requirements.txt  # Python dependencies
```

## 🚀 Getting Started

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd nlp_knowledge_base
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run Locally**
   ```bash
   cd web-app
   python app.py
   ```

4. **Access the Application**
   - Open your browser and navigate to `http://localhost:5000`

## 🌐 Deployment

This application is configured for deployment on Vercel:

1. **Install Vercel CLI**
   ```bash
   npm install -g vercel
   ```

2. **Deploy**
   ```bash
   vercel
   ```

## 📊 Data Organization

<div align="center">
  <img src="web-app/static/img/title_wordcloud.png" alt="Title Word Cloud" width="400"/>
  <p><em>Popular Topics in Questions</em></p>
</div>

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Stack Exchange community for valuable content
- Contributors and maintainers
- Open source NLP community 
