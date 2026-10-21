import os
import unittest

os.environ["LANGSMITH_TRACING"] = "false"

from backend.app.llm import ModelError, extract_web_answer


class ExploreTests(unittest.TestCase):
    def test_responses_web_output_keeps_text_and_deduplicated_citations(self):
        body = {
            "output": [
                {
                    "type": "web_search_call",
                    "action": {
                        "sources": [
                            {"title": "Company release", "url": "https://investor.example.com/release"},
                        ]
                    },
                },
                {
                    "type": "message",
                    "content": [
                        {
                            "type": "output_text",
                            "text": "The current public evidence adds context without changing the report verdict.",
                            "annotations": [
                                {
                                    "type": "url_citation",
                                    "title": "Company release",
                                    "url": "https://investor.example.com/release",
                                },
                                {
                                    "type": "url_citation",
                                    "url_citation": {
                                        "title": "Regulator filing",
                                        "url": "https://regulator.example.gov/filing",
                                    },
                                },
                            ],
                        }
                    ],
                },
            ]
        }

        answer, sources = extract_web_answer(body)

        self.assertIn("without changing the report verdict", answer)
        self.assertEqual(len(sources), 2)
        self.assertEqual(sources[0]["title"], "Company release")
        self.assertEqual(sources[1]["url"], "https://regulator.example.gov/filing")

    def test_responses_web_output_fails_closed_without_citations(self):
        body = {"output": [{"type": "message", "content": [{"type": "output_text", "text": "Unsupported answer", "annotations": []}]}]}

        with self.assertRaises(ModelError):
            extract_web_answer(body)

    def test_inline_markdown_links_become_ordered_source_markers(self):
        body = {
            "output": [
                {
                    "type": "message",
                    "content": [
                        {
                            "type": "output_text",
                            "text": "A [company release](https://example.com/release) supports the claim.",
                            "annotations": [],
                        }
                    ],
                }
            ]
        }

        answer, sources = extract_web_answer(body)

        self.assertEqual(answer, "A company release [1] supports the claim.")
        self.assertEqual(sources, [{"title": "company release", "url": "https://example.com/release"}])


if __name__ == "__main__":
    unittest.main()
