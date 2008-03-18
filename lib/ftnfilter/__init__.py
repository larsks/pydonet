import os, sys, tempfile
from pydonet.packet import Packet
from pydonet.message import Message
import optparse

def parse_args():
  parser = optparse.OptionParser()

  parser.add_option('-m', '--module')
  parser.add_option('-i', '--input-file')
  parser.add_option('-o', '--output-dir')

  opts, args = parser.parse_args()
  return opts, args

class DiscardMessage (Exception):
  pass

def runfilter(filter, packet, msg):
  def discard():
    raise DiscardMessage()

  try:
    fd = open(filter)
    exec fd in { 'M': msg, 'P': packet, 'discard': discard }
    return True
  except DiscardMessage:
    return False

def main():

  opts, args = parse_args()

  P = Packet(file = opts.input_file)
  (nP, nPname) = tempfile.mkstemp(dir = opts.output_dir)
  os.write(nP, P.serialize())

  for msg in P:
    if runfilter(opts.module, P, msg):
      os.write(nP, msg.serialize())

  os.close(nP)

