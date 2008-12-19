import urllib2
from xml.sax.saxutils import escape
from xml.dom import minidom

def textContent(node):
  str = ''
  for n in node.childNodes:
    if n.nodeType == n.TEXT_NODE:
      str += n.nodeValue
  return str

class ClickSMS:
  def __init__(self, username, password):
    self.username = username
    self.password = password

  def sendMessage(self, number, text, sender = None):
    if len(text) > 160:
      text = text[:156] + '...'
    message = "<Msg>\n\
  <Txn>sendsms</Txn>\n\
  <AccountID>%s</AccountID>\n\
  <Password>%s</Password>\n\
  <MobileNo>%s</MobileNo>\n\
  <Message>%s</Message>\n\
  <RateCode>1</RateCode>\n" % (escape(self.username), escape(self.password), escape(number), escape(text))
    if sender is not None:
      message += "  <SenderID>%s</SenderID>\n" % escape(sender)
    message += "</Msg>"
    req = urllib2.Request('http://service.clicksms.co.uk')
    req.add_header('Content-Type', 'text/xml')
    req.add_data(message)
    stream = urllib2.urlopen(req)
    dom = minidom.parse(stream)
    stream.close()
    status = textContent(dom.getElementsByTagName('StatusId')[0])
    if status != '0':
      raise Exception(textContent(dom.getElementsByTagName('StatusText')[0]))
