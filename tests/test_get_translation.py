import unittest
from utils.get_translation import lookup

class TestTranslation(unittest.TestCase):
    def test_multiple_meanings(self):
        # Test words known to have multiple meanings
        test_cases = [
            ('开', ['to open', 'to start', 'to turn on', 'to boil']),  # Common verb with many meanings
            ('把', ['to hold', 'to guard', 'handle', 'classifier for objects with handles']),  # Both verb and measure word
            ('面', ['face', 'side', 'surface', 'noodles']),  # Noun with multiple meanings
            ('行', ['line', 'row', 'OK', 'capable']),  # Both noun and adjective
        ]
        
        for word, expected_meanings in test_cases:
            with self.subTest(word=word):
                translations = lookup(word)
                # Check that we got multiple translations
                self.assertGreater(len(translations), 1, 
                    f"Expected multiple translations for '{word}', but got: {translations}")
                # Check that we got at least some of the expected meanings
                found_meanings = 0
                for meaning in expected_meanings:
                    if any(meaning.lower() in trans.lower() for trans in translations):
                        found_meanings += 1
                self.assertGreater(found_meanings, 0,
                    f"Expected to find at least one of {expected_meanings} in translations for '{word}', but got: {translations}")

    def test_single_character_multiple_meanings(self):
        # Test a single character that should have multiple meanings
        translations = lookup('大')
        self.assertGreater(len(translations), 1)
        expected = ['big', 'large', 'great']
        found_meanings = 0
        for meaning in expected:
            if any(meaning.lower() in trans.lower() for trans in translations):
                found_meanings += 1
        self.assertGreater(found_meanings, 0,
            f"Expected to find at least one of {expected} in translations, but got: {translations}")

    def test_known_characters(self):
        """Test translations for known characters using CC-CEDICT"""
        test_cases = [
            ("中", "hit"),  # "to hit (the mark)" is in definitions
            ("國", "country"),  # Should find 'country' in definitions
            ("中國", "China"),  # Should find 'China' in definitions
        ]
        
        for char, expected_substr in test_cases:
            with self.subTest(char=char):
                translations = lookup(char)
                self.assertTrue(len(translations) > 0, f"No translations found for {char}")
                # Check if expected substring appears in any of the translations
                found = any(expected_substr.lower() in trans.lower() for trans in translations)
                self.assertTrue(found, f"Expected '{expected_substr}' in translations of {char}")

    def test_empty_input(self):
        """Test empty string input"""
        self.assertEqual(lookup(''), [], "Empty input should return empty list")

    def test_not_found(self):
        """Test word that shouldn't exist in dictionary"""
        self.assertEqual(lookup('notachinesesword'), [], "Non-existent word should return empty list")
        self.assertEqual(lookup('☺'), [], "Non-Chinese character should return empty list")

    def test_multiple_characters(self):
        """Test lookup of multi-character words"""
        translations = lookup("中國")
        self.assertTrue(len(translations) > 0, "Should find translations for '中國'")
        # Check if 'China' appears in any of the translations
        found = any("China" in trans for trans in translations)
        self.assertTrue(found, "Expected to find 'China' in translations of '中國'")

    def test_result_format(self):
        """Test that results are in the correct format (strings)"""
        translations = lookup("中")
        self.assertTrue(len(translations) > 0, "Should find translations for '中'")
        for trans in translations:
            self.assertIsInstance(trans, str, "Each translation should be a string")

if __name__ == '__main__':
    unittest.main()