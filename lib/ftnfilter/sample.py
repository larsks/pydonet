'''This is a sample filter for use with ftnfilter.  You would use like this::

  ftnfilter -f /path/to/sample.py -z \
      -o /var/spool/ftn/inb.filtered \
      /var/spool/ftn/inb/*
'''

# I want a copy of D'Bridge release announcements in my
# DBRELEAS message area. copy() creates a new message
# with the appropriate AREA: line.
if M.fromUsername == 'Nick Andre' \
    and M.body.area == 'DBRIDGE' \
    and 'release' in M.subject.lower():
  copy('DBRELEAS')

# I want to discard all mail with the subject "Make money fast".  
# discard() removes the message from the packet.
if M.subject.lower() == 'make money fast':
  discard()

# ...unless they're serious. keep() reverses the effect of the 
# previous discard() for matching messages.
if 'seriously' in M.subject.lower():
  keep()

