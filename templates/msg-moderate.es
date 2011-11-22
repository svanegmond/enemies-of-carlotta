From: %(From)s
To: %(To)s
Reply-To: %(confirm)s
Subject: Por favor, modere este mensaje enviado a %(list)s
Content-type: multipart/mixed; boundary="%(boundary)s"
MIME-Version: 1.0

This is a multipart message in MIME format

--%(boundary)s
Content-type: text/plain; charset=utf-8

Hola,

Este mensaje lo ha enviado el gestor de listas de correo que lleva

    %(list)s

a los moderadores humanos que la supervisan.

¿Debería permitirse enviar a la lista el mensaje que sigue? En caso
afirmativo, responda a este mensaje o envíe un mensaje a

    %(confirm)s

Si no, envíe un mensaje a

    %(deny)s

Gracias.

--%(boundary)s
Content-type: message/rfc822
Content-disposition: inline; filename=original.txt

%(origmail)s--%(boundary)s--

