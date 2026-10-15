"""Opt-in live source-analysis check for thirteen synthetic development workflows."""
import argparse
import io
import json
from pathlib import Path
import sys
import time
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from backend.investigate import investigate
from backend.providers import ProviderError, provider_info, complete


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--approve-provider', action='store_true', required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--workflow', help='Run one registered workflow for diagnosis')
    parser.add_argument('--continue-validation-errors', action='store_true',
                        help='Check other workflows after rejected answers; never retry a workflow or continue on transport/quota failure')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    if args.output.exists():
        parser.error('Preserve existing evidence; choose a new output file')
    provider = provider_info()
    if not provider['configured']:
        parser.error('Configure the provider securely in the environment first')
    registry = json.loads((root / 'evaluations/capabilities.json').read_text())
    if args.workflow:
        registry = [entry for entry in registry if entry['id'] == args.workflow]
        if not registry:
            parser.error('Unknown workflow')
    results = []
    for entry in registry:
        fixture = root / 'evaluations/fixtures' / entry['fixtures'][0]
        selected = sorted(p.name for p in fixture.iterdir()
                          if p.is_file() and p.suffix in ('.py', '.md', '.sql', '.txt'))
        archive = io.BytesIO()
        with zipfile.ZipFile(archive, 'w') as output:
            for name in selected:
                output.writestr(name, (fixture / name).read_bytes())
        task = ('Perform a source-only ' + entry['id'] + ' review of this synthetic development fixture. '
                'Identify concrete relevant evidence and useful checks. Distinguish source observations '
                'from runtime verification. Do not claim tests or commands were executed.')
        started = time.monotonic()
        captured = {}
        def send(prompt, **kwargs):
            response = complete(prompt, **kwargs)
            captured['content'] = response['content']
            return response
        try:
            response = investigate(archive.getvalue(), selected, task, entry['id'], send=send)
            results.append({'workflow': entry['id'], 'schema_and_citations_passed': True,
                            'fixture': fixture.name, 'result': response})
        except ProviderError as exc:
            results.append({'workflow': entry['id'], 'schema_and_citations_passed': False,
                            'fixture': fixture.name, 'error': str(exc), 'rejected_synthetic_response': captured})
            # Only independently test the next case after an answer-validation
            # rejection. Quota, upstream and transport failures always stop.
            validation_error = (str(exc).startswith('Investigation response failed')
                                or str(exc).startswith('Provider returned an unfinished')
                                or str(exc).startswith('Provider returned an invalid, empty'))
            if not args.continue_validation_errors or not validation_error:
                break
        args.output.write_text(json.dumps({'provider': provider['id'], 'results': results,
            'limitations': 'Development source analysis only; no runtime or effectiveness certificate'}, indent=2), encoding='utf-8')
        print(json.dumps({'workflow': entry['id'], 'schema_and_citations_passed': results[-1]['schema_and_citations_passed']}), flush=True)
        # At most five submissions per minute; sleep never exceeds 13 seconds.
        time.sleep(max(0, 13 - (time.monotonic() - started)))
    args.output.write_text(json.dumps({'provider': provider['id'], 'results': results,
        'limitations': 'Development source analysis only; no runtime or effectiveness certificate'}, indent=2), encoding='utf-8')
    return 0 if len(results) == len(registry) and all(r['schema_and_citations_passed'] for r in results) else 1


if __name__ == '__main__':
    raise SystemExit(main())
