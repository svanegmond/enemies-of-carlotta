From: %(From)s
To: %(To)s
Subject: Felaktig adresslista för %(list)s
Content-type: multipart/mixed; boundary="%(boundary)s"
MIME-Version: 1.0

This is a multipart message in MIME format

--%(boundary)s
Content-type: text/plain; charset=utf-8

Hej! 

Det här brevet skickades av epostlistehanteraren som sköter listan
%(list)s.

Adresslistan du skickade är syntaktiskt felaktig. Du måste skriva exakt
en adress per rad och inget annat.

För instruktioner om hur man använder epostlistehanteraren, skicka
ett brev till to %(local)s-help@%(domain)s.

Om du har problem, kontakta personerna som äger listan på
%(local)s-owner@%(domain)s.

Tack.

--%(boundary)s
Content-type: message/rfc822
Content-disposition: inline; filename=original.txt

%(origmail)s--%(boundary)s--

