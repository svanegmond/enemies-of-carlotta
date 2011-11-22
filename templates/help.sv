From: %(From)s
To: %(To)s
Subject: Hjälp för epostlistan %(list)s
Content-type: text/plain; charset=utf-8
MIME-Version: 1.0

Hej! 

Detta är hjälptexten till epostlistan %(list)s.

Listan sköts av epostlistehanteraren EoC. Den förstår följande
kommandoadresser:

    %(local)s-help@%(domain)s

    	Skickar den här hjälptexten.

    %(local)s-subscribe@%(domain)s
    
    	Prenumerera på listan. Du kommer att få ett meddelande som 
    	ber dig bekräfta att du vill prenumerera.
	
    %(local)s-subscribe-foo=bar@%(domain)s
    
    	Anmäl adressen foo@bar som prenumerant. foo@bar kommer att
	få en bekräftelseförfrågan.

    %(local)s-unsubscribe@%(domain)s
    
    	Säg upp prenumerationen på listan. Du kommer att bli ombedd
    	att bekräfta.
	
    %(local)s-unsubscribe-foo=bar@%(domain)s
    
    	Säg upp prenumerationen för foo@bar. foo@bar kommer att få
	bekräfta.

Om du har problem som inte den här hjälptexten kan lösa, kontakta 
listans ägare på adressen %(local)s-owner@%(domain)s.

Tack.
