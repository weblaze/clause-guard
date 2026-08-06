import pdfplumber
import pytesseract
import os


class OCRService:
    def __init__(self):
        # Tesseract path will be handled by environment variables in Cloud
        self.tesseract_cmd = os.getenv("TESSERACT_PATH", "tesseract")
        pytesseract.pytesseract.tesseract_cmd = self.tesseract_cmd

    def extract_text_from_file(self, file_path: str) -> str:
        """Extract text from a local PDF file, falling back to OCR for scanned pages."""
        full_text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text and page_text.strip():
                    full_text += page_text + "\n"
                else:
                    # Fallback for scanned pages
                    img = page.to_image(resolution=300).original
                    full_text += pytesseract.image_to_string(img) + "\n"

        return full_text

    def is_tesseract_available(self) -> bool:
        """Verify Tesseract configuration."""
        try:
            pytesseract.get_tesseract_version()
            return True
        except Exception:
            return False
