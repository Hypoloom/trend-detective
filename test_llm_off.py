import ast
import os
import unittest

from phrase import CAUSAL, LEVELS, check_text, phrase
from router import STUB_DOMAINS, route
from tests import mocks

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class LlmOffTests(unittest.TestCase):
    def test_full_path_llm_off(self):
        plan = [("Is my pond going to get algae this summer?", "pond", mocks.pond_abstained()),
                ("Why are my oranges small?", "citrus", mocks.citrus_abstained()),
                ("What is the weather in Paris?", None, None)]
        for q, domain, result in plan:
            with self.subTest(q=q):
                r = route(q, domains=STUB_DOMAINS)
                self.assertEqual(r.domain, domain)
                if result is None:
                    self.assertIsNotNone(r.form)
                    continue
                for lvl in LEVELS:
                    text = phrase(result, lvl)
                    self.assertIn("cannot give a definite answer", text)
                    self.assertIsNone(CAUSAL.search(text))
                    self.assertTrue(check_text(text, result).ok)

    def test_non_abstained_mocks_llm_off(self):
        expect = {"no_trend": "No trend was found", "detected": "A trend was found",
                  "data_limited": "not enough data"}
        for name, needle in expect.items():
            for lvl in LEVELS:
                with self.subTest(mock=name, level=lvl):
                    self.assertIn(needle, phrase(getattr(mocks, name)(), lvl))

    def test_no_network_imports(self):
        banned = {"requests", "urllib", "urllib3", "http", "socket", "openai", "anthropic", "httpx", "aiohttp"}
        for fname in ("router.py", "phrase.py", "fallback_form.py"):
            with open(os.path.join(HERE, fname), encoding="utf-8") as f:
                tree = ast.parse(f.read())
            for node in ast.walk(tree):
                names = []
                if isinstance(node, ast.Import):
                    names = [a.name.split(".")[0] for a in node.names]
                elif isinstance(node, ast.ImportFrom) and node.module:
                    names = [node.module.split(".")[0]]
                with self.subTest(file=fname):
                    self.assertFalse(banned & set(names), names)


if __name__ == "__main__":
    unittest.main()