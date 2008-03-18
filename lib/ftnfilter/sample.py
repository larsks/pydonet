TWITS = (
  'Ward Dossche',
    )

if M.subject.lower() == 'new files received':
  print 'NEWFILES: %s re: %s' % (M.fromUsername, M.subject)
  discard()

if M.subject.lower() == 'fidonet via the internet':
  print 'BBSAD: %s re: %s' % (M.fromUsername, M.subject)
  discard()

if M.fromUsername == 'Nick Andre' \
    and M.area == 'DBRIDGE' \
    and 'release' in M.subject.lower():
  print 'DBRIDGE RELEASE: %s re: %s' % (M.fromUsername, M.subject)
  copy('DBRELEAS')

for t in TWITS:
  if M.fromUsername == t:
    print 'TWIT: %s re: %s' % (M.fromUsername, M.subject)
    M.area = 'TWIT'


