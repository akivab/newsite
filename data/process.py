import urllib, urllib2
from time import sleep
lines = open('all.csv', 'r').readlines()
for i in lines:
  name, link, date, image, text, page = i.split(',')
  params = {
    'title': name,
    'link': link,
    'date_posted': date,
    'images': image,
    'text': text,
    'page': page.strip(),
    'perform_as_post': True
  }

  opener = urllib2.build_opener()
  f = opener.open("http://www.danbamberger.com/items?%s" % urllib.urlencode(params))
  sleep(0.5)
