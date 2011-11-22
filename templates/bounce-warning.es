From: %(From)s
To: %(To)s
Subject: Sus mensajes están rebotando, %(list)s
Content-type: multipart/mixed; boundary="%(boundary)s"
MIME-Version: 1.0

This is a multipart message in MIME format

--%(boundary)s
Content-type: text/plain; charset=utf-8

Hola,

Usted es suscriptor de la lista de correo %(list)s.

Al menos uno de los mensajes que le envió la lista durante la última
semana rebotó. Si fue un problema temporal, puede ignorar este aviso.
Sin embargo, si su correo continúa rebotando, acabará siendo desuscrito
de forma automática de esta lista. Sentimos el inconveniente.

Encontrará el primer mensaje que rebotó adjunto.

Si desea instrucciones sobre el uso del software gestor de listas, envíe
un mensaje a %(local)s-help@%(domain)s .

Si tiene problemas, por favor, póngase en contacto con las personas que
gestionan la lista en %(local)s-owner@%(domain)s .

--%(boundary)s
Content-type: message/rfc822
Content-disposition: inline; filename=bounce.txt

%(bounce)s--%(boundary)s--

