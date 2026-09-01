from math import isclose

from pricing_market import LogitMarket, MarketConfig


SHIFT_MAX = 0.17328679513998632


def test_demand_shift_schedule() -> None:
    config = MarketConfig(
        demand_shift_max=SHIFT_MAX,
        demand_shift_ramp_end_round=40,
    )
    assert config.demand_shift_at(1) == 0.0
    assert isclose(config.demand_shift_at(40), SHIFT_MAX)
    assert isclose(config.demand_shift_at(100), SHIFT_MAX)


def test_outside_share_calibration() -> None:
    market = LogitMarket(
        MarketConfig(
            demand_shift_max=SHIFT_MAX,
            demand_shift_ramp_end_round=40,
        )
    )
    assert isclose(market.evaluate((2.0, 2.0), round_index=1).outside_share, 1 / 3)
    assert isclose(market.evaluate((2.0, 2.0), round_index=40).outside_share, 1 / 5)


def test_plateau_benchmarks_match_archived_design() -> None:
    mature = LogitMarket()
    expanding = LogitMarket(
        MarketConfig(
            demand_shift_max=SHIFT_MAX,
            demand_shift_ramp_end_round=40,
        )
    )
    assert isclose(mature.symmetric_nash_price(round_index=60), 1.472926656, abs_tol=1e-6)
    assert isclose(
        mature.symmetric_joint_profit_price(round_index=60),
        1.924980914,
        abs_tol=1e-6,
    )
    assert isclose(
        expanding.symmetric_nash_price(round_index=60), 1.485021492, abs_tol=1e-6
    )
    assert isclose(
        expanding.symmetric_joint_profit_price(round_index=60),
        2.054411174,
        abs_tol=1e-6,
    )
