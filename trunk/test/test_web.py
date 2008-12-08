import unittest
import webtest

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import main

from google.appengine.api import apiproxy_stub_map
from google.appengine.api import datastore_file_stub

def clear_datastore():
   # Use a fresh stub datastore.
   apiproxy_stub_map.apiproxy = apiproxy_stub_map.APIProxyStubMap()
   stub = datastore_file_stub.DatastoreFileStub(
           'appid', '/dev/null', '/dev/null')
   apiproxy_stub_map.apiproxy.RegisterStub('datastore_v3', stub)


class _Common(unittest.TestCase):

  def setUp(self):
      clear_datastore()
      self.application = main.application()
      self.app = webtest.TestApp(self.application)
      os.environ['USER_EMAIL'] = 'foo@bar.baz'


class MainTest(_Common):

  def test_default_page(self):
      response = self.app.get('/')
      self.assertEqual('200 OK', response.status)
      self.assertTrue('What do you want' in response)

  def test_wrong(self):
      response = self.app.get('/?do=zap')
      self.assertEqual('200 OK', response.status)
      self.assertTrue('Sorry' in response)

  def test_page_with_param(self):
      response = self.app.get('/?do=lookup%20Bob')
      self.assertEqual('200 OK', response.status)
      self.assertTrue('Oops' in response)

  def test_page_remember(self):
      response = self.app.get('/?do=remember%20Bob%20is%20your%20uncle')
      self.assertEqual('200 OK', response.status)
      self.assertTrue('OK, remembering' in response)
      response = self.app.get('/?do=lookup%20Bob')
      self.assertEqual('200 OK', response.status)
      self.assertTrue('Found 1' in response)
      response = self.app.get('/?do=remember%20Sue%20is%20your%20aunt')
      self.assertEqual('200 OK', response.status)
      self.assertTrue('OK, remembering' in response)
      response = self.app.get('/?do=lookup%20Bob')
      self.assertEqual('200 OK', response.status)
      self.assertTrue('Found 1' in response)
      response = self.app.get('/?do=l%20Bob')
      self.assertEqual('200 OK', response.status)
      self.assertTrue('Found 1' in response)

  '''
  def DONT_test_separate_users(self):
      # TODO: enable when Users are implemented (soon!)
      os.environ['USER'] = 'someuser'
      response = self.app.get('/?do=remember%20Bob%20is%20your%20uncle')
      self.assertEqual('200 OK', response.status)
      self.assertTrue('OK, remembering' in response)
      response = self.app.get('/?do=lookup%20Bob')
      self.assertEqual('200 OK', response.status)
      self.assertTrue('Found 1' in response)
      del os.environ['USER']
      response = self.app.get('/?do=l%20Bob')
      self.assertEqual('200 OK', response.status)
      self.assertTrue('Oops' in response)
      os.environ['USER'] = 'another'
      response = self.app.get('/?do=l%20Bob')
      self.assertEqual('200 OK', response.status)
      self.assertTrue('Oops' in response)
      os.environ['USER'] = 'someuser'
      response = self.app.get('/?do=lookup%20Bob')
      self.assertEqual('200 OK', response.status)
      self.assertTrue('Found 1' in response)
  '''

  def _keytest(self, verb):
      response = self.app.get('/?do=%s%%20#1' % verb)
      self.assertEqual('200 OK', response.status)
      self.assertTrue('Sorry' in response)
      response = self.app.get('/?do=%s%%20#2' % verb)
      self.assertEqual('200 OK', response.status)
      response = self.app.get('/?do=%s%%202' % verb)
      self.assertEqual('200 OK', response.status)
      response = self.app.get('/?do=%s%%20#foo' % verb)
      self.assertEqual('200 OK', response.status)
      self.assertTrue('Sorry' in response)

  def test_zaza(self):
      for verb in 'z', 'zaza':
        self._keytest(verb)

  def test_forget(self):
      for verb in 'f', 'forget':
        self._keytest(verb)


class BareTest(_Common):

  def test_default_page(self):
      response = self.app.get('/bare')
      self.assertEqual('200 OK', response.status)
      self.assertTrue('Search' in response)

  def test_page_with_param(self):
      response = self.app.get('/bare?search=Bob')
      self.assertEqual('200 OK', response.status)
      self.assertTrue('Found 0:' in response)

  def test_create(self):
      response = self.app.post('/bare', dict(create="Bob's your uncle"))
      self.assertEqual('200 OK', response.status)
      self.assertTrue('Created' in response)
      response = self.app.get('/bare?search=Bob')
      self.assertEqual('200 OK', response.status)
      self.assertTrue('Found 1:' in response)
      self.assertTrue('uncle' in response)

