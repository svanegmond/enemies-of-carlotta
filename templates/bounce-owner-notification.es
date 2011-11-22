From: %(From)s
To: %(To)s
Subject: Dirección eliminada de %(list)s
Content-type: multipart/mixed; boundary="%(boundary)s"
MIME-Version: 1.0

This is a multipart message in MIME format

--%(boundary)s
Content-type: text/plain; charset=utf-8

Hola,

El gestor que opera la lista de correo 

    %(list)s


ha enviado este mensaje a los operadores humanos de la lista.

La siguiente dirección ha sido eliminada de la lista debido a rebotes:

    %(address)s

Al final de este mensaje se adjunta el mensaje que rebotó. A menos que
esté pasando algo realmente extraño, este mensaje es sólo informativo, y
no necesita tomar ninguna acción al respecto.

Gracias.

--%(boundary)s
Content-type: message/rfc822
Content-disposition: inline; filename=bounce.txt
 
%(bounce)s--%(boundary)s--

