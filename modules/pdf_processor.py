import io
from pdf2image import convert_from_bytes
from PIL import Image
from typing import List


def convert_pdf_to_images(pdf_bytes: bytes) -> List[Image.Image]:
    """
    Convert PDF bytes to a list of PIL images.
    
    Args:
        pdf_bytes: PDF file content as bytes
        
    Returns:
        List of PIL Image objects, one per page
    """
    try:
        images = convert_from_bytes(pdf_bytes)
        return images
    except Exception as e:
        raise Exception(f"Failed to convert PDF to images: {str(e)}")


def process_multiple_pdfs(pdf_files) -> List[Image.Image]:
    """
    Process multiple PDF files and return all images.
    
    Args:
        pdf_files: List of uploaded PDF file objects
        
    Returns:
        List of all PIL Image objects from all PDFs
    """
    all_images = []
    
    for pdf_file in pdf_files:
        pdf_file.seek(0)
        pdf_bytes = pdf_file.read()
        images = convert_pdf_to_images(pdf_bytes)
        all_images.extend(images)
        
    return all_images
