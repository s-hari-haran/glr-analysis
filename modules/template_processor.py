import re
from docx import Document
from typing import List, Dict
import io


def extract_placeholders(doc: Document) -> List[str]:
    """
    Extract all placeholders from a DOCX document.
    
    Args:
        doc: python-docx Document object
        
    Returns:
        List of unique placeholder names (without {{ }})
    """
    placeholders = set()
    
    # Support both {{KEY}} and [KEY] placeholder styles
    placeholder_pattern = re.compile(r"{{(.*?)}}|\[(.*?)\]")

    for paragraph in doc.paragraphs:
        matches = placeholder_pattern.findall(paragraph.text)
        # matches is list of tuples because of alternation; pick the non-empty group
        for a, b in matches:
            name = (a or b)
            if name is not None:
                placeholders.add(name.strip())
    
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    matches = placeholder_pattern.findall(paragraph.text)
                    for a, b in matches:
                        name = (a or b)
                        if name is not None:
                            placeholders.add(name.strip())
    
    return sorted(list(placeholders))


def fill_docx_template(doc: Document, mapping: Dict[str, str]) -> Document:
    """
    Fill DOCX template by replacing placeholders with values.
    Handles cases where placeholders are split across multiple runs while preserving formatting.
    
    Args:
        doc: python-docx Document object
        mapping: Dictionary mapping placeholder names to values
        
    Returns:
        Modified Document object
    """
    def replace_paragraph_placeholders(paragraph, mapping):
        """Replace placeholders in a paragraph, preserving formatting where possible."""
        
        replaced_in_runs = False
        for run in paragraph.runs:
            run_changed = False
            run_text = run.text
            for key, value in mapping.items():
                k = str(key).strip()
                # Support both `{{KEY}}`, `{{ KEY }}` and `[KEY]`, `[ KEY ]` styles in runs
                placeholder_c = f"{{{{{k}}}}}"
                placeholder_c_spaced = f"{{{{ {k} }}}}"
                placeholder_b = f"[{k}]"
                placeholder_b_spaced = f"[ {k} ]"
                if placeholder_c in run_text or placeholder_c_spaced in run_text or placeholder_b in run_text or placeholder_b_spaced in run_text:
                    run_text = run_text.replace(placeholder_c, str(value))
                    run_text = run_text.replace(placeholder_c_spaced, str(value))
                    run_text = run_text.replace(placeholder_b, str(value))
                    run_text = run_text.replace(placeholder_b_spaced, str(value))
                    run_changed = True
            if run_changed:
                run.text = run_text
                replaced_in_runs = True
        
        if replaced_in_runs:
            return
        
        original_text = paragraph.text
        replaced_text = original_text
        for key, value in mapping.items():
            k = str(key).strip()
            placeholder_c = f"{{{{{k}}}}}"
            placeholder_c_spaced = f"{{{{ {k} }}}}"
            placeholder_b = f"[{k}]"
            placeholder_b_spaced = f"[ {k} ]"
            replaced_text = replaced_text.replace(placeholder_c, str(value))
            replaced_text = replaced_text.replace(placeholder_c_spaced, str(value))
            replaced_text = replaced_text.replace(placeholder_b, str(value))
            replaced_text = replaced_text.replace(placeholder_b_spaced, str(value))
        
        if replaced_text == original_text:
            return
        
        runs = list(paragraph.runs)
        if not runs:
            paragraph.add_run(replaced_text)
            return
        
        first_run_format = runs[0]
        
        for i in range(len(runs) - 1, -1, -1):
            runs[i]._element.getparent().remove(runs[i]._element)
        
        new_run = paragraph.add_run(replaced_text)
        new_run.bold = first_run_format.bold
        new_run.italic = first_run_format.italic
        new_run.underline = first_run_format.underline
        if first_run_format.style:
            new_run.style = first_run_format.style
        if first_run_format.font.size:
            new_run.font.size = first_run_format.font.size
        if first_run_format.font.name:
            new_run.font.name = first_run_format.font.name
        if first_run_format.font.color.rgb:
            new_run.font.color.rgb = first_run_format.font.color.rgb
    
    for paragraph in doc.paragraphs:
        replace_paragraph_placeholders(paragraph, mapping)
    
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    replace_paragraph_placeholders(paragraph, mapping)
    
    return doc


def load_template(file_bytes: bytes) -> Document:
    """
    Load a DOCX template from bytes.
    
    Args:
        file_bytes: DOCX file content as bytes
        
    Returns:
        python-docx Document object
    """
    return Document(io.BytesIO(file_bytes))


def save_document(doc: Document) -> bytes:
    """
    Save a DOCX document to bytes.
    
    Args:
        doc: python-docx Document object
        
    Returns:
        DOCX file content as bytes
    """
    output = io.BytesIO()
    doc.save(output)
    return output.getvalue()
