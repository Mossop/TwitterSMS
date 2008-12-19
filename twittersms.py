import sys, pickle
from clicksms import ClickSMS
from twitter import Twitter

class Settings:
  twitter_username = None
  twitter_password = None
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

if __name__ == '__main__':
  if len(sys.argv) == 2:
    f = open(sys.argv[1], 'r')
    settings = pickle.load(f)
    f.close()
    twitter = Twitter(settings.twitter_username, settings.twitter_password)
    sms = ClickSMS(settings.sms_username, settings.sms_password)
    (messages, settings.lastReplyID) = twitter.GetReplies(settings.lastReplyID)
    for message in messages:
      sms.sendMessage(settings.sms_number, "%s(r): %s" % (message.sender, message.text), '07624801423')
    (messages, settings.lastDirectMessageID) = twitter.GetDirectMessages(settings.lastDirectMessageID)
    for message in messages:
      sms.sendMessage(settings.sms_number, "%s(d): %s" % (message.sender, message.text), '07624801423')
    f = open(sys.argv[1], 'w')
    pickle.dump(settings, f)
    f.close()
  elif len(sys.argv) == 7:
    settings = Settings(sys.argv[2:])
    twitter = Twitter(settings.twitter_username, settings.twitter_password)
    (messages, settings.lastReplyID) = twitter.GetReplies()
    (messages, settings.lastDirectMessageID) = twitter.GetDirectMessages()
    f = open(sys.argv[1], 'w')
    pickle.dump(settings, f)
    f.close()
  else:
    print "Usage:"
    print "twittersms.py <settings> <twitter username> <twitter password> <sms username> <sms password> <sms number>"
    print "twittersms.py <settings>"
