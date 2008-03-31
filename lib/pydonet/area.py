import os, errno

class Area (object):

  def __init__ (self, path, lastRead = "1.MSG"):
    if not os.path.isdir(path):
      raise ValueError('Not a directory.', path)

    self.path = path
    self.lastReadName = lastRead
    self.lastMessage = 0

  def nextMessage(self):
    '''Returns a file object opened for writing to the next
    available message.'''

    msgnum = self.lastMessage
    fd = None

    while True:
      msgnum += 1
      path = os.path.join(self.path, '%d.MSG' % msgnum)
      if os.path.basename(path) == self.lastReadName:
        continue

      try:
        fd = os.open(path, os.O_CREAT|os.O_EXCL|os.O_WRONLY)
        break
      except OSError, detail:
        if detail.errno == errno.EEXIST:
          pass
        else:
          raise(detail)

    self.lastMessage = msgnum
    return os.fdopen(fd, 'w')

