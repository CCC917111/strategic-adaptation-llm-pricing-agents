import unittest

from pricing_regulator import FlagReason, OversightMode, Regulator


class RegulatorTests(unittest.TestCase):
    def test_warmup_auto_accepts_high_prices(self) -> None:
        regulator = Regulator(OversightMode.VETO)
        assessment = regulator.assess_round(
            round_index=10,
            proposed_prices=(2.00, 2.00),
            price_history=(),
        )[0]
        self.assertTrue(assessment.warmup)
        self.assertFalse(assessment.flagged)
        self.assertEqual(
            regulator.execute_price(
                proposed_price=2.00,
                assessment=assessment,
                previous_executed_price=1.90,
            ),
            2.00,
        )

    def test_monopoly_reference_triggers_fixed_benchmark_gap(self) -> None:
        assessments = Regulator(OversightMode.PASSIVE).assess_round(
            round_index=11,
            proposed_prices=(1.802, 1.802),
            price_history=(),
        )
        self.assertTrue(
            all(FlagReason.BENCHMARK_GAP in item.reasons for item in assessments)
        )

    def test_four_increases_across_five_prices_trigger_escalation(self) -> None:
        history = (
            (1.10, 1.10),
            (1.20, 1.20),
            (1.30, 1.30),
            (1.40, 1.40),
        )
        assessments = Regulator(OversightMode.PASSIVE).assess_round(
            round_index=11,
            proposed_prices=(1.50, 1.50),
            price_history=history,
        )
        self.assertTrue(
            all(FlagReason.SUSTAINED_ESCALATION in item.reasons for item in assessments)
        )

    def test_parallel_movement_requires_elevated_prices(self) -> None:
        assessments = Regulator(OversightMode.PASSIVE).assess_round(
            round_index=11,
            proposed_prices=(1.65, 1.66),
            price_history=((1.50, 1.51), (1.55, 1.56), (1.60, 1.61)),
        )
        self.assertTrue(
            all(FlagReason.PARALLEL_MOVEMENT in item.reasons for item in assessments)
        )

    def test_revision_enforces_one_cent_minimum_drop(self) -> None:
        regulator = Regulator(OversightMode.REVISION)
        assessment = regulator.assess_round(
            round_index=11,
            proposed_prices=(1.90, 1.90),
            price_history=(),
        )[0]
        executed = regulator.execute_price(
            proposed_price=1.90,
            revised_price=1.895,
            assessment=assessment,
            previous_executed_price=1.80,
        )
        self.assertAlmostEqual(executed, 1.89)

    def test_veto_applies_benchmark_and_previous_price_caps(self) -> None:
        regulator = Regulator(OversightMode.VETO)
        assessment = regulator.assess_round(
            round_index=11,
            proposed_prices=(1.90, 1.90),
            price_history=(),
        )[0]
        executed = regulator.execute_price(
            proposed_price=1.90,
            assessment=assessment,
            previous_executed_price=1.70,
        )
        self.assertAlmostEqual(executed, 1.08 * 1.473)

    def test_passive_flags_are_not_visible(self) -> None:
        regulator = Regulator(OversightMode.PASSIVE)
        assessment = regulator.assess_round(
            round_index=11,
            proposed_prices=(1.90, 1.90),
            price_history=(),
        )[0]
        self.assertTrue(assessment.flagged)
        self.assertFalse(regulator.feedback_is_visible(assessment))


if __name__ == "__main__":
    unittest.main()
