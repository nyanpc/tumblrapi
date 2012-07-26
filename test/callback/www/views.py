# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
from tumblr import Tumblr

from nyancast.tumblr import consumer
from django.core.urlresolvers import reverse

def make_tumblr(request, token=None, verifier=None):
    return Tumblr(consumer, token, callback_url=request.build_absolute_uri(reverse('www.views.done')), verifier=verifier)

def start(request):
    tumblr = make_tumblr(request)
    token, url = tumblr.request_token()
    request.session['auth_props'] = token
    return HttpResponseRedirect(url)

def done(request):
    tumblr = make_tumblr(request, request.session['auth_props'], request.GET.get('oauth_verifier'))
    del request.session['auth_props']
    print tumblr.authorized_token()
    return HttpResponse('OK')