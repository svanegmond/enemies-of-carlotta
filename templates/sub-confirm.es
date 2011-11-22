From: %(From)s
To: %(To)s
Reply-To: %(confirm)s
Subject: Por favor, confirme su suscripción a %(list)s
Content-type: multipart/mixed; boundary="%(boundary)s"
MIME-Version: 1.0

This is a multipart message in MIME format

--%(boundary)s
Content-type: text/plain; charset=utf-8

Hola,

Este mensaje se lo ha enviado el gestor automático que opera la
lista de correo %(list)s .

Alguien ha pedido que usted sea añadido como suscriptor de la lista.
Al final verá el mensaje enviado. Si no lo envió usted mismo, por favor,
póngase en contacto con quien lo hizo o con su administrador, para saber
qué sucede.

Si responde a este mensaje, confirmará que desea ser añadido como
suscriptor. No importa el contenido de la respuesta. Por lo común,
basta con usar la función normal de respuesta de su programa de correo.
De forma alternativa, puede enviar un mensaje a la siguiente dirección:

    %(confirm)s

Si desea instrucciones sobre el uso del software gestor de listas, envíe
un mensaje a %(local)s-help@%(domain)s .

Si tiene problemas, por favor, póngase en contacto con las personas que
gestionan la lista en %(local)s-owner@%(domain)s .
 
Gracias.

--%(boundary)s
Content-type: message/rfc822
Content-disposition: inline; filename=original.txt

%(origmail)s--%(boundary)s--

