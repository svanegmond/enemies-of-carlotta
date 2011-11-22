From: %(From)s
To: %(To)s
Reply-To: %(confirm)s
Subject: Por favor, modere esta suscripción a %(list)s
Content-type: multipart/mixed; boundary="%(boundary)s"
MIME-Version: 1.0

This is a multipart message in MIME format

--%(boundary)s
Content-type: text/plain; charset=utf-8

Hola,

Este mensaje lo ha enviado el gestor que opera la lista de correo

    %(list)s

a sus administradores humanos.

¿Debería permitirse a la siguiente dirección suscribirse a la lista?

    %(subscriber)s

En caso afirmativo, responda a este mensaje o envíe uno a

    %(confirm)s

Si desea rechazar al suscriptor, envíe un mensaje a

    %(deny)s

Gracias.

--%(boundary)s
Content-type: message/rfc822
Content-disposition: inline; filename=original.txt
 
%(origmail)s--%(boundary)s--

