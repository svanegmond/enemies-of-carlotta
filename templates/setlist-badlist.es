From: %(From)s
To: %(To)s
Subject: Dirección incorrecta para %(list)s
Content-type: multipart/mixed; boundary="%(boundary)s"
MIME-Version: 1.0

This is a multipart message in MIME format

--%(boundary)s
Content-type: text/plain; charset=utf-8

Hola,

Este mensaje se lo ha enviado el gestor de listas de correo que opera
sobre %(list)s .

La sintaxis de la dirección de lista a la que ha enviado el mensaje es
incorrecta. Debe haber una única dirección por línea, y nada más.

Si desea instrucciones sobre el uso del software gestor de listas, envíe
un mensaje a %(local)s-help@%(domain)s .

Si tiene problemas, por favor, póngase en contacto con las personas que
gestionan la lista en %(local)s-owner@%(domain)s .

Gracias.

--%(boundary)s
Content-type: message/rfc822
Content-disposition: inline; filename=original.txt

%(origmail)s--%(boundary)s--

