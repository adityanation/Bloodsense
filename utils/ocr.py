import os
import pytesseract
from PIL import Image

def get_tesseract_path():
    """Get the appropriate Tesseract path based on the environment."""
    if os.name == 'nt':  # Windows
        return r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    else:  # Linux/Unix (like Render)
        return '/usr/bin/tesseract'  # Standard Linux installation path

def extract_text_from_file(file_path):
    """Extract text from image files using Tesseract OCR."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    try:
        # Set Tesseract path based on environment
        tesseract_path = get_tesseract_path()
        if os.path.exists(tesseract_path):
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
        
        # Open and process the image
        image = Image.open(file_path)
        
        # Extract text using Tesseract
        text = pytesseract.image_to_string(image)
        
        if not text.strip():
            raise Exception("No text was extracted from the document. The file might be empty or corrupted.")
            
        return text.strip()

    except Exception as e:
        raise Exception(f"Error in OCR processing: {str(e)}") 