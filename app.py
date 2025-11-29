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
from modules.intelligent_filler import fill_template_with_intelligent_content


st.set_page_config(
    page_title="Insurance GLR Auto-Filler",
    page_icon="📋",
    layout="wide"
)

neo_brutal_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@700&display=swap');
    
    * {
        font-family: 'Space Grotesk', sans-serif;
    }
    
    [data-testid="stAppViewContainer"] {
        background-color: #1a1a1a;
        color: #ffffff;
    }
    
    [data-testid="stHeader"] {
        background-color: #000000;
    }
    
    .main-title {
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
        text-align: center;
        display: block;
    }
    
    .upload-section-wrapper {
        border: 5px solid #000000;
        padding: 25px;
        margin: 20px 0;
        background-color: #8338EC;
        box-shadow: 6px 6px 0px #000000;
    }
    
    .upload-section-wrapper h3 {
        color: #FFFFFF;
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 700;
        font-size: 1.8rem;
        margin-bottom: 15px;
        margin-top: 0;
    }
    
    .process-section-wrapper {
        border: 5px solid #000000;
        padding: 25px;
        margin: 20px 0;
        background-color: #FB5607;
        box-shadow: 6px 6px 0px #000000;
    }
    
    .process-section-wrapper h3 {
        color: #FFFFFF;
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 700;
        font-size: 1.8rem;
        margin-bottom: 15px;
        margin-top: 0;
    }
    
    .info-box {
        border: 4px solid #000000;
        padding: 15px;
        margin: 10px 0;
        background-color: #06FFA5;
        box-shadow: 4px 4px 0px #000000;
        font-weight: 600;
        color: #000000;
    }
    
    .warning-box {
        border: 4px solid #000000;
        padding: 15px;
        margin: 10px 0;
        background-color: #FFD60A;
        box-shadow: 4px 4px 0px #000000;
        font-weight: 600;
        color: #000000;
    }
    
    .success-box {
        border: 4px solid #000000;
        padding: 15px;
        margin: 10px 0;
        background-color: #06FFA5;
        box-shadow: 4px 4px 0px #000000;
        font-weight: 600;
        color: #000000;
    }
    
    .error-box {
        border: 4px solid #000000;
        padding: 15px;
        margin: 10px 0;
        background-color: #FF006E;
        box-shadow: 4px 4px 0px #000000;
        font-weight: 600;
        color: #FFFFFF;
    }
</style>
"""

st.markdown(neo_brutal_css, unsafe_allow_html=True)

st.markdown('<div class="main-title">📋 Insurance GLR Auto-Filler</div>', unsafe_allow_html=True)

api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    st.markdown(
        '<div class="error-box">⚠️ GEMINI_API_KEY not found! Please add it in the Secrets tab.</div>',
        unsafe_allow_html=True
    )
    st.stop()

st.markdown('<div class="upload-section-wrapper"><h3>📄 Section 1: Upload Template (.docx)</h3>', unsafe_allow_html=True)
template_file = st.file_uploader(
    "Upload your DOCX template with placeholders like {{NAME}}, {{AGE}}, etc.",
    type=['docx'],
    key="template"
)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="upload-section-wrapper"><h3>📑 Section 2: Upload Photo Reports (.pdf)</h3>', unsafe_allow_html=True)
pdf_files = st.file_uploader(
    "Upload one or more PDF files containing scanned insurance/medical documents",
    type=['pdf'],
    accept_multiple_files=True,
    key="pdfs"
)
st.markdown('</div>', unsafe_allow_html=True)

if template_file and pdf_files:
    st.markdown('<div class="process-section-wrapper"><h3>⚡ Section 3: Process Documents</h3>', unsafe_allow_html=True)
    
    if st.button("🚀 Analyze & Generate Filled Docx", key="process_btn"):
        
        st.session_state.extracted_text = None
        st.session_state.json_mapping = None
        st.session_state.final_docx = None
        st.session_state.template_bytes = None
        
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
                '<div class="info-box">📋 Step 3/6: Loading template and extracting placeholders...</div>',
                unsafe_allow_html=True
            )
            template_file.seek(0)
            template_bytes = template_file.read()
            st.session_state.template_bytes = template_bytes
            
            doc = load_template(template_bytes)
            placeholders = extract_placeholders(doc)
            st.markdown(
                f'<div class="success-box">✅ Found {len(placeholders)} placeholders: {", ".join(placeholders)}</div>',
                unsafe_allow_html=True
            )
            
            st.markdown(
                '<div class="info-box">🤖 Step 4/6: Mapping extracted text to placeholders...</div>',
                unsafe_allow_html=True
            )
            mapping = map_placeholders_to_values(extracted_text, placeholders, api_key)
            st.session_state.json_mapping = mapping
            st.markdown(
                '<div class="success-box">✅ Successfully mapped placeholders to values</div>',
                unsafe_allow_html=True
            )
            
            st.markdown(
                '<div class="info-box">✍️ Step 5/6: Filling template with extracted values...</div>',
                unsafe_allow_html=True
            )
            filled_doc = fill_docx_template(doc, mapping)
            st.markdown(
                '<div class="success-box">✅ Placeholder values filled</div>',
                unsafe_allow_html=True
            )
            
            st.markdown(
                '<div class="info-box">🤖 Step 6/6: Intelligently cleaning template instructions and filling remaining content...</div>',
                unsafe_allow_html=True
            )
            
            # Get the text from the partially-filled document to pass to intelligent filler
            partial_text = "\n".join([p.text for p in filled_doc.paragraphs])
            
            # Use Gemini to intelligently replace remaining template instructions with actual content
            try:
                cleaned_text = fill_template_with_intelligent_content(
                    partial_text, 
                    extracted_text, 
                    api_key
                )
                st.session_state.cleaned_text = cleaned_text
                st.markdown(
                    '<div class="success-box">✅ Template instructions cleaned and filled with actual content</div>',
                    unsafe_allow_html=True
                )
                
                # Now replace the paragraphs in the document with the cleaned text
                # This preserves formatting while updating content
                cleaned_lines = cleaned_text.split('\n')
                para_idx = 0
                for line in cleaned_lines:
                    if para_idx < len(filled_doc.paragraphs):
                        filled_doc.paragraphs[para_idx].text = line
                    para_idx += 1
                    
            except Exception as e:
                st.markdown(
                    f'<div class="warning-box">⚠️ Intelligent cleanup skipped: {str(e)}</div>',
                    unsafe_allow_html=True
                )
                # Continue with just the placeholder-filled version
            
            final_bytes = save_document(filled_doc, mapping)
            st.session_state.final_docx = final_bytes
            st.markdown(
                '<div class="success-box">🎉 Document complete and ready!</div>',
                unsafe_allow_html=True
            )
            # Run LLM validation (non-blocking if API unavailable)
            from modules.llm_validator import validate_filled_docx_bytes
            try:
                validation = validate_filled_docx_bytes(final_bytes, mapping, api_key)
                st.session_state.validation = validation
            except Exception as e:
                st.session_state.validation = {"status":"error","issues":[str(e)]}
            
        except Exception as e:
            st.markdown(
                f'<div class="error-box">❌ Error: {str(e)}</div>',
                unsafe_allow_html=True
            )
    
    st.markdown('</div>', unsafe_allow_html=True)

if st.session_state.get('final_docx'):
    st.markdown('<div class="upload-section-wrapper"><h3>💾 Section 4: Download Result</h3>', unsafe_allow_html=True)
    
    st.download_button(
        label="📥 Download Filled Document",
        data=st.session_state.final_docx,
        file_name="filled_document.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="upload-section-wrapper"><h3>🔍 Section 5: Verification (Optional)</h3>', unsafe_allow_html=True)
    
    with st.expander("📝 View Extracted OCR Text"):
        st.text_area(
            "Full extracted text from all PDF pages:",
            value=st.session_state.extracted_text,
            height=300,
            key="ocr_text"
        )
    
    with st.expander("🗺️ View JSON Mapping"):
        # Show editable mapping so user can tweak before re-filling
        mapping_json = st.session_state.get('json_mapping') or {}
        import json
        mapping_text = json.dumps(mapping_json, indent=2)
        edited = st.text_area("Edit mapping JSON (modify values or keys)", value=mapping_text, height=300)

        cols = st.columns([1,1,2])
        if cols[0].button("Load example mapping"):
            # Example mapping derived from user's example
            example = {
                "DATE_LOSS": "9/28/2024",
                "INSURED_NAME": "Richard Daly",
                "INSURED_H_STREET": "392 HEATH ST",
                "INSURED_H_CITY": "BAXLEY",
                "INSURED_H_STATE": "GA",
                "INSURED_H_ZIP": "31513-9214",
                "DATE_INSPECTED": "11/13/2024",
                "MORTGAGEE": "PennyMac",
                "TOL_CODE": "WIND",
                "CONTENTS_LOSS": "$500"
            }
            st.session_state.json_mapping = example
            edited = json.dumps(example, indent=2)

        if cols[1].button("Apply mapping & Re-fill"):
            try:
                new_mapping = json.loads(edited)
                st.session_state.json_mapping = new_mapping
                # Re-fill using persisted template bytes
                if st.session_state.get('template_bytes'):
                    doc = load_template(st.session_state.template_bytes)
                    filled_doc = fill_docx_template(doc, new_mapping)
                    final_bytes = save_document(filled_doc, new_mapping)
                    st.session_state.final_docx = final_bytes
                    st.success("Re-filled template with edited mapping. Download updated file below.")
                else:
                    st.error("Template bytes not found. Re-upload the template and try again.")
            except Exception as e:
                st.error(f"Failed to apply mapping: {str(e)}")

        # Show validation result if present
        validation = st.session_state.get('validation')
        if validation:
            st.markdown('**LLM Validation Result:**')
            st.write(validation.get('status'))
            if validation.get('issues'):
                st.markdown('**Issues:**')
                for it in validation.get('issues', []):
                    st.write('-', it)

            # Offer to apply suggested mapping if provided
            suggested = validation.get('suggested_mapping') or {}
            if suggested:
                if st.button('Apply LLM suggested mapping'):
                    st.session_state.json_mapping.update(suggested)
                    # Re-fill with suggested mapping
                    doc = load_template(st.session_state.template_bytes)
                    filled_doc = fill_docx_template(doc, st.session_state.json_mapping)
                    final_bytes = save_document(filled_doc, st.session_state.json_mapping)
                    st.session_state.final_docx = final_bytes
                    st.success('Applied LLM suggested mapping and re-filled document.')

            suggested_edits = validation.get('suggested_text_edits') or {}
            if suggested_edits:
                if st.button('Apply LLM suggested text edits'):
                    # Apply text edits directly to the saved docx bytes
                    from modules.template_processor import apply_text_edits_to_docx_bytes
                    cur = st.session_state.get('final_docx')
                    try:
                        new_bytes = apply_text_edits_to_docx_bytes(cur, suggested_edits)
                        st.session_state.final_docx = new_bytes
                        st.success('Applied suggested text edits. Download updated file below.')
                    except Exception as e:
                        st.error(f'Failed to apply LLM text edits: {str(e)}')

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
