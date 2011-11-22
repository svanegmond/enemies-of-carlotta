From: %(From)s
To: %(To)s
Reply-To: %(confirm)s
Subject: Var god moderera meddelande till %(list)s
Content-type: multipart/mixed; boundary="%(boundary)s"
MIME-Version: 1.0

This is a multipart message in MIME format

--%(boundary)s
Content-type: text/plain; charset=utf-8

Hej! 

Det här brevet skickades av epostlistehanteraren som sköter listan

    %(list)s

till de som modererar listan.

Ska meddelandet som visas nedan få skickas till listan?
I så fall, svara på det här brevet eller skicka ett tomt meddelande till

    %(confirm)s

Om inte, skicka ett meddelande till

    %(deny)s

Tack.

--%(boundary)s
Content-type: message/rfc822
Content-disposition: inline; filename=original.txt

%(origmail)s--%(boundary)s--

