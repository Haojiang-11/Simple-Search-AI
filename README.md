# 📚 Simple-Search-AI

A beautiful, AI-powered academic paper search tool built with Streamlit (using **Gemini 3 pro**). It helps researchers find papers from **Top-tier AI Conferences** (ICLR, NeurIPS, ICML, CVPR, etc.) using natural language queries and DeepSeek's reasoning capabilities.

## ✨ Features

- **🔍 Basic Search**: Directly search for papers using keywords (No API Key required).
- **🧠 AI Smart Search**: Describe your research intent in natural language, and the AI will extract keywords and rerank papers (Requires DeepSeek API Key).
- **🏆 Top-tier Conference Support**: Comprehensive coverage of prestigious AI venues including ICLR, NeurIPS, ICML, CVPR, ECCV, ICCV, and AAAI.
- **Real-time Retrieval**: Fetches the latest data from OpenReview, CVF, and arXiv.
- **Macaron UI Theme**: A clean, academic-friendly interface with a soft pastel color palette.
- **PDF Direct Links**: One-click access to paper PDFs.

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/Simple-Search-AI.git
cd Simple-Search-AI
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the App
```bash
streamlit run app.py
```

## 🔑 API Key Configuration
- **Basic Search**: Works out-of-the-box without any configuration.
- **AI Smart Search**: Uses **DeepSeek API** for keyword extraction and paper reranking. 
    - You need to enter your API Key in the sidebar settings.
    - The key is stored only in your browser session.

## 🛠️ Tech Stack
- **Frontend**: Streamlit
- **Search Backend**: OpenReview API, BeautifulSoup (for CVF), arXiv API
- **AI Logic**: OpenAI SDK (compatible with DeepSeek)

## 📄 License
[MIT License](LICENSE)
