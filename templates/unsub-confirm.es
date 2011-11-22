From: %(From)s
To: %(To)s
Reply-To: %(confirm)s
Subject: Por favor, confirme la cancelación de suscripción a %(list)s
Content-type: multipart/mixed; boundary="%(boundary)s"
MIME-Version: 1.0

This is a multipart message in MIME format

--%(boundary)s
Content-type: text/plain; charset=utf-8

Hola,

Este mensaje lo ha enviado el gestor de listas de correo que opera
sobre %(list)s .

Alguien ha pedido que se cancele su suscripción a la lista. Lea el mensaje
que se envió al final del todo. Si no lo envió usted mismo, por favor,
póngase en contacto con quien lo hizo, o sus administradores, y pregúnteles
qué está pasando.

Si responde a este mensaje, confirmará que desea la cancelación. Por lo
común, basta con usar la función normal de respuesta de su programa de
correo. De forma alternativa, puede enviar mensajes a las siguientes
direcciones:

    %(confirm)s

Si desea continuar con su suscripción, no hace falta que haga nada.

Si desea instrucciones sobre el uso del software gestor de listas, envíe
un mensaje a %(local)s-help@%(domain)s.

Si tiene problemas, por favor, póngase en contacto con las personas que
gestionan la lista en %(local)s-owner@%(domain)s.

Gracias.

--%(boundary)s
Content-type: message/rfc822
Content-disposition: inline; filename=original.txt

%(origmail)s--%(boundary)s--

