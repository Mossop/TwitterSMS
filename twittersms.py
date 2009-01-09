import sys, pickle
from clicksms import ClickSMS
from twitter import Twitter
from optparse import OptionParser
from urllib2 import HTTPError

class Settings:
  twitter_username = None
  twitter_password = None
  lastTimelineID = None
  lastDirectMessageID = None
  lastReplyID = None
  sms_username = None
  sms_password = None
  sms_number = None

  def __init__(self, args):
    self.twitter_username = args[0]
    self.twitter_password = args[1]
    self.sms_username = args[2]
    self.sms_password = args[3]
    self.sms_number = args[4]

def removeDuplicates(messages):
  pos = 1
  while pos < len(messages):
    if messages[pos].id == messages[pos-1].id:
      messages.pop(pos)
    else:
      pos += 1

def printUsage():
  print "Usage: twittersms.py init [options] <twitter username> <twitter password> <sms username> <sms password> <sms number>\n\
           Initialises settings and skips any existing messages.\n\n\
       twittersms.py skip [options]\n\
           Skips any new messages.\n\n\
       twittersms.py send [options]\n\
           Sends any new messages.\n\n\
Pass -h as an option for specific help on that syntax."

def getUpdates(skip, args):
  parser = OptionParser()
  parser.add_option('-f', '--file', dest='state', default='state',
                    help='use configuration in FILE, defaults to "state"', metavar='FILE')
  parser.add_option('-g', '--debug', action='store_true', dest='debug', default=False,
                    help='print debug output and don\'t actually send any messages')
  if not skip:
    parser.usage = '%prog send [options]'
    parser.add_option('-s', '--status', action='store_true', dest='status', default=False,
                      help='include regular status updates from users you follow')
    parser.add_option('-r', '--replies', action='store_true', dest='replies', default=False,
                      help='include replies')
    parser.add_option('-d', '--direct', action='store_true', dest='direct', default=False,
                      help='include direct messages')
    parser.add_option('-m', '--max', dest='max', default=10,
                      help='abort if MAX message were to be sent', metavar='MAX')
  else:
    parser.usage = '%prog skip [options]'
  (options, args) = parser.parse_args(args)
  if len(args) > 0:
    printUsage()
    return
  if options.debug:
    if not skip:
      print "Sending all new messages"
    else:
      print "Skipping all new messages"

  f = open(options.state, 'r')
  settings = pickle.load(f)
  f.close()
  twitter = Twitter(settings.twitter_username, settings.twitter_password)
  try:
    (statuses, settings.lastTimelineID) = twitter.GetTimeline(settings.lastTimelineID)
    (replies, settings.lastReplyID) = twitter.GetReplies(settings.lastReplyID)
    (directs, settings.lastDirectMessageID) = twitter.GetDirectMessages(settings.lastDirectMessageID)
    if options.debug:
      print "Seen %s statuses, %s replies and %s direct messages" % (len(statuses), len(replies), len(directs))
    if not skip:
      messages = []
      if not options.status and not options.replies and not options.direct:
        options.direct = True
      if options.status:
        messages += statuses
      if options.replies:
        messages += replies
      if options.direct:
        messages += directs
      messages.sort(key = lambda x: x.date)
      removeDuplicates(messages)
      if not options.debug and len(messages) > options.max:
        raise Exception("Refusing to send %s updates" % len(messages))
      sms = ClickSMS(settings.sms_username, settings.sms_password)
      for message in messages:
        if options.debug:
          print "%s message from %s: %s" % (message.type, message.sender, message.text)
        elif message.type == 'direct':
          sms.sendMessage(settings.sms_number, "%s(d): %s" % (message.sender, message.text),
                          '07624801423')
        else:
          sms.sendMessage(settings.sms_number, "%s: %s" % (message.sender, message.text),
                          '07624801423')
  except HTTPError, error:
    if error.code < 500 or error.code >= 600:
      print error
  except Exception, inst:
    print inst
  f = open(options.state, 'w')
  pickle.dump(settings, f)
  f.close()

def initSettings(args):
  parser = OptionParser()
  parser.usage = '%prog init [options] <twitter username> <twitter password> <sms username> <sms password> <sms number>'
  parser.add_option('-f', '--file', dest='state', default='state',
                    help='use configuration in FILE, defaults to "state"', metavar='FILE')
  parser.add_option('-g', '--debug', action="store_true", dest='debug', default=False,
                    help='print debug output and don\'t actually send any messages')
  (options, args) = parser.parse_args(args)

  if len(args) != 5:
    parser.print_help()
    exit()

  settings = Settings(args)
  twitter = Twitter(settings.twitter_username, settings.twitter_password)
  (messages, settings.lastTimelineID) = twitter.GetTimeline()
  (messages, settings.lastReplyID) = twitter.GetReplies()
  (messages, settings.lastDirectMessageID) = twitter.GetDirectMessages()
  f = open(options.state, 'w')
  pickle.dump(settings, f)
  f.close()

if __name__ == '__main__':
  if len(sys.argv) == 2 and (sys.argv[1] == '-h' or sys.argv[1] == '--help'):
    printUsage()
  elif len(sys.argv) < 2:
    getUpdates(False, sys.argv[1:])
  elif sys.argv[1] == 'send':
    getUpdates(False, sys.argv[2:])
  elif sys.argv[1] == 'skip':
    getUpdates(True, sys.argv[2:])
  elif sys.argv[1] == 'init':
    initSettings(sys.argv[2:])
  else:
    getUpdates(False, sys.argv[1:])
