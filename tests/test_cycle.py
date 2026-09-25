"""Offline Arm2 checks: demand path, hidden information, and fixed-horizon resume."""

import argparse
import asyncio
import contextlib
import io
import json
import math
import re
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch

from pricing_agents import PricingDecision
from pricing_experiment import run_cycle_experiment as entry
from pricing_experiment.persistence import ExperimentStore, round_to_dict
from pricing_market import LogitMarket
from pricing_market.cycle import CycleConfig, CyclicLogitMarket


class RecordingClient:
    """No network: constant prices and uniquely attributable private notes."""

    instances = []

    def __init__(self, **settings):
        self.settings = settings
        self.calls = []
        self.closed = False
        type(self).instances.append(self)

    async def generate(self, *, system_prompt, user_prompt):
        firm = int(re.search(r"^Firm: (\d+)$", user_prompt, re.M).group(1))
        round_index = int(re.search(r"^Round: (\d+)$", user_prompt, re.M).group(1))
        self.calls.append((firm, round_index, system_prompt, user_prompt))
        return PricingDecision(
            price=1.6,
            justification=f"Independent test price for firm {firm}.",
            used_competitor_info=False,
            notes=f"PRIVATE_FIRM_{firm}_ROUND_{round_index}",
        )

    async def close(self):
        self.closed = True


def fake_api_module():
    module = types.ModuleType("pricing_agents.openai_compatible_client")
    module.OpenAICompatibleModelClient = RecordingClient
    return patch.dict(sys.modules, {module.__name__: module})


def arguments(output, *, resume=False):
    return argparse.Namespace(
        output=Path(output), resume=resume, model="offline-test-model",
        thinking_level="high", temperature=1.2, round_delay=0,
        endpoint_host="example.invalid", source_sha256={"offline-fixture": "test"},
    )


class CycleConfigTests(unittest.TestCase):
    def test_default_path_has_two_complete_periods_and_expected_extrema(self):
        cycle = CycleConfig()
        values = [cycle.state(r)["market_size"] for r in range(1, 81)]
        for round_index, expected in ((1, 100), (11, 150), (21, 100),
                                      (31, 50), (41, 100), (51, 150), (71, 50)):
            self.assertAlmostEqual(cycle.state(round_index)["market_size"], expected)
        self.assertEqual(values[:40], values[40:])
        self.assertAlmostEqual(min(values), 50)
        self.assertAlmostEqual(max(values), 150)
        self.assertEqual(cycle.state(1)["t"], 0)
        self.assertEqual(cycle.state(41)["cycle"], 2)
        self.assertEqual(cycle.state(1)["phase"], "expansion")
        self.assertEqual(cycle.state(21)["phase"], "contraction")
        self.assertEqual(cycle.state(11)["phase"], "turning")
        self.assertEqual(cycle.state(31)["phase"], "turning")

    def test_repeated_lookup_does_not_advance_demand(self):
        cycle = CycleConfig()
        expected = cycle.state(11)
        self.assertEqual(cycle.state(11), expected)
        cycle.state(80)
        self.assertEqual(cycle.state(11), expected)

    def test_zero_amplitude_is_stationary(self):
        cycle = CycleConfig(baseline=12, amplitude=0)
        for round_index in range(1, 81):
            self.assertEqual(cycle.state(round_index)["market_size"], 12)
            self.assertEqual(cycle.state(round_index)["phase"], "stationary")

    def test_invalid_cycle_parameters_are_rejected(self):
        cases = [
            {"baseline": value} for value in (0, -1, math.inf, math.nan)
        ] + [
            {"amplitude": value} for value in (-0.1, 1, math.inf, math.nan)
        ] + [
            {"period": value} for value in (0, 3, 4.5, True)
        ]
        for kwargs in cases:
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                CycleConfig(**kwargs)
        for value in (0, -1, 1.5, True):
            with self.subTest(round_index=value), self.assertRaises(ValueError):
                CycleConfig().state(value)


class CyclicMarketTests(unittest.TestCase):
    def test_demand_scaling_changes_quantity_and_profit_but_not_shares(self):
        market = CyclicLogitMarket()
        reference = LogitMarket().evaluate((1.6, 1.8))
        for round_index, scale in ((1, 100), (11, 150), (31, 50)):
            result = market.evaluate((1.6, 1.8), round_index=round_index)
            self.assertAlmostEqual(result.market_size, scale)
            self.assertEqual(result.outside_share, reference.outside_share)
            for observed, original in zip(result.firms, reference.firms):
                self.assertEqual(observed.share, original.share)
                self.assertAlmostEqual(observed.quantity, original.quantity * scale)
                self.assertAlmostEqual(observed.profit, original.profit * scale)

    def test_static_optimal_prices_are_invariant_to_positive_scale(self):
        market = CyclicLogitMarket()
        reference = LogitMarket()
        for round_index in (1, 11, 31, 51, 71):
            self.assertAlmostEqual(
                market.symmetric_nash_price(round_index=round_index),
                reference.symmetric_nash_price(), places=6,
            )
            self.assertAlmostEqual(
                market.symmetric_joint_profit_price(round_index=round_index),
                reference.symmetric_joint_profit_price(), places=6,
            )
            self.assertAlmostEqual(
                market.best_response(1.8, round_index=round_index),
                reference.best_response(1.8), places=6,
            )

    def test_stationary_reference_does_not_change_when_round_is_passed(self):
        market = LogitMarket()
        self.assertEqual(market.evaluate((1.6, 1.8)),
                         market.evaluate((1.6, 1.8), round_index=31))


class CycleRunnerTests(unittest.TestCase):
    def setUp(self):
        RecordingClient.instances.clear()

    def test_full_80_round_run_preserves_private_memory_and_hides_cycle(self):
        client = RecordingClient()
        runner = entry.make_runner(client, seed=0)
        rows = asyncio.run(runner.run(80))
        self.assertEqual(len(rows), 80)
        self.assertEqual(len(client.calls), 160)
        for row in rows:
            self.assertEqual(row.executed_prices, (1.6, 1.6))
            self.assertEqual(row.revisions, (None, None))
            self.assertEqual(row.market_outcome.market_size,
                             CycleConfig().state(row.round_index)["market_size"])
        for firm, round_index, system, user in client.calls:
            with self.subTest(firm=firm, round_index=round_index):
                self.assertNotIn(f"PRIVATE_FIRM_{1-firm}_", user)
                if round_index > 1:
                    self.assertIn(f"PRIVATE_FIRM_{firm}_ROUND_{round_index-1}", user)
                    self.assertIn(f"Round {round_index-1}: own_price=", user)
                self.assertNotIn(f"Round {round_index}: own_price=", user)
                self.assertNotIn("oversight_status=", user)
                for hidden in ("market_size", "beta", "phase", "sin(",
                               "amplitude", "cycle", "expansion", "contraction"):
                    self.assertNotIn(hidden, (system + user).lower())
                self.assertNotIn("rival_quantity", user)
                self.assertNotIn("rival_profit", user)

    def test_persisted_resume_matches_uninterrupted_rounds_and_private_notes(self):
        async def scenario(directory):
            uninterrupted = entry.make_runner(RecordingClient(), 3)
            await uninterrupted.run(80)
            first = entry.make_runner(RecordingClient(), 3)
            store = ExperimentStore(directory)
            store.initialize({"offline": True}, resume=False)
            for _ in range(17):
                store.append_round(await first.run_round())
            resumed_client = RecordingClient()
            resumed = entry.make_runner(resumed_client, 3)
            resumed.restore(store.load_rounds())
            await resumed.run(63)
            return uninterrupted, resumed, resumed_client

        with tempfile.TemporaryDirectory() as directory:
            uninterrupted, resumed, client = asyncio.run(scenario(directory))
        self.assertEqual([round_to_dict(row) for row in uninterrupted.rounds],
                         [round_to_dict(row) for row in resumed.rounds])
        self.assertEqual(client.calls[0][1], 18)
        self.assertIn("PRIVATE_FIRM_0_ROUND_17", client.calls[0][3])
        self.assertNotIn("PRIVATE_FIRM_1_", client.calls[0][3])

    def test_live_entry_point_is_fixed_horizon_and_completed_resume_makes_no_calls(self):
        with tempfile.TemporaryDirectory() as directory, fake_api_module():
            args = arguments(directory)
            with contextlib.redirect_stdout(io.StringIO()):
                result = asyncio.run(entry.run_cell(args, 2, asyncio.Semaphore(6)))
            self.assertEqual(result, {"seed": 2, "status": "completed", "rounds": 80})
            client = RecordingClient.instances[0]
            self.assertEqual(len(client.calls), 160)
            self.assertTrue(client.closed)
            self.assertEqual(client.settings["seed"], 2)
            self.assertEqual(client.settings["temperature"], 1.2)
            store = ExperimentStore(Path(directory) / "seed2")
            manifest = json.loads(store.manifest_path.read_text())
            self.assertFalse(manifest["config"]["early_stopping"])
            self.assertEqual(manifest["stopping"], {"reason": "fixed_horizon", "round": 80})
            args.resume = True
            repeated = asyncio.run(entry.run_cell(args, 2, asyncio.Semaphore(6)))
            self.assertEqual(repeated, result)
            self.assertEqual(len(RecordingClient.instances), 1)
            args.temperature = 1.0
            with self.assertRaisesRegex(ValueError, "configuration differs"):
                asyncio.run(entry.run_cell(args, 2, asyncio.Semaphore(6)))

    def test_live_entry_point_partial_resume_uses_next_round_without_replay(self):
        async def scenario(directory):
            args = arguments(directory, resume=True)
            store = ExperimentStore(Path(directory) / "seed4")
            store.initialize(entry.cell_config(args, 4), resume=False)
            first = entry.make_runner(RecordingClient(), 4)
            for _ in range(40):
                store.append_round(await first.run_round())
            result = await entry.run_cell(args, 4, asyncio.Semaphore(6))
            return result, store.load_rounds()

        with tempfile.TemporaryDirectory() as directory, fake_api_module():
            with contextlib.redirect_stdout(io.StringIO()):
                result, rows = asyncio.run(scenario(directory))
        self.assertEqual(result["rounds"], 80)
        client = RecordingClient.instances[-1]
        self.assertEqual(len(client.calls), 80)
        self.assertEqual(client.calls[0][1], 41)
        self.assertAlmostEqual(rows[40].market_outcome.market_size, 100)
        self.assertIn("PRIVATE_FIRM_0_ROUND_40", client.calls[0][3])


if __name__ == "__main__":
    unittest.main()
