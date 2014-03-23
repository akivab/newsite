from google.appengine.api import mail
from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.ext.webapp import template
import logging
import json
from models import *
import urllib, os, re

import jinja2
import webapp2


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

ALLOWED_USERS = ['dan@danbamberger.com',
                 'akiva.bamberger@gmail.com']

def needs_redirect(req):
  if re.search('danbamberger.com', req.request.url):
    req.redirect('http://www.thebambergergroup.com')
    return True
  return False

def get_realplus_listing(listing_text, index, opt_shorten=False):
  listing_data = listing_text.split('|')
  price_color = 'green'
  price = float(listing_data[19])
  text = '<span style="color:%s">$%.02f</span><br/>%s' % (price_color, price, listing_data[38])
  tmp = {
    'link': '/realplus?page=%d' % index,
    'images': listing_data[39:48],
    'text': text if not opt_shorten else text[:550] + '...',
    'title': listing_data[11]
  }
  return tmp

def json_dump(model):
  return {
    'link': model.link,
    'title': model.title,
    'text': model.text,
    'page': model.page,
    'date_posted': model.date_posted,
    'added': str(model.added),
    'ranking': model.ranking,
    'images': model.images[0] if len(model.images) > 0 else '',
    'id': model.key.id()
  }

class NewListingsPageHandler(webapp2.RequestHandler):
  def post(self):
    latest = self.request.get('latest')
    # remove the first line if it's just a header
    listing = Listings.query().order(-Listings.added).get()
    if not listing: listing = Listings()
    listing.text = latest
    listing.put()
    self.response.out.write(listing.text)


class ItemHandler(webapp2.RequestHandler):
  def get(self):
    if needs_redirect(self): return
    if users.get_current_user().email().lower() not in ALLOWED_USERS:
      self.error(404)
      return
    items = Item.query().fetch(1000)
    self.response.out.write(json.dumps([json_dump(item) for item in items]))

  def post(self):
    if needs_redirect(self): return
    if users.get_current_user().email().lower() not in ALLOWED_USERS:
      self.error(404)
      return
    if self.request.get('id'):
      item = ndb.Key('Item', int(self.request.get('id'))).get()
      if self.request.get('action') == 'DELETE':
        item.key.delete()
        self.response.out.write('Deleted item!')
        return
    else:
      item = Item()
      top_ranking = Item.gql('order by ranking desc limit 1').get()
      if top_ranking:
        item.ranking = top_ranking.ranking if top_ranking.ranking else 0
        item.ranking += 1

    if self.request.get('link'):
      item.link = self.request.get('link')
    if self.request.get('page'):
      item.page = self.request.get('page')
    if self.request.get('date_posted'):
      item.date_posted = self.request.get('date_posted')
    if self.request.get('images'):
      item.images = self.request.get('images').split(',')
    if self.request.get('ranking'):
      item.ranking = int(self.request.get('ranking'))
    if self.request.get('title'):
      item.title = self.request.get('title')
    if self.request.get('text'):
      item.text = self.request.get('text')[:500]

    item.put()
    self.response.out.write(json.dumps(json_dump(item)))

class RealPlusHandler(webapp2.RequestHandler):
  def get(self):
    index = self.request.get('page')
    try:
      index = int(index)
    except Exception, e:
      self.redirect('/')
      return
    listing = Listings.query().order(-Listings.added).get()
    if not listing:
      return
    listings = [l for l in listing.text.split('\n')[1:] if len(l.strip()) > 0]
    template_data = {
      'listing': get_realplus_listing(listings[int(index)], index),
      'PAGE': 'listing.html'
    }
    path = os.path.join(os.path.dirname(__file__), 'index.html') 
    rendered_page = template.render(path, template_data)
    self.response.out.write(rendered_page)


class MainHandler(webapp2.RequestHandler):
  def post(self):
    if needs_redirect(self): return
    name = self.request.get("name")
    email = self.request.get("email")
    phone = self.request.get("phone")
    message = self.request.get("message")
    mail.send_mail(sender="akiva.bamberger@gmail.com",
                   to="dan@thebambergergroup.com,akiva.bamberger@gmail.com",
                   subject="Message from danbamberger.com",
                   body="Sent from %s (%s, %s):\n\n%s" % (name, email, phone, message))
    self.redirect('/contact#email_received')

  def add_realplus(self, template_data):
    listing = Listings.query().order(-Listings.added).get()
    if not listing:
      return
    listings = [l for l in listing.text.split('\n')[1:] if len(l.strip()) > 0]
    for i, listing_text in enumerate(listings):
      template_data['newsletters'] += [get_realplus_listing(listing_text, i, True)]


  def add_fake_data(self, template_data):
    template_data['closed'] = [{
      'link': '/r/images/selling.jpg',
      'images': ['/r/images/selling.jpg'],
      'title': 'Best apartment in the world'
    }] * 10 + [{
      'link': '/r/images/selling.jpg',
      'images': ['/r/images/selling.jpg'],
      'title': 'Best apartment in the world'
    }]
    logging.info(template_data['closed'])

  def get(self):
    if needs_redirect(self): return
    page = 'home'
    template_data = {}

    paths = ['buyers', 'about', 'contact', 'listings', 'thereport', 'press', 'team']
    for p in paths:
      if re.match('/%s' % p, self.request.path):
        page = p

    if page in ['listings', 'thereport']:
      template_data['PAGE'] = 'items.html'
      template_data['newsletters'] = []
      if page == 'thereport':
        template_data['newsletters'] = Item.gql('WHERE page=:1 order by ranking desc', page).fetch(1000)
      if page == 'listings':
        template_data['closed'] = Item.gql('WHERE page=:1 order by ranking desc', 'rented').fetch(1000)
        if len(template_data['closed']) == 0:
          self.add_fake_data(template_data)

        self.add_realplus(template_data)
         
    else:
      template_data['PAGE'] = '%s.html' % page
    template_data['path'] = page
    path = os.path.join(os.path.dirname(__file__), 'index.html') 
    rendered_page = template.render(path, template_data)
    self.response.out.write(rendered_page)

app = webapp2.WSGIApplication(
    [('/items', ItemHandler),
     ('/new', NewListingsPageHandler),
     ('/realplus', RealPlusHandler),
     ('/.*', MainHandler)],
     debug=False)
