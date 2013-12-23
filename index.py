from google.appengine.ext import ndb
from google.appengine.ext.webapp import template
import urllib, os, re
from google.appengine.api import mail
import logging
import json
from models import *

import jinja2
import webapp2


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

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

class ItemHandler(webapp2.RequestHandler):
  def get(self):
    items = Item.query().fetch(1000)
    self.response.out.write(json.dumps([json_dump(item) for item in items]))

  def post(self):
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

class MainHandler(webapp2.RequestHandler):
  def post(self):
    name = self.request.get("name")
    email = self.request.get("email")
    phone = self.request.get("phone")
    message = self.request.get("message")
    mail.send_mail(sender="akivab@google.com",
                   to="dbamberger7@gmail.com,akiva.bamberger@gmail.com",
                   subject="Message from danbamberger.com",
                   body="Sent from %s (%s, %s):\n\n%s" % (name, email, phone, message))
    self.redirect('/contact#email_received')


  def get(self):
    userAgent = self.request.headers['User-Agent']
    if "Windows" in userAgent and "MSIE" in userAgent:
      self.redirect('http://www.citi-habitats.com/agent_profile.php?id=BAM')
    page = 'home'
    template_data = {}

    paths = ['buyers', 'about', 'contact', 'listings', 'thereport', 'sellers']
    for p in paths:
      if re.match('/%s' % p, self.request.path):
        page = p

    if page in ['listings', 'thereport']:
      template_data['PAGE'] = 'items.html'
      template_data['newsletters'] = Item.gql('WHERE page=:1 order by ranking desc', page).fetch(1000)
    else:
      template_data['PAGE'] = '%s.html' % page
    path = os.path.join(os.path.dirname(__file__), 'index.html') 
    rendered_page = template.render(path, template_data)
    self.response.out.write(rendered_page)

app = webapp2.WSGIApplication(
    [('/items', ItemHandler),
     ('/.*', MainHandler)],
     debug=False)
