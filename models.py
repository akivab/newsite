from google.appengine.ext import ndb

class Item(ndb.Model):
  link = ndb.StringProperty()
  title = ndb.StringProperty()
  text = ndb.TextProperty()
  page = ndb.StringProperty(choices=['listings', 'thereport', 'rented'])
  rented = ndb.BooleanProperty()
  date_posted = ndb.StringProperty()
  images = ndb.StringProperty(repeated=True)
  added = ndb.DateTimeProperty(auto_now_add=True)
  ranking = ndb.IntegerProperty(default=0)

