import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from preview_lookup import general_image,preview_candidates,AUTH,NO_IMAGE
class PreviewTests(unittest.TestCase):
 def test_ratings(self):
  for item in ({'nsfwLevel':1},{'nsfwLevel':'None'},{'browsingLevel':1}):self.assertTrue(general_image(item))
  for item in ({},{'nsfwLevel':2},{'browsingLevel':3},{'nsfwLevel':1,'nsfw':True},{'nsfwLevel':1,'type':'video'}):self.assertFalse(general_image(item))
 def test_fallback_and_hash_check(self):
  sha='a'*64;version={'id':1,'files':[{'hashes':{'SHA256':sha}}],'images':[]}
  good={'url':'https://example.invalid/sample.png','nsfwLevel':'None'}
  with patch('preview_lookup.fetch_json',side_effect=[version,{'items':[]},{**version,'images':[good]}]) as request:
   candidates,error=preview_candidates({'sha':sha},{},'https://civitai.com')
   self.assertEqual(candidates,[good]);self.assertEqual(error,'')
   self.assertIn('civitai.red',request.call_args_list[-1].args[0])
  with patch('preview_lookup.fetch_json',return_value={'files':[],'images':[good]}):
   self.assertEqual(preview_candidates({'sha':sha},{},'https://civitai.com'),([],NO_IMAGE))
 def test_auth_and_offline(self):
  with patch('preview_lookup.fetch_json',side_effect=HTTPError('https://example.invalid',401,'Unauthorized',{},None)):
   self.assertEqual(preview_candidates({'sha':'a'*64},{},'https://civitai.com'),([],AUTH))
  with patch('preview_lookup.fetch_json') as request:
   preview_candidates({'sha':'a'*64},{},'https://civitai.com',False);request.assert_not_called()
