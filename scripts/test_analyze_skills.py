"""Regression checks for misleading text extraction, without model dependencies."""
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from analyze_skills import clean_text, tokens, shingles, fetch_entry


class ExtractionTests(unittest.TestCase):
    def test_frontmatter_and_code_cannot_create_false_shared_advice(self):
        source = '''---
name: unrelated
---
Never remove a meaningful qualification from prose.
```yaml
repeated framework installation instructions everywhere
```
Keep [source attribution](https://example.com/original) when revising a claim.
'''
        cleaned = clean_text(source)
        self.assertNotIn('unrelated', cleaned)
        self.assertNotIn('installation', cleaned)
        self.assertNotIn('https', cleaned)
        self.assertIn('Never remove', cleaned)
        self.assertIn('source attribution', cleaned)

    def test_opposite_instructions_remain_different(self):
        self.assertNotEqual(tokens(clean_text('Use passive voice when the actor is irrelevant.')),
                            tokens(clean_text('Never use passive voice when the actor is irrelevant.')))
        self.assertIn('never', tokens(clean_text('Never use passive voice when the actor is irrelevant.')))

    def test_shingles_do_not_invent_cross_paragraph_quotations(self):
        self.assertEqual(shingles('one two three\nfour five six'), set())
        self.assertEqual(shingles('one two three four five\nsix seven eight nine ten'),
                         {'one two three four five', 'six seven eight nine ten'})

    def test_corrupt_cached_source_is_excluded_before_analysis(self):
        with TemporaryDirectory() as folder:
            expected = '0' * 64
            (Path(folder) / (expected + '.txt')).write_text('Modified source, not the pinned original.')
            source, error = fetch_entry({'id': 'test/skill', 'source_sha256': expected}, Path(folder))
        self.assertIsNone(source)
        self.assertIn('checksum mismatch', error['reason'])


if __name__ == '__main__':
    unittest.main()
