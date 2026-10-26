import importlib.util
import tempfile
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('update_news', ROOT / 'scripts' / 'update_news.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class TestNews(unittest.TestCase):
    def test_parse(self):
        result = mod.parse_rss((ROOT / 'tests' / 'example-feed.xml').read_bytes(), 'TEST')
        self.assertEqual(len(result), 3)
        self.assertTrue(all(item['source'] == 'TEST' for item in result))

    def test_generate_json(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / 'headlines.json'
            mod.write_json(target, [{'title': 'Example headline', 'source': 'TEST'}])
            import json
            content = json.loads(target.read_text(encoding='utf-8'))
            self.assertFalse(content['demo'])
            self.assertEqual(content['headlines'][0]['title'], 'Example headline')
            self.assertIn('Z', content['updated_at'])

if __name__ == '__main__':
    unittest.main()
