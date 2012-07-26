# -*- coding: utf-8 -*-
'''
Created on Jul 6, 2012
@author: nyan
'''
from oauth2 import Client, Consumer, Token
import httplib2
from urlparse import parse_qsl
import urllib
import json

class TumblrException(Exception):
    pass

class Tumblr(object):
    base_url = 'api.tumblr.com/v2'
    request_token_url = 'http://www.tumblr.com/oauth/request_token'
    authorize_url = 'http://www.tumblr.com/oauth/authorize'
    access_token_url = 'http://www.tumblr.com/oauth/access_token'
    
    def __init__(self, consumer=None, token=None, client_kwargs={}, headers={}, callback_url=None, verifier=None):
        self.headers = headers
        self.callback_url = callback_url
        if 'User-Agent' not in self.headers:
            self.headers['User-Agent'] = 'Tumblr Python Library'
        if consumer and token:
            self.consumer = Consumer(**consumer)
            self.token = Token(token['oauth_token'], token['oauth_token_secret'])
            if verifier:
                self.token.set_verifier(verifier)
            self.client = Client(self.consumer, self.token, **client_kwargs)
        elif consumer:
            self.consumer = Consumer(**consumer)
            self.token = None
            self.client = Client(self.consumer, **client_kwargs)
        else:
            self.consumer = None
            self.token = None
            self.client = httplib2.Http(**client_kwargs)
    
    def request_token(self):
        callback_url = self.callback_url or 'oob'
        resp, content = self.client.request(self.request_token_url, 'POST', headers=self.headers)
        if resp['status'] != '200':
            raise TumblrException
        request_tokens = dict(parse_qsl(content))
        request_tokens['oauth_callback'] = callback_url
        redirect_url = self.authorize_url + '?' + urllib.urlencode(request_tokens)
        return (request_tokens, redirect_url)
        
    def authorized_token(self):
        resp, content = self.client.request(self.access_token_url, 'POST', headers=self.headers)
        if resp['status'] != '200':
            print resp
            print content
        return dict(parse_qsl(content))
    
    def blog(self, hostname, call, method='get', **kwargs):
        kwargs['api_key'] = self.consumer.key
        if method.lower() == 'get':
            uri = 'http://{baseurl}/blog/{hostname}{call}?{qs}'.format(baseurl=self.base_url, hostname=hostname, call=call, qs=urllib.urlencode(kwargs))
            body = ''
        else:
            uri = 'http://{baseurl}/blog/{hostname}{call}'.format(baseurl=self.base_url, hostname=hostname, call=call)
            body = urllib.urlencode(kwargs)
        
        print "%s: %s" % (method.upper(), uri)
        _resp, answ = self.client.request(uri, method.upper(), body, headers=self.headers)
        answ = json.loads(answ)
        if answ['meta']['status'] != 200:
            raise TumblrException(repr(answ))
        else:
            return answ['response']
    def user(self, call, method='get', **kwargs):
        kwargs['api_key'] = self.consumer.key
        if method.lower() == 'get':
            uri = 'http://{baseurl}/user{call}{qs}'.format(baseurl=self.base_url, call=call, qs=('?' + urllib.urlencode(kwargs)) if kwargs.keys() else '')
            body = ''
        else:
            uri = 'http://{baseurl}/user{call}'.format(baseurl=self.base_url, call=call)
            body = urllib.urlencode(kwargs)
        print "%s: %s [%s]" % (method.upper(), uri, body)
        _resp, answ = self.client.request(uri, method.upper(), body, headers=self.headers)
        answ = json.loads(answ)
        if answ['meta']['status'] != 200:
            raise TumblrException(repr(answ))
        else:
            return answ['response']

if __name__ == '__main__':
    from nyancast.tumblr import consumer, token
    from pprint import pprint as pp
    tumblr = Tumblr(consumer, token)
    pp(tumblr.blog('nyancast.tumblr.com', '/followers'))
    pp(tumblr.user('/info'))
    pp(tumblr.user('/following'))
    