From: %(From)s
To: %(To)s
Subject: Ayuda de la lista de correo %(list)s
Content-type: text/plain; charset=utf-8
MIME-Version: 1.0

Hola,

éste es el texto de ayuda de la lista de correo  %(list)s.

La lista la maneja el gestor de listas de correo EoC, que
entiende las siguientes órdenes mediante direcciones de correo:

    %(local)s-help@%(domain)s

    	Envía este texto de ayuda.

    %(local)s-subscribe@%(domain)s
    
	Suscribirse a la lista. Recibirá una petición de confirmación.
	
    %(local)s-subscribe-foo=bar@%(domain)s
    
	Suscribir la dirección foo@bar a la lista. foo@bar recibirá la
	petición de confirmación.

    %(local)s-unsubscribe@%(domain)s
    
	Desuscribirse de la lista. Recibirá una petición de confirmación.
	
    %(local)s-unsubscribe-foo=bar@%(domain)s
    
	Desuscribir la dirección foo@bar de la lista. foo@bar recibirá la
	petición de confirmación.

Si tiene algún problema que no resuelva este texto de ayuda, póngase en
contacto por favor con la persona que supervisa la lista en
%(local)s-owner@%(domain)s .

Gracias.
