#!/usr/bin/python

# This module that implements sending mail via QMQP. See
#
#   	http://cr.yp.to/proto/qmqp.html
#
# for a description of the protocol.
#
# This module was written by Jaakko Niemi <liiwi@lonesom.pp.fi> for
# Enemies of Carlotta. It is licensed the same way as Enemies of Carlotta:
# GPL version 2.

import socket, string

class QMQPException(Exception):
    '''Base class for all exceptions raised by this module.'''

class QMQPTemporaryError(QMQPException):
    '''Class for temporary errors'''
    def __init__(self, msg):
        self.msg = msg
        
    def __str__(self):
        return "QMQP-Server said: %s" % self.msg
        
class QMQPPermanentError(QMQPException):
    '''Class for permanent errors'''
    def __init__(self, msg):
        self.msg = msg
        
    def __str__(self):
        return "QMQP-Server said: %s" % self.msg

class QMQPConnectionError(QMQPException):
    '''Class for connection errors'''
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return "Error was: %s" % self.msg

class QMQP:
    '''I handle qmqp connection to a server'''

    file = None

    def __init__(self, host = 'localhost'):
        '''Start'''
        if host:
            resp = self.connect(host)

    def encode(self, stringi):
	    ret = '%d:%s,' % (len(stringi), stringi) 
	    return ret

    def decode(self, stringi):
	    stringi = string.split(stringi, ':', 1)
	    stringi[1] = string.rstrip(stringi[1], ',')
	    if len(stringi[1]) is not int(stringi[0]):
		    print 'malformed netstring encounterd'
 	    return stringi[1]

    def connect(self, host = 'localhost'):
        for sres in socket.getaddrinfo(host, 628, 0, socket.SOCK_STREAM):
            af, socktype, proto, canonname, sa = sres
            try:
                self.sock = socket.socket(af, socktype, proto)
                self.sock.connect(sa)
            except socket.error:
                print 'connect failed'
                if self.sock:
                    self.sock.close()
                self.sock = None
                continue
            break
        if not self.sock:
            raise socket.error
        return 0
        
    def send(self, stringi):
        if self.sock:
            try:
                self.sock.sendall(stringi)
            except socket.error, err:
                self.sock.close()
                raise QMQPConnectionError, err
        else:
            print 'not connected'

    def getreply(self):
        if self.file is None:
            self.file = self.sock.makefile('rb')
        while 1:
            line = self.file.readline()
            if line == '':
                self.sock.close()
                print 'ERORORR'
	    break
        line = self.decode(line)
        return line

    def quit(self):
        self.sock.close()

    def sendmail(self, from_addr, to_addrs, msg):
	    recipients = ''
	    msg = self.encode(msg)
	    from_addr = self.encode(from_addr)

# I don't understand why len(to_addrs) <= 1 needs to be handled differently.
# Anyway, it doesn't seem to work with Postfix. --liw
#	    if len(to_addrs) > 1:
#		    for t in to_addrs:
#			    recipients = recipients + self.encode(t)
#	    else:
#		    recipients = self.encode(to_addrs[0])

	    for t in to_addrs:
		    recipients = recipients + self.encode(t)
	    output = self.encode(msg + from_addr + recipients)
	    self.send(output)
	    ret = self.getreply()
	    if ret[0] == 'K':
		    return ret[1:]
	    if ret[0] == 'Z':
		    raise QMQPTemporaryError, ret[1:]
	    if ret[0] == 'D':
		    raise QMQPPermanentError, ret[1:]

if __name__ == '__main__':
    a = QMQP()
    maili = 'asfasdfsfdasfasd'
    envelope_sender = 'liw@liw.iki.fi'
    recips = [ 'liw@liw.iki.fi' ]    
    retcode = a.sendmail(envelope_sender, recips, maili)
    print retcode
    a.quit()
