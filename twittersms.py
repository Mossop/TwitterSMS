import sys, urllib2, pickle
from xml.dom import minidom

def textContent(node):
  str = ''
  for n in node.childNodes:
    if n.nodeType == n.TEXT_NODE:
      str += n.nodeValue
  return str

class Settings:
  twitter_username = None
  twitter_password = None
  twitter_lastDirectMessage = None
  twitter_lastReply = None
  sms_username = None
  sms_password = None
  sms_number = None

  def __init__(self, args):
    self.twitter_username = args[0]
    self.twitter_password = args[1]
    self.sms_username = args[2]
    self.sms_password = args[3]
    self.sms_number = args[4]

class ClickSMS:
  def __init__(self, settings):
    self.settings = settings

  def sendMessage(self, sender, text):
    if len(text) > 160:
      text = text[:156] + '...'
    message = "<Msg>\n\
  <Txn>sendsms</Txn>\n\
  <AccountID>%s</AccountID>\n\
  <Password>%s</Password>\n\
  <MobileNo>%s</MobileNo>\n\
  <SenderID>%s</SenderID>\n\
  <Message>%s</Message>\n\
  <RateCode>1</RateCode>\n\
</Msg>" % (self.settings.sms_username, self.settings.sms_password, self.settings.sms_number, sender, text)
    req = urllib2.Request('http://service.clicksms.co.uk')
    req.add_header('Content-Type', 'text/xml')
    req.add_data(message)
    stream = urllib2.urlopen(req)
    dom = minidom.parse(stream)
    stream.close()
    status = textContent(dom.getElementsByTagName('StatusId')[0])
    if status != '0':
      print textContent(dom.getElementsByTagName('StatusText')[0])

class Message:
  def __init__(self, element):
    for node in element.childNodes:
      if node.nodeType == node.ELEMENT_NODE:
        if node.tagName == 'id':
          self.id = textContent(node)
        elif node.tagName == 'text':
          self.text = textContent(node)
        elif node.tagName == 'user' or node.tagName == 'sender':
          for n in node.childNodes:
            if n.nodeType == n.ELEMENT_NODE and n.tagName == 'screen_name':
              self.sender = textContent(n)

class Twitter:
  def __init__(self, settings):
    self.settings = settings
    
    auth_handler = urllib2.HTTPBasicAuthHandler(self)
    opener = urllib2.build_opener(auth_handler)
    urllib2.install_opener(opener)

  def _getStream(self, url):
    stream = urllib2.urlopen(url)
    dom = minidom.parse(stream)
    stream.close()
    return dom

  def add_password(self, realm, uri, user, password):
    return

  def find_user_password(self, realm, uri):
    return (self.settings.twitter_username, self.settings.twitter_password)

  def GetDirectMessages(self):
    messages = []
    url = 'http://twitter.com/direct_messages.xml'
    if self.settings.twitter_lastDirectMessage is not None:
      url += '?since_id=' + self.settings.twitter_lastDirectMessage
    dom = self._getStream(url)
    for node in dom.documentElement.childNodes:
      if node.nodeType == node.ELEMENT_NODE and node.tagName == 'direct_message':
        message = Message(node)
        if self.settings.twitter_lastDirectMessage is None or message.id > self.settings.twitter_lastDirectMessage:
          self.settings.twitter_lastDirectMessage = message.id
        messages += [message]
    return messages

  def GetReplies(self):
    messages = []
    url = 'http://twitter.com/statuses/replies.xml'
    if self.settings.twitter_lastReply is not None:
      url += '?since_id=' + self.settings.twitter_lastReply
    dom = self._getStream(url)
    for node in dom.documentElement.childNodes:
      if node.nodeType == node.ELEMENT_NODE and node.tagName == 'status':
        message = Message(node)
        if self.settings.twitter_lastReply is None or message.id > self.settings.twitter_lastReply:
          self.settings.twitter_lastReply = message.id
        messages += [message]
    return messages

if __name__ == '__main__':
  if len(sys.argv) == 2:
    f = open(sys.argv[1], 'r')
    settings = pickle.load(f)
    f.close()
    twitter = Twitter(settings)
    sms = ClickSMS(settings)
    messages = twitter.GetReplies()
    for message in messages:
      sms.sendMessage(message.sender, message.text)
    messages = twitter.GetDirectMessages()
    for message in messages:
      sms.sendMessage('07624801423', "%s: %s" % (message.sender, message.text))
    f = open(sys.argv[1], 'w')
    pickle.dump(settings, f)
    f.close()
  elif len(sys.argv) == 7:
    settings = Settings(sys.argv[2:])
    twitter = Twitter(settings)
    twitter.GetReplies()
    twitter.GetDirectMessages()
    f = open(sys.argv[1], 'w')
    pickle.dump(settings, f)
    f.close()
  else:
    print "Usage:"
    print "twittersms.py <settings> <twitter username> <twitter password> <sms username> <sms password> <sms number>"
    print "twittersms.py <settings>"
