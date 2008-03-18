Pydonet
=======

Author: Lars Kellogg-Stedman (1:322/761)
        lars@oddbit.com

Pydonet is a collection of Python modules for interacting with FTN
format mail packets and messages.

Reading a mail packet
~~~~~~~~~~~~~~~~~~~~~

To read an uncompressed mail packet (*.pkt)::

  from pydonet.packet import Packet
  p = Packet(file = 'sample.pkg')
  print 'Packet from %s to %s.' % (p.origAddr, p.destAddr)

To read a mail packet compressed with Zip::

  import zipfile
  from pydonet.packet import Packet

  zf = zipfile.Zipfile('sample.mo0')
  p = Packet(data = zf.read('sample.pkt'))
  print 'Packet from %s to %s.' % (p.origAddr, p.destAddr)

Iterating over messages
~~~~~~~~~~~~~~~~~~~~~~~

A Packet is a Python iterator.  You can iterate over all the messages
in a packet like this::

  for msg in p:
    print 'Message from', msg.fromUsername

Reading messages
~~~~~~~~~~~~~~~~

You will most often interact with messages as the payload of mail
packets.  However, Pydonet can also read FTN format messages stored in
individual files:

  from pydonet.message import Message
  msg = Message(file = '33.msg')

Once you have a message, you can extract data from both the message
header and the body, including kludge lines (yuck), seen-by lines
(horrors) and other should-never-have-been-embedded in the message
body data::

  print 'From:', msg.fromUsername

  # Note the trailing ':' on the kludge name.  This is necessary
  # because some kludges (INTL) don't use colons.  Durrr.  Also, 
  # since some kludges are multi-valued, you'll always get back a
  # list. 
  print 'MSGID', msg.body.klines['MSGID:'][0]

FTNFilter
=========

FTNFilter makes it easy to filter your inbound mail packets.  It is
designed for use in a BinkD environment, where it would typically take
packets received by BinkD and filter them before placing them in the
inbound queue of some other application.  For example:

.. figure:: images/mailflow.png

