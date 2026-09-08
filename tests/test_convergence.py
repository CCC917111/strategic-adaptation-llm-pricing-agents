import unittest

from pricing_experiment.convergence import convergence_diagnostics


class ConvergenceTests(unittest.TestCase):
    def test_no_check_before_round_40(self) -> None:
        self.assertIsNone(convergence_diagnostics([(1.5, 1.6)] * 39))

    def test_stable_prices_stop_at_round_40(self) -> None:
        result = convergence_diagnostics([(1.5, 1.6)] * 40)
        self.assertIsNotNone(result)
        assert result is not None
        self.assertTrue(result["stable"])
        self.assertEqual(result["round"], 40)

    def test_checks_only_every_five_rounds(self) -> None:
        self.assertIsNone(convergence_diagnostics([(1.5, 1.6)] * 41))
        self.assertIsNotNone(convergence_diagnostics([(1.5, 1.6)] * 45))

    def test_mean_shift_prevents_stopping(self) -> None:
        prices = [(1.5, 1.6)] * 30 + [(1.55, 1.65)] * 10
        result = convergence_diagnostics(prices)
        self.assertIsNotNone(result)
        assert result is not None
        self.assertFalse(result["stable"])


if __name__ == "__main__":
    unittest.main()
