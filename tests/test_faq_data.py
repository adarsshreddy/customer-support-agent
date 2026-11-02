import unittest

from faq_data import find_best_faq, load_faqs


class FaqDataTests(unittest.TestCase):
    def setUp(self) -> None:
        self.faqs = load_faqs()

    def test_loads_faqs_from_project_directory(self) -> None:
        self.assertGreaterEqual(len(self.faqs), 1)
        self.assertTrue(all(faq["question"] and faq["answer"] for faq in self.faqs))

    def test_matches_order_tracking_question(self) -> None:
        result = find_best_faq("How can I track my order?", self.faqs)

        self.assertIsNotNone(result)
        self.assertIn("track your order", result["answer"])

    def test_matches_return_policy_question(self) -> None:
        result = find_best_faq("What is your return policy?", self.faqs)

        self.assertIsNotNone(result)
        self.assertIn("7 days", result["answer"])

    def test_does_not_guess_for_unknown_or_vague_questions(self) -> None:
        self.assertIsNone(find_best_faq("Can you change my subscription?", self.faqs))
        self.assertIsNone(find_best_faq("order", self.faqs))


if __name__ == "__main__":
    unittest.main()
