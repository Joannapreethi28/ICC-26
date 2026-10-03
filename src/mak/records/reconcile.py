"""Compare golden headlines with covered-data records without rewriting either."""
from __future__ import annotations

from collections import Counter
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path
import re

import duckdb

from mak.config import DB_PATH, GOLDEN_PATH, RESULTS_DIR
from mak.fetch.facts import localize
from mak.records.compute import COMPUTABLE, compute
from mak.records.golden import load_golden


def _number(value):
    try:
        return Decimal(value.replace(',', '').rstrip('*'))
    except InvalidOperation:
        return None


def reconcile(*, db_path: Path = DB_PATH, golden_path: Path = GOLDEN_PATH) -> list[dict]:
    rows = []
    conn = duckdb.connect(str(db_path), read_only=True) if Path(db_path).is_file() else None
    try:
        for golden in load_golden(golden_path):
            if golden.intent_id not in COMPUTABLE:
                continue
            computed = compute(golden.intent_id, golden.gender, db_path=db_path)
            row = dict(intent_id=golden.intent_id, gender=golden.gender, golden_holder=golden.holder,
                       golden_value=golden.value, golden_as_of=golden.as_of,
                       computed_holder=computed.holder if computed else None,
                       computed_value=computed.value if computed else None,
                       computed_as_of=computed.as_of if computed else None,
                       delta=None, status='flagged', reason='Database or usable computed record unavailable.')
            if computed:
                a, b = _number(golden.value), _number(computed.value)
                if a is not None and b is not None:
                    row['delta'] = str(b - a)
                same_value = golden.value.replace(',', '') == computed.value.replace(',', '')
                identity = localize(golden, 'en').ids.get('cricsheet')
                same_holder = golden.holder.casefold() == computed.holder.casefold() or (
                    identity is not None and identity == computed.ids.get('cricsheet'))
                if same_value and same_holder:
                    row.update(status='match', reason='Holder and value agree; snapshot dates are retained separately.')
                elif same_value:
                    row['reason'] = ('Value agrees, but holder names differ and a unique registry identity is not established. '
                                     'Do not claim an identity match from equal figures alone.')
                else:
                    start, latest = conn.execute('''SELECT min(date), max(date) FROM matches
                        WHERE gender=? AND match_type=?''', [golden.gender, golden.format]).fetchone()
                    suffix = golden.intent_id.split('_', 1)[1]
                    if golden.country == 'Afghanistan':
                        row.update(status='explained', reason='Cricsheet withholds Afghanistan matches; the covered-data leader is not an all-time substitute.')
                    elif suffix in ('HS', 'TEAM', 'BBI'):
                        event = re.search(r'\b\d{4}-\d{2}-\d{2}\b', golden.context)
                        event_date = date.fromisoformat(event[0]) if event else None
                        if event_date:
                            team = golden.country or golden.holder
                            count = conn.execute('''SELECT count(*) FROM matches WHERE gender=? AND match_type=?
                                AND date=? AND (team1=? OR team2=?)''',
                                [golden.gender, golden.format, event_date, team, team]).fetchone()[0]
                            if count == 0:
                                row.update(status='explained', reason=f'Golden event absent: {team}, {event_date}. '
                                    f'Supplied {golden.gender} {golden.format} coverage is {start} to {latest}.')
                            else:
                                row['reason'] = 'Golden event date/team occurs in the DB, but the record differs; inspect scorecard completeness.'
                        else:
                            row['reason'] = 'Golden event date is not identifiable from context; manual source comparison required.'
                    else:
                        row.update(status='explained', reason=f'Covered-match aggregate only ({start} to {latest}); '
                            f'golden snapshot is {golden.as_of}. Missing early matches, incomplete series and/or update lag '
                            'can change totals and leaders. This is a coverage explanation, not an audited match-by-match delta.')
            rows.append(row)
    finally:
        if conn:
            conn.close()
    return rows


def write_report(path: Path = RESULTS_DIR / 'reconciliation.md', *, db_path: Path = DB_PATH) -> list[dict]:
    rows = reconcile(db_path=db_path)
    counts = Counter(r['status'] for r in rows)
    lines = [
        '# Golden / Cricsheet reconciliation', '',
        f'Measured {date.today().isoformat()}: {len(rows)} computable golden rows; '
        + ', '.join(f'{counts[status]} {status}' for status in ('match', 'explained', 'flagged')) + '.', '',
        'The other 24 golden rows describe World Cups or firsts and are not recomputed by this module. '
        'Every golden row retains its original source/date. Golden facts always win; this report does not freshly certify them.', '',
        '`explained` means a documented coverage difference, not numerical proof of every missing run/wicket. '
        '`flagged` stays open for review. Delta is computed minus golden for scalar values only; '
        'it is not necessarily a same-player difference. Bowling/team scorelines have no scalar delta.', '',
        '| Intent | Category | Golden holder / value / date | Computed holder / value / date | Delta | Status | Reason |',
        '|---|---|---|---|---|---|---|',
    ]
    for r in rows:
        cells = [r['intent_id'], r['gender'],
                 f"{r['golden_holder']} / {r['golden_value']} / {r['golden_as_of']}",
                 f"{r['computed_holder']} / {r['computed_value']} / {r['computed_as_of']}",
                 r['delta'] if r['delta'] is not None else 'n/a', r['status'], r['reason']]
        lines.append('| ' + ' | '.join(str(v).replace('|', '\\|') for v in cells) + ' |')
    lines += ['', 'Sources and definitions: [Cricsheet downloads](https://cricsheet.org/downloads/), '
              '[JSON schema](https://cricsheet.org/format/json/), `data/golden/records_v1.csv`, '
              '`docs/phase3-facts.md`. Known golden-source limitations remain in `audit_golden()`.']
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('\n'.join(lines) + '\n', encoding='utf-8', newline='\n')
    return rows


if __name__ == '__main__':
    print(dict(Counter(r['status'] for r in write_report())))
