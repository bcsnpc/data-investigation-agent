"""SELECT compiler over actual discovered schema only, no business literals."""
import datetime,decimal

def q(v):
 if not isinstance(v,str) or not v or len(v)>128:raise ValueError('EXPORT_IDENTIFIER')
 return '['+v.replace(']',']]')+']'
def select(schema,table,columns,*,fabric):
 expressions=[];names=[]
 for c in columns:
  col=q(c['name']);kind=c['logical_type'];names.append(c['name'])
  if kind=='BINARY':col='CONVERT(varchar(max),'+col+',2)'
  elif kind in ('DATE','DATETIME'):col='CONVERT(varchar(40),'+col+',127)'
  elif kind=='DECIMAL':col='CONVERT(varchar(100),'+col+(',2)' if c.get('native_type','').lower() in ('money','smallmoney') else ')')
  elif kind=='REAL':col='CONVERT(varchar(100),'+col+',3)'
  expressions.append(col+' AS '+q(c['name']))
 # Existing Fabric worker appends the three self-report columns itself.
 return {'query':'SELECT '+','.join(expressions)+' FROM '+q(schema)+'.'+q(table),'result_columns':names,'max_rows':10000,'parameters':[],'read_only_objects':[q(schema)+'.'+q(table)],'require_read_only':True,'response_mode':'records'}
def decode(v,kind):
 if v is None:return None
 if kind=='TEXT':return v
 if kind=='INTEGER':return int(v)
 if kind=='REAL':return float(v)
 if kind=='DECIMAL':return decimal.Decimal(v)
 if kind=='DATE':datetime.date.fromisoformat(v);return v
 if kind=='DATETIME':datetime.datetime.fromisoformat(v);return v
 if kind=='BINARY':return bytes.fromhex(v)
 if kind=='BOOLEAN':
  if v not in ('True','False','1','0'):raise ValueError('EXPORT_BOOLEAN')
  return v in ('True','1')
 raise ValueError('EXPORT_TYPE_UNSUPPORTED')
