From: %(From)s
To: %(To)s
Subject: Din epost studsar, %(list)s
Content-type: multipart/mixed; boundary="%(boundary)s"
MIME-Version: 1.0

This is a multipart message in MIME format

--%(boundary)s
Content-type: text/plain; charset=utf-8

Hej! 

Du prenumererar på epostlistan %(list)s.

Epost skickad till dig av epostlistehanteraren har studsat åtminstone
en gång under den senaste veckan eller så. Om detta berodde på ett
tillfälligt fel kan du bortse från den här varningen. Fortsätter dina
brev att studsa kommer du i slutändan automatiskt att bli borttagen 
från listan över prenumeranter. Vi beklagar detta.

Den första studsen är bifogad.

För instruktioner om hur man använder epostlistehanteraren, skicka
ett brev till %(local)s-help@%(domain)s.

Om du har problem, kontakta personerna som äger listan på
%(local)s-owner@%(domain)s.

Tack.

--%(boundary)s
Content-type: message/rfc822
Content-disposition: inline; filename=bounce.txt

%(bounce)s--%(boundary)s--

