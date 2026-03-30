import pytesseract
import pdfplumber
from PIL import Image
import io
import os
from dotenv import load_dotenv

load_dotenv()

# Configure Tesseract path from .env
TESSERACT_CMD = os.getenv("TESSERACT_PATH", r"C:\Program Files\Tesseract-OCR\tesseract.exe")
pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD

class OCRService:
    @staticmethod
    def extract_text_from_pdf(file_path: str) -> str:
        """Extract text from PDF using pdfplumber, falling back to Tesseract OCR if no text found."""
        full_text = ""
        
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                
                if page_text and page_text.strip():
                    full_text += page_text + "\n"
                else:
                    # No text found, likely a scanned image. Use OCR.
                    # Convert page to image for Tesseract
                    img = page.to_image(resolution=300).original
                    ocr_text = pytesseract.image_to_string(img)
                    full_text += ocr_text + "\n"
                    
        return full_text

    @staticmethod
    def is_tesseract_available() -> bool:
        """Check if Tesseract is correctly configured."""
        try:
            pytesseract.get_tesseract_version()
            return True
        except Exception:
            return False
