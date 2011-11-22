From: %(From)s
To: %(To)s
Reply-To: %(confirm)s
Subject: Godkänn ny prenumeration på %(list)s
Content-type: multipart/mixed; boundary="%(boundary)s"
MIME-Version: 1.0

This is a multipart message in MIME format

--%(boundary)s
Content-type: text/plain; charset=utf-8

Hej! 

Det här brevet skickades av epostlistehanteraren som sköter listan

    %(list)s

till listans ägare.

Ska följande adress få lov att prenumerera på listan?

    %(subscriber)s

I så fall, svara på det här brevet eller skicka ett tomt brev till

    %(confirm)s

Om du vill avvisa ansökan, skicka ett tomt brev till

    %(deny)s

Tack.

--%(boundary)s
Content-type: message/rfc822
Content-disposition: inline; filename=original.txt
 
%(origmail)s--%(boundary)s--

