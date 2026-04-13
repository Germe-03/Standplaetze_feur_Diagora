import unittest

from Model.User import User


class TestUserModel(unittest.TestCase):
    def test_role_setter_rejects_empty_role(self):
        user = User(1, "Muster", "Max", "secret", "User")
        with self.assertRaises(ValueError):
            user.role = ""


if __name__ == "__main__":
    unittest.main()
