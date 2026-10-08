import unittest,time,json

from unittest.mock import patch,MagicMock

import civitai_auth as auth,network

class AuthTests(unittest.TestCase):

 def tearDown(self):

  auth.clear();network.OFFLINE=False;network.COOLDOWN.clear()

 def test_recover_source_after_earlier_unknown(self):

  from features import enrich

  engine=MagicMock();engine.cache={'details':{'abc':{'status':'SHA256一致'}}}

  row={'sha':'abc','url':''}

  version={'modelId':2991085,'id':3391775,'files':[{'hashes':{'SHA256':'abc'}}]}

  with patch('features.fetch_json',side_effect=[version,{}]):

   enrich(engine,row,'https://civitai.red')

  self.assertEqual(row['url'],'https://civitai.red/models/2991085?modelVersionId=3391775')

 def test_safe_rejection_details(self):
  import io
  from urllib.error import HTTPError
  for body,expected in [(b'{"code":"INVALID_ORIGIN"}','INVALID_ORIGIN'),(b'{"message":"origin not allowed secret-token"}','origin_rejected'),(b'<html>Cloudflare</html>','cloudflare_challenge'),(b'{"message":"secret-token"}','unclassified_json_rejection')]:
   error=HTTPError('https://auth.civitai.com',403,'Forbidden',{},io.BytesIO(body))
   self.assertEqual(auth.rejection_detail(error),expected)
 def test_bearer_expiry(self):

  auth.TOKEN='secret';auth.EXPIRES=time.time()+60

  self.assertEqual(auth.bearer(),'secret')

  auth.EXPIRES=0;self.assertEqual(auth.bearer(),'')

 def test_host_isolation_and_no_redirect(self):

  auth.TOKEN='secret';auth.EXPIRES=time.time()+60

  with patch('urllib.request.build_opener') as build:

   build.return_value.open.return_value.__enter__.return_value.read.return_value=b'{}'

   for url,expected in [('https://civitai.com/api/v1/images',True),('https://civitai.red/api/v1/images',True),('https://huggingface.co/api/models',False),('https://civitai.com.evil.invalid/api/v1/images',False),('https://civitai.com/other',False)]:

    network.request_json(url)

    req=build.return_value.open.call_args.args[0]

    self.assertEqual(req.get_header('Authorization'), 'Bearer secret' if expected else None)

    if expected:self.assertIsInstance(build.call_args.args[0],auth.NoRedirect)

  self.assertNotIn('secret',str(network.diagnostics()))

 def test_offline(self):

  network.OFFLINE=True

  with patch('urllib.request.build_opener') as build:

   with self.assertRaises(RuntimeError):network.request_json('https://civitai.com/api/v1/images')

   build.assert_not_called()

 def test_pkce_exchange(self):

  from urllib.parse import urlparse,parse_qs

  class Server:

   timeout=0

   def __init__(self,address,handler):self.handler=handler

   def __enter__(self):return self

   def __exit__(self,*args):pass

   def handle_request(self):

    callback=object.__new__(self.handler)

    callback.path='/oauth/callback?code=demo&state='+state['value']

    callback.send_response=MagicMock();callback.send_header=MagicMock();callback.end_headers=MagicMock();callback.wfile=MagicMock()

    callback.do_GET()

  state={}

  def browser(url):

   q=parse_qs(urlparse(url).query);state['value']=q['state'][0]

   self.assertEqual(q['scope'],['37']);self.assertEqual(q['code_challenge_method'],['S256'])

   self.assertEqual(len(q['code_challenge'][0]),43);return True

  with patch.object(auth,'HTTPServer',Server),patch.object(auth.webbrowser,'open',browser),patch.object(auth,'build_opener') as build:

   build.return_value.open.return_value.__enter__.return_value.read.return_value=json.dumps(dict(access_token='test-token',expires_in=3600,scope='37')).encode()

   results=[];auth.login('public-client',lambda *args:results.append(args))

   self.assertTrue(results[0][0]);self.assertEqual(auth.bearer(),'test-token')

   req=build.return_value.open.call_args.args[0]

   self.assertEqual(req.get_header('Origin'),'http://localhost:47831')

   q=parse_qs(req.data.decode());self.assertIn('code_verifier',q);self.assertNotIn('client_secret',q)

if __name__=='__main__':unittest.main()

