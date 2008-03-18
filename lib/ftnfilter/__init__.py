import os, sys, tempfile, zipfile
from pydonet.packet import Packet
from pydonet.message import Message
import optparse

def parse_args():
  parser = optparse.OptionParser()

  parser.add_option('-m', '--module')
  parser.add_option('-o', '--output-dir')
  parser.add_option('-z', '--zip', action='store_true')

  opts, args = parser.parse_args()
  return opts, args

class StopMessageProcessing (Exception):
  pass

def runfilter(filter, packet, msg):
  state = {
      'disposition': 'keep',
      'messages': []
      }

  def discard():
    '''Discard a message.'''

    state['disposition'] = 'discard'

  def keep():
    '''Deliver the message normally.  This is the default behavior; you
    would use the keep() command to reverse a previous discard().'''

    state['disposition'] = 'keep'

  def stop():
    '''Stop message processing at this point (do not process
    additional rules)'''

    raise StopMessageProcessing()

  def copy(area):
    '''Generate a new copy of the message in the given message
    area.'''

    x = Message(data = msg.serialize())
    x.area = area
    state['messages'].append(x)

  try:
    fd = open(filter)
    exec fd in { 'M': msg, 'P': packet,
        'discard': discard,
        'copy': copy,
        'keep': keep,
        'stop': stop}
  except StopMessageProcessing:
    pass

  return state

def process_packet(P, name, opts):
  print '+ Processing:', name

  (nP, nPname) = tempfile.mkstemp(dir = opts.output_dir)
  os.write(nP, P.serialize())

  count = 0
  for msg in P:
    print '  %s -> %s: %s' % (msg.fromUsername, msg.toUsername, msg.subject)
    state = runfilter(opts.module, P, msg)
    if state['disposition'] == 'keep':
      count += 1
      os.write(nP, msg.serialize())

    # Write out any new messages that were generated by copy()
    # operations in the filter.
    for msg in state['messages']:
      os.write(nP, msg.serialize())

  os.write(nP, '\x00\x00')
  os.close(nP)

  if count > 0:
    os.rename(nPname, os.path.join(opts.output_dir, name))
  else:
    print '+ Removing %s (no messages)' % name
    os.unlink(nPname)

def main():

  opts, args = parse_args()

  for arg in args:
    if opts.zip:
      z = zipfile.ZipFile(arg)
      for f in z.namelist():
        P = Packet(data = z.read(f))
        process_packet(P, f, opts)
    else:
      P = Packet(file = arg)
      process_packet(P, os.path.basename(arg), opts)

