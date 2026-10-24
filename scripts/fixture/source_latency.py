"""Live fixture admission for scored source-before-load cases, never a verdict.

Publisher controls own the reversible rows and schedule. This reader-only
check runs immediately before submission; its receipts are not engine inputs.
"""
import copy
from datetime import datetime, timezone
from .source_history import SourceHistoryScenario, row, FIELDS, number
from .pipeline_schedule import instant, same_configuration


class InvalidLatencyFixture(ValueError):
    fixture_invalid = True


def invalid(reason):
    raise InvalidLatencyFixture('LATENCY_FIXTURE_INVALID:' + reason)


def attested(native):
    if (native.get('read_only_verified') is not True or
            native.get('surface_report_binding') != 'VALUE_QUERY'):
        invalid('LIVE_READ_NOT_ATTESTED')


class LatencySourceScenario:
    def __init__(self, baseline):
        self.source = SourceHistoryScenario(baseline)

    @staticmethod
    def bronze_observation(value):
        value = row(value)
        return {
            'query': 'SELECT COUNT_BIG(*) AS matched_rows,SUM(CONVERT(bigint,units)) AS units '
                     'FROM [dbo].[stock_movements_round_two_20261003] WHERE movement_id=@movement_id',
            'parameters': [{'name': '@movement_id', 'value': value['movement_id']}],
            'read_only_objects': ['[dbo].[stock_movements_round_two_20261003]'],
            'max_rows': 2, 'result_columns': ['matched_rows', 'units']}

    def admit(self, source_reader, bronze_reader, schedule_reader, values, *, owned_schedule, clock):
        """Call native ports afresh for each ticket, then recheck the schedule.

        No mutation is available here. The caller keeps its control in place
        through the ticket and then uses the journalled restoration recipe.
        An invalid fixture stops before SUBMIT_ATTEMPT, not as a scored failure.
        """
        if not isinstance(values, list) or not 1 <= len(values) <= 3:
            invalid('ROW_BOUND')
        values = [row(v) for v in values]
        if len({v['movement_id'] for v in values}) != len(values):
            invalid('DUPLICATE_ID')
        started = clock()
        observations = []
        try:
            for expected in values:
                source_request = self.source.observation([expected])
                source = source_reader(source_request)
                attested(source)
                actual = source.get('rows', [])
                if (len(actual) != 1 or
                        row({k: actual[0][k] for k in FIELDS}) != expected):
                    invalid('SOURCE_ROW_MISSING_OR_CHANGED')
                lower_request = self.bronze_observation(expected)
                lower = bronze_reader(lower_request)
                attested(lower)
                rows = lower.get('rows', [])
                if len(rows) != 1:
                    invalid('BRONZE_RESULT_SHAPE')
                if number(rows[0]['matched_rows']) != 0:
                    invalid('SOURCE_NO_LONGER_AHEAD_OF_BRONZE')
                if rows[0]['units'] is not None:
                    invalid('EMPTY_RESULT_COLLAPSED')
                observations.append({'source_request': source_request, 'source_native': source,
                                     'bronze_request': lower_request, 'bronze_native': lower})
            schedules = schedule_reader()  # Never accept the creation receipt as current state.
            matches = [v for v in schedules if v.get('id') == owned_schedule['id']]
            checked = clock()
            if instant(checked) < instant(started):
                invalid('CLOCK_MOVED_BACKWARDS')
            if (len(matches) != 1 or matches[0].get('enabled') is not True or
                    not same_configuration(matches[0].get('configuration', {}),
                                           owned_schedule['expected']['configuration'])):
                invalid('OWNED_FUTURE_SCHEDULE_MISSING_OR_CHANGED')
            config = matches[0]['configuration']
            start = datetime.fromisoformat(config['startDateTime'].replace('Z', '+00:00'))
            if start.tzinfo is None:
                start = start.replace(tzinfo=timezone.utc)
            if (config.get('localTimeZoneId') != 'UTC' or start <= instant(checked)):
                invalid('LOAD_SCHEDULE_NOT_IN_FUTURE')
        except InvalidLatencyFixture:
            raise
        except Exception as error:
            raise InvalidLatencyFixture('LATENCY_FIXTURE_INVALID:LIVE_CHECK_FAILED:' +
                                        type(error).__name__) from error
        return {'status': 'LIVE_SOURCE_AHEAD_OF_BRONZE_FOR_SCORED_SUBMISSION',
                'started_at': started, 'checked_at': checked, 'observations': observations,
                'schedule_native': copy.deepcopy(matches[0]),
                'scope': 'Fixture admission only; not investigator diagnostic evidence',
                'restoration': 'Remove owned schedule, restore only native-version-matched rows, '
                               'verify full prior row hash after the dependent ticket.'}
