from google import genai
from google.genai import types
from fpdf import FPDF
import pathlib
import os
from typing import List
import config
from sentence_transformers import SentenceTransformer, util
import matplotlib.pyplot as plt
import streamlit as st
import subprocess
import requests
import re
import base64
import urllib.parse
import webbrowser
import tempfile
import time

client = genai.Client(api_key=config.GOOGLE_API_KEY)

semantic_model = SentenceTransformer("all-MiniLM-L6-v2")

os.environ["TOKENIZERS_PARALLELISM"] = "false"

def convert_local_pdf_to_latex_text(pdf_path: str) -> str:
    try:
        filepath = pathlib.Path(pdf_path)
        if not filepath.exists():
            raise FileNotFoundError(f"File not found: {pdf_path}")
        prompt = """
You are a university exam paper digitizer.

Your task is to extract **only the exam questions and their marking scheme** from this PDF and convert them into a clean, structured LaTeX-style text format.

📌 Strict Instructions:
1. ❌ Completely ignore:
    - University or institution names
    - Semester details, course/subject codes
    - Exam duration, total marks, dates
    - Instructions to candidates, headers, footers, or page numbers

2. ✅ Focus only on the actual questions **and their marks**:
    - Include **paper instructions** meant for students (e.g., “Attempt all questions”)
    - Use **manual numbering** (`Q1.`, `Q2.`, etc.)
    - Subparts as `(a)`, `(b)`, etc.
    - Insert `\\textbf{OR}` if applicable
    - Use LaTeX formatting for math
    - Use `[\\textbf{Figure or Diagram Here}]` for diagrams

3. 📝 Preserve marks exactly as shown

4. 🔍 No hallucination, skipping, paraphrasing, or reordering

5. 🧱 Preserve the paper’s original structure

📄 Output:
Return a **clean LaTeX-style multiline string** of only the questions and marking scheme.
"""

        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=[
                types.Part.from_bytes(
                    data=filepath.read_bytes(), mime_type="application/pdf"
                ),
                prompt,
            ],
        )
        return response.text.strip()
    except Exception as e:
        print(f"[ERROR] Failed to process PDF '{pdf_path}': {e}")
        return ""

def process_all_pdfs(folder_path: str) -> List[str]:
    extracted_texts = []
    if not os.path.exists(folder_path):
        print(f"[ERROR] Folder not found: {folder_path}")
        return extracted_texts
    pdf_files = [f for f in os.listdir(folder_path) if f.lower().endswith(".pdf")]
    if not pdf_files:
        print(f"[INFO] No PDF files found in: {folder_path}")
        return extracted_texts
    for pdf_file in sorted(pdf_files):
        full_path = os.path.join(folder_path, pdf_file)
        print(f"[INFO] Processing: {pdf_file}")
        text = convert_local_pdf_to_latex_text(full_path)
        if text:
            extracted_texts.append(text)
        else:
            print(f"[WARNING] Skipped {pdf_file} due to processing error.")
    return extracted_texts

def generate_new_question_paper(joined_corpus: str) -> str:
    prompt = f"""
You are an AI assistant trained to generate university-level exam question papers.

🎯 Your task:

Based on the following university-level question papers, generate a new question paper that closely follows their:

- Pattern and formatting
- Structure and layout
- Topic distribution and difficulty
- Types of questions asked (theory, numerical, conceptual, etc.)

🧠 Guidelines:
- Use **Part A, Part B** if present
- Include numerical problems in **LaTeX**
- Use Markdown for diagrams: `![diagram_label](diagram_description)`
- Maintain length, style, and complexity
- Infer the subject from previous content
- Do NOT repeat questions
- Return only the **question paper text**

---

=== START OF PREVIOUS PAPERS ===
{joined_corpus}
=== END ===

Now, generate the new question paper below:
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash", contents=[types.Part(text=prompt)]
        )
        return response.text.strip()
    except Exception as e:
        print(f"[ERROR] Failed to generate new paper: {e}")
        return ""

def semantic_similarity(text1: str, text2: str) -> float:
    embedding1 = semantic_model.encode(text1, convert_to_tensor=True)
    embedding2 = semantic_model.encode(text2, convert_to_tensor=True)
    similarity_score = util.cos_sim(embedding1, embedding2).item()
    return round(similarity_score * 100, 2)

def plot_similarity_graph(similarity_scores):
    fig, ax = plt.subplots()
    filenames = list(similarity_scores.keys())
    values = list(similarity_scores.values())
    bars = ax.barh(filenames, values, color="skyblue")
    ax.set_xlabel("Similarity (%)")
    ax.set_title("Similarity of Generated Paper with Previous Papers")
    # Add percentage labels to each bar
    ax.bar_label(bars, fmt="%.1f%%", padding=5)
    plt.tight_layout()
    return fig

def clean_and_format_paper_to_latex(raw_paper_text: str) -> str:
    prompt = rf"""
You are a LaTeX formatting assistant.

Your task is to take the following university-level question paper and convert it into a clean, structured **LaTeX document**, strictly following these rules:

📌 **Important Instructions**:

1. ✅ Include:
    - Only the **paper instructions**, **marking scheme**, and **questions**
    - Proper formatting using `\\section*`, `\\subsection*`, etc., if needed
    - Use `\\textbf{{}}` or `\\textit{{}}` where appropriate
    - Mathematical symbols or expressions must be in **LaTeX math mode**

2. ❌ Do NOT include:
    - University name
    - Term, semester, year, or subject code
    - Headers, footers, page numbers, or watermarks

Now convert the following paper into LaTeX accordingly:

=== START OF RAW PAPER ===
{raw_paper_text}
=== END ===

Return the output as a **standalone LaTeX document**, starting with `\\documentclass` and ending with `\\end{{document}}`.
"""

    try:
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=[types.Part(text=prompt)],
        )
        return response.text.strip()
    except Exception as e:
        print(f"[ERROR] Failed to format paper in LaTeX: {e}")
        return ""

def open_latex_in_overleaf(latex_string: str) -> str:
    # Remove enclosing markdown latex block if present
    match = re.search(r"```latex\s*(.*?)\s*```", latex_string, re.DOTALL)
    latex_code = match.group(1).strip() if match else latex_string.strip()
    # Base64 encode for URL
    latex_bytes = latex_code.encode("utf-8")
    base64_encoded = base64.b64encode(latex_bytes).decode("utf-8")
    data_uri = f"data:application/x-tex;base64,{base64_encoded}"
    encoded_uri = urllib.parse.quote(data_uri, safe="")
    overleaf_url = f"https://www.overleaf.com/docs?snip_uri={encoded_uri}"
    webbrowser.open(overleaf_url)
    return overleaf_url


st.set_page_config(page_title="Question Paper Generator", layout="wide")
st.title("📄 University Question Paper Generator (AI-powered)")

uploaded_files = st.file_uploader(
    "Upload 10 to 20 previous university exam PDFs",
    type=["pdf"],
    accept_multiple_files=True,
)

if uploaded_files:
    if len(uploaded_files) < 10 or len(uploaded_files) > 20:
        st.warning("Please upload at least 10 and at most 20 PDFs.")
        st.stop()

    with tempfile.TemporaryDirectory() as temp_dir:
        st.info("Starting PDF processing...")
        progress_text = st.empty()
        progress_bar = st.progress(0)
        processing_status = st.empty()

        extracted_texts = []
        filenames = []

        for i, uploaded_file in enumerate(uploaded_files):
            filename = uploaded_file.name
            temp_path = os.path.join(temp_dir, filename)
            filenames.append(filename)
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.read())

            progress_text.text(f"📄 Processing {filename}...")
            processing_status.markdown("🔄 Converting to LaTeX-style text...")
            latex_text = convert_local_pdf_to_latex_text(temp_path)
            extracted_texts.append(latex_text)

            progress_bar.progress((i + 1) / len(uploaded_files))
            time.sleep(0.5)

        processing_status.markdown("🧠 Generating new question paper...")
        joined_text = "\n\n".join(extracted_texts)
        generated_paper = generate_new_question_paper(joined_text)

        processing_status.markdown("🧼 Cleaning & formatting into LaTeX...")
        latex_final = clean_and_format_paper_to_latex(generated_paper)

        processing_status.markdown("📤 Uploading to Overleaf...")
        overleaf_link = open_latex_in_overleaf(latex_final)

        st.success("✅ All done! Generated paper is ready.")
        st.markdown(
            f"[📄 View Generated Paper on Overleaf]({overleaf_link})",
            unsafe_allow_html=True,
        )

        st.divider()

        st.markdown("### 📊 Similarity Index Plot")

        processing_status.markdown("🔎 Calculating similarity scores...")
        similarity_scores = {
            filenames[i]: semantic_similarity(generated_paper, extracted_texts[i])
            for i in range(len(extracted_texts))
        }

        fig = plot_similarity_graph(similarity_scores)
        st.pyplot(fig)

        processing_status.empty()
        progress_text.empty()
        progress_bar.empty()
