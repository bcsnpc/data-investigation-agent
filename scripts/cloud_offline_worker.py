"""Fixed offline worker entrypoint. No live mode, credentials or shell tool."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import socket
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
TEST_MODULES = (
    'test_round24_native_index.py',
    'test_round24_parallel.py',
    'test_round24_paths.py',
    'test_round24_query_feedback.py',
    'test_round24_smoke_configuration.py',
    'test_round24_actual_cost.py',
    'test_round24_health_smoke.py',
    'test_round24_policy.py',
    'test_round24_postgres.py',
    'test_round24_query_patterns.py',
    'test_round24_runtime_anthropic.py',
    'test_round23_intake_queries.py','test_round23_reasoning.py',
    'test_round23_triage_tools.py','test_round23_platform.py',
    'test_round23_guided_cases.py','test_round23_answers_native.py',
    'test_round23_text_resolver.py','test_round23_native_catalog.py','test_round23_live_facts.py',
    'test_round_twenty_state.py', 'test_shared_read_transactions.py',
    'test_build_phase.py', 'test_scan_budget_reallocation.py',
    'test_source_availability.py',
    'test_investigator_frontier.py', 'test_fixture_failure_scenarios.py', 'test_fixture_source_latency.py',
    'test_operational_run_selection.py', 'test_operational_intake.py', 'test_calculation_intake.py', 'test_control_meter_reporting.py',
    'test_normal_audit.py',
    'test_worker_capture_publication.py', 'test_worker_lifecycle.py', 'test_smoke_demo_expectation.py',
    'test_streaming_tape.py', 'test_smoke_run_bound_capture.py',
    'test_connection_rotation.py', 'test_facts_ledger.py', 'test_runtime_facts_microsoft.py',
    'test_access_budget_policy.py', 'test_capture_publication_retry.py', 'test_ledger_investigator.py', 'test_investigator_case.py', 'test_investigator_playbook.py', 'test_investigator_checkpoint.py', 'test_investigator_heavy_reader.py', 'test_investigator_harness.py', 'test_enrichment.py',
    'test_essentials_intake.py', 'test_explain_questions.py', 'test_item_metadata_history.py',
    'test_ledger_verdict_proof.py', 'test_ledger_investigator_ports.py', 'test_cloud_ledger_investigator.py', 'test_collector_schedule.py',
    'test_live_gateway.py', 'test_tape_decoders.py', 'test_model_transport_retry.py',
    'test_keyed_readback.py', 'test_native_diagnostics.py',
    'test_budget_tape_contract.py', 'test_provider_tape_contract.py', 'test_ticket_protocol.py',
    'test_shared_usage_replay.py', 'test_cloud_verification_first_error.py',
    'test_streaming_verification_snapshot.py', 'test_batched_database_audit.py',
    'test_run_database_audits.py', 'test_cloud_verification_window.py',
    'test_cloud_runner_context.py', 'test_unified_runner.py',
    'test_runner_graph_schedule.py', 'test_cloud_verification_capture.py',
    'test_shared_application_capture.py', 'test_cloud_verification_proof.py',
    'test_shared_catalog_capture.py',
    'test_recorded_engine_image.py',
    'test_cloud_runtime_storage.py', 'test_demo_admission.py', 'test_graph_value_verification.py', 'test_graph_value_bridge.py',
    'test_capture_transaction_publication.py', 'test_cloud_dax_authorization.py',
    'test_cloud_value_execution.py', 'test_cloud_value_mapping.py',
    'test_cloud_value_verifier.py',
    'test_runner_replay_materialize.py',
)


def partition(entries, shard, shards):
    if type(shard) is not int or type(shards) is not int or not 1 <= shards <= 8 or not 0 <= shard < shards:
        raise ValueError('INVALID_OFFLINE_SHARD')
    return [entry for index, entry in enumerate(entries) if index % shards == shard]


def sealed_file(root, relative, digest):
    root = Path(root).resolve()
    if not isinstance(relative, str) or Path(relative).is_absolute():
        raise ValueError('EVIDENCE_PATH_MUST_BE_RELATIVE')
    path = (root / relative).resolve()
    if not path.is_relative_to(root) or not path.is_file():
        raise ValueError('EVIDENCE_OUTSIDE_MOUNT_OR_MISSING')
    if not isinstance(digest, str) or not re.fullmatch('[0-9a-f]{64}', digest):
        raise ValueError('EVIDENCE_HASH_REQUIRED')
    if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
        raise ValueError('EVIDENCE_HASH_DIFFERS')
    return path


def replay(manifest, evidence, output, shard, shards, executor, *, private_failures=None):
    if set(manifest) != {'version', 'entries'} or manifest['version'] != 1:
        raise ValueError('OFFLINE_REPLAY_MANIFEST')
    entries = manifest['entries']
    if not isinstance(entries, list) or not entries or len(entries) > 10000:
        raise ValueError('OFFLINE_REPLAY_ENTRIES')
    identifiers = [entry.get('id') for entry in entries]
    if any(not isinstance(value, str) or not re.fullmatch('[A-Za-z0-9_-]{1,120}', value) for value in identifiers) or len(set(identifiers)) != len(identifiers):
        raise ValueError('OFFLINE_REPLAY_IDENTITIES')
    rows = []
    for entry in partition(entries, shard, shards):
        row = {'id': entry['id'], 'matched': False}
        try:
            required = {'id', 'tape_path', 'tape_sha256', 'engine_revision'}
            optional = {'estate_manifest_path', 'estate_manifest_sha256'}
            present_optional = set(entry) & optional
            if not required <= set(entry) or set(entry) - required - optional or (present_optional and present_optional != optional):
                raise ValueError('OFFLINE_REPLAY_ENTRY')
            if not re.fullmatch('[0-9a-f]{40}', entry['engine_revision']):
                raise ValueError('IMMUTABLE_ENGINE_REVISION_REQUIRED')
            tape = sealed_file(evidence, entry['tape_path'], entry['tape_sha256'])
            estate = sealed_file(evidence, entry['estate_manifest_path'], entry['estate_manifest_sha256']) if 'estate_manifest_path' in entry else None
            result = executor(tape, Path(output) / entry['id'], entry['engine_revision'], estate_manifest=estate)
            row['matched'] = result.get('matched') is True
            if not row['matched'] and private_failures is not None:
                private_failures.append({'id': entry['id'], 'kind': 'REPLAY_RETURNED_MISMATCH', 'result': result})
        except Exception as exc:
            # No provider body, connection details or exception text in public CI logs.
            row['error_type'] = type(exc).__name__
            if private_failures is not None:
                private_failures.append({'id': entry['id'], 'error_type': type(exc).__name__,
                                         'reason': str(exc), **({'first_tape_errors': exc.private_replay_diagnostics}
                                             if hasattr(exc, 'private_replay_diagnostics') else {})})
        rows.append(row)
    return {'mode': 'SEALED_REPLAY', 'shard': shard, 'shards': shards, 'count': len(rows),
            'matched': sum(row['matched'] for row in rows), 'network_requests': 0,
            'physical_requests': 0, 'rows': rows,
            'claim': 'Byte replay only; this result does not substitute for outcome acceptance.'}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mode', choices=('tests', 'replay'), default='tests')
    parser.add_argument('--shard', type=int, default=0)
    parser.add_argument('--shards', type=int, default=8)
    parser.add_argument('--output', type=Path, default=Path('/results'))
    parser.add_argument('--repo', type=Path)
    parser.add_argument('--manifest', type=Path)
    parser.add_argument('--evidence', type=Path)
    args = parser.parse_args(argv)
    partition([], args.shard, args.shards)
    os.environ['DIA_LIVE_ACCESS_DISABLED'] = '1'
    args.output.mkdir(parents=True, exist_ok=True)
    os.environ['DIA_GATEWAY_AUDIT_FILE'] = str(args.output / 'gateway-denials.jsonl')
    if args.mode == 'tests':
        modules = partition(TEST_MODULES, args.shard, args.shards)
        # Test code uses explicitly injected fake transports; deployment runs
        # this container with --network=none as a second independent boundary.
        command = [sys.executable, '-m', 'pytest', '-q', *[str(ROOT / 'scripts' / item) for item in modules],
                   '--junitxml=' + str(args.output / f'shard-{args.shard}.xml')]
        return subprocess.run(command, cwd=ROOT, timeout=900, check=False).returncode
    if any(value is None for value in (args.repo, args.manifest, args.evidence)):
        parser.error('replay requires --repo, --manifest and --evidence mounts')
    def refused(*_args, **_kwargs):
        raise RuntimeError('NETWORK_FORBIDDEN')
    socket.create_connection = refused
    socket.socket.connect = refused
    # Historical replay extracts the exact pinned git revision and separately
    # disables sockets in that child. No git fetch is attempted by the worker.
    repo = args.repo.resolve()
    spec = importlib.util.spec_from_file_location('cloud_recorded_engine', repo / 'acceptance/unknown_domain/recorded_engine.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    sys.path.insert(0, str(repo / 'scripts'))
    failures = []
    result = replay(json.loads(args.manifest.read_bytes()), args.evidence, args.output,
                    args.shard, args.shards, module.replay_revision, private_failures=failures)
    if failures:
        (args.output / f'shard-{args.shard}-private-failures.json').write_text(
            json.dumps({'mode': 'PRIVATE_REPLAY_DIAGNOSTICS', 'failures': failures}, indent=2) + '\n', encoding='utf-8')
    (args.output / f'shard-{args.shard}.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({key: value for key, value in result.items() if key != 'rows'}))
    return 0 if result['matched'] == result['count'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
