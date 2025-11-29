"""
Intelligent template content filler using Gemini LLM.
This module takes a template with generic/boilerplate text and fills it with 
actual report content extracted from OCR or provided text.
"""

from google import genai
from typing import Dict, List
import re


def fill_template_with_intelligent_content(
    template_text: str,
    extracted_report_text: str,
    api_key: str
) -> str:
    """
    Use Gemini to intelligently clean up template instructions and fill with actual data.
    This works AFTER placeholder replacement - focuses on removing generic options/instructions.
    
    Args:
        template_text: The template/partial document text (placeholders already replaced)
        extracted_report_text: The actual report text extracted from OCR or documents
        api_key: Gemini API key
        
    Returns:
        Cleaned report text with template instructions replaced by actual content
    """
    
    client = genai.Client(api_key=api_key)
    
    prompt = f"""You are an insurance report specialist. I have a partially-filled insurance report (placeholders already replaced with actual names/dates/addresses).
However, the report still contains template instructions, unused sections, and "Choose an item." dropdown placeholders that need to be cleaned up and filled with actual content.

CURRENT REPORT (with some content filled, but many template instructions still present):
{template_text}

ACTUAL INSPECTION DATA (use this to determine relevance and fill content):
{extracted_report_text}

Your critical tasks:
1. **REMOVE IRRELEVANT SECTIONS**: Delete entire sections that don't apply to this loss. For example:
   - If loss is vehicle damage, remove roof damage sections, hail/wind damage sections, tree damage sections
   - If there's no water damage, remove sections about interior water damage
   - If no salvage potential is mentioned, keep only "does not appear to be any salvage potential"
   - Remove duplicate/repeated sections (I see sections repeated multiple times)
   
2. **REMOVE "Choose an item." PLACEHOLDERS**: Replace with actual values or delete the entire line if not applicable

3. **FILL GENERIC OPTIONS** in parentheses like:
   - (one story, raised ranch...) → actual building type
   - (25 year 3-tab, 30 year laminate...) → actual roof type
   - (wind, hail, tree, vehicle...) → actual damage type
   - (all, dwelling, garage...) → applicable structure
   
4. **REMOVE TEMPLATE INSTRUCTIONS** like:
   - (Name whom you spoke with and verified mortgagee information)
   - (Be sure to describe...)
   - (Put "N/A" if...)
   - Instructional text in angle brackets <...>
   
5. **CONSOLIDATE DUPLICATE SECTIONS**: Remove repeated paragraphs/sections

6. **CLEAN UP SPACING**: Remove extra blank lines while preserving structure

7. **KEEP PROFESSIONAL FORMAT**: Maintain section headings and structure

IMPORTANT: 
- Only include sections relevant to THIS specific loss
- Remove/hide sections that clearly don't apply
- Replace all "Choose an item." with actual values OR delete the entire sentence if not applicable
- Keep the report concise and professional

Return ONLY the cleaned/filled report text. Do not add any explanation or meta-commentary."""

    response = client.models.generate_content(
        model="gemini-2.0-flash-001",
        contents=prompt
    )
    
    if not response.text:
        raise Exception("Empty response from Gemini for intelligent content fill")
    
    return response.text.strip()


def extract_sections_from_report(report_text: str) -> Dict[str, str]:
    """
    Extract key sections from a report text for structured data extraction.
    
    Args:
        report_text: Full report text
        
    Returns:
        Dictionary with section names as keys and content as values
    """
    sections = {}
    current_section = None
    current_content = []
    
    lines = report_text.split('\n')
    
    section_headers = [
        'General Loss Report',
        'Date of Loss',
        'Insurable Interest',
        'Dwelling Description',
        'Property Condition',
        'Inspection',
        'Dwelling',
        'Roof',
        'Front Elevation',
        'Right Elevation',
        'Rear Elevation',
        'Back Elevation',
        'Left Elevation',
        'Interior',
        'Other Structures',
        'Contents',
        'Review',
        'Supplement',
        'Priors',
        'Code Items',
        'Overhead & Profit',
        'MICA/QA Assist',
        'Mortgagee Information',
        'Cause and Origin',
        'Subrogation',
        'Salvage'
    ]
    
    for line in lines:
        stripped = line.strip()
        
        # Check if this line is a section header
        is_header = False
        for header in section_headers:
            if stripped.lower() == header.lower():
                if current_section:
                    sections[current_section] = '\n'.join(current_content).strip()
                current_section = header
                current_content = []
                is_header = True
                break
        
        if not is_header and current_section:
            current_content.append(line)
    
    # Add the last section
    if current_section:
        sections[current_section] = '\n'.join(current_content).strip()
    
    return sections
