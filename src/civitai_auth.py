"""Experimental public-client OAuth. Credentials are session-only."""
import base64,hashlib,json,secrets,time,threading,webbrowser
from http.server import HTTPServer,BaseHTTPRequestHandler
from urllib.parse import urlencode,urlparse,parse_qs
from urllib.request import Request,build_opener,HTTPRedirectHandler
STATUS='Not connected'
TOKEN='';EXPIRES=0;GENERATION=0;LOGIN_LOCK=threading.Lock()
REDIRECT='http://localhost:47831/oauth/callback'
BASE='https://auth.civitai.com/api/auth/oauth/'
class NoRedirect(HTTPRedirectHandler):
 def redirect_request(self,*args):return None
def clear():
 global TOKEN,EXPIRES,GENERATION
 TOKEN='';EXPIRES=0;GENERATION+=1
def bearer():
 return TOKEN if time.time()<EXPIRES else ''
def rejection_detail(exc):
 try:
  raw=exc.read(65536)
 except Exception:return 'response_unavailable'
 if str(getattr(exc,'headers',{}).get('cf-mitigated','')).lower()=='challenge':return 'cloudflare_challenge'
 try:
  data=json.loads(raw)
 except Exception:
  text=raw.decode('utf-8',errors='replace').lower()
  return 'cloudflare_challenge' if 'cloudflare' in text or 'just a moment' in text else 'non_json_rejection'
 allowed={'invalid_grant','invalid_client','invalid_request','unsupported_grant_type','invalid_scope','INVALID_ORIGIN','MISSING_ORIGIN','UNAUTHORIZED_CLIENT','INVALID_CODE','INVALID_CODE_VERIFIER','ACCESS_DENIED','FORBIDDEN'}
 for key in ('error','code'):
  value=data.get(key)
  if isinstance(value,str) and value in allowed:return value
 # Classify only; never expose arbitrary response text or credentials.
 text=str(data.get('error_description',''))+' '+str(data.get('message',''))
 if 'origin' in text.lower():return 'origin_rejected'
 if 'client' in text.lower() and 'public' in text.lower():return 'public_client_rejected'
 return 'unclassified_json_rejection'

def login(client_id,notify):
 global TOKEN,EXPIRES,STATUS
 original_notify=notify
 def notify(ok,message):
  global STATUS
  STATUS=message
  original_notify(ok,message)
 if not LOGIN_LOCK.acquire(blocking=False):notify(False,'Another authorization is already in progress.');return
 generation=GENERATION
 verifier=secrets.token_urlsafe(48);state=secrets.token_urlsafe(32)
 challenge=base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).decode().rstrip('=')
 result={}
 class Callback(BaseHTTPRequestHandler):
  def log_message(self,*args):pass
  def do_GET(self):
   parsed=urlparse(self.path);q=parse_qs(parsed.query)
   valid=parsed.path=='/oauth/callback' and secrets.compare_digest(q.get('state',[''])[0],state)
   if not valid:
    self.send_response(400);self.end_headers();self.wfile.write(b'Invalid callback.');return
   result.update(code=q.get('code',[''])[0],error=bool(q.get('error')))
   self.send_response(200);self.send_header('Content-Type','text/plain; charset=utf-8');self.end_headers()
   self.wfile.write(b'Authorization code received. Return to Model Library Organizer to check whether connection succeeded.')
 try:
  with HTTPServer(('127.0.0.1',47831),Callback) as server:
   server.timeout=1
   url=BASE+'authorize?'+urlencode(dict(response_type='code',client_id=client_id,redirect_uri=REDIRECT,scope='37',state=state,code_challenge=challenge,code_challenge_method='S256'))
   if not webbrowser.open(url):raise RuntimeError('browser')
   deadline=time.monotonic()+180
   while not result and time.monotonic()<deadline:server.handle_request()
  if not result.get('code'):notify(False,'Authorization cancelled or timed out.');return
  request=Request(BASE+'token',data=urlencode(dict(grant_type='authorization_code',code=result['code'],code_verifier=verifier,client_id=client_id,redirect_uri=REDIRECT)).encode(),headers={'Content-Type':'application/x-www-form-urlencoded','Origin':'http://localhost:47831','Accept':'application/json','User-Agent':'ModelLibraryOrganizer/1.0'})
  with build_opener(NoRedirect()).open(request,timeout=20) as response:
   raw=response.read(1024*1024+1)
   if len(raw)>1024*1024:raise ValueError('response size')
   data=json.loads(raw)
  token=data.get('access_token','');seconds=min(3600,max(0,int(data.get('expires_in',0))))
  if not isinstance(token,str) or not token or '\r' in token or '\n' in token or seconds<=0:raise ValueError('token')
  if int(data.get('scope',0))&37!=37:raise ValueError('missing UserRead / ModelsRead / MediaRead permissions')
  if generation!=GENERATION:notify(False,'Authorization was cancelled locally.');return
  TOKEN=token;EXPIRES=time.time()+seconds
  notify(True,'Connected for this session (up to 1 hour). Select a model to retry its preview.')
 except Exception as exc:
  clear()
  code=getattr(exc,'code',None)
  reason=''
  if code:reason=': '+rejection_detail(exc)
  elif isinstance(exc,ValueError) and str(exc)=='missing UserRead / ModelsRead / MediaRead permissions':
   reason=': enable UserRead, ModelsRead and MediaRead in OAuth Apps, then reconnect'
  notify(False,'Civitai token exchange failed'+(' (HTTP '+str(code)+')' if code else ' ('+type(exc).__name__+')')+reason+'.')

 finally:LOGIN_LOCK.release()
