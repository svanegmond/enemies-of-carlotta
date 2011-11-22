From: %(From)s
To: %(To)s
Subject: Adress borttagen från %(list)s
Content-type: multipart/mixed; boundary="%(boundary)s"
MIME-Version: 1.0

This is a multipart message in MIME format

--%(boundary)s
Content-type: text/plain; charset=utf-8

Hej! 

Det här brevet skickades av epostlistehanteraren som sköter listan

    %(list)s

till listans ägare.

Följande adress har tagits bort från listan p.g.a. att posten studsar:

    %(address)s

Studsmeddelandet är bifogat med det här brevet. Såvida inte något
riktigt märkligt pågår är det här brevet bara till för att informera 
dig och du behöver inte vidta någon åtgärd.

Tack.

--%(boundary)s
Content-type: message/rfc822
Content-disposition: inline; filename=bounce.txt
 
%(bounce)s--%(boundary)s--

