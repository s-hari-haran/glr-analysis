# Insurance GLR Auto-Filler

## Overview

This is a Streamlit-based document automation application that processes insurance and medical reports. The system extracts text from PDF photo reports using OCR, intelligently maps the extracted data to template placeholders using AI, and generates filled DOCX documents automatically. It leverages Google's Gemini AI for both vision-based OCR and intelligent data mapping.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture

**Framework:** Streamlit web application with a neo-brutalism design theme
- Bold, high-contrast UI with thick borders and flat shadows
- Wide layout configuration for better document viewing
- Multi-step workflow: template upload → PDF upload → processing → download

**Design Pattern:** Single-page application with sequential processing steps
- Upload section for DOCX template (single file)
- Upload section for PDF photo reports (multiple files supported)
- Unified "Analyze & Generate" action button
- Progress feedback during OCR, LLM processing, and template filling
- Download interface for completed documents

### Backend Architecture

**Processing Pipeline:**
1. **PDF Processing** (`pdf_processor.py`)
   - Converts PDF files to images using pdf2image library
   - Handles multiple PDF files, extracting all pages as PIL Image objects
   - Enables page-by-page OCR processing

2. **OCR Layer** (`gemini_ocr.py`)
   - Uses Gemini 2.5 Flash vision model for text extraction
   - Processes each image individually, extracting all readable text
   - Combines multi-page results into unified text corpus
   - Optimized for insurance and medical document formats

3. **AI Mapping** (`gemini_mapper.py`)
   - Uses Gemini LLM to intelligently match extracted text to template placeholders
   - JSON-based mapping output for structured data handling
   - Handles missing values gracefully with empty string fallbacks
   - Ensures exact placeholder name matching without delimiter artifacts

4. **Template Processing** (`template_processor.py`)
   - Extracts placeholders from DOCX templates using regex pattern `{{placeholder}}`
   - Searches both paragraph text and table cells
   - Replaces placeholders while preserving document formatting
   - Handles complex cases where placeholders span multiple runs in the DOCX structure

**Architecture Choice Rationale:**
- **Modular design:** Separates concerns (PDF→Image, Image→Text, Text→Mapping, Mapping→Document) for maintainability
- **Stateless processing:** Each request processes independently, simplifying deployment
- **AI-first approach:** Leverages Gemini for both OCR and intelligent mapping instead of rule-based extraction, providing flexibility for varied document formats

### Data Flow

1. User uploads template DOCX → placeholder extraction
2. User uploads PDF reports → conversion to images
3. Images processed through Gemini Vision → extracted text
4. Extracted text + placeholders sent to Gemini LLM → JSON mapping
5. Mapping applied to template → filled DOCX generated
6. User downloads completed document

## External Dependencies

### Third-Party APIs
- **Google Gemini API:** 
  - Model: gemini-2.5-flash (for both vision and text processing)
  - Purpose: OCR from images and intelligent data mapping
  - Authentication: API key required (stored as GEMINI_API_KEY secret)

### Python Libraries
- **streamlit:** Web application framework
- **google-genai:** Official Google Generative AI Python SDK
- **python-docx:** DOCX file manipulation and template processing
- **pdf2image:** PDF to image conversion (requires poppler system dependency)
- **Pillow (PIL):** Image processing and manipulation

### System Dependencies
- **poppler:** Required by pdf2image for PDF rendering

### Configuration Requirements
- Gemini API key must be provided (via GEMINI_API_KEY secret)
- No database required (stateless processing)
- No authentication system (single-user or public access model)

## Implementation Status

### Completed Features (MVP)
- ✅ Neo-brutalist UI with bold colors, thick borders, and blocky components
- ✅ DOCX template upload with automatic placeholder detection (`{{PLACEHOLDER}}` pattern)
- ✅ Multiple PDF photo report uploads with pdf2image conversion
- ✅ Gemini Vision OCR (gemini-2.5-flash) for text extraction from images
- ✅ Gemini LLM intelligent mapping of extracted text to placeholders
- ✅ Automated DOCX template filling with extracted values
- ✅ Progress indicators for OCR, LLM mapping, and template filling stages
- ✅ Download button for final filled DOCX document
- ✅ Optional expandable sections for OCR text and JSON mapping verification
- ✅ Session state management for re-runs
- ✅ PDF file rewinding for multiple processing runs

### Known Limitations

**Template Formatting Preservation:**
- Placeholders entirely within a single run: ✅ Perfect formatting preservation (recommended)
- Placeholders split across multiple runs: ⚠️ Functional replacement with partial formatting loss
  - The split-run fallback collapses the placeholder span into a single run
  - Hyperlinks and fine-grained character styling within the placeholder span may be lost
  - Replacement text inherits formatting from the first run of the original placeholder
  - This is an acceptable compromise for MVP scope
  - Future enhancement: Surgical replacement of only the placeholder span

**Recommendation:** Design templates with placeholders entirely within single runs for best results.

## Recent Changes

**2025-01-25:** Initial MVP implementation completed
- Implemented modular backend architecture with separate processors for PDF, OCR, mapping, and template filling
- Created hybrid placeholder replacement approach: perfect for single-run, functional fallback for split-run
- Fixed critical bugs: PDF file rewinding, session state reset, split-run placeholder handling
- Deployed neo-brutalist UI with custom CSS styling