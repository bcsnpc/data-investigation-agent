"""Validated proposed destinations and deterministic content; no provider calls."""
import json
import re


def validate_destination(value):
    if not isinstance(value, dict) or set(value) != {'issue', 'notification'}:
        raise ValueError('Destination requires issue and notification settings')
    issue, notification = value['issue'], value['notification']
    if not isinstance(issue, dict) or set(issue) != {'provider', 'repository'} or issue['provider'] != 'github':
        raise ValueError('Unsupported issue destination')
    repository = issue['repository']
    if (not isinstance(repository, str) or len(repository) > 200
            or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9-]*/[A-Za-z0-9_][A-Za-z0-9_.-]*', repository)):
        raise ValueError('Repository must be an explicit owner/name')
    if not isinstance(notification, dict) or set(notification) != {'provider', 'recipients'} or notification['provider'] != 'email':
        raise ValueError('Unsupported notification destination')
    recipients = notification['recipients']
    if not isinstance(recipients, list) or not 1 <= len(recipients) <= 20:
        raise ValueError('Specify one to twenty email recipients')
    if any(not isinstance(address, str) or len(address) > 254 or not re.fullmatch(
            r"[A-Za-z0-9][A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]*@[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?)+", address)
           for address in recipients):
        raise ValueError('Recipients must be plain email addresses')
    if len({address.casefold() for address in recipients}) != len(recipients):
        raise ValueError('Duplicate recipient')


def destination_preview(draft, destination):
    validate_destination(destination)
    # Provider-specific encoding and mention suppression belong to the future adapter.
    body = '\n\n'.join((draft['scope'], 'Owner: ' + draft['team'],
                        'Severity: ' + draft['severity'],
                        'Impact by currency:\n' + json.dumps(draft['impact_by_currency'], sort_keys=True, indent=2),
                        'Affected records:\n' + json.dumps(draft['affected_records'], sort_keys=True, indent=2),
                        'Local evidence reference: ' + draft['evidence_reference'],
                        'Human triage required. No remediation authorized.'))
    return {'issue': {'provider': 'github', 'repository': destination['issue']['repository'],
                      'title': draft['title'], 'body': body},
            'notification': {'provider': 'email', 'recipients': list(destination['notification']['recipients']),
                             'subject': draft['title'], 'body': draft['notification_text'] + '\n\n' + body},
            'external_delivery_enabled': False,
            'limitation': 'Proposed content only. Provider permissions, recipient ownership and delivery are unverified. Evidence references are local paths.'}
