.TH ENEMIES\-OF\-CARLOTTA 1
.SH NAME
enemies\-of\-carlotta \- sencillo gestor de listas de correo
.SH SYNOPSIS
.B enemies\-of\-carlotta 
.IR "" [ opciones "] [" direcciones ]
.SH "DESCRIPCIÓN"
.B enemies\-of\-carlotta
es un gestor sencillo para listas de correo.
Si no sabe qué es un gestor de listas de correo, es mejor que 
aprenda lo que son, antes de intentar usar uno concreto.
Por desgracia, no hay espacio para eso en una página de
manual.
.PP
Enemies of Carlotta mantiene todos los datos sobre las listas de correo
en un directorio llamado
.I ~/.enemies\-of\-carlotta .
Se creará automáticamente en cuanto usted cree la primera lista.
Tendrá que hacer arreglos a mano para que el gestor de listas pueda
procesar los mensajes. 
Los detalles varían de un servidor de correo a otro.
Para qmail y Postfix, véase más adelante.
.PP
Cada lista tiene uno o más propietarios, que también moderan suscripciones
o incluso algunos o todos los envíos a la lista.
En listas sin moderación alguna, el propietario de la lista es el 
responsable de contestar las dudas acerca de la lista.
En listas con moderación completa, tienen que aprobar cada mensaje, antes
de que éste pueda enviarse a la lista.
En listas con la opción
.IR posting=auto ,
los mensajes de los suscriptores se envían automáticamente a la lista,
y los moderadores tienen que aprobar el resto de mensajes.
.SH OPCIONES
.TP
.BR \-\-name= lista@ejemplo.com
Especifica sobre qué lista ha de actuar la orden especificada.
Casi todas las restantes opciones precisan que especifique antes el nombre
de la lista con la opción antedicha.
Con las opciones
\-\-edit, \-\-subscribe, \-\-unsubscribe, y \-\-list ,
el nombre puede abreviarse quitando el signo @ y el dominio que le sigue.
.TP
.BI \-\-create
Crear una lista nueva.
Ha de especificar al menos un propietario con la opción
.BR \-\-owner .
.TP
.BI \-\-owner= dirección
Al crear una lista, especifica un propietario de la lista.
.TP
.BI \-\-language= código\-idioma
Establece el código de idioma que se usa para buscar plantillas.
El código debería estar vacío (opción por defecto, es decir inglés), o
un código de dos letras como
.B fi
o
.BR es .
.TP	
.B \-\-cleaning\-woman
Se encarga de las direcciones de rebote y hace otras limpiezas varias.
Ha de ejecutar periódicamente 
.B "enemies\-of\-carlotta \-\-cleaning\-woman" ,
algo así como una vez por hora.
Efectuará una limpieza de todas sus listas.
.TP
.BI \-\-destroy
Eliminar la lista.
.TP
.BI \-\-edit
Modificar la configuración de la lista.
.TP
.BI \-\-subscription= tipo
Al crear una lista, establece su modo de suscripción a
.I free
(libre) o bien
.IR moderated 
(moderado).
Úselo con 
.BR \-\-edit ,
o con
.BR \-\-create .
.TP
.BI \-\-posting= tipo
Al crear una lista, establece su modo de envío de mensajes a
.IR free
(libre),
.IR auto
(auto),
o bien
.IR moderated 
(moderado).
Úselo con
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
¿Debería notificarse a los dueños de la lista cuando alguien se
suscribe o desuscribe de ella?
Use
.I yes
o
.IR no .
Por defecto es no.
.TP
.BI \-\-mail\-on\-forced\-unsubscription= yes\-o\-no
¿Debería notificarse a los dueños de la lista cuando se elimina a
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
Añade suscriptores a una lista de correo.
Los argumentos que no son opciones, son las direcciones que hay que
suscribir a la lista.
Observe que las direcciones que se añadan mediante este procedimiento 
no recibirán una confirmación de suscripción, sino que se las 
suscribirá directamente.
.TP
.BI \-\-unsubscribe
Elimina suscriptores de una lista de correo.
Los argumentos que no son opciones, son las direcciones que hay que
desuscribir de la lista.
Observe que las direcciones que se eliminen mediante este procedimiento 
no recibirán una confirmación de desuscripción, sino que se las eliminará
directamente.
.TP
.B \-\-incoming
Encargarse de un mensaje que se recibe por la entrada estándar.
La dirección del remitente del envoltorio SMTP 
(envelope sender address) debe especificarse mediante la variable 
de entorno 
.I SENDER ,
y la dirección del destinatario del envoltorio SMTP 
(SMTP envelope recipient address) debe especificarse en la variable
de entorno
.I RECIPIENT .
(qmail y Postfix lo hacen automáticamente).
.TP
.BI \-\-skip\-prefix= cadena
Antes de analizar la dirección del destinatario para ver a qué lista se
refiere, eliminar 
.I cadena 
de su comienzo.
Esta característica ayuda en el caso de los dominios virtuales de
qmail y Postfix; véase más arriba.
.TP
.BI \-\-domain= nombre.dominio
Antes de analizar la dirección del destinatario para ver a qué lista se 
refiere, sustituir la parte del dominio por
.IR nombre. dominio .
Esta característica es útil en el caso de los dominios virtuales de
Postfix.
.TP
.BI \-\-is\-list
¿Se refiere la lista especificada en la opción 
.B \-\-name
a una lista válida?
Devuelve un estado de salida de cero (éxito) si es válida, o un estado
de uno (fallo) si no es válida.
.TP
.BI \-\-sendmail= ruta\-hasta\-el\-programa
Utilice
.I ruta\-hasta\-el\-programa
en lugar de 
.B /usr/sbin/sendmail
para enviar correo por medio de una interfaz de línea de órdenes.
Nótese que la orden alternativa debe seguir las convenciones de la 
interfaz de línea de órdenes sendmail.
.TP
.BI \-\-smtp\-server= nombre.de.servidor
Enviar el correo usando el servidor SMTP 
.I nombre.de.servidor
(puerto 25).
El server ha de estar configurado para permitir que la lista 
pueda efectuar la retransmisión de correo a través de él.
Nótese que la opción por defecto es usar la interfaz de línea
de órdenes. Esta opción de enviar por SMTP sólo se utilizará
si la especifica explícitamente.
.TP
.BI \-\-qmqp\-server= nombredemaquina
Enviar correo usando el servidor QMQP que hay en
.I nombredemaquina
(puerto 628).
El servidor debe estar configurado para permitir que la máquina de
la lista reenvíe correo a través suyo.
Tenga en cuenta que por defecto se usa una interfaz de línea de
órdenes para el envío; sólo se utilizará QMQP si especifica esta opción.
.TP
.BI \-\-moderate
Forzar la moderación de mensajes para un mensaje dado, incluso si va a ir
a parar a una lista de mensajes donde se puede envíar libremente.
Puede usar esta opción para el filtrado de correo electrónico no 
solicitado (spam):
sus mensajes entrantes pasan por el filtro de spam que usted especifique
y si el mensaje califica como spam, se solicita la moderación del mensaje
por parte de una persona.
.TP
.BI \-\-post
Forzar el envío de un mensaje entrante a una lista dada, incluso si
va a ir a parar a una lista que tenga el envío moderado.
Puede usar esta opción cuando hay una comprobación externa de si
un correo es aceptable en una lista; por ejempo, si dispone de 
un comprobador de firmas digitales.
.TP
.BI \-\-quiet
De forma predeterminada, los mensajes de registro de depuración se envían
al flujo de salida de error estándar.
Con esta opción, se anula dicho comportamiento.
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
Obtiene los valores de una o más variables de configuración.
El nombre de las variables se da en la línea de órdenes tras las opciones.
Cada valor se imprime en una línea aparte.
.TP
.BI \-\-set
Establece los valores de una o más variables de configuración.
Los nombres y valores se dan en la línea de órdenes tras las opciones
y separadas por signos 'igual' ("=").
Por ejemplo, lo siguiente establecería el finlandés como idioma de una
lista:
.B "enemies\-of\-carlotta \-\-name=foo@bar \-\-set language=fi"
.TP
.BI \-\-version
Muestra la versión del programa.
.TP
.BI \-\-show\-lists
Muestra las listas conocidas para enemies\-of\-carlotta.
.SH CONFIGURACIÓN
Cada lista está representada por un directorio, que recibe el nombre
de la lista, y que está dentro de
.IR ~/.enemies\-of\-carlotta .
Dicho directorio contiene varios ficheros y directorios, que se describen
más abajo. En general, no es necesario tocarlos para nada.
Sin embargo, determinadas configuraciones, un tanto esotéricas, sólo pueden
establecerse editando a mano el fichero de configuración de la lista.
.TP
.B config
El fichero de configuración de la lista.
Su contenido se describe más abajo.
.TP
.B subscribers
Base de datos de suscriptores.
Cada línea contiene un grupo de suscriptores, siendo los cinco 
primeros campos delimitados por espacios el identificador del grupo,
el estado la marca temporal de cuándo se creó el grupo, la 
marca temporal de cuándo cambió su estado de 'ok' a 'bounced' 
(rebotado), y el identificador de la devolución (bounce).
.TP
.B archive\-box
Mensajes de la lista archivados.
.TP
.B bounce\-box
Grupos de mensajes rebotados (bounce) y que no están en estado 'ok'.
.TP
.B headers\-to\-add
Cabeceras a añadir a los mensajes enviados a esta lista.
Se copian al principio de cualquier cabecera existente exactamente tal
como estén en el fichero, tras haber añadido las cabeceras de la lista
("List\-ID", etc) y eliminado las mencionadas en
.B headers\-to\-remove .
.TP
.B headers\-to\-remove
Estas cabeceras se eliminan de los mensajes enviados a la lista.
.TP
.B moderation\-box
Mensajes en espera de aprobación por parte del moderador.
.TP
.B subscription\-box
Solicitudes de suscripción y desuscripción en espera de confirmación
por parte del usuario.
.TP
.B templates
Directorio que contiene plantillas (opcionales) específicas a la lista.
Si existe este directorio, se buscan las plantillas allí antes de ir en
busca de plantillas globales. Un fichero vacío indica que el mensaje
correspondiente no será enviado. Esto puede usarse, por ejemplo, para
desactivar los mensajes «espere por la moderación» en determinadas
listas.
.TP
.B plugins
Directorio que contiene plugins. Son archivos fuente en Python que
carga EoC automáticamente al arrancar.
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
Especifíquelas con la opción
.I \-\-owner .
.TP
.B moderators
Lista de las direcciones de los moderadores.
Especifíquelas con la opción
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
Los rebotes son ignorados en esta lista. Útil por ejemplo si la lista
debe tener una lista fija de suscriptores.
.TP
.B language
Sufijo para las plantillas, para permitir el suporte de múltiples
lenguas.
(Si
.I language
tiene el valor "es", entonces a la plantilla llamada "aficionados" se la busca 
en primer lugar como "aficionados.es".)
.TP
.B pristine\-headers
No usar codificación MIME para las cabeceras. Establecer a "yes" para no 
hacerlo, cualquier otra cosa (incluyendo vacío o sin establecer) 
significa que se utilizará la codificación.
.SH EJEMPLOS
Para crear una lista llamada
.IR cinefilos@ejemplo.com ,
cuyo propietario sea
.IR dingo@ejemplo.com ,
utilice la siguiente orden (todo en una línea):
.sp 1
.nf
.RS
enemies\-of\-carlotta \-\-name=cinefilos@ejemplo.com
\-\-owner=dingo@ejemplo.com \-\-create
.RE
.PP
Observe que debe configurar su servidor de correo en concreto 
para que el correo llegue a la lista.
Para qmail y postfix, véase infra.
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
que contengan la línea
.sp 1
.RS
|enemies\-of\-carlotta \-\-incoming
.RE
.PP
Si tiene configurado un dominio virtual, ejemplo.com, y los correos
se entregan vía
.I /var/qmail/control/virtualdomains a pepe\-ejemplodotcom ,
los ficheros se llamarían
.I .qmail\-ejemplodotcom\-aficionados
y 
.I .qmail\-ejemplodotcom\-aficionados-default
y contendrían
.sp 1
.RS
|enemies\-of\-carlotta \-\-incoming \-\-skip\-prefix=pepe\-ejemplodotcom\-
.RE
.sp 1
(todo en una línea, claro, por si acaso su lector de páginas de manual
formatea la orden anterior en varias líneas).
.SH POSTFIX
Con postfix, ha de configurar un fichero
.I .forward
que contenga
.sp 1
.RS
"|procmail \-p"
.RE
.sp 1
y además un fichero 
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
que típicamente está en 
.I /etc/postfix/virtual_regexp
(añada 
.I "virtual_maps = regexp:/etc/postfix/virtual_regexp"
a su fichero 
.I /etc/postfix/main.cf
para activar esta carcterística).
El fichero de expresiones regulares ha de hacer cosas extrañas para
conservar la dirección del destinatario.
Añada lo siguiente al fichero de expresiones regulares:
.sp 1
.RS
/^su\.dominio\.virtual$/ dummy
.br
/^(sulista|sulista\-.*)@(su\.dominio\.virtual)$/ pepe+virtual\-$1
.RE
.sp 1
(Lo anterior estaba en dos líneas). Utilize
.B pepe-virtual
en lugar del anterior si el
.I recipient_delimiter
de su Postfix está configurado para usar un signo menos en vez de más.
Luego, en su fichero
.I .procmailrc
añada la opción 
.I "\-\-skip\-prefix=pepe\-virtual\-"
y también
.I \-\-domain=your.virtual.domain
para las dos llamadas a 
.BR enemies\-of\-carlotta .
.PP
(Sí, nosotros también pensamos que estas configuraciones son demasiado complicadas).
.SH "ÓRDENES PARA EL CORREO"
Los usuarios y los propietarios de las listas utilizan 
Enemies of Carlotta a través del correo electrónico, usando para ello
direcciones a modo de órdenes, como por ejemplo
.BR aficionados\-subscribe@ejemplo.com .
He aquí una lista de todas las órdenes que pueden usar tanto usuarios 
como propietarios de listas de correo.
En todos estos ejemplos, el nombre de la lista de correo es
.BR aficionados@ejemplo.com .
.SS "Órdenes a través de correo que pueden usar todos"
Estas órdenes están pensadas para el uso general.
No precisan de ningún privilegio especial.
.TP
.BR aficionados@ejemplo.com
Enviar correo a todos los suscritos a la lista.
El mensaje pueden haberlo aprobado previamente de forma manual los administradores
de la lista, que están facultados para rechazar los mensajes.
.TP
.BR aficionados\-owner@ejemplo.com
Enviar un correo al propietario o propietarios de la lista.
.TP
.BR aficionados\-help@ejemplo.com
Enviar un correo a esta dirección hace que el gestor de listas de 
correo nos devuelva un correo con la ayuda existente sobre la
lista en cuestión.
.TP
.BR aficionados\-subscribe@ejemplo.com
Envíe un mensaje a esta dirección para suscribirse a la lista.
El gestor de listas de correo le responderá con una confirmación 
de suscripción.
No se le suscribirá a la lista a menos que responda a la petición
de confirmación. 
De esta forma, un usuario malicioso no podrá poner su dirección 
en una o en muchas listas de correo.
.TP
.BR aficionados\-subscribe\-pepe=ejemplo.com@ejemplo.com
Esta es una manera alternativa de la dirección de suscripción.
Si desea suscribirse a la lista de correo con una dirección distinta
a aquella desde la que envía el mensaje, utilice esta modalidad.
En este caso, la dirección para suscribirse es pepe@ejemplo.com.
Nótese que la petición de confirmación se envía a Pepe, puesto
que es su dirección la que va a añadirse a la lista.
.TP
.BR aficionados\-unsubscribe@ejemplo.com
Para desuscribirse de una lista, envíe un correo a esta dirección
desde la dirección que desea desuscribir de la lista.
De nuevo recibirá una petición de confirmación, para evitar que
un usuario malicioso le desuscriba de una lista de correo contra su 
voluntad.
.TP
.BR aficionados\-unsubscribe\-pepe=ejemplo.com@ejemplo.com
Para desuscribir a Pepe, use esta dirección.
De nuevo, es Pepe quien recibirá la petición de confirmación.
.SS "Órdenes a través de correo que pueden usar los propietarios de las listas"
Se trata de órdenes que pueden usar los propietarios de listas para administrar su lista.
.TP
.BR aficionados\-subscribe\-pepe=ejemplo.com@ejemplo.com
Si un propietario de una lista envía un correo a la dirección anterior, 
él recibirá la petición de confirmación, y no Pepe.
Generalmente es mejor que los usuarios se suscriban ellos mismos, pero 
a veces los propietarios de listas pueden desear esta característica,
cuando tienen permiso de la persona afectada y quieren resultar más
útiles.
.TP
.BR aficionados\-unsubscribe\-pepe=ejemplo.com@ejemplo.com
Los propietarios de listas también pueden desuscribir a otros usuarios.
.TP
.BR aficionados\-list@ejemplo.com
Para ver quién está en la lista, envíe un correo a esta dirección.
Sólo funciona si la dirección del remitente del correo coincide
con un propietario de la lista. La dirección "sender address" se usa
a nivel del protocolo SMTP, y no es la del encabezamiento "From:"
.TP
.BR aficionados\-setlist@ejemplo.com
Esta orden permite al propietario de una lista especificar de una 
sola vez toda la lista de suscriptores. Es equivalente a utilizar
montones y montones de órdenes \-subscribe y \-unsubscribe, sólo que menos
tedioso.
Todo el que resulte añadido a la lista recibe un mensaje de bienvenida,
y todo el que quede eliminado de la lista recibe un mensaje de despedida.
.TP
.BR aficionados\-setlistsilently@ejemplo.com
Semejante a -setlist, pero no se envían mensajes ni de bienvenida, ni 
de despedida.
.SH PLUGINS
Enemies of Carlotta admite plugins.
Si no sabe programar en Python, probablemente se puede saltar esta
sección.
.PP
Un plugin es un módulo de Python (fichero con un sufijo
.B .py
en el nombre), situado en el directorio
.B ~/.enemies-of-carlotta/plugins .
Los plugins se cargan automáticamente durante el arranque, si la versión
declarada de su interfaz se ajusta con la implementada por Enemies of
Carlotta. La versión de la interfaz se declara en la variable global del
módulo
.BR PLUGIN_INTERFACE_VERSION .
.PP
Los plugin pueden definir funciones que serán invocadas desde los lugares
apropiados del código EoC.
Por el momento, la única función de enganche (hook) disponible es
.BR send_mail_to_subscribers_hook ,
que puede manipular un mensaje antes de que sea enviado a los suscriptores.
La función debe parecerse a esto:
.PP
.ti +5
def send_mail_to_subscribers_hook(list, text):
.PP
El argumento
.I list
es una referencia al objeto
.I MailingList
que corresponde a la lista en cuestión, y
.I text
es el texto completo del mensaje de correo en su forma actual.
La función debe devolver el nuevo contenido del mensaje de correo.
.SH FICHEROS
.TP
.I ~/.enemies\-of\-carlotta
Aquí están todos los ficheros relacionados con sus listas de correo.
.TP
.I ~/.enemies\-of\-carlotta/secret
Contraseña secreta que se usa para generar direcciones firmadas
para comprobación de rebotes de correo y verificación de suscripción.
.TP
.I ~/.enemies\-of\-carlotta/aficionados@ejemplo.com
Directorio que contiene los datos relativos a la lista 
aficionados@ejemplo.com. Excepto el fichero
.I config
de este directorio, no debe editar a mano nada de lo contenido en él.
.TP
.I ~/.enemies\-of\-carlotta/aficionados@ejemplo.com/config
Fichero de configuración de la lista de correo.
Quizá tenga que editar este fichero a mano si desea cambiar el estado
de moderación de la lista o sus propietarios.
.SH "VÉASE TAMBIÉN"
Visite la página de 
.I "Enemies of Carlotta"
alojada en 
.IR http://www.iki.fi/liw/eoc/ .
.TP
La traducción de esta página ha corrido a cargo de Iván Juanes
.BR kerberos@gulic.org
y de Ricardo Cárdenes
.BR heimy@gulic.org
como parte de los proyectos del grupo Gulic.
