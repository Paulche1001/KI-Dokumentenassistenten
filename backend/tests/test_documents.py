import unittest
from unittest.mock import patch

import pymupdf
from fastapi.testclient import TestClient

from app.main import app


def make_pdf(*texts: str, password: str | None = None) -> bytes:
    """Erzeugt kleine Test-PDFs im Speicher, ohne private Dokumente einzuchecken."""
    with pymupdf.open() as document:
        for text in texts:
            page = document.new_page()
            if text:
                page.insert_text((72, 72), text)
        if password:
            return document.tobytes(
                encryption=pymupdf.PDF_ENCRYPT_AES_256,
                owner_pw=password,
                user_pw=password,
            )
        return document.tobytes()


class DocumentUploadTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.addCleanup(self.client.close)

    def upload(self, content: bytes, filename: str = "example.pdf"):
        return self.client.post(
            "/api/documents/extract", files={"file": (filename, content, "application/pdf")}
        )

    def test_extracts_pages_and_preserves_source_numbers(self):
        response = self.upload(make_pdf("First page", "Second page"))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["filename"], "example.pdf")
        self.assertEqual(data["page_count"], 2)
        self.assertEqual(data["pages"], [
            {"page_number": 1, "text": "First page"},
            {"page_number": 2, "text": "Second page"},
        ])
        self.assertEqual(data["warnings"], [])

    def test_empty_middle_page_keeps_following_source_number(self):
        response = self.upload(make_pdf("First", "", "Third"))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["pages"][1], {"page_number": 2, "text": ""})
        self.assertEqual(data["pages"][2]["page_number"], 3)
        self.assertIn("2", data["warnings"][0])

    def test_pdf_without_text_explains_ocr_limitation(self):
        response = self.upload(make_pdf(""))
        self.assertEqual(response.status_code, 422)
        self.assertIn("OCR", response.json()["detail"])

    def test_password_protected_pdf_is_rejected(self):
        response = self.upload(make_pdf("Secret", password="test-password"))
        self.assertEqual(response.status_code, 422)
        self.assertIn("passwortgeschützt", response.json()["detail"])

    def test_non_pdf_extension_is_rejected(self):
        self.assertEqual(self.upload(b"plain text", "notes.txt").status_code, 415)

    def test_fake_pdf_is_rejected(self):
        self.assertEqual(self.upload(b"This is not a PDF").status_code, 422)

    def test_image_renamed_to_pdf_is_rejected(self):
        with pymupdf.open(stream=make_pdf("Image"), filetype="pdf") as document:
            image = document[0].get_pixmap().tobytes("png")
        self.assertEqual(self.upload(image).status_code, 422)

    def test_empty_upload_is_rejected(self):
        self.assertEqual(self.upload(b"").status_code, 422)

    def test_missing_upload_is_rejected(self):
        self.assertEqual(self.client.post("/api/documents/extract").status_code, 422)

    def test_size_limit_is_enforced(self):
        with patch("app.api.documents.MAX_UPLOAD_BYTES", 100):
            self.assertEqual(self.upload(b"x" * 101).status_code, 413)

    def test_page_limit_is_enforced(self):
        with patch("app.services.pdf.MAX_PAGES", 1):
            response = self.upload(make_pdf("One", "Two"))
        self.assertEqual(response.status_code, 422)
        self.assertIn("Seiten", response.json()["detail"])

    def test_health_endpoint_still_works(self):
        self.assertEqual(self.client.get("/api/health").json(), {"status": "ok"})


if __name__ == "__main__":
    unittest.main()
