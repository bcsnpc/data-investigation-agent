"""Notebook helper: verify Bronze identities and read recorded Delta versions only."""


def read_pinned_bronze(spark, delta_table, binding):
    if binding.get('status') != 'BOUND_INPUTS':
        raise ValueError('Verified Bronze input binding required')
    expected = {'customers', 'products', 'orders', 'order_lines', 'payments',
                'shipments', 'shipment_lines', 'refunds', 'refund_lines', 'audit_log'}
    if len(binding['tables']) != 10 or {r['source_table'] for r in binding['tables']} != expected:
        raise ValueError('Complete ten-table Bronze binding required')
    frames = {}
    for row in binding['tables']:
        name, path = row['source_table'], row['destination']
        if name in frames:
            raise ValueError('Duplicate Bronze input')
        version = row['delta_version']
        if type(version) is not int or version < 0:
            raise ValueError('Pinned Delta version required')
        table = delta_table.forPath(spark, path)
        if table.detail().select('id').first()[0] != row['delta_table_id']:
            raise ValueError('Bronze table identity changed: ' + name)
        # Missing/vacuumed versions propagate an error. Never retry against latest.
        frame = spark.read.format('delta').option('versionAsOf', version).load(path)
        if frame.schema.jsonValue() != row['delta_schema']:
            raise ValueError('Bronze schema changed: ' + name)
        if frame.count() != row['rows']:
            raise ValueError('Bronze row count changed: ' + name)
        if table.detail().select('id').first()[0] != row['delta_table_id']:
            raise ValueError('Bronze table replaced during read: ' + name)
        frames[name] = frame
    return frames
