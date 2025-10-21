import unittest
from src.conflict_detector import ConflictDetector

class TestConflictDetector(unittest.TestCase):

    def setUp(self):
        self.detector = ConflictDetector()

    def test_find_merge_conflicts(self):
        # Example input with merge conflicts
        codebase = {
            'file1.py': 'print("Hello World")\n<<<<<<< HEAD\nprint("English Change")\n=======\nprint("French Change")\n>>>>>>> feature-branch',
            'file2.py': 'def example_function():\n    pass\n'
        }
        conflicts = self.detector.find_merge_conflicts(codebase)
        expected_conflicts = {
            'file1.py': {
                'conflict': 'print("English Change")\nprint("French Change")',
                'lines': [2]
            }
        }
        self.assertEqual(conflicts, expected_conflicts)

    def test_no_merge_conflicts(self):
        codebase = {
            'file1.py': 'print("Hello World")\nprint("No Conflict")',
            'file2.py': 'def example_function():\n    pass\n'
        }
        conflicts = self.detector.find_merge_conflicts(codebase)
        self.assertEqual(conflicts, {})

if __name__ == '__main__':
    unittest.main()