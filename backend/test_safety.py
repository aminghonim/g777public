import unittest
import os
import sys
import shutil

# Ensure backend can be imported
sys.path.append(os.getcwd())

from backend.core.safety import SafetyProtocol


class TestSafetyProtocol(unittest.TestCase):
    def setUp(self):
        self.safety = SafetyProtocol(root_dir=".test_safety")
        self.test_file = "test_file.txt"
        with open(self.test_file, "w") as f:
            f.write("Original Content")

    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
        if os.path.exists(".test_safety"):
            shutil.rmtree(".test_safety")

    def test_snapshot_creation(self):
        sid = self.safety.create_atomic_snapshot(self.test_file)
        self.assertTrue(sid.endswith("test_file.txt"))
        self.assertTrue(os.path.exists(os.path.join(".test_safety", "snapshots", sid)))

    def test_rollback(self):
        sid = self.safety.create_atomic_snapshot(self.test_file)

        # Modify file
        with open(self.test_file, "w") as f:
            f.write("Modified Content")

        # Rollback
        success = self.safety.rollback(sid, self.test_file)
        self.assertTrue(success)

        with open(self.test_file, "r") as f:
            content = f.read()
            self.assertEqual(content, "Original Content")

    def test_python_validation_valid(self):
        code = "def hello(): print('world')"
        valid, msg = self.safety.validate_code_safety(code, "python")
        self.assertTrue(valid)

    def test_python_validation_syntax_error(self):
        code = "def hello(): print('world'"  # Missing parenthesis
        valid, msg = self.safety.validate_code_safety(code, "python")
        self.assertFalse(valid)
        self.assertIn("Syntax Error", msg)

    def test_python_validation_security_risk(self):
        code = "import os; os.system('rm -rf /')"
        valid, msg = self.safety.validate_code_safety(code, "python")
        self.assertFalse(valid)
        self.assertIn("Security Risk", msg)


if __name__ == "__main__":
    unittest.main()
