import unittest,io,json,urllib.error
from unittest.mock import patch
import network
from providers import lookup,hf_lookup,AUTO

class ProviderTests(unittest.TestCase):
 def setUp(self):network.RECORDS.clear();network.COOLDOWN.clear()
 def test_hf_exact_hash(self):
  sha='f'*64
  with patch('providers.fetch_json',side_effect=[[{'id':'author/model'}],{'siblings':[{'rfilename':'x.safetensors','lfs':{'sha256':sha}}]}]):
   info,status=hf_lookup(sha,'model.safetensors');self.assertEqual(info['source'],'https://huggingface.co/author/model')
 def test_hf_name_not_enough(self):
  with patch('providers.fetch_json',side_effect=[[{'id':'author/model'}],{'siblings':[{'lfs':{'sha256':'wrong'}}]}]):
   self.assertIsNone(hf_lookup('f'*64,'model.safetensors')[0])
 def test_partial_failure_preserved(self):
  with patch('providers.api_lookup',return_value=(None,'通信失敗 (HTTP 403)')),patch('providers.hf_lookup',return_value=({'source':'https://huggingface.co/a/b'},'HF SHA256一致')):
   info,status=lookup('f'*64,'model',AUTO);self.assertEqual({c['site'] for c in info['source_checks']},{'Civitai.red','Civitai.com','Hugging Face','SeaArt','Tensor.Art'});self.assertIn('通信失敗',status)
 def test_rate_limit_pause_and_private_log(self):
  url='https://example.org/api/models?search=privatefilename'
  error=urllib.error.HTTPError(url,429,'limit',{'Retry-After':'60'},None)
  with patch('network.urllib.request.urlopen',side_effect=error) as req:
   with self.assertRaises(urllib.error.HTTPError):network.request_json(url)
   with self.assertRaises(network.ServicePaused):network.request_json(url)
   self.assertEqual(req.call_count,1)
  out=json.dumps(network.diagnostics());self.assertNotIn('privatefilename',out);self.assertIn('429',out)
 def test_404_does_not_pause(self):
  error=urllib.error.HTTPError('https://example.org/test',404,'missing',{},None)
  with patch('network.urllib.request.urlopen',side_effect=error):
   with self.assertRaises(urllib.error.HTTPError):network.request_json('https://example.org/test')
  self.assertFalse(network.COOLDOWN)
 def test_html_response_diagnostic(self):
  class Response(io.BytesIO):pass
  with patch('network.urllib.request.urlopen',return_value=Response(b'<html>Login</html>')):
   with self.assertRaises(RuntimeError):network.request_json('https://example.org/test')
  self.assertEqual(network.diagnostics()[-1]['status'],'JSONDecodeError')
if __name__=='__main__':unittest.main()
