import urllib2
from xml.dom import minidom
from datetime import datetime
from time import strptime

def textContent(node):
  str = ''
  for n in node.childNodes:
    if n.nodeType == n.TEXT_NODE:
      str += n.nodeValue
  return str

class Message:
  def __init__(self, twitter, element):
    if element.tagName == 'direct_message':
      self.type = 'direct'
    else:
      self.type = 'status'
    for node in element.childNodes:
      if node.nodeType == node.ELEMENT_NODE:
        if node.tagName == 'id':
          self.id = textContent(node)
        elif node.tagName == 'text':
          self.text = textContent(node)
        elif node.tagName == 'created_at':
          self.date = datetime(*(strptime(textContent(node), '%a %b %d %H:%M:%S +0000 %Y')[0:6]))
        elif node.tagName == 'in_reply_to_screen_name':
          if textContent(node) == twitter.username:
            self.type = 'reply'
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

  def GetTimeline(self, lastID = None):
    newID = lastID
    messages = []
    url = 'http://twitter.com/statuses/friends_timeline.xml'
    if lastID is not None:
      url += '?since_id=' + lastID
    dom = self._getStream(url)
    for node in dom.documentElement.childNodes:
      if node.nodeType == node.ELEMENT_NODE and node.tagName == 'status':
        message = Message(self, node)
        if message.id <= lastID:
          continue
        if message.id > newID:
          newID = message.id
        if message.sender != self.username:
          messages += [message]
    return (messages, newID)

  def GetDirectMessages(self, lastID = None):
    newID = lastID
    messages = []
    url = 'http://twitter.com/direct_messages.xml'
    if lastID is not None:
      url += '?since_id=' + lastID
    dom = self._getStream(url)
    for node in dom.documentElement.childNodes:
      if node.nodeType == node.ELEMENT_NODE and node.tagName == 'direct_message':
        message = Message(self, node)
        if message.id <= lastID:
          continue
        if message.id > newID:
          newID = message.id
        messages += [message]
    return (messages, newID)

  def GetReplies(self, lastID = None):
    newID = lastID
    messages = []
    url = 'http://twitter.com/statuses/replies.xml'
    if lastID is not None:
      url += '?since_id=' + lastID
    dom = self._getStream(url)
    for node in dom.documentElement.childNodes:
      if node.nodeType == node.ELEMENT_NODE and node.tagName == 'status':
        message = Message(self, node)
        if message.id <= lastID:
          continue
        if message.id > newID:
          newID = message.id
        if message.sender != self.username:
          messages += [message]
    return (messages, newID)
