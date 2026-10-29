#!/usr/bin/env python3
"""Let It Glow LAN audio sync v0.3 - standard library only."""
import json, mimetypes, os, re, time, urllib.request, threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit
PORT=int(os.getenv('LIG_PORT','8098'))
FPP_API=os.getenv('LIG_FPP_API','http://127.0.0.1/api/fppd/status')
MEDIA=Path(os.getenv('LIG_MEDIA_DIR','/home/fpp/media/music')).resolve()
ALLOWED={'.mp3','.wav','.ogg','.m4a','.aac','.flac'}
HTML=Path(__file__).with_name('index.html').read_bytes()
lock=threading.Lock()
cache={'at':0,'data':None}
def find(obj,keys):
    if isinstance(obj,dict):
        for k in keys:
            if k in obj and obj[k] not in (None,''):return obj[k]
        for v in obj.values():
            x=find(v,keys)
            if x is not None:return x
    elif isinstance(obj,list):
        for v in obj:
            x=find(v,keys)
            if x is not None:return x
    return None
def snapshot():
    now=time.monotonic()
    with lock:
        if cache['data'] is not None and now-cache['at']<0.15:
            return dict(cache['data'],serverTime=time.time())
        try:
            with urllib.request.urlopen(FPP_API,timeout=1.5) as r: data=json.load(r)
        except Exception as e:return {'ok':False,'error':'FPP API niet bereikbaar: '+str(e),'serverTime':time.time()}
        media=find(data,['mediaName','mediaFilename','mediaFile','media'])
        if isinstance(media,dict):media=find(media,['mediaName','name','filename'])
        if not isinstance(media,str):media=None
        elapsed=find(data,['secondsElapsed','secondsPlayed','elapsedSeconds','elapsed'])
        if media:
            media=Path(media).name
            p=(MEDIA/media).resolve()
            if not p.is_file() or p.parent!=MEDIA or p.suffix.lower() not in ALLOWED:media=None
        try:elapsed=max(0,float(elapsed))
        except (ValueError,TypeError):elapsed=0
        status=str(find(data,['status_name','status']) or '')
        if any(x in status.lower() for x in ('idle','stopped','stopping')):media=None
        snap={'ok':True,'media':media,'elapsed':elapsed,'title':find(data,['mediaTitle']) or media or 'Geen nummer','rawStatus':status[:80], 'sampleTime':time.time()}
        cache.update(at=time.monotonic(),data=snap)
        return dict(snap,serverTime=time.time())
class Handler(BaseHTTPRequestHandler):
    def reply(self,code,body,typ):
        self.send_response(code)
        self.send_header('Content-Type',typ)
        self.send_header('Cache-Control','no-store, max-age=0')
        self.send_header('Content-Length',str(len(body)))
        self.end_headers();self.wfile.write(body)
    def do_GET(self):
        p=urlsplit(self.path).path
        if p=='/':return self.reply(200,HTML,'text/html; charset=utf-8')
        if p=='/api/status':return self.reply(200,json.dumps(snapshot()).encode(),'application/json')
        if p.startswith('/media/'):
            name=unquote(p[7:]);path=(MEDIA/name).resolve()
            if not name or '/' in name or '\\' in name or path.parent!=MEDIA or path.suffix.lower() not in ALLOWED or not path.is_file():return self.send_error(404)
            size=path.stat().st_size;start=0;end=size-1
            rng=self.headers.get('Range','')
            if rng:
                m=re.fullmatch(r'bytes=(\d*)-(\d*)',rng)
                if not m:return self.send_error(416)
                if m.group(1):start=int(m.group(1));end=int(m.group(2)) if m.group(2) else end
                elif m.group(2):start=max(0,size-int(m.group(2)))
                if start>=size or end<start:return self.send_error(416)
                end=min(end,size-1)
            self.send_response(206 if rng else 200)
            self.send_header('Content-Type',mimetypes.guess_type(path.name)[0] or 'application/octet-stream')
            self.send_header('Accept-Ranges','bytes');self.send_header('Cache-Control','no-store')
            self.send_header('Content-Length',str(end-start+1))
            if rng:self.send_header('Content-Range',f'bytes {start}-{end}/{size}')
            self.end_headers()
            try:
                with path.open('rb') as f:
                    f.seek(start);remaining=end-start+1
                    while remaining:
                        chunk=f.read(min(65536,remaining))
                        if not chunk:break
                        self.wfile.write(chunk);remaining-=len(chunk)
            except (BrokenPipeError,ConnectionResetError):pass
            return
        self.send_error(404)
    def log_message(self,fmt,*args):pass
if __name__=='__main__':
    print(f'Let It Glow Audio v0.3 at http://0.0.0.0:{PORT}',flush=True)
    ThreadingHTTPServer(('0.0.0.0',PORT),Handler).serve_forever()
