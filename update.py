import urllib2,re,os
from HTMLParser import HTMLParser

listings = 'http://www.citi-habitats.com/real-estate-agents/profiles/Dan-Bamberger-569240'
newsletters = 'http://us2.campaign-archive1.com/home/?u=f832646624bdbf8d1d0cd3146&id=9ff3e65fde'
def enum(**enums):
    return type('Enum', (), enums)
Types = enum(TITLE=1,PRICE=2,AVAIL=3,DESCR=4)

class LinkParser(HTMLParser):
  listings = {}
  newsletters = {}
  lastDate = None
  def handle_starttag(self, tag, attrs):
    amap = {'class': None, 'title':None, 'href':None}
    for i in attrs: amap[i[0]] = i[1]
    if not amap['href']: return
    m = re.search('viewsales.php\?adID=(\d+)', amap['href'])
    if m: self.listings[m.group(1)] = 1
    m = re.search('eepurl.com', amap['href'])
    if m and self.lastDate:
      self.newsletters[amap['href']] = [amap['title'], self.lastDate]
  def handle_data(self, data):
    if not data: return
    m = re.match('\d{2}\/\d{2}/201\d', data)
    if m: self.lastDate = m.group(0)

class ListingParser(HTMLParser):
  def __init__(self):
    HTMLParser.__init__(self)
    self.act = None
    self.imgs = {}
    self.title = None
    self.desc = None
    self.price = None
    self.place = None
    self.avail = None
  def handle_starttag(self, tag, attrs):
    if len(attrs) == 0: return
    amap = {'class':None,'name':None, 'style':None}
    self.act = None
    for i in attrs: amap[i[0]] = i[1]
    if amap['class'] in ['listing_title', 'listing_h1']:
      self.act = Types.TITLE
    elif amap['class'] == 'listing_price':
      self.act = Types.PRICE
    elif amap['name'] == 'long_descr':
      self.act = Types.DESCR
    elif amap['class'] == 'listing_img' and amap['src'][:3] != 'php':
      self.imgs[amap['src'].replace('252x376','504x752')] = 1
      
  def handle_data(self, data):
    data = data.strip()
    if self.act == Types.TITLE and not self.title:
      self.title = data
    elif self.act == Types.DESCR and not self.desc:
      self.desc = data
    elif self.act == Types.PRICE:
      if not self.place:
        self.place = data
      elif data[0] == '$':
        self.price = data
    elif re.match('CLOSED', data) or re.match('\*In Contract', data):
      self.avail = data

class NewsletterParser(HTMLParser):
  def __init__(self):
    HTMLParser.__init__(self)
    self.text = ''
    self.start = False
    self.imgsrc = None
  def handle_starttag(self, tag, attrs):
    amap = {'src':None, 'class':None}
    for i in attrs: amap[i[0]] = i[1]
    if amap['class'] == 'bodyContent': self.start = True
    if amap['src'] and re.search('gallery.mailchimp.com', amap['src']) and not re.search('banner\d.gif', amap['src']):
      self.imgsrc = amap['src']
  def handle_data(self, data):
    if self.start: self.text += data 

def getImgs(imgs, key):
  directory = 'resources/images/%s' % key
  if os.path.exists(directory): return
  os.makedirs(directory)
  count = 1
  for img in imgs:
    if re.match('http', img):
      f = open('resources/images/%s/%d.jpg' % (key, count), 'w')
      f.write(urllib2.urlopen(img).read())
      f.close()
      count += 1
    
def getListing(key):
  page = 'http://www.citi-habitats.com/viewsales.php?adID=%s' % key
  parser = ListingParser()
  parser.feed(urllib2.urlopen(page).read())
  f = open('data/listings/%s.txt' % key, 'w')
  if not parser.title: parser.title = parser.place
  if not parser.avail: parser.avail = 'Available'
  print parser.title
  for i in [page, parser.title, parser.avail, parser.price,parser.desc]:
    if not i: i = ''
    f.write('%s\n' % i)
  f.close()
  getImgs([i for i in parser.imgs], key)

parser = LinkParser()
data = urllib2.urlopen(listings).read()
print data
parser.feed(data)
for key in parser.listings:
  print key
  getListing(key)
'''
parser = LinkParser()
parser.feed(urllib2.urlopen(newsletters).read())
for url in parser.newsletters:
  title, date = parser.newsletters[url]
  parser2 = NewsletterParser()
  parser2.feed(repr(urllib2.urlopen(url).read()))
  text = parser2.text.replace('\\n', ' ').replace('\\t', ' ').replace('\\r','').replace('\n', ' ')
  text = re.sub('\s+', ' ', text)
  fname = '%s%s%s.txt' % (date[-4:],date[:2],date[-7:-5])
  f = open('data/newsletters/%s' % fname, 'w')
  for i in [title,url,date,parser2.imgsrc,text]:
    f.write('%s\n' % i)
  f.close()
'''
