From: %(From)s
To: %(To)s
Reply-To: %(confirm)s
Subject: Bekräfta avslut på prenumeration på %(list)s
Content-type: multipart/mixed; boundary="%(boundary)s"
MIME-Version: 1.0

This is a multipart message in MIME format

--%(boundary)s
Content-type: text/plain; charset=utf-8

Hej! 

Det här brevet skickades av epostlistehanteraren som sköter epostlistan
%(list)s.

Du, eller någon i ditt ställe, har begärt att din prenumeration på 
listan ska avslutas. Meddelandet i fråga finns längst ner. Om du inte 
skickade det själv, kontakta avsändaren eller dennes administratör och 
fråga vad som pågår.

Genom att besvara det här brevet bekräftar du att du inte längre vill
prenumerera på listan. Innehållet i svaret spelar ingen roll. Vanligtvis
går det bra att använda den vanliga svara-funktionen i ditt epostprogram.
Alternativt kan du skicka ett tomt meddelande till följande adress:

    %(confirm)s

Om du vill fortsätta prenumerera behöver du inte göra någonting alls.

För instruktioner om hur man använder epostlistehanteraren, skicka
ett brev till to %(local)s-help@%(domain)s.

Om du har problem, kontakta personerna som äger listan på
%(local)s-owner@%(domain)s.

Tack.

--%(boundary)s
Content-type: message/rfc822
Content-disposition: inline; filename=original.txt

%(origmail)s--%(boundary)s--

