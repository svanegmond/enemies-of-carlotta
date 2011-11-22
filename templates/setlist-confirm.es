From: %(From)s
To: %(To)s
Reply-To: %(confirm)s
Subject: Por favor, modere la lista de suscriptores de %(list)s
Content-type: multipart/mixed; boundary="%(boundary)s"
MIME-Version: 1.0

This is a multipart message in MIME format

--%(boundary)s
Content-type: text/plain; charset=utf-8

Hola,

Este mensaje se lo ha enviado el gestor de listas de correo que opera
sobre %(list)s .

Uno de los miembros de la lista (o alguien que pretende serlo) ha pedido
que se cambie el registro de suscriptores. Se adjunta el mensaje de la 
petición, con el nuevo conjunto de suscriptores. Si acepta el cambio, 
responda a este mensaje. En caso contrario, limítese a ignorarlo.

Tenga en cuenta que se cambiará la lista de suscriptores completa por la
lista que aparece debajo. Olvidaré todos los suscriptores antiguos a menos
que también estén en la lista nueva.

Si desea instrucciones sobre el uso del software gestor de listas, envíe
un mensaje a %(local)s-help@%(domain)s .

Si tiene problemas, por favor, póngase en contacto con las personas que
gestionan la lista en %(local)s-owner@%(domain)s .

Gracias.

--%(boundary)s
Content-type: message/rfc822
Content-disposition: inline; filename=original.txt

%(origmail)s--%(boundary)s--

