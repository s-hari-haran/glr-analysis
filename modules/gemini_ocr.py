import io
import os
from PIL import Image
from google import genai
from google.genai import types
from typing import List


def extract_text_from_image(image: Image.Image, api_key: str) -> str:
    """
    Extract text from a single image using Gemini Vision.
    
    Args:
        image: PIL Image object
        api_key: Gemini API key
        
    Returns:
        Extracted text as string
    """
    try:
        client = genai.Client(api_key=api_key)
        
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='PNG')
        img_bytes = img_byte_arr.getvalue()
        
        prompt = """Extract all readable text from this insurance or medical document page.
Return plain text only. No explanations. No headings. Just the raw interpreted text."""
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                types.Part.from_bytes(
                    data=img_bytes,
                    mime_type="image/png",
                ),
                prompt
            ],
        )
        
        return response.text if response.text else ""
        
    except Exception as e:
        raise Exception(f"Failed to extract text from image: {str(e)}")


def extract_text_from_images(images: List[Image.Image], api_key: str) -> str:
    """
    Extract text from multiple images and combine into one string.
    
    Args:
        images: List of PIL Image objects
        api_key: Gemini API key
        
    Returns:
        Combined extracted text from all images
    """
    all_text = []
    
    for idx, image in enumerate(images):
        text = extract_text_from_image(image, api_key)
        if text:
            all_text.append(f"--- Page {idx + 1} ---\n{text}")
    
    return "\n\n".join(all_text)
