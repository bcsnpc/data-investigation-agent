"""Bounded Microsoft same-statement self-description, shared by compiler and grammar."""

def scalar(property_name):
    if property_name not in ('ProviderName','Catalog'):raise ValueError('Unsupported self-description property')
    return 'CONCATENATEX(SELECTCOLUMNS(FILTER(INFO.PROPERTIES(),[PropertyName]="'+property_name+'"),"ReportValue",[Value]),[ReportValue],"")'

SCALARS=tuple(scalar(name) for name in ('ProviderName','Catalog'))

def compose(query):
    if not query.startswith('EVALUATE '):raise ValueError('One EVALUATE required for self-report')
    return 'EVALUATE ADDCOLUMNS('+query.removeprefix('EVALUATE ')+',"surface_identity",USERPRINCIPALNAME(),"surface_engine",'+SCALARS[0]+',"surface_object",'+SCALARS[1]+')'
