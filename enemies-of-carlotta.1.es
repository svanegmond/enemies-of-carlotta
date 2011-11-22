.TH ENEMIES\-OF\-CARLOTTA 1
.SH NAME
enemies\-of\-carlotta \- sencillo gestor de listas de correo
.SH SYNOPSIS
.B enemies\-of\-carlotta 
.IR "" [ opciones "] [" direcciones ]
.SH "DESCRIPCI�N"
.B enemies\-of\-carlotta
es un gestor sencillo para listas de correo.
Si no sabe qu� es un gestor de listas de correo, es mejor que 
aprenda lo que son, antes de intentar usar uno concreto.
Por desgracia, no hay espacio para eso en una p�gina de
manual.
.PP
Enemies of Carlotta mantiene todos los datos sobre las listas de correo
en un directorio llamado
.I ~/.enemies\-of\-carlotta .
Se crear� autom�ticamente en cuanto usted cree la primera lista.
Tendr� que hacer arreglos a mano para que el gestor de listas pueda
procesar los mensajes. 
Los detalles var�an de un servidor de correo a otro.
Para qmail y Postfix, v�ase m�s adelante.
.PP
Cada lista tiene uno o m�s propietarios, que tambi�n moderan suscripciones
o incluso algunos o todos los env�os a la lista.
En listas sin moderaci�n alguna, el propietario de la lista es el 
responsable de contestar las dudas acerca de la lista.
En listas con moderaci�n completa, tienen que aprobar cada mensaje, antes
de que �ste pueda enviarse a la lista.
En listas con la opci�n
.IR posting=auto ,
los mensajes de los suscriptores se env�an autom�ticamente a la lista,
y los moderadores tienen que aprobar el resto de mensajes.
.SH OPCIONES
.TP
.BR \-\-name= lista@ejemplo.com
Especifica sobre qu� lista ha de actuar la orden especificada.
Casi todas las restantes opciones precisan que especifique antes el nombre
de la lista con la opci�n antedicha.
Con las opciones
\-\-edit, \-\-subscribe, \-\-unsubscribe, y \-\-list ,
el nombre puede abreviarse quitando el signo @ y el dominio que le sigue.
.TP
.BI \-\-create
Crear una lista nueva.
Ha de especificar al menos un propietario con la opci�n
.BR \-\-owner .
.TP
.BI \-\-owner= direcci�n
Al crear una lista, especifica un propietario de la lista.
.TP
.BI \-\-language= c�digo\-idioma
Establece el c�digo de idioma que se usa para buscar plantillas.
El c�digo deber�a estar vac�o (opci�n por defecto, es decir ingl�s), o
un c�digo de dos letras como
.B fi
o
.BR es .
.TP	
.B \-\-cleaning\-woman
Se encarga de las direcciones de rebote y hace otras limpiezas varias.
Ha de ejecutar peri�dicamente 
.B "enemies\-of\-carlotta \-\-cleaning\-woman" ,
algo as� como una vez por hora.
Efectuar� una limpieza de todas sus listas.
.TP
.BI \-\-destroy
Eliminar la lista.
.TP
.BI \-\-edit
Modificar la configuraci�n de la lista.
.TP
.BI \-\-subscription= tipo
Al crear una lista, establece su modo de suscripci�n a
.I free
(libre) o bien
.IR moderated 
(moderado).
�selo con 
.BR \-\-edit ,
o con
.BR \-\-create .
.TP
.BI \-\-posting= tipo
Al crear una lista, establece su modo de env�o de mensajes a
.IR free
(libre),
.IR auto
(auto),
o bien
.IR moderated 
(moderado).
�selo con
.BR \-\-edit ,
o con
.BR \-\-create .
.TP
.BI \-\-archived= yes\-o\-no
Especifica si los mensajes de la lista deben archivarse en el directorio
.B archive\-box
en el directorio de la lista que a su vez existe dentro del directorio
.B "~/.enemies\-of\-carlotta" .
Utilice 
.I yes
o bien
.IR no .
.TP
.BI \-\-mail\-on\-subscription\-changes= yes\-o\-no
�Deber�a notificarse a los due�os de la lista cuando alguien se
suscribe o desuscribe de ella?
Use
.I yes
o
.IR no .
Por defecto es no.
.TP
.BI \-\-mail\-on\-forced\-unsubscription= yes\-o\-no
�Deber�a notificarse a los due�os de la lista cuando se elimina a
alguien de la lista forzosamente por exceso de rebotes?
Use
.I yes
o
.IR no .
Por defecto es no.
.TP
.BI \-\-list
Muestra los suscriptores de una lista de correo.
.TP
.BI \-\-subscribe
A�ade suscriptores a una lista de correo.
Los argumentos que no son opciones, son las direcciones que hay que
suscribir a la lista.
Observe que las direcciones que se a�adan mediante este procedimiento 
no recibir�n una confirmaci�n de suscripci�n, sino que se las 
suscribir� directamente.
.TP
.BI \-\-unsubscribe
Elimina suscriptores de una lista de correo.
Los argumentos que no son opciones, son las direcciones que hay que
desuscribir de la lista.
Observe que las direcciones que se eliminen mediante este procedimiento 
no recibir�n una confirmaci�n de desuscripci�n, sino que se las eliminar�
directamente.
.TP
.B \-\-incoming
Encargarse de un mensaje que se recibe por la entrada est�ndar.
La direcci�n del remitente del envoltorio SMTP 
(envelope sender address) debe especificarse mediante la variable 
de entorno 
.I SENDER ,
y la direcci�n del destinatario del envoltorio SMTP 
(SMTP envelope recipient address) debe especificarse en la variable
de entorno
.I RECIPIENT .
(qmail y Postfix lo hacen autom�ticamente).
.TP
.BI \-\-skip\-prefix= cadena
Antes de analizar la direcci�n del destinatario para ver a qu� lista se
refiere, eliminar 
.I cadena 
de su comienzo.
Esta caracter�stica ayuda en el caso de los dominios virtuales de
qmail y Postfix; v�ase m�s arriba.
.TP
.BI \-\-domain= nombre.dominio
Antes de analizar la direcci�n del destinatario para ver a qu� lista se 
refiere, sustituir la parte del dominio por
.IR nombre. dominio .
Esta caracter�stica es �til en el caso de los dominios virtuales de
Postfix.
.TP
.BI \-\-is\-list
�Se refiere la lista especificada en la opci�n 
.B \-\-name
a una lista v�lida?
Devuelve un estado de salida de cero (�xito) si es v�lida, o un estado
de uno (fallo) si no es v�lida.
.TP
.BI \-\-sendmail= ruta\-hasta\-el\-programa
Utilice
.I ruta\-hasta\-el\-programa
en lugar de 
.B /usr/sbin/sendmail
para enviar correo por medio de una interfaz de l�nea de �rdenes.
N�tese que la orden alternativa debe seguir las convenciones de la 
interfaz de l�nea de �rdenes sendmail.
.TP
.BI \-\-smtp\-server= nombre.de.servidor
Enviar el correo usando el servidor SMTP 
.I nombre.de.servidor
(puerto 25).
El server ha de estar configurado para permitir que la lista 
pueda efectuar la retransmisi�n de correo a trav�s de �l.
N�tese que la opci�n por defecto es usar la interfaz de l�nea
de �rdenes. Esta opci�n de enviar por SMTP s�lo se utilizar�
si la especifica expl�citamente.
.TP
.BI \-\-qmqp\-server= nombredemaquina
Enviar correo usando el servidor QMQP que hay en
.I nombredemaquina
(puerto 628).
El servidor debe estar configurado para permitir que la m�quina de
la lista reenv�e correo a trav�s suyo.
Tenga en cuenta que por defecto se usa una interfaz de l�nea de
�rdenes para el env�o; s�lo se utilizar� QMQP si especifica esta opci�n.
.TP
.BI \-\-moderate
Forzar la moderaci�n de mensajes para un mensaje dado, incluso si va a ir
a parar a una lista de mensajes donde se puede env�ar libremente.
Puede usar esta opci�n para el filtrado de correo electr�nico no 
solicitado (spam):
sus mensajes entrantes pasan por el filtro de spam que usted especifique
y si el mensaje califica como spam, se solicita la moderaci�n del mensaje
por parte de una persona.
.TP
.BI \-\-post
Forzar el env�o de un mensaje entrante a una lista dada, incluso si
va a ir a parar a una lista que tenga el env�o moderado.
Puede usar esta opci�n cuando hay una comprobaci�n externa de si
un correo es aceptable en una lista; por ejempo, si dispone de 
un comprobador de firmas digitales.
.TP
.BI \-\-quiet
De forma predeterminada, los mensajes de registro de depuraci�n se env�an
al flujo de salida de error est�ndar.
Con esta opci�n, se anula dicho comportamiento.
.TP
.BI \-\-sender= foo@ejemplo.com
.TP
.BI \-\-recipient= foo@ejemplo.com
Estas dos opciones se usan junto a
.B \-\-incoming
y
.B \-\-is\-list
para imponerse a las variables de entorno
.B SENDER
y
.BR RECIPIENT ,
respectivamente.
.TP
.BI \-\-get
Obtiene los valores de una o m�s variables de configuraci�n.
El nombre de las variables se da en la l�nea de �rdenes tras las opciones.
Cada valor se imprime en una l�nea aparte.
.TP
.BI \-\-set
Establece los valores de una o m�s variables de configuraci�n.
Los nombres y valores se dan en la l�nea de �rdenes tras las opciones
y separadas por signos 'igual' ("=").
Por ejemplo, lo siguiente establecer�a el finland�s como idioma de una
lista:
.B "enemies\-of\-carlotta \-\-name=foo@bar \-\-set language=fi"
.TP
.BI \-\-version
Muestra la versi�n del programa.
.TP
.BI \-\-show\-lists
Muestra las listas conocidas para enemies\-of\-carlotta.
.SH CONFIGURACI�N
Cada lista est� representada por un directorio, que recibe el nombre
de la lista, y que est� dentro de
.IR ~/.enemies\-of\-carlotta .
Dicho directorio contiene varios ficheros y directorios, que se describen
m�s abajo. En general, no es necesario tocarlos para nada.
Sin embargo, determinadas configuraciones, un tanto esot�ricas, s�lo pueden
establecerse editando a mano el fichero de configuraci�n de la lista.
.TP
.B config
El fichero de configuraci�n de la lista.
Su contenido se describe m�s abajo.
.TP
.B subscribers
Base de datos de suscriptores.
Cada l�nea contiene un grupo de suscriptores, siendo los cinco 
primeros campos delimitados por espacios el identificador del grupo,
el estado la marca temporal de cu�ndo se cre� el grupo, la 
marca temporal de cu�ndo cambi� su estado de 'ok' a 'bounced' 
(rebotado), y el identificador de la devoluci�n (bounce).
.TP
.B archive\-box
Mensajes de la lista archivados.
.TP
.B bounce\-box
Grupos de mensajes rebotados (bounce) y que no est�n en estado 'ok'.
.TP
.B headers\-to\-add
Cabeceras a a�adir a los mensajes enviados a esta lista.
Se copian al principio de cualquier cabecera existente exactamente tal
como est�n en el fichero, tras haber a�adido las cabeceras de la lista
("List\-ID", etc) y eliminado las mencionadas en
.B headers\-to\-remove .
.TP
.B headers\-to\-remove
Estas cabeceras se eliminan de los mensajes enviados a la lista.
.TP
.B moderation\-box
Mensajes en espera de aprobaci�n por parte del moderador.
.TP
.B subscription\-box
Solicitudes de suscripci�n y desuscripci�n en espera de confirmaci�n
por parte del usuario.
.TP
.B templates
Directorio que contiene plantillas (opcionales) espec�ficas a la lista.
Si existe este directorio, se buscan las plantillas all� antes de ir en
busca de plantillas globales. Un fichero vac�o indica que el mensaje
correspondiente no ser� enviado. Esto puede usarse, por ejemplo, para
desactivar los mensajes �espere por la moderaci�n� en determinadas
listas.
.TP
.B plugins
Directorio que contiene plugins. Son archivos fuente en Python que
carga EoC autom�ticamente al arrancar.
Los plugins pueden variar la manera en que opera EoC.
.PP
El fichero
.B config
tiene un formato 
.IR palabra_clave = valor
:
.PP
.RS
.nf
[list]
owners = liw@liw.iki.fi
archived = no
posting = free
subscription = free
mail\-on\-subscription\-changes = yes
mail\-on\-forced\-unsubscribe = yes
language = es
.fi
.RE
.PP
Las palabras clave
.BR archived , 
.BR posting ,
y 
.B subscription 
corresponden a las opciones de su mismo nombre.
Otras palabras clave son:
.TP
.B owners
Lista de las direcciones de los propietarios.
Especif�quelas con la opci�n
.I \-\-owner .
.TP
.B moderators
Lista de las direcciones de los moderadores.
Especif�quelas con la opci�n
.I \-\-moderator .
.TP
.B mail\-on\-subscription\-changes
Especifica si hay que mandar un correo a los propietarios 
de la lista cada vez que un usuario se suscribe o se desuscribe.
.TP
.B mail\-on\-forced\-unsubscribe
Especifica si hay que mandar un correo a los propietarios de la lista 
cada vez que un usuario es dado de baja por excesivo rebote de mensajes.
.TP
.B ignore_bounce
Los rebotes son ignorados en esta lista. �til por ejemplo si la lista
debe tener una lista fija de suscriptores.
.TP
.B language
Sufijo para las plantillas, para permitir el suporte de m�ltiples
lenguas.
(Si
.I language
tiene el valor "es", entonces a la plantilla llamada "aficionados" se la busca 
en primer lugar como "aficionados.es".)
.TP
.B pristine\-headers
No usar codificaci�n MIME para las cabeceras. Establecer a "yes" para no 
hacerlo, cualquier otra cosa (incluyendo vac�o o sin establecer) 
significa que se utilizar� la codificaci�n.
.SH EJEMPLOS
Para crear una lista llamada
.IR cinefilos@ejemplo.com ,
cuyo propietario sea
.IR dingo@ejemplo.com ,
utilice la siguiente orden (todo en una l�nea):
.sp 1
.nf
.RS
enemies\-of\-carlotta \-\-name=cinefilos@ejemplo.com
\-\-owner=dingo@ejemplo.com \-\-create
.RE
.PP
Observe que debe configurar su servidor de correo en concreto 
para que el correo llegue a la lista.
Para qmail y postfix, v�ase infra.
.PP
To see the subscribers on that list:
.sp 1
.RS
enemies\-of\-carlotta \-\-name=cinefilos@ejemplo.com \-\-list
.RE
.PP
Quien quiera suscribirse a la lista ha de escribir un correo a:
.sp 1
.RS
cinefilos\-subscribe@ejemplo.com
.RE
.SH QMAIL
Con qmail, para conseguir que el correo entrante sea procesado por 
Enemies of Carlotta, tiene que crear dos ficheros
.I .qmail\-extension
por cada lista.
Por ejemplo, si su nombre de usuario es pepe y quiere ejecutar la
lista pepe\-aficionados, ha de crear dos ficheros, 
.I .qmail\-aficionados
y 
.IR .qmail\-aficionados\-default ,
que contengan la l�nea
.sp 1
.RS
|enemies\-of\-carlotta \-\-incoming
.RE
.PP
Si tiene configurado un dominio virtual, ejemplo.com, y los correos
se entregan v�a
.I /var/qmail/control/virtualdomains a pepe\-ejemplodotcom ,
los ficheros se llamar�an
.I .qmail\-ejemplodotcom\-aficionados
y 
.I .qmail\-ejemplodotcom\-aficionados-default
y contendr�an
.sp 1
.RS
|enemies\-of\-carlotta \-\-incoming \-\-skip\-prefix=pepe\-ejemplodotcom\-
.RE
.sp 1
(todo en una l�nea, claro, por si acaso su lector de p�ginas de manual
formatea la orden anterior en varias l�neas).
.SH POSTFIX
Con postfix, ha de configurar un fichero
.I .forward
que contenga
.sp 1
.RS
"|procmail \-p"
.RE
.sp 1
y adem�s un fichero 
.I .procmailrc
que contenga
.sp 1
.RS
:0
.br
* ? enemies\-of\-carlotta \-\-name=$RECIPIENT \-\-is\-list
.br
| enemies\-of\-carlotta \-\-incoming
.RE
.PP
Para usar Enemies of Carlotta con un dominio virtual de Postfix, 
ha de configurar un 
.I "mapa virtual de expresiones regulares",
que t�picamente est� en 
.I /etc/postfix/virtual_regexp
(a�ada 
.I "virtual_maps = regexp:/etc/postfix/virtual_regexp"
a su fichero 
.I /etc/postfix/main.cf
para activar esta carcter�stica).
El fichero de expresiones regulares ha de hacer cosas extra�as para
conservar la direcci�n del destinatario.
A�ada lo siguiente al fichero de expresiones regulares:
.sp 1
.RS
/^su\.dominio\.virtual$/ dummy
.br
/^(sulista|sulista\-.*)@(su\.dominio\.virtual)$/ pepe+virtual\-$1
.RE
.sp 1
(Lo anterior estaba en dos l�neas). Utilize
.B pepe-virtual
en lugar del anterior si el
.I recipient_delimiter
de su Postfix est� configurado para usar un signo menos en vez de m�s.
Luego, en su fichero
.I .procmailrc
a�ada la opci�n 
.I "\-\-skip\-prefix=pepe\-virtual\-"
y tambi�n
.I \-\-domain=your.virtual.domain
para las dos llamadas a 
.BR enemies\-of\-carlotta .
.PP
(S�, nosotros tambi�n pensamos que estas configuraciones son demasiado complicadas).
.SH "�RDENES PARA EL CORREO"
Los usuarios y los propietarios de las listas utilizan 
Enemies of Carlotta a trav�s del correo electr�nico, usando para ello
direcciones a modo de �rdenes, como por ejemplo
.BR aficionados\-subscribe@ejemplo.com .
He aqu� una lista de todas las �rdenes que pueden usar tanto usuarios 
como propietarios de listas de correo.
En todos estos ejemplos, el nombre de la lista de correo es
.BR aficionados@ejemplo.com .
.SS "�rdenes a trav�s de correo que pueden usar todos"
Estas �rdenes est�n pensadas para el uso general.
No precisan de ning�n privilegio especial.
.TP
.BR aficionados@ejemplo.com
Enviar correo a todos los suscritos a la lista.
El mensaje pueden haberlo aprobado previamente de forma manual los administradores
de la lista, que est�n facultados para rechazar los mensajes.
.TP
.BR aficionados\-owner@ejemplo.com
Enviar un correo al propietario o propietarios de la lista.
.TP
.BR aficionados\-help@ejemplo.com
Enviar un correo a esta direcci�n hace que el gestor de listas de 
correo nos devuelva un correo con la ayuda existente sobre la
lista en cuesti�n.
.TP
.BR aficionados\-subscribe@ejemplo.com
Env�e un mensaje a esta direcci�n para suscribirse a la lista.
El gestor de listas de correo le responder� con una confirmaci�n 
de suscripci�n.
No se le suscribir� a la lista a menos que responda a la petici�n
de confirmaci�n. 
De esta forma, un usuario malicioso no podr� poner su direcci�n 
en una o en muchas listas de correo.
.TP
.BR aficionados\-subscribe\-pepe=ejemplo.com@ejemplo.com
Esta es una manera alternativa de la direcci�n de suscripci�n.
Si desea suscribirse a la lista de correo con una direcci�n distinta
a aquella desde la que env�a el mensaje, utilice esta modalidad.
En este caso, la direcci�n para suscribirse es pepe@ejemplo.com.
N�tese que la petici�n de confirmaci�n se env�a a Pepe, puesto
que es su direcci�n la que va a a�adirse a la lista.
.TP
.BR aficionados\-unsubscribe@ejemplo.com
Para desuscribirse de una lista, env�e un correo a esta direcci�n
desde la direcci�n que desea desuscribir de la lista.
De nuevo recibir� una petici�n de confirmaci�n, para evitar que
un usuario malicioso le desuscriba de una lista de correo contra su 
voluntad.
.TP
.BR aficionados\-unsubscribe\-pepe=ejemplo.com@ejemplo.com
Para desuscribir a Pepe, use esta direcci�n.
De nuevo, es Pepe quien recibir� la petici�n de confirmaci�n.
.SS "�rdenes a trav�s de correo que pueden usar los propietarios de las listas"
Se trata de �rdenes que pueden usar los propietarios de listas para administrar su lista.
.TP
.BR aficionados\-subscribe\-pepe=ejemplo.com@ejemplo.com
Si un propietario de una lista env�a un correo a la direcci�n anterior, 
�l recibir� la petici�n de confirmaci�n, y no Pepe.
Generalmente es mejor que los usuarios se suscriban ellos mismos, pero 
a veces los propietarios de listas pueden desear esta caracter�stica,
cuando tienen permiso de la persona afectada y quieren resultar m�s
�tiles.
.TP
.BR aficionados\-unsubscribe\-pepe=ejemplo.com@ejemplo.com
Los propietarios de listas tambi�n pueden desuscribir a otros usuarios.
.TP
.BR aficionados\-list@ejemplo.com
Para ver qui�n est� en la lista, env�e un correo a esta direcci�n.
S�lo funciona si la direcci�n del remitente del correo coincide
con un propietario de la lista. La direcci�n "sender address" se usa
a nivel del protocolo SMTP, y no es la del encabezamiento "From:"
.TP
.BR aficionados\-setlist@ejemplo.com
Esta orden permite al propietario de una lista especificar de una 
sola vez toda la lista de suscriptores. Es equivalente a utilizar
montones y montones de �rdenes \-subscribe y \-unsubscribe, s�lo que menos
tedioso.
Todo el que resulte a�adido a la lista recibe un mensaje de bienvenida,
y todo el que quede eliminado de la lista recibe un mensaje de despedida.
.TP
.BR aficionados\-setlistsilently@ejemplo.com
Semejante a -setlist, pero no se env�an mensajes ni de bienvenida, ni 
de despedida.
.SH PLUGINS
Enemies of Carlotta admite plugins.
Si no sabe programar en Python, probablemente se puede saltar esta
secci�n.
.PP
Un plugin es un m�dulo de Python (fichero con un sufijo
.B .py
en el nombre), situado en el directorio
.B ~/.enemies-of-carlotta/plugins .
Los plugins se cargan autom�ticamente durante el arranque, si la versi�n
declarada de su interfaz se ajusta con la implementada por Enemies of
Carlotta. La versi�n de la interfaz se declara en la variable global del
m�dulo
.BR PLUGIN_INTERFACE_VERSION .
.PP
Los plugin pueden definir funciones que ser�n invocadas desde los lugares
apropiados del c�digo EoC.
Por el momento, la �nica funci�n de enganche (hook) disponible es
.BR send_mail_to_subscribers_hook ,
que puede manipular un mensaje antes de que sea enviado a los suscriptores.
La funci�n debe parecerse a esto:
.PP
.ti +5
def send_mail_to_subscribers_hook(list, text):
.PP
El argumento
.I list
es una referencia al objeto
.I MailingList
que corresponde a la lista en cuesti�n, y
.I text
es el texto completo del mensaje de correo en su forma actual.
La funci�n debe devolver el nuevo contenido del mensaje de correo.
.SH FICHEROS
.TP
.I ~/.enemies\-of\-carlotta
Aqu� est�n todos los ficheros relacionados con sus listas de correo.
.TP
.I ~/.enemies\-of\-carlotta/secret
Contrase�a secreta que se usa para generar direcciones firmadas
para comprobaci�n de rebotes de correo y verificaci�n de suscripci�n.
.TP
.I ~/.enemies\-of\-carlotta/aficionados@ejemplo.com
Directorio que contiene los datos relativos a la lista 
aficionados@ejemplo.com. Excepto el fichero
.I config
de este directorio, no debe editar a mano nada de lo contenido en �l.
.TP
.I ~/.enemies\-of\-carlotta/aficionados@ejemplo.com/config
Fichero de configuraci�n de la lista de correo.
Quiz� tenga que editar este fichero a mano si desea cambiar el estado
de moderaci�n de la lista o sus propietarios.
.SH "V�ASE TAMBI�N"
Visite la p�gina de 
.I "Enemies of Carlotta"
alojada en 
.IR http://www.iki.fi/liw/eoc/ .
.TP
La traducci�n de esta p�gina ha corrido a cargo de Iv�n Juanes
.BR kerberos@gulic.org
y de Ricardo C�rdenes
.BR heimy@gulic.org
como parte de los proyectos del grupo Gulic.
