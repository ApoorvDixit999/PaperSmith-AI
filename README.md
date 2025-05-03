# 🛠️ PaperSmith-AI: AI-Powered University Question Paper Generator

**PaperSmith-AI** is a Streamlit-based web application that uses advanced AI models (Google Gemini + Sentence Transformers) to generate a brand-new university-level question paper based on 10–20 previously uploaded exam PDFs. It preserves the original structure, difficulty, and formatting — then outputs the result as a fully formatted LaTeX document, ready to open in Overleaf.

---

## 🚀 Features

✅ Extracts only **questions and marking schemes** from uploaded PDFs  
✅ Generates a **new question paper** using Gemini AI, mimicking original structure and difficulty  
✅ Automatically formats output in **LaTeX** (standalone document)  
✅ Opens the final result directly in **Overleaf**  
✅ Computes **semantic similarity** to original papers and shows a visual comparison  

---

## 🖼️ Demo

> _Coming soon!_  
Screenshots or a Loom video demo can go here.

---

## 📂 Project Structure

```
PaperSmith-AI/
├── app.py                  # Main Streamlit application
├── config.py               # Stores Google API key
├── requirements.txt        # Python dependencies
├── README.md               # Project documentation
└── .streamlit/
    └── config.toml         # Optional: Streamlit theming
```

---

## 🧠 How It Works

1. **Upload PDFs** of previous university exams (10–20)
2. The app extracts only the **questions and marks**
3. AI (Gemini) generates a **new paper** based on the pattern
4. Output is formatted as a **clean LaTeX document**
5. Optionally, it opens directly in **Overleaf**
6. A **semantic similarity graph** compares new vs. originals

---

## 🛠️ Setup Instructions

### 1. Clone the repo

```bash
git clone https://github.com/your-username/PaperSmith-AI.git
cd PaperSmith-AI
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Add your Google API key

Create a `config.py` file:

```python
# config.py
GOOGLE_API_KEY = "your_google_api_key_here"
```

> You can get an API key from [Google AI Studio](https://makersuite.google.com/)

### 4. Run the app

```bash
streamlit run app.py
```

---

## 📦 Requirements

- Python 3.8+
- Google Generative AI SDK
- Streamlit
- Sentence Transformers
- FPDF
- Matplotlib

All dependencies are listed in `requirements.txt`.

---

## 📊 Example Output

- ✅ LaTeX-formatted exam paper
- ✅ Overleaf URL
- ✅ Semantic similarity plot like this:

```
Similarity of Generated Paper with Previous Papers
+----------------------------------+-------+
| previous_exam1.pdf              | 87.5% |
| previous_exam2.pdf              | 84.2% |
| ...                              | ...   |
```

---

## ✨ Credits

Built with ❤️ using:
- [Google Generative AI](https://ai.google.dev/)
- [Sentence Transformers](https://www.sbert.net/)
- [Streamlit](https://streamlit.io)
- [LaTeX](https://www.latex-project.org/)
