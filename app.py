import streamlit as st
import os
from modules.pdf_processor import process_multiple_pdfs
from modules.gemini_ocr import extract_text_from_images
from modules.template_processor import (
    extract_placeholders,
    fill_docx_template,
    load_template,
    save_document
)
from modules.gemini_mapper import map_placeholders_to_values


st.set_page_config(
    page_title="Insurance GLR Auto-Filler",
    page_icon="📋",
    layout="wide"
)

neo_brutal_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@700&display=swap');
    
    .main {
        background-color: #f5f5f5;
    }
    
    h1 {
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 700;
        font-size: 3.5rem;
        color: #000000;
        text-shadow: 4px 4px 0px #FF006E;
        border: 6px solid #000000;
        padding: 20px;
        background-color: #FFBE0B;
        margin-bottom: 30px;
        box-shadow: 8px 8px 0px #000000;
    }
    
    .upload-section {
        border: 5px solid #000000;
        padding: 25px;
        margin: 20px 0;
        background-color: #8338EC;
        box-shadow: 6px 6px 0px #000000;
    }
    
    .upload-section h3 {
        color: #FFFFFF;
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 700;
        font-size: 1.8rem;
        margin-bottom: 15px;
    }
    
    .stButton > button {
        background-color: #FB5607;
        color: #FFFFFF;
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 700;
        font-size: 1.5rem;
        border: 5px solid #000000;
        padding: 20px 40px;
        box-shadow: 6px 6px 0px #000000;
        transition: all 0.1s;
        cursor: pointer;
        width: 100%;
    }
    
    .stButton > button:hover {
        transform: translate(3px, 3px);
        box-shadow: 3px 3px 0px #000000;
    }
    
    .stButton > button:active {
        transform: translate(6px, 6px);
        box-shadow: 0px 0px 0px #000000;
    }
    
    .stDownloadButton > button {
        background-color: #3A86FF;
        color: #FFFFFF;
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 700;
        font-size: 1.3rem;
        border: 5px solid #000000;
        padding: 15px 30px;
        box-shadow: 6px 6px 0px #000000;
        transition: all 0.1s;
        width: 100%;
    }
    
    .stDownloadButton > button:hover {
        transform: translate(3px, 3px);
        box-shadow: 3px 3px 0px #000000;
    }
    
    .info-box {
        border: 4px solid #000000;
        padding: 15px;
        margin: 10px 0;
        background-color: #06FFA5;
        box-shadow: 4px 4px 0px #000000;
        font-weight: 600;
    }
    
    .warning-box {
        border: 4px solid #000000;
        padding: 15px;
        margin: 10px 0;
        background-color: #FFD60A;
        box-shadow: 4px 4px 0px #000000;
        font-weight: 600;
    }
    
    .success-box {
        border: 4px solid #000000;
        padding: 15px;
        margin: 10px 0;
        background-color: #06FFA5;
        box-shadow: 4px 4px 0px #000000;
        font-weight: 600;
    }
    
    .error-box {
        border: 4px solid #000000;
        padding: 15px;
        margin: 10px 0;
        background-color: #FF006E;
        color: #FFFFFF;
        box-shadow: 4px 4px 0px #000000;
        font-weight: 600;
    }
    
    .stExpander {
        border: 4px solid #000000;
        background-color: #FFFFFF;
        box-shadow: 4px 4px 0px #000000;
    }
    
    .uploadedFile {
        border: 3px solid #000000;
        background-color: #FFFFFF;
        box-shadow: 3px 3px 0px #000000;
    }
</style>
"""

st.markdown(neo_brutal_css, unsafe_allow_html=True)

st.markdown('<h1 style="text-align: center;">📋 Insurance GLR Auto-Filler</h1>', unsafe_allow_html=True)

api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    st.markdown(
        '<div class="error-box">⚠️ GEMINI_API_KEY not found! Please add it in the Secrets tab.</div>',
        unsafe_allow_html=True
    )
    st.stop()

st.markdown('<div class="upload-section">', unsafe_allow_html=True)
st.markdown('<h3>📄 Section 1: Upload Template (.docx)</h3>', unsafe_allow_html=True)
template_file = st.file_uploader(
    "Upload your DOCX template with placeholders like {{NAME}}, {{AGE}}, etc.",
    type=['docx'],
    key="template"
)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="upload-section">', unsafe_allow_html=True)
st.markdown('<h3>📑 Section 2: Upload Photo Reports (.pdf)</h3>', unsafe_allow_html=True)
pdf_files = st.file_uploader(
    "Upload one or more PDF files containing scanned insurance/medical documents",
    type=['pdf'],
    accept_multiple_files=True,
    key="pdfs"
)
st.markdown('</div>', unsafe_allow_html=True)

if template_file and pdf_files:
    st.markdown('<div class="upload-section" style="background-color: #FB5607;">', unsafe_allow_html=True)
    st.markdown('<h3>⚡ Section 3: Process Documents</h3>', unsafe_allow_html=True)
    
    if st.button("🚀 Analyze & Generate Filled Docx", key="process_btn"):
        
        st.session_state.extracted_text = None
        st.session_state.json_mapping = None
        st.session_state.final_docx = None
        
        try:
            st.markdown(
                '<div class="info-box">📥 Step 1/5: Converting PDFs to images...</div>',
                unsafe_allow_html=True
            )
            images = process_multiple_pdfs(pdf_files)
            st.markdown(
                f'<div class="success-box">✅ Converted {len(pdf_files)} PDF(s) into {len(images)} images</div>',
                unsafe_allow_html=True
            )
            
            st.markdown(
                '<div class="info-box">🔍 Step 2/5: Running OCR with Gemini Vision...</div>',
                unsafe_allow_html=True
            )
            extracted_text = extract_text_from_images(images, api_key)
            st.session_state.extracted_text = extracted_text
            st.markdown(
                f'<div class="success-box">✅ Extracted {len(extracted_text)} characters of text</div>',
                unsafe_allow_html=True
            )
            
            st.markdown(
                '<div class="info-box">📋 Step 3/5: Extracting placeholders from template...</div>',
                unsafe_allow_html=True
            )
            template_bytes = template_file.read()
            doc = load_template(template_bytes)
            placeholders = extract_placeholders(doc)
            st.markdown(
                f'<div class="success-box">✅ Found {len(placeholders)} placeholders: {", ".join(placeholders)}</div>',
                unsafe_allow_html=True
            )
            
            st.markdown(
                '<div class="info-box">🤖 Step 4/5: Mapping values with Gemini LLM...</div>',
                unsafe_allow_html=True
            )
            mapping = map_placeholders_to_values(extracted_text, placeholders, api_key)
            st.session_state.json_mapping = mapping
            st.markdown(
                '<div class="success-box">✅ Successfully mapped all placeholders to values</div>',
                unsafe_allow_html=True
            )
            
            st.markdown(
                '<div class="info-box">✍️ Step 5/5: Filling template with extracted data...</div>',
                unsafe_allow_html=True
            )
            template_file.seek(0)
            template_bytes = template_file.read()
            doc = load_template(template_bytes)
            filled_doc = fill_docx_template(doc, mapping)
            final_bytes = save_document(filled_doc)
            st.session_state.final_docx = final_bytes
            st.markdown(
                '<div class="success-box">🎉 Template filled successfully!</div>',
                unsafe_allow_html=True
            )
            
        except Exception as e:
            st.markdown(
                f'<div class="error-box">❌ Error: {str(e)}</div>',
                unsafe_allow_html=True
            )
    
    st.markdown('</div>', unsafe_allow_html=True)

if st.session_state.get('final_docx'):
    st.markdown('<div class="upload-section" style="background-color: #3A86FF;">', unsafe_allow_html=True)
    st.markdown('<h3>💾 Section 4: Download Result</h3>', unsafe_allow_html=True)
    
    st.download_button(
        label="📥 Download Filled Document",
        data=st.session_state.final_docx,
        file_name="filled_document.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="upload-section" style="background-color: #06FFA5;">', unsafe_allow_html=True)
    st.markdown('<h3>🔍 Section 5: Verification (Optional)</h3>', unsafe_allow_html=True)
    
    with st.expander("📝 View Extracted OCR Text"):
        st.text_area(
            "Full extracted text from all PDF pages:",
            value=st.session_state.extracted_text,
            height=300,
            key="ocr_text"
        )
    
    with st.expander("🗺️ View JSON Mapping"):
        st.json(st.session_state.json_mapping)
    
    st.markdown('</div>', unsafe_allow_html=True)
else:
    if not template_file:
        st.markdown(
            '<div class="warning-box">⚠️ Please upload a DOCX template to begin</div>',
            unsafe_allow_html=True
        )
    if not pdf_files:
        st.markdown(
            '<div class="warning-box">⚠️ Please upload at least one PDF report to begin</div>',
            unsafe_allow_html=True
        )
