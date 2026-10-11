import unittest
from scripts.release_safety import risk, validate_promotion

SHA = "a" * 40
DIGEST = "sha256:" + "b" * 64

class ReleaseSafetyTests(unittest.TestCase):
    def test_allow_docs_only(self):
        self.assertEqual(risk(["docs/guide.md", "README.md"]), "low")

    def test_block_sensitive_and_unknown(self):
        for paths in ([], ["terraform/main.tf"], [".github/workflows/deploy.yml"],
                      ["src/app.py"], ["scripts/release_safety.py"], ["../docs/a.md"]):
            self.assertEqual(risk(paths), "high")

    def test_promotion_requires_approved_verified_source(self):
        source = {"dev": {"commit_sha": SHA, "image_digest": DIGEST,
                          "smoke_passed": True, "approved": True}}
        self.assertTrue(validate_promotion(source, "test", SHA, DIGEST))
        self.assertFalse(validate_promotion(source, "production", SHA, DIGEST))
        self.assertFalse(validate_promotion(source, "test", "c" * 40, DIGEST))
        source["dev"]["approved"] = False
        self.assertFalse(validate_promotion(source, "test", SHA, DIGEST))

if __name__ == "__main__":
    unittest.main()
