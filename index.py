from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from django.utils import simplejson as json
import urllib, os, re
from google.appengine.api import mail
from google.appengine.api import memcache

class MainPage(webapp.RequestHandler):
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
    page = 'home.html'
    template_data = {}
    paths = ['buyers', 'about', 'contact', 'listings', 'thereport', 'sellers']
    for p in paths:
      if re.match('/%s' % p, self.request.path):
        page = '%s.html' % p
#    rendered_page = memcache.get(page)
#    if rendered_page is not None:
#      self.response.out.write(rendered_page)
#      return
    if page == 'listings.html':
      aptspath = os.path.join(os.path.dirname(__file__), 'data/listings/')
      aptdir = os.listdir(aptspath)
      goodpics = []
      badpics = []
      toend = ['804391.txt', '170854.txt']
      for apt in sorted(aptdir):
        lines = open('%s/%s' % (aptspath, apt), 'r').readlines()
        url,title,availability,price,maintext = lines[:5]
        img = '%s/' % apt[:-4]
        color = 'green'
        if not re.search('vailable', availability): color='red'
        availability = '<span style="color:%s">%s</span>' % (color,availability)
        thisapt = [{'url':url,'title':title,'img':img,'availability':availability,'price':price,'maintext':maintext}]
        if color == 'green':
          if apt in toend: goodpics = goodpics + thisapt
          else: goodpics = thisapt + goodpics 
        else:
          if apt in toend: badpics = badpics + thisapt
          else: badpics = thisapt + badpics
      template_data['apts'] = goodpics + badpics
    if page == 'thereport.html':
      newspath = os.path.join(os.path.dirname(__file__), 'data/newsletters/')
      newsdir = os.listdir(newspath)
      td = []
      for news in reversed(sorted(newsdir)):
        lines = open('%s/%s' % (newspath, news), 'r').readlines()
        title, url, date, img = lines[:4]
        maintext = '\n'.join(lines[4:])[:400].replace('\n','<br>') + '...'
        td.append({'img': img, 'maintext': maintext, 'date':date, 'url':url, 'title':title})
      template_data['newsletters'] = td
    template_data['PAGE'] = page
    path = os.path.join(os.path.dirname(__file__), 'index.html') 
    rendered_page = template.render(path, template_data)
    memcache.add(page, rendered_page, 7200)
    self.response.out.write(rendered_page)

application = webapp.WSGIApplication(
    [('/.*', MainPage)],
     debug=False)

def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()
