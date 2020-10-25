# Obteniendo la *PLOAM password* de un router F@ST 5657 <!-- omit in toc -->

Lo que te voy a contar **no es una vulnerabilidad**, ni tampoco un fallo de seguridad del operador. Las acciones descritas tan sólo afectan a tu propio router.

Se trata, sencillamente, de aprovechar la administración remota.

Pero también podemos verlo como un modo de acercarse a un problema y trazar un plan con las opciones disponibles, para obtener el resultado deseado. Resultado que se aparta del diseño original del sistema. Es, dicho de otra manera, un relato sobre **hacking**.

- [Redes de fibra](#redes-de-fibra)
- [Aproximaciones fallidas](#aproximaciones-fallidas)
- [El CWMP, más conocido por TR-069](#el-cwmp-más-conocido-por-tr-069)
- [Ganar admin](#ganar-admin)
- [MitM al CWMP TR-069](#mitm-al-cwmp-tr-069)
- [Habilitar administración por SSH](#habilitar-administración-por-ssh)

## Redes de fibra

La semana pasada me instalaron "la fibra".

Han pasado diez años desde el comienzo en Telefónica de un proyecto llamado FTTH (Fiber To The Home). Consistía en sustituir por fibra óptica el par trenzado de la *última milla*. Sonaba a ciencia ficción por entonces. La fibra estaba reservada a los troncales y redes de enlace especiales. Lo más próximo era ONO, y el bucle de abonado seguía haciéndolo con coaxial.

Al grano, no conozco la redes de fibra. Nunca he trabajando con ellas. Pero parece ser que, a diferencia de las redes de ADSL, para establecer la comunicación con la central se necesita una contraseña de acceso.

![Pestaña de configuración de la PLOAM Password](img/ploam_password_input.png)

Lo primero que hace el instalador tras encender el router es introducir la contraseña. A propósito, si le preguntas por ella quizá te la revele, pero le estás poniendo en un compromiso. Porque con toda seguridad le han ordenado que no lo haga.

Esa contraseña la necesitarás si piensas sustituir el router del operador por uno tuyo. Pero también si se te estropea el actual o sufre algún problema. Sin contraseña no hay conexión, y sin conexión no hay administración remota. Solo queda enviar un técnico a domicilio a reparar la avería.

Quedémonos con que hay un dato desconocido, y vamos a intentar obtenerlo.

## Aproximaciones fallidas

Lo primero es buscar en internet si alguien lo ha hecho antes, por supuesto. Algunos modelos anteriores tenían descuidos evidentes.

El modelo 5655v2, según parece, tenía la [password en la interfaz web][1]. Es un fallo común en formularios web hechos con prisas o sin conocer los componentes. Inaceptable.

Un firmware más reciente del mismo modelo corrige ese fallo y ya no puede obtenerse la contraseña desde la interfaz web. Debe hacerse entrando con una shell al sistema y leyendo el fichero de configuración. Viene deshabilitada, no obstante, pero puede habilitarse mediante [opciones indocumentadas][2] en la web.

Pero en mi modelo, el F@ST 5657, tampoco funciona ya este último método. Habrá que echarle imaginación.

Miramos los **puertos abiertos**. Quién sabe, tal vez la administración por telnet o por SSH está activada de serie. Si bien sería extraño que esté activada pero en la web no aparezcan opciones para desactivarla.

    $ nmap 192.168.1.1 -sV

    Starting Nmap 7.60 ( https://nmap.org ) at 2020-10-24 21:03 CEST
    Nmap scan report for home (192.168.1.1)
    Host is up (0.0035s latency).
    Not shown: 845 closed ports, 148 filtered ports
    PORT      STATE SERVICE     VERSION
    53/tcp    open  domain      dnsmasq 2.78
    80/tcp    open  http        lighttpd
    139/tcp   open  netbios-ssn Samba smbd 3.X - 4.X (workgroup: HOME)
    443/tcp   open  ssl/http    lighttpd
    445/tcp   open  netbios-ssn Samba smbd 3.X - 4.X (workgroup: HOME)
    5060/tcp  open  sip?
    49153/tcp open  upnp        Portable SDK for UPnP devices 1.6.18 (Linux 4.1.51-5.02L.05; UPnP 1.0)
    Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel:4.1.51-5.02l.05

No parece. El DNS (80), la web de administración (80), la web por https (443), compartir ficheros (139 y 445), el teléfono (5060) y el uPnP (49153). Quizá alguno de los servicios tenga exploits conocidos. Pero vamos a seguir mirando.

**Descarga de la configuración**. Vamos a lo fácil. Hago un backup de la configuración por si puedo ver la contraseña directamente. O tal vez podría manipular el backup para activar el telnet o el SSH cuando lo cargue.

![img-aead10](img/aead10.png)

No es texto, es un fichero binario. Quizá comprimido, cifrado o las dos cosas. AEAD me recuerda a *authenticated encryption with associated data*, prefiero buscar otro camino.

## El CWMP, más conocido por TR-069

CWMP son las siglas de *CPE WAN Management Protocol* y CPE, a su vez, las de *Customer Premises Equipment*. En español también se le llama EDC: Equipo en Domicilio del Cliente.

Son equipos propiedad de la compañía suministradora pero que están en tu casa. Como *tu router*. Esta advertencia es importante: por regla general, el router es de la compañía, no tuyo. Está cedido como el contador de telegestión de la luz o del gas. Manipular *tu router* sin autorización puede tener consecuencias, por ejemplo que el operador no se haga cargo si sufres una avería y te cobre la revisión.

Ahora pongámonos un instante en la piel de un técnico de soporte. Cuando tienes una red con decenas de miles equipos deslocalizados en casa del cliente te interesa tenerlos lo más controlados posible, configurarlos desde el mismo punto y recibir información periódica sobre su estado y la conexión. Marca, modelo, número de serie, versión del firmware, atenuación, parámetros de sincronización y hasta la temperatura.

Hay un cacharro llamado ACS (*Auto Configuration Server*) al que se conecta el router nada más enchufarlo a la fibra o el ADSL. Este le proporciona los parámetros necesarios. Entre otras cosas, le cambia la contraseña de administrador y al cliente le deja un usuario más o menos restringido. ¿Te suena?

En parte para que el sobrino del cliente no toque donde no sabe, se quede sin conexión y te llame culpándote de ello.

Tras esta primera vez, el CPE se conecta al ACS periódicamente para informar de algunos parámetros. Eso se llama Technical Report (TR), de ahi TR-069.

El ACS sirve también para hacer diagnóstico remoto de las incidencias. Si un cliente te llama diciendo que no tiene internet, puedes confirmarlo rápidamente mirando en el sistema su último estado: qué router tiene, hace cuanto que se lo pusieron, si está on-line o cuándo fue su último informe periódico.

Por si fuera poco, tienes la posibilidad de enviar comandos para reiniciárselo remotamente, subir y bajar ficheros, actualizar el firmware, o conectarte al equipo para abrirle puertos o lo que necesite.

¿Verdad que suena bien?

## Ganar admin

Dado que las opciones del TR-069 no aparecen entrando con el usuario 1234, ni se pueden ver llamando al backend de la web directamente, para continuar la historia necesitamos entrar como administrador.

![Con el usuario 1234 no aparece la opción](img/no_TR_as_1234.png)

La forma más fácil para ganar admin en tu propio router es reiniciarlo a valores de fábrica. La *PLOAM Password* se debería conservar en un espacio protegido. Sin embargo, existe la posibilidad de que se borre. Te quedarías sin Internet y toca llamar. Tenlo en cuenta.

Este router se reinicia presionando el botón de reset durante unos 20 segundos. El procedimiento está descrito en tutoriales para modelos similares.

Una vez reiniciado y, por supuesto, desconectado de la red ya podemos entrar como *admin* y ver las opciones del cliente TR-069.

![opciones del cliente TR-069](img/TR_as_admin.png)

La URL del ACS y el usuario se ven a simple vista. La contraseña ya la veremos después. Créeme.

La PLOAM Password no te la va a mostrar ni siquiera como admin.

En esa pantalla, aprovechamos para desactivar el cliente. Así no se cambiará la contraseña. Haremos también un backup de la configuración. Así cuando queramos recuperar el usuario administrador más adelante ya no necesitamos reiniciar a valores de fábrica, será suficiente cargar esta configuración.

## MitM al CWMP TR-069

¿Te has fijado en la URL del ACS? Es HTTPS. O sea una web. ¿Y si nos conectamos qué tiene?

![acs unauthorized](img/acs_unauthorized.png)

Pero aún teniendo el usuario y contraseña no conocemos el protocolo. Puedes mirar [la especificación][3], es pública. Vas a ver que es SOAP y varios comandos, pero no vas a sacar nada en claro.

Lo que sí resultaría útil es escuchar la comunicación entre el router y el ACS. ¿Pero cómo hacemos eso?

¿Con Wireshark? No, la comunicación sale por la interfaz de fibra, no la vas a ver. Además es HTTPs, irá cifrada.
¿Con Burpsuite? No, el router no nos deja configurar un proxy.
¿Con Burpsuite en modo proxy transparente? No, el DNS y la tabla de rutas se lo proporciona el operador y no podemos cambiarlo. Un ARP spoofing o rogue DHCP no van a colar.

Si pudiera cambiar la URL para apuntar a un servidor ACS mío, tal vez pudiera extraer información útil.

Cambio la URL a la IP de un servidor local:

![url cambiada a un servidor local](img/acs_url_raspberry.png)

Y activo el cliente. A ver si llega la petición...

    pi@raspberrypi:~$ netcat -lvp 10302
    Listening on [0.0.0.0] (family 0, port 10302)
    Connection from [192.168.1.1] port 10302 [tcp/*] accepted (family 2, sport 53720)
    POST /OLT********/11/ HTTP/1.1
    Host: 192.168.1.121:10302
    User-Agent: gSOAP/2.7
    Content-Type: text/xml; charset=utf-8
    Content-Length: 2280
    Connection: keep-alive
    SOAPAction:

    <?xml version="1.0" encoding="UTF-8"?>
    <SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:cwmp="urn:dslforum-org:cwmp-1-0">
    ...

¡Sí! Pero ¿cómo sé qué responder?

Hay un ACS opensource: [Genie ACS][4]. Pero la gracia está en averiguar los parámetros que le ponen remotamente, no en ponerle los que yo quiera.

Necesito:

- recibir la petición en la URL local, es un POST.
- registrarla a un fichero
- enviar esa petición tal cual a la URL legítima y obtener una respuesta
- registrarla a un fichero
- reenviar la respuesta al router

Necesito un proxy, pero que haga reenvío de una petición a otra URL. Habrá herramientas por ahí, pero en 30 minutos no dí con una apropiada. Así que retomé un script python similar de otro proyecto y lo modifiqué: [app.py][app.py].

¿Cómo es la conversación con el ACS? Se parece a este diagrama:

![Ejemplo de comunicación CWMP](img/cwmp_example.png)

Lo primero que envía el router es marca, modelo y número de serie, así como el estado en que se encuentra. Para que que el ACS sepa qué valores enviar. En este caso es bootstrap (la primera conexión) así que el ACS enviará todo lo necesario.

```xml
<SOAP-ENV:Body>
    <cwmp:Inform>
        <DeviceId>
            <Manufacturer>Sagemcom</Manufacturer>
            <OUI>44A****</OUI>
            <ProductClass>FAST5657</ProductClass>
            <SerialNumber>N******9</SerialNumber>
        </DeviceId>
        <Event xsi:type="SOAP-ENC:Array" SOAP-ENC:arrayType="cwmp:EventStruct[1]">
            <EventStruct>
                <EventCode>0 BOOTSTRAP</EventCode>
                <CommandKey></CommandKey>
            </EventStruct>
        </Event>
```

El router envía información sobre su firmware, IP y la URL para conexión remota desde el ACS.

```xml
<ParameterValueStruct>
    <Name>Device.DeviceInfo.HardwareVersion</Name>
    <Value xsi:type="xsd:string">1.00</Value>
</ParameterValueStruct>
<ParameterValueStruct>
    <Name>Device.DeviceInfo.SoftwareVersion</Name>
    <Value xsi:type="xsd:string">SGDV10000031</Value>
</ParameterValueStruct>
<ParameterValueStruct>
    <Name>Device.ManagementServer.ConnectionRequestURL</Name>
    <Value xsi:type="xsd:string">http://188.a.b.c:7547/y1jkmvCPagHJ8QvS</Value>
</ParameterValueStruct>
```

La URL de conexión contiene una cadena aleatoria generada por el CPE. Si no se conoce esta cadena, no se puede conectar remotamente.

Por cierto, ¿la forma de enumerar los parámetros tipo `Device.DeviceInfo.SoftwareVersion` no te recuerda un poco a SNMP?

Ahora el ACS le solicita los parámetros disponibles en el equipo y su tipo para adaptar la configuración y enviársela.

El router envía información sobre básicamente todo. Wifis configuradas, equipos conectados, asignaciones DHCP de la red interna, VPN, procesos en ejecución... un volcado completo.

Tras esto el ACS le envía todos los parámetros que en equipo no tiene. Por ejemplo, fija la contraseña para la conexión remota:

```xml
<cwmp:SetParameterValues>
    <ParameterList soap-enc:arrayType="cwmp:ParameterValueStruct[7]">
        <ParameterValueStruct>
            <Name>Device.ManagementServer.ConnectionRequestUsername</Name>
            <Value xsi:type="xsd:string">44A***-N7202*********</Value>
        </ParameterValueStruct>
        <ParameterValueStruct>
            <Name>Device.ManagementServer.ConnectionRequestPassword</Name>
            <Value xsi:type="xsd:string">3bcf6***</Value>
        </ParameterValueStruct>
    </ParameterList>
    <ParameterKey>n/a</ParameterKey>
</cwmp:SetParameterValues>
```

Ignoro si la contraseña es siempre la misma para un cliente o la misma para todos. Pero no supone un riesgo cuando el nombre de usuario va en relación al número de serie y la URL se genera de manera aleatoria. Si quisieras atacar un router ajeno usando este método necesitarías:

- Contraseña: pongamos que es genérica, la tienes
- ID numérico del fabricante del router: podrías averiguarlo
- Protocolo: podrías averiguarlo.
- Número de serie del dispositivo: no lo sabes
- URL: es aleatoria, no la sabes

También, por supuesto, fija la contraseña del usuario administrador. La apuntamos.

```xml
<cwmp:SetParameterValues>
    <ParameterList soap-enc:arrayType="cwmp:ParameterValueStruct[1]">
        <ParameterValueStruct>
            <Name>Device.Users.User.4.Password</Name>
            <Value xsi:type="xsd:string">16225227</Value>
        </ParameterValueStruct>
    </ParameterList>
    <ParameterKey>n/a</ParameterKey>
</cwmp:SetParameterValues>
```

También están los datos de la conexión SIP y otros que ahora mismo no nos resultan relevantes.

De la *PLOAM Password* ni rastro. Tiene sentido: si puedes conectar a ACS y por tanto a la red, la password es correcta. ¿Para qué te va a enviar otra?

¿Ahora qué hacemos?

## Habilitar administración por SSH

El router hace un volcado completo de la configuración, con todos los parámetros que soporta. Se me ocurre buscar entre los parámetros a ver si alguno me da una pista sobre cómo seguir.

Buscamos por ejemplo `telnet`. Encuentro esto:

```xml
<ParameterInfoStruct>
    <Name>Device.Services.X_MM_RemoteAccess.HTTPEnable</Name>
    <Writable>1</Writable>
</ParameterInfoStruct>
<ParameterInfoStruct>
    <Name>Device.Services.X_MM_RemoteAccess.HTTPSEnable</Name>
    <Writable>1</Writable>
</ParameterInfoStruct>
<ParameterInfoStruct>
    <Name>Device.Services.X_MM_RemoteAccess.TELNETEnable</Name>
    <Writable>1</Writable>
</ParameterInfoStruct>
<ParameterInfoStruct>
    <Name>Device.Services.X_MM_RemoteAccess.SSHEnable</Name>
    <Writable>1</Writable>
</ParameterInfoStruct>
```

Parecen parámetros para activar distintos modos de acceso remoto. Y son *writable*. Voy a buscar en Google el parámetro X_MM_RemoteAccess.

![La búsqueda en google sólo encuentra un resultado](img/x_mm_remoteaccess.png)

¿Un sólo resultado? Qué desconcertante. Habría esperado un modelo de datos XML al menos, o un PDF describiendo la función. Pero el estándar CWMP 

Cuando el equipo informa al ACS de los valores de dichos parámetros vemos que sólo están activas las interfaces web http y https:

```xml
<ParameterValueStruct>
    <Name>Device.Services.X_MM_RemoteAccess.HTTPEnable</Name>
    <Value xsi:type="xsd:boolean">true</Value>
</ParameterValueStruct>
<ParameterValueStruct>
    <Name>Device.Services.X_MM_RemoteAccess.HTTPSEnable</Name>
    <Value xsi:type="xsd:boolean">true</Value>
</ParameterValueStruct>
<ParameterValueStruct>
    <Name>Device.Services.X_MM_RemoteAccess.TELNETEnable</Name>
    <Value xsi:type="xsd:boolean">false</Value>
</ParameterValueStruct>
<ParameterValueStruct>
    <Name>Device.Services.X_MM_RemoteAccess.SSHEnable</Name>
    <Value xsi:type="xsd:boolean">false</Value>
</ParameterValueStruct>
```

Como tengo interceptadas las comunicaciones con el Servidor de Configuración, modifico la respuesta para activar estos parámetros y ponerlos a `true`. Los valores a inyectar están en el fichero [injectiondata.xml][injectiondata.xml].

Desde dentro de la red no veo más puertos abiertos. Es lógico, si son puertos de administración remota, estarán abiertos hacia afuera.

Huelga decir que esta prueba sólo la puedo hacer porque estoy por fuera del **CG-NAT**. Si estuviera tras el CG-NAT, tendría una IP externa privada, una 100.x.x.x seguramente y no podría llegar a ella desde una máquina en Internet.

Me conecto utilizando la conexión wifi compartida del móvil y... ¡sí! El 22 y el 23 ahora están abiertos.

    $ telnet 188.127.xx.xx
    Trying 188.127.xx.xx...
    Connected to 188.127.xx.xx.
    Escape character is '^]'.
    Connection closed by foreign host.
    $

Vaya... algo no le gusta. Me ha abierto los puertos, pero me está cerrando la conexión. ¿El firewall? Sigamos buscando.

Justo debajo de los parámetros anteriores hay otro que nos da una pista para seguir:

```xml
<ParameterValueStruct>
    <Name>Device.Services.X_MM_RemoteAccess.TrustedDomain.1.Enable</Name>
    <Value xsi:type="xsd:boolean">true</Value>
</ParameterValueStruct>
<ParameterValueStruct>
    <Name>Device.Services.X_MM_RemoteAccess.TrustedDomain.1.IPAddress</Name>
    <Value xsi:type="xsd:string">212.a.b.c</Value>
</ParameterValueStruct>
<ParameterValueStruct>
    <Name>Device.Services.X_MM_RemoteAccess.TrustedDomain.1.PrefixLength</Name>
    <Value xsi:type="xsd:unsignedInt">24</Value>
</ParameterValueStruct>
```

Por lo visto el panel de control, aunque activo, no está accesible para cualquiera. Piensa que si pones un panel de administración en el puerto 80 abierto a internet, es cuestión de tiempo que alguien pruebe la combinación 1234/1234. Con lo que un extraño tendría el mismo control sobre el dispositivo que tienes tú. Por eso se establece ese `TrustedDomain`.

Miro la IP con que sale mi conexión 4G, la añado a los parámetros que inyectábamos antes y...

    $ telnet 188.127.xx.xx
    Trying 188.127.xx.xx...
    Connected to 188.127.xx.xx.
    Escape character is '^]'.

    home login:

¡Sí!. Tenemos shell. Probamos con el usuario admin y la contraseña que vimos antes en el log del proxy:

    home login: admin 
    Password: <vista en el log>

    BusyBox v1.22.1 (2020-04-20 07:57:05 CEST) built-in shell (ash)
    Enter 'help' for a list of built-in commands.

    admin@home:/tmp$ 

¡Bien! ¿Nos podemos hacer root? Probamos con root/root:

    admin@home:/tmp$ su -
    Password: <root>

    BusyBox v1.22.1 (2020-04-20 07:57:05 CEST) built-in shell (ash)
    Enter 'help' for a list of built-in commands.

    root@home:~# 

Ahora, con shell de administrador ya podemos volcar la configuración que queramos. Bien de un fichero, o bien de la memoria de un proceso si no estuviera en un fichero.

Pero está:

    root@home:/opt/filesystem1/data# ls
    lastrandom        optical_conf.txt
    root@home:/opt/filesystem1/data# cat optical_conf.txt 
    375a5xxxxxxxxxxxxx
    root@home:/opt/filesystem1/data# 

Son caracteres hexadecimales. Evidentemente el router la necesita en claro, para poder enviarla. No puedes sustituirla por un hash, por ejemplo. Podría cifrarse para hacerlo más complicado, pero ¿por qué ocultarle un parámetro de configuración al usuario root?

Esta clave está también en el fichero de configuración `/opt/filesystem1/conf/backup-cfg.xml`, pero aquí se llama *RegId*

```xml
<Optical>
    <Interfaces element-count="1" new-id="2">
        <Interface uid="1">
            <Enable>true</Enable>
            <Alias>OPTICAL0</Alias>
            <LowerLayers></LowerLayers>
        </Interface>
    </Interfaces>
    <G988>
        <EquipmentManagement>
            <OnuG>
                <TrafficManagementOption>0</TrafficManagementOption>
            </OnuG>
            <SoftwareImages element-count="2" new-id="3"/>
        </EquipmentManagement>
        <OnuMode>RG_PPTP</OnuMode>
        <OperatorConf>true</OperatorConf>
        <Software0UbiDev>/dev/ubi0_4</Software0UbiDev>
        <Software1UbiDev>/dev/ubi0_5</Software1UbiDev>
        <RegId>375axxxxxxxxxxxxx</RegId>
        <IgnoreDsPbitGemMapping>true</IgnoreDsPbitGemMapping>
    </G988>
</Optical>
```

¿Para qué quiero la clave? ¡Para nada! Ese no es el objetivo. 

Lo que yo buscaba es ver si podía obtener ese dato a pesar de todas las trabas, aprendiendo por el camino cómo se hace la administración remota.













[1]: https://bandaancha.eu/foros/extraer-gpon-router-sagemcom-fast-5655v2-1731346

[2]: https://naseros.com/2020/07/14/como-extraer-clave-gpon-y-sip-del-sagemcom-fast-5655v2-de-masmovil-pepephone-y-yoigo/

[3]: https://www.broadband-forum.org/technical/download/TR-069.pdf

[4]: https://genieacs.com/

[app.py]: app.py
[injectiondata.xml]: injectiondata.xml