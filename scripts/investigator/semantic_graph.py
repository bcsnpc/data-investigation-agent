"""Conservative DAX reference analysis, never a DAX evaluator or SQL translator."""
import re

VERSION = 'references-v1'
TOKEN = re.compile(r'''(?P<space>\s+)|(?P<comment>//[^\n]*|--[^\n]*|/\*[\s\S]*?\*/)|(?P<string>"(?:[^"]|"")*")|(?P<table>'(?:[^']|'')*')|(?P<ref>\[(?:[^\]]|\]\])*\])|(?P<name>[A-Za-z_][A-Za-z_0-9]*)|(?P<number>\d+(?:\.\d+)?)|(?P<operator>[(),+*/=<>!&|^{}.;:-])''')
OPERATIONS = {'SUM':'ADDITIVE','COUNTROWS':'COUNT','COUNT':'COUNT','DISTINCTCOUNT':'DISTINCT_COUNT',
              'DIVIDE':'RATIO','CALCULATE':'FILTERED_MEASURE','HASONEVALUE':'FILTER_CONTEXT',
              'IF':'CONDITIONAL','USERELATIONSHIP':'RELATIONSHIP_SWITCH','DATEADD':'TIME_SHIFT',
              'SAMEPERIODLASTYEAR':'TIME_SHIFT'}


def tokenize(expression):
    if isinstance(expression, list) and all(isinstance(x,str) for x in expression):
        expression='\n'.join(expression)
    if not isinstance(expression,str) or len(expression)>100000:
        return [],['Missing or oversized expression']
    tokens=[];gaps=[];position=0
    while position<len(expression):
        match=TOKEN.match(expression,position)
        if not match:
            gaps.append('Unrecognized expression syntax');break
        position=match.end()
        if match.lastgroup not in ('space','comment'):
            tokens.append((match.lastgroup,match.group()))
    return tokens,gaps


def analyze(assets):
    tables={a['id']:a['name'] for a in assets if a['kind']=='SemanticTable'}
    measures=[a for a in assets if a['kind']=='Measure']
    columns=[a for a in assets if a['kind']=='SemanticColumn']
    index={}
    for a in measures+columns:
        index.setdefault(a['name'].casefold(),[]).append(a)
    nodes={}
    for measure in measures:
        tokens,gaps=tokenize(measure['metadata'].get('expression'))
        dependencies=set();references=set();operations=set();functions=set()
        for i,(kind,value) in enumerate(tokens):
            if kind in ('name','table') and not (i+1<len(tokens) and tokens[i+1][1]=='('):
                table_name=value[1:-1].replace("''", "'") if kind=='table' else value
                matches=[identity for identity,name in tables.items() if name.casefold()==table_name.casefold()]
                if len(matches)==1:references.add(matches[0])
                if not matches and i>=2 and tokens[i-1][1]=='(' and tokens[i-2][1].upper()=='COUNTROWS':
                    gaps.append('Unresolved table reference: '+value)
                if kind=='name' and value.upper() in ('VAR','RETURN'):
                    gaps.append('Variable context analysis unavailable')
            if kind=='name' and i+1<len(tokens) and tokens[i+1][1]=='(':
                functions.add(value.upper())
                if value.upper() in OPERATIONS:operations.add(OPERATIONS[value.upper()])
            if kind=='operator' and value in ('+','-','*','/'):
                operations.add('DERIVED_ARITHMETIC')
            if kind!='ref':continue
            name=value[1:-1].replace(']]',']').casefold()
            qualifier=None
            if i and tokens[i-1][0] in ('table','name'):
                qualifier=tokens[i-1][1]
                if tokens[i-1][0]=='table':qualifier=qualifier[1:-1].replace("''", "'")
            candidates=index.get(name,[])
            if qualifier is not None:
                candidates=[a for a in candidates if tables.get(a['parent_id'],'').casefold()==qualifier.casefold()]
            else:
                # Unqualified columns can depend on row context. Never guess
                # a measure when a column of the same name is also possible.
                candidates=[a for a in candidates if a['kind']=='Measure' or a['parent_id']==measure['parent_id']]
            if len(candidates)!=1:
                gaps.append('Unresolved or ambiguous reference: '+value);continue
            a=candidates[0];references.add(a['id'])
            if a['kind']=='Measure':dependencies.add(a['id'])
        unknown=sorted(functions-OPERATIONS.keys())
        if unknown:gaps.append('Operation analysis unavailable: '+', '.join(unknown))
        if dependencies:operations.add('MEASURE_DEPENDENCY')
        nodes[measure['id']]={'id':measure['id'],'name':measure['name'],'hash':measure['content_hash'],
            'dependencies':sorted(dependencies),'references':sorted(references),'operations':sorted(operations),
            'gaps':sorted(set(gaps)),'provenance':'DERIVED_DETERMINISTICALLY',
            'native_queryability':'UNKNOWN','upstream_reconciliation':'UNKNOWN'}
    # Bounded reachability detects cycles without recursive Python calls.
    for identity,node in nodes.items():
        pending=list(node['dependencies']);seen=set()
        while pending:
            child=pending.pop()
            if child==identity:
                node['gaps'].append('Cyclic measure dependency');break
            if child in seen:continue
            seen.add(child);pending.extend(nodes.get(child,{}).get('dependencies',[]))
        node['dependency_state']='PARTIAL' if node['gaps'] else 'SUPPORTED'
    # A parent's recursive graph is partial when any descendant is partial.
    changed=True
    while changed:
        changed=False
        for node in nodes.values():
            if node['dependency_state']=='SUPPORTED' and any(nodes[d]['dependency_state']!='SUPPORTED' for d in node['dependencies']):
                node['dependency_state']='PARTIAL';node['gaps'].append('Dependency has analysis gaps');changed=True
    relationships=[{'id':a['id'],'hash':a['content_hash'],'definition':a['metadata'],
                    'execution_context_verified':False} for a in assets if a['kind']=='SemanticRelationship']
    return {'version':VERSION,'measures':nodes,'relationships':relationships,
            'dependency_state':'SUPPORTED' if nodes and all(n['dependency_state']=='SUPPORTED' for n in nodes.values()) else 'PARTIAL',
            'limitation':'Reference discovery and operation labels only; Power BI executes DAX. No filter propagation or upstream equivalence is certified.'}


def affected(changes, *graphs):
    reached=set(changes)
    while True:
        additions={node['id'] for graph in graphs if graph for node in graph['measures'].values()
                   if set(node['references']) & reached}
        if additions<=reached:break
        reached|=additions
    all_measures={identity for graph in graphs if graph for identity in graph['measures']}
    return sorted(reached & all_measures)
