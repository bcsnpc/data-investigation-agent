"""On-device positional OCR. No model, estate read, or temporary image file."""
import base64,json,math,subprocess
from pathlib import Path

def validate(value):
    if (not isinstance(value,dict)or value.get('engine')!='Windows.Media.Ocr' or
            not isinstance(value.get('lines'),list)or len(value['lines'])>400):
        raise ValueError('LOCAL_OCR_RESPONSE_INVALID')
    width,height=value.get('width'),value.get('height')
    if type(width)is not int or type(height)is not int or not 1<=width<=5000 or not 1<=height<=5000:
        raise ValueError('LOCAL_OCR_DIMENSIONS_INVALID')
    total=0
    for line in value['lines']:
        if not isinstance(line,dict)or not isinstance(line.get('text'),str)or '\x00'in line['text']:raise ValueError('LOCAL_OCR_TEXT_INVALID')
        if not isinstance(line.get('words'),list)or len(line['words'])>1000:raise ValueError('LOCAL_OCR_WORD_BOUND_INVALID')
        total+=len(line['text'])
        for item in [line,*line.get('words',[])]:
            if not isinstance(item,dict)or not isinstance(item.get('text'),str)or len(item['text'])>16000:raise ValueError('LOCAL_OCR_WORD_INVALID')
            r=item.get('region')
            if not isinstance(r,dict):raise ValueError('LOCAL_OCR_REGION_INVALID')
            if (set(r)!={'x','y','width','height'}or any(type(n)not in(int,float)or not math.isfinite(n)for n in r.values())or
                    min(r.values())<0 or r['x']+r['width']>width+1 or r['y']+r['height']>height+1):
                raise ValueError('LOCAL_OCR_REGION_INVALID')
    if total>16000:raise ValueError('LOCAL_OCR_TEXT_BOUND_EXCEEDED')
    return value

def read(raw,mime):
    from .screenshot_intake import inspect_image
    inspect_image(raw,mime)
    command=['powershell.exe','-NoProfile','-NonInteractive','-ExecutionPolicy','Bypass','-File',str(Path(__file__).with_name('windows_ocr.ps1'))]
    result=subprocess.run(command,input=json.dumps({'base64':base64.b64encode(raw).decode()}),capture_output=True,text=True,encoding='utf8',timeout=45)
    if result.returncode:raise ValueError('LOCAL_OCR_UNAVAILABLE: '+result.stderr[-1200:])
    return validate(json.loads(result.stdout.lstrip('\ufeff')))
