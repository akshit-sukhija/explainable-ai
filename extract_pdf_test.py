import unittest
import os
from pypdf import PdfWriter
from extract_pdf_text import extract_text_from_pdf

class TestPDFExtraction(unittest.TestCase):
    def setUp(self):
        self.test_pdf = "test_sample.pdf"
        self.writer = PdfWriter()
        self.writer.add_blank_page(width=72, height=72)
        with open(self.test_pdf, "wb") as f:
            self.writer.write(f)

    def tearDown(self):
        if os.path.exists(self.test_pdf):
            os.remove(self.test_pdf)

    def test_extract_text(self):
        # Since we created a blank PDF, text should be empty or minimal
        # This mostly tests that the function runs without error on a valid file
        text = extract_text_from_pdf(self.test_pdf)
        self.assertIsInstance(text, str)

if __name__ == "__main__":
    unittest.main()
