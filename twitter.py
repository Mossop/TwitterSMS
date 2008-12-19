import urllib2
from xml.dom import minidom

def textContent(node):
  str = ''
  for n in node.childNodes:
    if n.nodeType == n.TEXT_NODE:
      str += n.nodeValue
  return str

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
  def __init__(self, username, password):
    self.username = username
    self.password = password
    
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
    return (self.username, self.password)

  def GetDirectMessages(self, lastID = None):
    messages = []
    newest = None
    url = 'http://twitter.com/direct_messages.xml'
    if lastID is not None:
      url += '?since_id=' + lastID
    dom = self._getStream(url)
    for node in dom.documentElement.childNodes:
      if node.nodeType == node.ELEMENT_NODE and node.tagName == 'direct_message':
        message = Message(node)
        if message.id > newest:
          newest = message.id
        messages += [message]
    return (messages, newest)

  def GetReplies(self, lastID = None):
    messages = []
    newest = None
    url = 'http://twitter.com/statuses/replies.xml'
    if lastID is not None:
      url += '?since_id=' + lastID
    dom = self._getStream(url)
    for node in dom.documentElement.childNodes:
      if node.nodeType == node.ELEMENT_NODE and node.tagName == 'status':
        message = Message(node)
        if message.id > newest:
          newest = message.id
        messages += [message]
    return (messages, newest)
