"""Comparable scalar projection, separate from execution-surface attestation."""
from decimal import Decimal,InvalidOperation


def quantity(rows, surface_report_columns=None):
    """Exclude only declared report columns; preserve non-scalar result structure.

    Declarations come from the compiled request, never guessed column names.
    The receipt and its separately validated attestation remain unchanged.
    """
    labels=set()
    for label in (surface_report_columns or {}).values():
        labels.update((label,'['+label+']'))
    if isinstance(rows,list):
        rows=[{k:v for k,v in row.items() if k not in labels} if isinstance(row,dict) else row for row in rows]
    if not isinstance(rows,list) or len(rows)!=1 or not isinstance(rows[0],dict) or len(rows[0])!=1:return rows
    cell=next(iter(rows[0].values()))
    if isinstance(cell,dict) and 'value' not in cell:
        raise ValueError('Measured cell omitted its value; absence is not BLANK')
    value=cell['value'] if isinstance(cell,dict) else cell
    if value is None:return {'quantity':None}
    try:number=Decimal(str(value))
    except (InvalidOperation,ValueError):return {'quantity':str(value)}
    return {'quantity':format(number.normalize(),'f') if number!=0 else '0'}
