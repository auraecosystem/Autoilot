import unittest

from lmlm_ir import IRValidationError, validate_ir


VALID_IR = {
    "operation": "model.generate",
    "provider": "local",
    "model": "default",
    "input": {"type": "text", "source": "user_input"},
    "permissions": ["inference"],
    "verification": {"required": True},
}


class IRValidatorTests(unittest.TestCase):
    def test_accepts_valid_request(self):
        self.assertEqual(validate_ir(VALID_IR), VALID_IR)

    def test_normalizes_permission_order(self):
        document = dict(VALID_IR, permissions=["inference"])
        self.assertEqual(validate_ir(document)["permissions"], ["inference"])

    def test_rejects_unknown_top_level_key(self):
        document = dict(VALID_IR, shell=True)
        with self.assertRaises(IRValidationError):
            validate_ir(document)

    def test_rejects_unapproved_capability(self):
        document = dict(VALID_IR, permissions=["inference", "filesystem"])
        with self.assertRaises(IRValidationError):
            validate_ir(document)

    def test_rejects_unknown_operation(self):
        document = dict(VALID_IR, operation="python.exec")
        with self.assertRaises(IRValidationError):
            validate_ir(document)

    def test_rejects_duplicate_permissions(self):
        document = dict(VALID_IR, permissions=["inference", "inference"])
        with self.assertRaises(IRValidationError):
            validate_ir(document)

    def test_rejects_invalid_verification_type(self):
        document = dict(
            VALID_IR, verification={"required": "yes"}
        )
        with self.assertRaises(IRValidationError):
            validate_ir(document)


if __name__ == "__main__":
    unittest.main()
