import json
from google import genai
from typing import List, Dict


def map_placeholders_to_values(
    extracted_text: str,
    placeholders: List[str],
    api_key: str
) -> Dict[str, str]:
    """
    Use Gemini LLM to map extracted text to placeholder values.
    
    Args:
        extracted_text: Text extracted from PDFs via OCR
        placeholders: List of placeholder names from template
        api_key: Gemini API key
        
    Returns:
        Dictionary mapping placeholder names to extracted values
    """
    response_text = ""
    try:
        client = genai.Client(api_key=api_key)
        
        prompt = f"""From the extracted report text below, fill values for each placeholder.
Here are the placeholders: {placeholders}

Return a VALID JSON object ONLY, mapping each placeholder name to its correct extracted value.

If a value is missing, return an empty string.

JSON keys MUST match placeholders EXACTLY and MUST NOT include curly braces.

Extracted text:
{extracted_text}

Return only the JSON object, no other text."""
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        
        if not response.text:
            raise Exception("Empty response from Gemini")
        
        response_text = response.text.strip()
        
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        
        response_text = response_text.strip()
        
        mapping = json.loads(response_text)
        
        final_mapping = {}
        for placeholder in placeholders:
            final_mapping[placeholder] = mapping.get(placeholder, "")
        
        return final_mapping
        
    except json.JSONDecodeError as e:
        raise Exception(f"Failed to parse JSON response from Gemini: {str(e)}\nResponse: {response_text}")
    except Exception as e:
        raise Exception(f"Failed to map placeholders: {str(e)}")
