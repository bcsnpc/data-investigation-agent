"""Evidence-backed lexical labels, not a business ontology or name resolver."""
import re

UNUSABLE={'data','information','records','other','something','stuff','things','input','output',
          'source','target','table','column','schema','frame','dataset','joined','result','lookup',
          'silver','gold','bronze','sql','dax','delta','receipt','select','from','where'}
ABSTRACTIONS=('other information','the information before the last check','earlier information',
              'available information','checked information','information feeding','matching records')

def safe_term(term):
    return (isinstance(term,str) and re.fullmatch(r'[A-Za-z]{3,32}(?: [A-Za-z]{3,32}){0,3}',term) is not None
            and all(word.casefold() not in UNUSABLE for word in term.split()))

def validate_terms(terms,contract):
    if not terms:return {}
    if set(terms)!={'subject','matched'}:raise ValueError('Business vocabulary roles differ')
    for value in terms.values():
        if not safe_term(value.get('text')):raise ValueError('Business vocabulary is a technical or unusable label')
        if value.get('definition_hash')!=contract.get('definition_hash') or value.get('definition_asset_id')!=contract.get('definition_asset_id'):
            raise ValueError('Business vocabulary definition differs')
        index=value.get('operation_index');start=value.get('source_start');end=value.get('source_end')
        operations=contract.get('operations',[])
        if type(index)!=int or not 0<=index<len(operations):raise ValueError('Business vocabulary operation differs')
        expression=operations[index].get('expression','')
        if type(start)!=int or type(end)!=int or not 0<=start<end<=len(expression) or expression[start:end]!=value['text']:
            raise ValueError('Business vocabulary has no exact definition span')
        if (start and (expression[start-1].isalnum() or expression[start-1]=='_')) or (end<len(expression) and (expression[end].isalnum() or expression[end]=='_')):
            raise ValueError('Business vocabulary is part of a technical identifier')
    if terms['subject']['text']==terms['matched']['text']:raise ValueError('Business vocabulary roles are ambiguous')
    return terms

def validate_text(text,expected):
    # Closed composition admits no invented domain nouns, arbitrary provider
    # text, identifiers or untraceable substitutions. Procedural/action words
    # are fixed contract language; all interpolated domain labels are grounded.
    if text!=expected:raise ValueError('Business wording differs from evidence-backed composition')
    if any(p in text.casefold() for p in ABSTRACTIONS):raise ValueError('Unintelligible business abstraction')
    if re.search(r'\b(?:silver|gold|bronze|sql|dax|schema|receipt)\b|[A-Za-z]+_[A-Za-z0-9_]+|[A-Za-z0-9.]+[\\/][A-Za-z0-9_.-]+|://|\[[^\]]+\]|\b[A-Za-z]+\.[A-Za-z]+\b|[A-Za-z]:[\\/]|\b[0-9a-f]{8}-[0-9a-f-]{27,}\b|\b[A-Za-z]+[-_][0-9a-f]{6,}\b',text,re.I):
        raise ValueError('Technical identifier in business explanation')
    return text
