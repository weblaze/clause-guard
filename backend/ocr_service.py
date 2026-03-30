import requests
import pdfplumber
import pytesseract
from PIL import Image
import os
import io

class OCRService:
    def __init__(self):
        # Tesseract path will be handled by environment variables in Cloud
        self.tesseract_cmd = os.getenv("TESSERACT_PATH", "tesseract")
        pytesseract.pytesseract.tesseract_cmd = self.tesseract_cmd

    def extract_text_from_url(self, file_url: str) -> str:
        """Fetch PDF from public URL and extract text, falling back to OCR if needed."""
        try:
            response = requests.get(file_url)
            response.raise_for_status()
            pdf_data = io.BytesIO(response.content)
            
            full_text = ""
            with pdfplumber.open(pdf_data) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text and page_text.strip():
                        full_text += page_text + "\n"
                    else:
                        # Fallback for scanned pages
                        img = page.to_image(resolution=300).original
                        full_text += pytesseract.image_to_string(img) + "\n"
            
            return full_text
        except Exception as e:
            raise Exception(f"Failed to fetch or extract text from {file_url}: {str(e)}")

    def is_tesseract_available(self) -> bool:
        """Verify Tesseract configuration."""
        try:
            pytesseract.get_tesseract_version()
            return True
        except Exception:
            return False
