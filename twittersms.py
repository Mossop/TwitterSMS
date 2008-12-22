import sys, pickle, time
from clicksms import ClickSMS
from twitter import Twitter

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

if __name__ == '__main__':
  if len(sys.argv) == 2:
    f = open(sys.argv[1], 'r')
    settings = pickle.load(f)
    f.close()
    twitter = Twitter(settings.twitter_username, settings.twitter_password)
    sms = ClickSMS(settings.sms_username, settings.sms_password)
    try:
      messages = []
      (msgs, settings.lastTimelineID) = twitter.GetTimeline(settings.lastTimelineID)
      #messages += msgs
      (msgs, settings.lastReplyID) = twitter.GetReplies(settings.lastReplyID)
      messages += msgs
      (msgs, settings.lastDirectMessageID) = twitter.GetDirectMessages(settings.lastDirectMessageID)
      messages += msgs
      if len(messages) > 10:
        raise Exception("Refusing to send %s updates" % len(messages))
      messages.sort(key = lambda x: x.date)
      removeDuplicates(messages)
      for message in messages:
        if message.type == 'direct':
          sms.sendMessage(settings.sms_number, "%s(d): %s" % (message.sender, message.text))
        else:
          sms.sendMessage(settings.sms_number, "%s: %s" % (message.sender, message.text))
    except Exception, inst:
      print inst
    f = open(sys.argv[1], 'w')
    pickle.dump(settings, f)
    f.close()
  elif len(sys.argv) == 7:
    settings = Settings(sys.argv[2:])
    twitter = Twitter(settings.twitter_username, settings.twitter_password)
    (messages, settings.lastTimelineID) = twitter.GetTimeline()
    (messages, settings.lastReplyID) = twitter.GetReplies()
    (messages, settings.lastDirectMessageID) = twitter.GetDirectMessages()
    f = open(sys.argv[1], 'w')
    pickle.dump(settings, f)
    f.close()
  else:
    print "Usage:"
    print "twittersms.py <settings> <twitter username> <twitter password> <sms username> <sms password> <sms number>"
    print "twittersms.py <settings>"
