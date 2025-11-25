import io
import os
import time
import shutil
import subprocess
from PIL import Image
from google import genai
from google.genai import types
from typing import List


def _local_ocr_with_pytesseract(image: Image.Image) -> str:
    try:
        import pytesseract
        return pytesseract.image_to_string(image)
    except Exception:
        return ""


def _local_ocr_with_cli(image: Image.Image) -> str:
    # Use tesseract CLI if available
    try:
        if not shutil.which("tesseract"):
            return ""
        from tempfile import NamedTemporaryFile
        with NamedTemporaryFile(suffix=".png", delete=False) as inp:
            image.save(inp.name, format="PNG")
            inp_path = inp.name
        out_path = inp_path + "_out"
        subprocess.run(["tesseract", inp_path, out_path], check=True)
        with open(out_path + ".txt", "r", encoding="utf-8") as f:
            text = f.read()
        try:
            os.remove(inp_path)
            os.remove(out_path + ".txt")
        except Exception:
            pass
        return text
    except Exception:
        return ""


def extract_text_from_image(image: Image.Image, api_key: str) -> str:
    """
    Extract text from a single image using Gemini Vision.
    
    Args:
        image: PIL Image object
        api_key: Gemini API key
        
    Returns:
        Extracted text as string
    """
    # Try the Gemini Vision API with retries/backoff, then fall back to local OCR
    max_attempts = 3
    backoff_base = 1.5

    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format="PNG")
    img_bytes = img_byte_arr.getvalue()

    prompt = """Extract all readable text from this insurance or medical document page.
Return plain text only. No explanations. No headings. Just the raw interpreted text."""

    last_exc = None
    for attempt in range(1, max_attempts + 1):
        try:
            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[
                    types.Part.from_bytes(
                        data=img_bytes,
                        mime_type="image/png",
                    ),
                    prompt,
                ],
            )

            if response and getattr(response, "text", None):
                return response.text
            # Empty response: treat as retryable
            last_exc = Exception("Empty response from Gemini")
        except Exception as e:
            last_exc = e
            # If this is the last attempt, break and try fallback
            if attempt < max_attempts:
                sleep_time = backoff_base ** attempt
                time.sleep(sleep_time)
                continue
            # else fall through to local OCR

    # If we reach here, Gemini calls failed. Try local OCR fallbacks.
    # First try pytesseract, then tesseract CLI.
    try:
        text = _local_ocr_with_pytesseract(image)
        if text and text.strip():
            return text
    except Exception:
        pass

    try:
        text = _local_ocr_with_cli(image)
        if text and text.strip():
            return text
    except Exception:
        pass

    # Nothing worked — raise the original error (or a summarized message)
    msg = "Failed to extract text from image: " + (str(last_exc) if last_exc else "Unknown error")
    msg += (
        "\n\nLocal OCR fallback attempted but not available. To enable local OCR, install `tesseract-ocr`"
        " (system package) and the Python package `pytesseract`."
    )
    raise Exception(msg)


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
