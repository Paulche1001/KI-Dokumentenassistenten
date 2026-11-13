import unittest

from app.schemas.documents import DocumentPage
from app.services.chunking import chunk_pages
from app.services.chunking import split_text


class ChunkingTests(unittest.TestCase):
    def test_empty_text_returns_empty_list(self):
        self.assertEqual(split_text("", 10, 0), [])

    def test_whitespace_returns_empty_list(self):
        self.assertEqual(split_text("  \n\t ", 10, 0), [])

    def test_zero_chunk_size_is_rejected(self):
        with self.assertRaises(ValueError):
            split_text("Hallo", 0, 0)

    def test_overlap_equal_to_chunk_size_is_rejected(self):
        with self.assertRaises(ValueError):
            split_text("Hallo", 10, 10)

    def test_splits_text_with_overlap(self):
        text = "Eins zwei drei vier fünf sechs"
        self.assertEqual(split_text(text, 15, 4), [
            "Eins zwei drei",
            "drei vier fünf",
            "fünf sechs"
        ])

    def test_chunks_keep_original_page_numbers(self):
        pages = [
            DocumentPage(page_number=1, text="Hallo"),
            DocumentPage(page_number=2, text=""),
            DocumentPage(page_number=3, text="Welt"),
        ]
        chunks = chunk_pages(pages, 10, 0)
        self.assertEqual(len(chunks), 2)
        self.assertEqual(chunks[0].page_number, 1)
        self.assertEqual(chunks[1].page_number, 3)
        self.assertEqual([chunk.chunk_index for chunk in chunks], [0, 1])