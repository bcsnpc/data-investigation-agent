"""Parse declared Power BI URL context; never open links or infer user state.

Native identifiers stay adapter-owned. Binding a parsed reference to retained
model columns is a separate step; parsing does not declare a readable surface.
"""
import re
from urllib.parse import urlsplit, parse_qsl
from uuid import UUID


class LinkRefused(ValueError):
    pass


NAME=r'[A-Za-z_][A-Za-z_0-9]*'
TOKEN=re.compile(r"\s*(?:(?P<string>'(?:[^']|'')*')|(?P<number>[+-]?(?:\d+(?:\.\d+)?)(?:[eE][+-]?\d+)?)|(?P<name>"+NAME+r")|(?P<punct>[/(),]))")


def identifier(value):
    return re.sub(r'_x([0-9a-fA-F]{4})_',lambda m:chr(int(m[1],16)),value)


def predicates(expression):
    """Faithful eq/in conjunction subset; all other forms refuse as a whole."""
    if not isinstance(expression,str) or not 1<=len(expression)<=2000:
        raise LinkRefused('URL filter exceeds its bound or is empty')
    tokens=[];position=0
    while position<len(expression):
        if not expression[position:].strip():break
        match=TOKEN.match(expression,position)
        if match is None:raise LinkRefused('Unsupported URL filter syntax')
        tokens.append((match.lastgroup,match[match.lastgroup]));position=match.end()
    cursor=0
    def take(kind=None,word=None):
        nonlocal cursor
        if cursor>=len(tokens):raise LinkRefused('Incomplete URL filter')
        token=tokens[cursor];cursor+=1
        if kind is not None and token[0]!=kind or word is not None and token[1]!=word:
            raise LinkRefused('Unsupported URL filter syntax')
        return token[1]
    def literal():
        if cursor>=len(tokens):raise LinkRefused('Missing URL filter value')
        kind=tokens[cursor][0]
        if kind=='string':return {'kind':'STRING','value':take('string')[1:-1].replace("''", "'")}
        if kind=='number':return {'kind':'NUMBER','value':take('number')}
        raise LinkRefused('Unsupported URL filter literal type')
    result=[]
    while cursor<len(tokens):
        table=identifier(take('name'));take('punct','/');field=identifier(take('name'))
        operation=take('name');values=[]
        if operation=='eq':values=[literal()]
        elif operation=='in':
            take('punct','(');values.append(literal())
            while cursor<len(tokens) and tokens[cursor]==('punct',','):
                take('punct',',');values.append(literal())
            take('punct',')')
        else:raise LinkRefused('Unsupported URL filter operator: '+operation)
        if len({v['kind'] for v in values})!=1:raise LinkRefused('Mixed URL filter literal types')
        result.append({'table':table,'field':field,'operator':'IN','values':values})
        if len(result)>12 or len(values)>64:raise LinkRefused('URL filter exceeds its restriction bound')
        if cursor<len(tokens):
            take('name','and')
            if cursor==len(tokens):raise LinkRefused('Incomplete URL filter after conjunction')
    if not result:raise LinkRefused('Empty URL filter')
    return result


def guid(value):
    try:return str(UUID(value))
    except (ValueError,AttributeError,TypeError):raise LinkRefused('Invalid report or workspace identifier') from None


def parse(link):
    if not isinstance(link,str) or not 1<=len(link)<=8000:
        raise LinkRefused('Report link exceeds its bound')
    try:
        url=urlsplit(link)
        port=url.port
    except ValueError:
        raise LinkRefused('Malformed report link') from None
    if (url.scheme!='https' or url.hostname!='app.powerbi.com' or url.username or
            url.password or port not in (None,443) or url.fragment):
        raise LinkRefused('Unsupported report link origin or fragment')
    pairs=parse_qsl(url.query,keep_blank_values=True)
    params={}
    for key,value in pairs:
        if key in params:raise LinkRefused('Repeated report link parameter: '+key)
        if key not in ('reportId','pageName','filter','$filter','bookmarkGuid','ctid','experience','autoAuth'):
            raise LinkRefused('Unrecognised report link parameter: '+key)
        params[key]=value
    if 'filter' in params and '$filter' in params:raise LinkRefused('Repeated URL filter declaration')
    path=re.fullmatch(r'/groups/([^/]+)/reports/([^/]+)(?:/([A-Za-z0-9_-]+))?/?',url.path)
    if path:
        workspace=None if path[1]=='me' else guid(path[1]);report=guid(path[2]);page=path[3]
        if 'reportId' in params and guid(params['reportId'])!=report:
            raise LinkRefused('Conflicting report identifiers in link')
        if 'pageName' in params and page is not None and params['pageName']!=page:
            raise LinkRefused('Conflicting report pages in link')
        page=page or params.get('pageName')
    elif url.path=='/reportEmbed' and 'reportId' in params:
        workspace=None;report=guid(params['reportId']);page=params.get('pageName')
    else:raise LinkRefused('Unsupported report link path')
    if page is not None and not re.fullmatch('[A-Za-z0-9_-]{1,200}',page):
        raise LinkRefused('Unsupported page identifier')
    if 'ctid' in params:guid(params['ctid'])
    bookmark=params.get('bookmarkGuid')
    if bookmark is not None and not re.fullmatch('[A-Za-z0-9_-]{1,200}',bookmark):
        raise LinkRefused('Unsupported bookmark reference')
    expression=params.get('filter',params.get('$filter'))
    restrictions=predicates(expression) if expression is not None else []
    if bookmark is not None and expression is not None:
        raise LinkRefused('Bookmark and URL-filter precedence is not established')
    return {'provenance':'SHARED_URL','workspace_id':workspace,'report_id':report,
            'page_id':page,'bookmark_reference':bookmark,'predicates':restrictions,
            'claims_active_user_state':False}
