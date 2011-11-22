From: %(From)s
To: %(To)s
Reply-To: %(confirm)s
Subject: Var god kontrollera ny prenumerantlista för %(list)s
Content-type: multipart/mixed; boundary="%(boundary)s"
MIME-Version: 1.0

This is a multipart message in MIME format

--%(boundary)s
Content-type: text/plain; charset=utf-8

Hej! 

Det här brevet skickades av epostlistehanteraren som sköter epostlistan
%(list)s.

En av listägarna (eller någon som låtsas vara en) har begärt att
prenumerantlistan ändras. Brevet innehållande begäran är bifogat.
Om du accepterar ändringen, svara på det här brevet. I annat fall, 
ignorera det bara.

Observera att hela prenumerantlistan kommer att ändras till nedanstående
adresslista. Alla tidigare prenumeranter som inte finns med på den nya 
listan kommer att glömmas.

För instruktioner om hur man använder epostlistehanteraren, skicka
ett brev till to %(local)s-help@%(domain)s.

Om du har problem, kontakta personerna som äger listan på
%(local)s-owner@%(domain)s.

Tack.

--%(boundary)s
Content-type: message/rfc822
Content-disposition: inline; filename=original.txt

%(origmail)s--%(boundary)s--

