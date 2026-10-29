import unittest
from unittest.mock import patch, MagicMock
from app import call_llm

class TestApp(unittest.TestCase):
    @patch("app.requests.post")
    def test_ok(self, mock_post):
        mock_post.return_value = MagicMock(status_code=200, json=lambda: {
            "choices": [{"message": {"content": '{"category":"bug","priority":"low","summary":"x","tags":[],"requires_human":false}'}}]
        })
        mock_post.return_value.raise_for_status.return_value = None
        self.assertEqual(call_llm("text")[0], "{")