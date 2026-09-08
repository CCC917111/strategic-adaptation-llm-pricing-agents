import unittest

from pricing_market import LogitMarket, MarketConfig


class LogitMarketTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = MarketConfig()
        self.market = LogitMarket(self.config)

    def test_shares_include_outside_option_and_sum_to_one(self) -> None:
        outcome = self.market.evaluate((1.50, 1.50))
        total = outcome.outside_share + sum(firm.share for firm in outcome.firms)
        self.assertAlmostEqual(total, 1.0, places=12)
        self.assertGreater(outcome.outside_share, 0.0)

    def test_lower_price_receives_more_demand(self) -> None:
        outcome = self.market.evaluate((1.40, 1.60))
        self.assertGreater(outcome.firms[0].share, outcome.firms[1].share)

    def test_marginal_cost_price_has_zero_profit(self) -> None:
        outcome = self.market.evaluate((1.00, 1.50))
        self.assertAlmostEqual(outcome.firms[0].profit, 0.0)

    def test_calibrated_benchmarks_match_documentation(self) -> None:
        self.assertAlmostEqual(self.market.symmetric_nash_price(), 1.472926656)
        self.assertAlmostEqual(
            self.market.standalone_monopoly_price(), 1.801985010
        )
        self.assertAlmostEqual(
            self.market.symmetric_joint_profit_price(), 1.924980914
        )

    def test_best_response_is_locally_profit_maximizing(self) -> None:
        rival_price = 1.802
        response = self.market.best_response(rival_price)
        center = self.market.evaluate((response, rival_price)).firms[0].profit
        lower = self.market.evaluate((response - 0.001, rival_price)).firms[0].profit
        upper = self.market.evaluate((response + 0.001, rival_price)).firms[0].profit
        self.assertGreater(center, lower)
        self.assertGreater(center, upper)


if __name__ == "__main__":
    unittest.main()
