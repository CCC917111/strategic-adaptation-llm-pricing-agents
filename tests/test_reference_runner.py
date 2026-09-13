import asyncio
import json

import pytest

from pricing_agents import PricingDecision
from pricing_experiment import run_reference_experiment as entry


def test_official_runner_saves_a_complete_offline_simulation(tmp_path, monkeypatch):
    instances = []

    class FakeGoogleClient:
        def __init__(self, **kwargs):
            self.settings = kwargs
            self.calls = 0
            self.closed = False
            instances.append(self)

        async def generate(self, *, system_prompt, user_prompt):
            self.calls += 1
            return PricingDecision(
                price=1.60,
                justification='Offline test decision.',
                used_competitor_info=False,
                notes='Hold the test price.',
            )

        async def close(self):
            self.closed = True

    monkeypatch.setattr(entry, 'GeminiModelClient', FakeGoogleClient)
    args = entry.build_parser().parse_args([
        '--mode', 'passive', '--seed', '7', '--model', 'offline-test-model',
        '--output', str(tmp_path), '--rounds', '40', '--round-delay', '0',
    ])
    asyncio.run(entry.run(args))
    manifest = json.loads((tmp_path / 'manifest.json').read_text())
    rows = [json.loads(line) for line in (tmp_path / 'rounds.jsonl').read_text().splitlines()]
    assert manifest['status'] == 'completed'
    assert manifest['config']['transport'] == 'google'
    assert manifest['config']['api_method'] == 'google-genai-generate-content'
    assert manifest['config']['model'] == 'offline-test-model'
    assert len(rows) == 40
    assert all(row['executed_prices'] == [1.6, 1.6] for row in rows)
    assert instances[0].calls == 80
    assert instances[0].settings == {'model': 'offline-test-model', 'seed': 7, 'thinking_level': 'high'}
    assert instances[0].closed


def test_removed_relay_option_is_rejected_before_running(tmp_path):
    with pytest.raises(SystemExit):
        entry.build_parser().parse_args([
            '--mode', 'passive', '--output', str(tmp_path),
            '--transport', 'openai-compatible',
        ])
