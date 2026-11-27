# Live Track SALT

[English](README.md) · **Español** · [Todos los idiomas](#idiomas)

**El control migratorio para Home Assistant, en un solo mapa.** Live Track
SALT pone en tu mapa de Home Assistant los aviones que se usan en el control
migratorio, dondequiera que vuelen: los aviones de ICE, de CBP y de otras
agencias federales, los aviones de línea que hacen vuelos chárter para ICE
Air, y los de agencias estatales y locales con un papel documentado en ese
trabajo. También dibuja cada avión de una zona que elijas y, con una clave
gratuita, los buques de la Guardia Costera que se usan en el trabajo
migratorio, allí donde se hace ese trabajo.

> **Live Track SALT es un módulo de Live Track**, una familia de
> integraciones de Home Assistant que dibujan todo lo que se mueve, y el tiempo
> que atraviesa, en un mapa compartido: aviones, barcos, trenes y tiempo.
> Instálalo solo, o junto a los demás módulos
> ([lista abajo](#parte-de-live-track-los-demás-módulos)).

> **Sigue creciendo, y las ideas son bienvenidas.** Live Track SALT cubre hoy
> los aviones de la lista dondequiera que los oigan los receptores de los
> voluntarios, y los buques de la lista en cuatro zonas de agua, y estamos
> añadiendo más fuentes de datos. ¿Falta el tuyo?
> [Sugiérelo](#ayúdanos-a-hacerlo-crecer), o añádelo tú mismo: te ayudaremos a
> hacerlo.

**Estado: 0.1.6, publicada.** En el catálogo del Marketplace ([instálalo más
abajo](#instalarlo-paso-a-paso)).

Obra original de StrausbergAutomationWorks. Sin relación con adsb.fi,
adsb.lol, aisstream.io, la Federal Aviation Administration (Estados Unidos),
ADS-B Radar, Planespotters.net, Wikidata, Wikimedia Commons, ninguna agencia
del gobierno, ninguna aerolínea ni ningún operador de aviones, ni respaldado
por ellos.

> ⚠ **No es un sistema de alerta.** Muestra datos públicos, normalmente de
> hace unos segundos y a veces de un minuto o más, y solo los aviones que
> transmiten donde los receptores de los voluntarios los oyen. Un avión puede
> volar con el transpondedor apagado o con su identidad oculta, y muchos
> aviones que se usan en este trabajo todavía no están en la lista. **Un mapa
> vacío no significa que no haya actividad de control migratorio cerca de
> ti.** Un avión en el mapa no dice nada de quién va a bordo ni de por qué
> vuela.

---

## Contenido

1. [Todo lo que hace](#todo-lo-que-hace)
2. [Dónde funciona](#dónde-funciona)
3. [Parte de Live Track: los demás módulos](#parte-de-live-track-los-demás-módulos)
4. [Antes de empezar](#antes-de-empezar)
5. [Instalarlo, paso a paso](#instalarlo-paso-a-paso)
6. [Configurarlo, paso a paso](#configurarlo-paso-a-paso)
7. [Claves gratuitas que activan más, paso a paso](#claves-gratuitas-que-activan-más-paso-a-paso)
8. [Poner el mapa en un panel de control](#poner-el-mapa-en-un-panel-de-control)
9. [Usarlo en automatizaciones](#usarlo-en-automatizaciones)
10. [Todo lo del mapa, en detalle](#todo-lo-del-mapa-en-detalle)
11. [Todas las entidades que crea](#todas-las-entidades-que-crea)
12. [Qué envía y qué descarga](#qué-envía-y-qué-descarga)
13. [Ayúdanos a hacerlo crecer](#ayúdanos-a-hacerlo-crecer)
14. [Idiomas](#idiomas)
15. [Créditos y licencias](#créditos-y-licencias)
16. [Palabras clave](#palabras-clave)

---

## Todo lo que hace

### En el mapa, sin configurar nada

Al configurarlo eliges una **zona de interés**: un centro en el mapa y un
radio alrededor. Empieza en tu casa. Los aviones de la lista aparecen
dondequiera que vuelen; la zona de interés añade cada uno de los demás aviones
que haya dentro.

| Qué | Dónde | De dónde |
|---|---|---|
| **Aviones de la lista**: cada avión de la lista pública EnforcementAircraft, con su agencia en la etiqueta y dibujado con luces rojas y azules intermitentes | en cualquier parte del mundo donde los oigan los receptores | adsb.fi, o adsb.lol cuando adsb.fi no responde; la lista EnforcementAircraft |
| **Chárteres de ICE Air**: aviones de línea que hacen vuelos chárter para ICE Air, entre otros trabajos, con la etiqueta "ICE Air Charter?" y un brillo fijo | en cualquier parte del mundo | lo mismo |
| **Vuelos de ICE Air**: mientras un avión transmite un indicativo de ICE Air, su etiqueta pierde el signo de interrogación. Un avión que no está en la lista y vuela con uno se dibuja como chárter y se vigila en todas partes desde entonces | en cualquier parte para los aviones de la lista; en tu zona de interés para los demás | adsb.fi |
| **Aviones de las fuerzas federales del orden en el registro de la FAA**: dibujados en azul con luces, para que aparezca también un avión matriculado después de crear la lista | en cualquier parte del mundo (aviones matriculados en los Estados Unidos) | el registro de aeronaves de la FAA (Estados Unidos) |
| **Detecciones**: un avión que no está en la lista y transmite un indicativo que usa DHS (`TROY` y cifras) lleva la etiqueta "Detected, unconfirmed" (detectado, sin confirmar), se dibuja sin luces bajo un anillo blanco discontinuo, y se vigila en todas partes desde entonces | encontrado en tu zona de interés, luego en cualquier parte | adsb.fi |
| **Cada avión de tu zona de interés**: cada uno dibujado como su propio tipo y girado hacia donde vuela | tu zona de interés | adsb.fi, o adsb.lol |
| **Fotos**: una foto del avión, con el nombre del fotógrafo, al señalarlo | cada avión del que Planespotters.net tiene foto | Planespotters.net ([más](#fotos)) |

### Activado con tu propia clave o cuenta gratuita

| Clave o cuenta gratuita | Qué añade |
|---|---|
| clave de **aisstream.io** | los buques de la Guardia Costera de la lista pública EnforcementVessels, dentro de cuatro zonas de agua donde se hace trabajo migratorio, cada uno con su foto cuando Wikimedia Commons tiene una ([más](#fotos)) |
| clave de **adsb.lol** | más peticiones al día a adsb.lol, la segunda fuente, para que el mapa siga funcionando durante una caída larga de adsb.fi |

Cada una se consigue en unos minutos: [paso a paso abajo](#claves-gratuitas-que-activan-más-paso-a-paso).

---

## Dónde funciona

Las listas tratan del control migratorio en los Estados Unidos: todas las
agencias que contienen son agencias de los Estados Unidos. Sus aviones se
dibujan dondequiera que vuelen, también en vuelos a otros países.

| Región | Qué obtienes | De dónde | Necesita |
|---|---|---|---|
| **Todo el mundo** | los aviones de la lista, y cada avión de tu zona de interés, donde voluntarios mantienen receptores: densos sobre Norteamérica y Europa, más escasos en otros lugares, y pocos o ninguno lejos en el mar | adsb.fi, adsb.lol | nada |
| **Norteamérica**: el Caribe | buques de la Guardia Costera de la lista alrededor de Puerto Rico (Estados Unidos) y en el Canal de la Mona, en el Paso de los Vientos entre Cuba y Haití, y en el Estrecho de Florida, las Bahamas y el Canal de Yucatán | aisstream.io, la lista EnforcementVessels | una clave gratuita |
| **Norteamérica**: Estados Unidos | aviones de las fuerzas federales del orden del registro de la FAA, y nombres de propietarios de aviones matriculados en los Estados Unidos | el registro de aeronaves de la FAA | nada |
| **Norteamérica**: Estados Unidos | buques de la Guardia Costera de la lista frente al sur de California | aisstream.io, la lista EnforcementVessels | una clave gratuita |

¿No está en la lista? [Dínoslo](#ayúdanos-a-hacerlo-crecer). Donde alguien
publique los datos abiertamente, estudiaremos añadirlos.

⚠ **La cobertura es buena donde hay receptores, y no existe donde no los
hay.** Un avión solo aparece si el receptor de un voluntario lo oye, o si
varios receptores juntos pueden localizarlo.

⚠ **Buques: aisstream.io no oyó ningún buque en el Canal de la Mona ni en el
Paso de los Vientos** cuando lo medimos en octubre de 2026, así que puede que
los buques de la lista no aparezcan allí. Fuera de las cuatro zonas, un buque
de la lista hace trabajo normal de la Guardia Costera: se cuenta, pero no se
dibuja.

---

## Parte de Live Track: los demás módulos

Live Track es un conjunto de integraciones de Home Assistant, una por cada
tipo de cosa que se mueve, todas dibujadas en la misma tarjeta de mapa. Cada
una funciona sola; juntas forman una sola imagen en vivo. Comparten la tarjeta
de mapa y una biblioteca de Python
([saw-livetrack](https://github.com/StrausbergAutomationWorks/LiveTrackCore)),
así que instalar otra no añade peticiones a una fuente que otra ya lee.

| Módulo | Qué pone en el mapa | Estado |
|---|---|---|
| [Live Track Aircraft](https://github.com/StrausbergAutomationWorks/LiveTrackAircraft) | aviones sobre ti por ADS-B, con rutas e iconos por tipo | publicado |
| [Live Track Ships](https://github.com/StrausbergAutomationWorks/LiveTrackShips) | buques y barcos por AIS, cerca de ti o en cualquier lugar | publicado |
| [Live Track Commuter Rail](https://github.com/StrausbergAutomationWorks/LiveTrackCommuterRail) | trenes de cercanías en Norteamérica, Europa y Australia | publicado |
| [Live Track Intercity Rail](https://github.com/StrausbergAutomationWorks/LiveTrackIntercityRail) | trenes interurbanos y de larga distancia en Norteamérica, Europa y Australia | publicado |
| **Live Track SALT** | aviones y buques de inmigración y de las fuerzas federales del orden, a partir de listas públicas (este módulo) | publicado |
| [Live Track Weather](https://github.com/StrausbergAutomationWorks/LiveTrackWeather) | tiempo, tormentas y riesgos naturales | publicado |
| [Live Track Internet](https://github.com/StrausbergAutomationWorks/LiveTrackInternet) | cortes de internet, cables submarinos y enlaces terrestres | publicado |
| Live Track Stations | paneles de salidas y avisos de "hora de salir" para cada estación | previsto |
| Live Track Satellites | satélites que pasan sobre ti | previsto |
| Live Track Freight Trains | trenes de mercancías y de obras donde los ferrocarriles los publican | previsto |
| Live Track Transit | autobuses urbanos, tranvías, ferris y metro | previsto |
| Live Track Intercity Buses | autocares interurbanos y regionales | previsto |
| Live Track Commuter Buses | autobuses de cercanías | previsto |
| [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard) | la tarjeta de mapa compartida en la que dibuja cada módulo | publicada, instalada con cada módulo |

Todo es gratuito y de código abierto. Nada se reserva para patrocinadores.

---

## Antes de empezar

* **Home Assistant** 2026.11 o posterior.
* **El Marketplace** (HACS) en tu Home Assistant, para instalarlo y
  actualizarlo de la forma fácil. Sin él puedes copiar los archivos a mano.
* **Acceso a Internet** para Home Assistant: todo viene de fuentes públicas.
* Nada que pagar y ninguna cuenta necesaria para los aviones. Las dos claves
  gratuitas de arriba son opcionales.
* Home Assistant instala por sí mismo el paquete de Python que necesita
  (`saw-livetrack`) la primera vez que se carga la integración.

---

## Instalarlo, paso a paso

### Desde el Marketplace (recomendado)

1. En Home Assistant, abre **Configuración → Marketplace** (HACS).
2. Busca **Live Track SALT** y ábrelo.
3. Elige **Descargar** (o **Instalar**).
4. **Reinicia Home Assistant**: **Configuración → Sistema → Reparaciones**
   ofrece el reinicio, o usa **Configuración → Sistema → Reiniciar Home
   Assistant**.

Si la búsqueda no lo encuentra, añádelo por su enlace: elige la pestaña
**Añadir desde enlace** (o el menú de tres puntos → **Repositorios
personalizados**), escribe `StrausbergAutomationWorks/LiveTrackSALT`, elige
**Integración** si te pide el tipo y continúa desde el paso 3.

Después, el Marketplace ofrece cada versión nueva como actualización.

### A mano

1. Descarga el código fuente de la
   [última versión](https://github.com/StrausbergAutomationWorks/LiveTrackSALT/releases/latest).
2. Copia su carpeta `custom_components/live_track_salt` en la carpeta
   `custom_components` de la carpeta de configuración de tu Home Assistant
   (crea `custom_components` si no existe).
3. Reinicia Home Assistant.

Para actualizar a mano, sustituye la carpeta por la de la nueva versión y
reinicia.

---

## Configurarlo, paso a paso

El diálogo de configuración está en inglés. Sus campos se nombran aquí tal
como los muestra.

1. Abre **Configuración → Dispositivos y servicios**.
2. Elige **Añadir integración** (abajo a la derecha) y busca **Live Track
   SALT**.
3. **Centre of the focus area** (centro de la zona de interés): arrastra el
   marcador al centro de la zona donde quieres ver cada avión. Empieza en tu
   casa. Para que tu casa siga siendo privada, muévelo
   ([por qué](#qué-envía-y-qué-descarga)).
4. **Radius of the focus area (km)** (radio de la zona de interés): hasta qué
   distancia del centro se muestra cada avión, de 1 a 463 km (0,6 a
   288 millas). Si dudas, deja 56 km (35 millas).
5. **Most aircraft shown in the focus area (listed aircraft are always
   shown)** (máximo de aviones mostrados en la zona de interés; los de la
   lista se muestran siempre): deja 250. Es un límite de seguridad solo para
   la zona de interés.
6. **Show listed aircraft outside the focus area** (mostrar los aviones de la
   lista fuera de la zona de interés): déjalo activado. Desactivado, limita
   también los aviones de la lista a la zona de interés.
7. Deja vacíos por ahora los dos campos de claves. Cada uno se explica más
   abajo.
8. Elige **Enviar**.

Eso es todo. Los aviones de la lista que están volando aparecen en menos de un
minuto, y los aviones de tu zona de interés en 15 segundos. La entrada lleva
como título el centro y el radio, por ejemplo `39.817, -84.050 - 56 km`. Solo
hay una entrada: la lista es la misma esté donde esté la zona de interés, así
que una segunda entrada se rechaza. Los aviones de las fuerzas federales del
orden del registro de la FAA aparecen cuando el registro se ha descargado,
normalmente en los primeros minutos
([Qué envía y qué descarga](#qué-envía-y-qué-descarga)).

### Cambiar lo que muestra: las opciones

Abre **Configuración → Dispositivos y servicios → Live Track SALT →
Configurar** (el engranaje). Cada opción, en palabras sencillas:

| Opción | Qué hace | Por defecto |
|---|---|---|
| **Centre of the focus area** | mueve la zona de interés; el título de la entrada la sigue | tu casa |
| **Radius of the focus area (km)** | hasta qué distancia del centro se muestra cada avión, de 1 a 463 km (0,6 a 288 millas) | 56 km (35 millas) |
| **Most aircraft shown in the focus area (listed aircraft are always shown)** | un límite de seguridad, de 1 a 1000; cuando hay más aviones en la zona de interés, se conservan los más cercanos. Los aviones de la lista y los de las fuerzas federales del orden se conservan siempre | 250 |
| **Show listed aircraft outside the focus area** | desactivado, limita también los aviones de la lista a la zona de interés | activado |
| **aisstream.io API key, for listed vessels (optional; free at aisstream.io)** | tu propia clave para aisstream.io; sin ella no se muestra ningún buque ([cómo conseguir una](#claves-gratuitas-que-activan-más-paso-a-paso)) | vacío |
| **adsb.lol API key (optional; your own, sent only to adsb.lol, which is asked while adsb.fi is failing)** | tu propia clave para adsb.lol ([cómo conseguir una](#claves-gratuitas-que-activan-más-paso-a-paso)) | vacío |

Vacía un campo de clave para dejar de usar esa clave.

---

## Claves gratuitas que activan más, paso a paso

Las dos son gratuitas y personales: cada persona que instala Live Track SALT
obtiene la suya. Pega cada una en **Configuración → Dispositivos y servicios →
Live Track SALT → Configurar**, y elige **Enviar**.

### aisstream.io (buques de la Guardia Costera de la lista, cuatro zonas de agua)

aisstream.io te identifica con una cuenta de GitHub, que también es gratuita.

1. Abre <https://aisstream.io/account> y elige **Continue with GitHub**.
2. Crea allí una clave de API nueva. La página que hay tras el inicio de
   sesión no es pública, así que sus botones no se nombran aquí; la
   documentación de aisstream.io dice que las claves se crean en esta página y
   que una clave nueva se muestra una sola vez.
3. Copia la clave en ese momento.
4. Pégala en **aisstream.io API key, for listed vessels (optional; free at
   aisstream.io)**.

⚠ aisstream.io permite tres conexiones por cuenta y tres por cada dirección
pública de Internet. Live Track SALT usa una, para los buques de la lista; la
comparte con Live Track Ships cuando Ships está instalado con la misma clave.
Si otros programas usan la misma clave o la misma conexión a Internet,
cuéntalos también.

### adsb.lol (más peticiones a la segunda fuente, todo el mundo)

Live Track SALT pregunta primero a adsb.fi, y pregunta a adsb.lol solo
mientras adsb.fi no responde. Sin clave, adsb.lol permite 500 peticiones al
día desde una dirección de Internet, que una caída de adsb.fi puede agotar en
unas dos horas. Una clave sube ese límite. No necesitas una para empezar.

1. Abre <https://www.adsb.lol/request>.
2. Rellena **email** (correo), **What will you use it for?** (para qué la
   usarás) y **How are you complying with the ODbL 1.0 licensing terms?**
   (cómo cumples las condiciones de la licencia ODbL 1.0); el nombre y la
   empresa son opcionales. Elige **Send request**.
3. Confirma tu dirección de correo en menos de 24 horas: adsb.lol borra una
   petición que no se confirma. adsb.lol dice que lee la respuesta sobre la
   ODbL antes de enviar una clave, y que las direcciones de Outlook, Hotmail y
   Live a menudo rechazan su correo.
4. Si alimentas adsb.lol con un receptor propio, usa en su lugar tu clave de
   colaborador (feeder). Tus claves están en **My keys** en adsb.lol
   (<https://www.adsb.lol/mmb>).
5. Pega la clave en **adsb.lol API key (optional; your own, sent only to
   adsb.lol, which is asked while adsb.fi is failing)**.

La clave solo se envía a adsb.lol. Si adsb.lol la rechaza (incorrecta o
caducada), Live Track SALT sigue sin ella, y el atributo `adsblol_key` del
sensor muestra `refused` hasta que cambies la clave. Si no, muestra `set`, o
`none` sin clave. No hace falta ninguna contraseña ni ningún secreto.

---

## Poner el mapa en un panel de control

El mapa es [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard),
la tarjeta en la que dibuja cada módulo de Live Track. **Se instala con Live
Track SALT**: nada que descargar, nada que copiar, ningún recurso que añadir.

1. Abre un panel de control, elige el lápiz (**Editar panel de control**) y
   luego **Añadir tarjeta**.
2. Baja hasta el final y elige **Manual**.
3. Pega esto, y elige **Guardar**:

```yaml
type: custom:live-track-map-card
entity_filter:
  include:
    - domain: geo_location
      attributes:
        source: live_track_salt
      options:
        display: attribute
        attribute: marker_label
        position_transition: auto
  exclude:
    - state: unavailable
```

Los otros módulos de Live Track van en `entity_filter` del mismo modo: una
regla `- domain: geo_location` más por cada fuente.

**En el mapa:**

* Cada avión se dibuja como su propio tipo, girado hacia donde vuela, y se
  mueve con suavidad entre las posiciones que comunica. Cada buque de la lista
  se dibuja como un casco, girado hacia su rumbo.
* La etiqueta de un avión de la lista es su agencia (`CBP`, `ICE`). Un chárter
  de ICE Air dice `ICE Air Charter?`, una detección `Detected, unconfirmed`.
  Los demás aviones muestran su indicativo, su operador o su tipo.
* **Señala** un marcador para ver quién lo opera, qué dice la lista de él y
  su foto cuando la hay. **Haz clic** en él para ver todos sus detalles y una
  foto más grande, enlazada con su página ([Fotos](#fotos)).

La tarjeta mantiene una sola fila de recurso del panel de control para todos
los módulos de Live Track juntos: la versión más nueva de la tarjeta que lleve
cualquiera de ellos, nunca una más antigua. Una tarjeta que hayas instalado tú
desde el Marketplace no se toca. Si los recursos de tus paneles de control
están definidos en YAML (`lovelace: resource_mode: yaml`), no se puede
registrar nada por ti: un aviso en **Reparaciones** da entonces la línea exacta
que hay que añadir, que se parece a esta, con la dirección propia de la
integración en lugar de los marcadores de posición:

```yaml
lovelace:
  resource_mode: yaml
  resources:
    - url: /live_track_salt/map-card/<12 hex>/live-track-map-card.js?v=<version>&h=<12 hex>
      type: module
```

Al borrar la entrada de Live Track SALT, la fila pasa a otro módulo de Live
Track, o se quita si no queda ninguno. Si se borran los archivos de la
integración mientras su entrada sigue configurada, y no hay instalado ningún
otro módulo de Live Track, quita tú mismo la fila de la tarjeta en
**Configuración → Paneles de control → Recursos**. Para instalar la tarjeta a
mano, sigue el README de la tarjeta. Una fila que hayas creado tú, para una
copia en `/local/` o en cualquier otra dirección, nunca se cambia ni se elimina.
Mientras cargue la tarjeta, todos los módulos Live Track le dejan la tarjeta,
incluso cuando un módulo trae una versión más nueva, y nada en
**Reparaciones** lo indica. Para volver a la copia del módulo, elimina tu fila
en **Configuración → Paneles de control → Recursos** y reinicia Home Assistant.
Si borras el archivo de tu copia, elimina también su fila: mientras quede una
fila cuyo archivo ya no existe, el módulo no añade ninguna fila propia.
Cualquier otra tarjeta de mapa que muestre entidades
`geo_location` muestra también los aviones y los buques, como marcadores
simples.

---

## Usarlo en automatizaciones

Todo es una entidad normal de Home Assistant, así que el editor de
automatizaciones funciona con ello, sin código.

**Una notificación en el teléfono cuando un buque de la Guardia Costera de la
lista está en una de las cuatro zonas de agua** (necesita la clave de
aisstream.io):

1. **Configuración → Automatizaciones y escenas → Crear automatización → Crear
   nueva automatización**.
2. **Cuando**: **Añadir disparador**, escribe `numérico` en el cuadro de
   búsqueda y elige **El estado numérico cruzó el umbral**. Elige la
   **Entidad** **Live Track SALT aircraft shown**, el **Atributo** **Vessels
   shown** (`vessels_shown`), y en **Por encima de**, **Número fijo**, escribe
   `0`.
3. **Entonces hacer**: **Añadir acción**, busca la acción de notificación de
   tu teléfono (lleva el nombre de tu teléfono), y escribe un mensaje, por
   ejemplo:

   ```text
   Hay un buque de la Guardia Costera de la lista en el mapa
   ```

4. **Guardar**.

**Otras ideas:** una luz que se enciende mientras un avión de la lista está en
tu zona de interés sobre Puerto Rico, con la opción **Show listed aircraft
outside the focus area** desactivada y el atributo `listed_shown` por encima
de 0; un contador en el panel de control de los aviones de la lista que están
en el aire, a partir de `listed_shown`; un mensaje cuando Live Track SALT
propone un nuevo avión de ICE Air para la lista, cuando cambia el atributo
`proposed_for_list`; una notificación cuando aparece un buque frente al sur de
California, a partir de `vessels_shown`.

---

## Todo lo del mapa, en detalle

### Aviones de la lista

[EnforcementAircraft](https://github.com/StrausbergAutomationWorks/EnforcementAircraft)
es una lista pública de aviones que se usan en el control migratorio,
publicada por StrausbergAutomationWorks, cada entrada con sus fuentes: aviones
de las fuerzas federales del orden (DHS, CBP, ICE, DOJ, USMS), los aviones de
línea chárter que vuelan para ICE Air, y agencias estatales y locales con un
papel documentado en el control migratorio. El 19 de noviembre de 2026 tenía
416 aviones, 344 de ellos confirmados por sus fuentes.

Live Track SALT pide cada avión de la lista una vez por minuto, esté donde
esté. Un avión de la lista se dibuja con luces rojas y azules intermitentes y
con su agencia en la etiqueta. Cada uno cita la lista y la fuente de la que
viene su posición.

Los aviones transmiten su posición por radio, con un sistema llamado ADS-B.
Voluntarios de todo el mundo mantienen receptores y comparten lo que oyen a
través de redes comunitarias: Live Track SALT pregunta a adsb.fi, y a adsb.lol
cuando adsb.fi no responde. Fuera de tu zona de interés, un avión de la lista
se mueve una vez por minuto.

En cada avión: `enforcement_status` (`sourced`, `ice_air_charter` o
`detected_unconfirmed`), `enforcement_agency`, `enforcement_entry`,
`operator_short`, `outside_radius`, `identity` (el código hexadecimal),
`callsign`, `registration`, `aircraft_type`, `altitude_m`, `speed_kmh`,
`course_deg`, `last_seen`.

### Chárteres de ICE Air y vuelos de ICE Air

Algunos aviones de línea de la lista hacen vuelos chárter para ICE Air, entre
otros trabajos. Llevan la etiqueta `ICE Air Charter?` y se dibujan con un
brillo fijo: el signo de interrogación dice que el avión hace vuelos chárter
para ICE Air, no que este vuelo sea uno de ellos.

Mientras un avión matriculado en los Estados Unidos transmite un indicativo de
ICE Air (`VELUX` o `TYSON` con dos cifras, `TYS` con una a cuatro cifras, o
`UX` con dos cifras, solo o detrás de `VEL` o `GXA`), es un vuelo de ICE Air:
la etiqueta de un chárter pierde el signo de interrogación, un avión del
gobierno de la lista conserva su propia etiqueta, y `ice_air_flight` nombra la
familia del indicativo. Un avión que no está en la lista y vuela con uno en tu
zona de interés se dibuja como chárter (`ice_air_charter_flight`), se recuerda
tras un reinicio, se vigila en todas partes desde entonces, y aparece en el
atributo `proposed_for_list` del sensor.

### Aviones de las fuerzas federales del orden en el registro de la FAA

Cada avión que el registro de la FAA (Estados Unidos) indica como propiedad de
una agencia federal del orden se vigila también en todas partes, para que
aparezca un avión matriculado después de crear la lista. Se dibuja en azul con
luces y con el nombre del registro (`identified_by: faa_government`).

### Detecciones

Un avión que no está en la lista y transmite en tu zona de interés un
indicativo que usa DHS (`TROY` y cifras) es una detección. Lleva la etiqueta
`Detected, unconfirmed` (detectado, sin confirmar), se dibuja sin luces bajo un
anillo blanco discontinuo, se recuerda tras un reinicio, y se vigila en todas
partes desde entonces. Un avión cuya dirección la fuente marca como protegida
por privacidad lleva la etiqueta `Potential PIA` (posible PIA), nunca más.

⚠ Una detección no es una conclusión. Solo la revisión propia de la lista
añade un avión a la lista.

### Tu zona de interés

Se dibuja cada avión que haya dentro de tu zona de interés, como en
[Live Track Aircraft](https://github.com/StrausbergAutomationWorks/LiveTrackAircraft),
pedido cada 15 segundos. Cuando hay dentro más aviones de los que permite la
opción **Most aircraft shown in the focus area (listed aircraft are always
shown)**, se conservan los más cercanos; los aviones de la lista se conservan
siempre.

**Con Live Track Aircraft instalado**, cada uno se ocupa de su parte: dentro
de la zona de Live Track Aircraft, Live Track Aircraft dibuja cada avión,
incluidos los de la lista; en todos los demás lugares los dibuja Live Track
SALT. Comparten una sola petición a las fuentes, ningún avión se dibuja dos
veces, y una zona de interés que está entera dentro de la zona de Live Track
Aircraft no cuesta ninguna petición propia.

### Buques de la Guardia Costera de la lista

[EnforcementVessels](https://github.com/StrausbergAutomationWorks/EnforcementVessels)
es una lista pública de buques de la Guardia Costera nombrados en el trabajo
migratorio, publicada por StrausbergAutomationWorks, cada uno con su fuente,
junto con las cuatro zonas de agua donde se hace ese trabajo. El 19 de
noviembre de 2026 tenía 41 buques.

Con una clave de aisstream.io, Live Track SALT sigue esos buques por sus
números MMSI. Un buque de la lista solo se dibuja dentro de una de las cuatro
zonas, en verde militar con el brillo rojo y azul, con su agencia en la
etiqueta. Al señalarlo se muestra su nombre, por ejemplo
`USCGC Benjamin Bottoms (WPC 1132) · USCG`. Un buque que no se oye durante 30
minutos se quita.

**Con Live Track Ships instalado**, Live Track Ships dibuja él mismo un buque
de la lista, con el mismo aspecto, y Live Track SALT se lo deja a Ships: un
buque, un marcador.

⚠ Los buques comunican su posición por AIS solo donde un receptor los oye.
Cuando lo medimos, a las 01:25 hora central (Estados Unidos) del 19 de
noviembre de 2026, se oían cuatro buques de la lista, todos fuera de las cuatro
zonas, y no se dibujó ninguno.

### Fotos

**Aviones.** Al señalar un avión, el mapa muestra una foto suya de
[Planespotters.net](https://www.planespotters.net), si la hay, con el nombre
del fotógrafo al lado. Haz clic en el avión para ver la foto más grande; la
foto enlaza con su página en Planespotters.net. No hay nada que configurar.

La foto se busca solo cuando alguien señala ese avión, nunca para todos los
aviones del mapa. Tu Home Assistant la pide a Planespotters.net por el código
hexadecimal del avión y guarda la respuesta, una foto o ninguna, durante 12
horas, solo en memoria, así que un reinicio la olvida. El navegador que muestra
el mapa carga la imagen directamente de Planespotters.net. Home Assistant no
descarga, guarda ni reenvía ninguna imagen.

**Buques de la Guardia Costera de la lista.** Un buque de la lista muestra una
foto de [Wikimedia Commons](https://commons.wikimedia.org) cuando
[Wikidata](https://www.wikidata.org) tiene una para él, con el nombre del autor
y la licencia. Se busca por el número IMO del buque y, si así no se encuentra
nada, por su número MMSI. El 21 de noviembre de 2026, 29 de los 41 buques de la
lista tenían una. Una foto encontrada se guarda 30 días y un "sin foto" 14, en
la carpeta `.storage` de Home Assistant. El navegador carga la imagen desde
Wikimedia.

⚠ Una foto muestra el avión o el buque como lo vio el fotógrafo, quizá con
otra pintura, otro operador u otro nombre. No todos los aviones ni todos los
buques tienen foto.

⚠ No se busca foto para un avión que vuela con una dirección temporal por
privacidad (el programa Privacy ICAO Address de la FAA, Estados Unidos), porque
ese código hexadecimal no identifica el avión, ni para una traza sin un código
hexadecimal real.

⚠ Todavía no hay ninguna opción para desactivar las fotos.

Cada avión con código hexadecimal lleva `marker_photo_lookup`: la dirección en
tu Home Assistant donde el mapa pide su foto. Solo alguien que haya iniciado
sesión en tu Home Assistant puede usarla. Un buque con foto la lleva en
`marker_photo`. El registrador no guarda ninguno de los dos. Las fotos son obra
de sus fotógrafos: consulta [Créditos y licencias](#créditos-y-licencias).

---

## Todas las entidades que crea

| Entidad | Qué es |
|---|---|
| `sensor.live_track_salt_aircraft_shown` | **Live Track SALT aircraft shown**: cuántos aviones hay ahora en el mapa, los de la lista y los de tu zona de interés juntos |
| `geo_location.salt_aircraft_…` | una por avión, con el nombre de su código hexadecimal (`geo_location.salt_aircraft_a1b2c3`); viene y se va con el avión |
| `geo_location.salt_vessel_…` | una por buque de la lista dentro de una de las cuatro zonas, con el nombre de su MMSI (`geo_location.salt_vessel_338926432`); viene y se va con el buque |

Cada marcador lleva `source: live_track_salt`, y su estado es su distancia al
centro de tu zona de interés en kilómetros.

Los atributos del sensor dicen lo que pasa: `listed_shown` (aviones de la
lista en el mapa), `outside_radius` (aviones dibujados fuera de tu zona de
interés), `claimed_elsewhere` (aviones que dibuja Live Track Aircraft en su
lugar), `federal_registrants`, `detected_by_callsign`, `proposed_for_list`,
`vessels_shown`, `vessels_outside_theatres` (buques de la lista oídos fuera de
las cuatro zonas), `vessels_claimed_elsewhere` (buques de la lista que dibuja
Live Track Ships en su lugar), `vessel_list`, `vessel_feed`, `circle_status`
(la última respuesta para tu zona de interés: `ok`, o qué falló),
`hex_status`, `source_backoff`, `adsblol_key`, `list`, `radius_km`,
`max_aircraft` y `nationwide`.

⚠ **Los marcadores no tienen identificador único, a propósito.** Los aviones
vienen y se van por miles, y una fila del registro para cada uno haría que
Home Assistant arrancara más despacio sin ningún beneficio. Por eso no se
pueden renombrar, ocultar ni asignar a un área en la interfaz. Sus
identificadores de entidad vienen igualmente del código hexadecimal o del
MMSI, así que el mismo avión o buque recibe siempre el mismo identificador. El
sensor tiene identificador único y se puede renombrar.

⚠ **Tu base de datos.** El registrador de Home Assistant guarda una fila nueva
cada vez que cambia una entidad, y un marcador en movimiento cambia en cada
actualización: cada 15 segundos en tu zona de interés, una vez por minuto en
otros lugares. Live Track SALT solo deja fuera del registrador, por sí mismo,
los atributos de las fotos. Si no quieres el historial de cada marcador, déjalos fuera del
registrador. Añade esto a `configuration.yaml` y reinicia:

```yaml
recorder:
  exclude:
    entity_globs:
      - geo_location.salt_aircraft_*
      - geo_location.salt_vessel_*
```

Si tu `configuration.yaml` ya tiene una sección `recorder:`, añade solo los
dos patrones, bajo `exclude:` y `entity_globs:`. Una tarjeta de mapa
configurada para dibujar el historial no tendrá entonces rastro que dibujar.
El sensor cuesta poco: sus atributos toman pocos valores, así que el
registrador los guarda una vez.

---

## Qué envía y qué descarga

**Sobre tu ubicación.** El centro y el radio de tu zona de interés se envían a
adsb.fi en cada actualización, cada 15 segundos, y a adsb.lol mientras adsb.fi
no responde. El centro se envía tal como lo has puesto, y empieza en tu casa:
para dejar de enviar tu casa, aleja el centro de ella (**Configurar** →
**Centre of the focus area**) o borra la entrada. Cuando tu zona de interés
está entera dentro de la zona de Live Track Aircraft, no se envía nada para
ella. La petición de cada minuto solo lleva los códigos hexadecimales de los
aviones que se vigilan. aisstream.io recibe tu clave de aisstream.io y los
números MMSI de la lista de buques, con una zona que cubre todo el mundo: nada
sobre dónde estás. Tu clave de adsb.lol solo va a adsb.lol. Cuando alguien
señala un avión en el mapa, su código hexadecimal se envía a
Planespotters.net, como mucho una vez cada 12 horas por avión, y el navegador
que muestra el mapa carga la foto desde allí. Los números IMO y MMSI de los
buques de la lista se envían a Wikidata y los nombres de sus archivos de foto
a Wikimedia Commons, y el navegador carga esas fotos desde Wikimedia. Todavía
no hay ninguna opción para impedirlo. No se envía nada más sobre ti a ninguna
parte. Cada servicio ve tu dirección de Internet, como cualquier sitio web.

**Cuánto.** Tamaños medidos el 19 de noviembre de 2026 a las 01:25 hora
central (Estados Unidos). ⚠ Es de noche en Norteamérica, cuando vuelan muchos
menos aviones.

| Fuente | Qué y cada cuánto | Tamaño medido | Tras un error |
|---|---|---|---|
| adsb.fi | cada avión de tu zona de interés, cada 15 segundos; una petición por minuto para todos los aviones vigilados juntos (los de la lista, los de las fuerzas federales del orden del registro de la FAA y las detecciones) | zona de interés de 56 km (35 millas): 0,7 KB (1 avión); de 463 km (288 millas) sobre Texas: 18,9 KB (37 aviones), y 307 KB (535 aviones) de día, el 1 de noviembre de 2026 a las 14:01; la petición de cada minuto para los 416 aviones de la lista: 3,6 KB (6 en el aire) | pregunta a adsb.lol en su lugar. Una fuente que rechaza con HTTP 429 se salta durante el tiempo que pide, hasta 15 minutos; tras dos fallos de otro tipo seguidos, durante 1 minuto, que se dobla hasta 10 minutos. Una zona de interés que falla conserva su última respuesta durante tres actualizaciones |
| adsb.lol | las mismas peticiones, solo mientras adsb.fi no responde; la zona de interés como mucho cada 30 segundos | zona de interés de 463 km sobre Texas: 18,3 KB | lo mismo |
| aisstream.io | una conexión, siempre abierta; los buques de la lista llegan a medida que comunican su posición | 2 mensajes, 638 bytes, en 120 segundos | se vuelve a conectar tras una pausa de 2 segundos, que se dobla hasta 5 minutos |
| Planespotters.net | una petición por la foto de un avión la primera vez que alguien lo señala, y luego ninguna para ese avión durante 12 horas. Las respuestas se guardan solo en memoria. El navegador que muestra el mapa carga la foto por sí mismo | 407 bytes con foto, 13 bytes sin ella (dos aviones, 21 de noviembre de 2026) | tras un HTTP 429, no se pide ninguna foto durante el tiempo que pida Planespotters.net, o durante 10 minutos; tras un HTTP 403, durante un día |
| Wikidata y Wikimedia Commons | solo para los buques de la lista: hasta tres peticiones por cada 20 buques, como mucho una ronda cada 10 segundos; una foto encontrada se vuelve a pedir a los 30 días, un "sin foto" a los 14 | 126 KB por 20 buques, en tres respuestas de 0,8 KB, 94 KB y 31 KB; 15 fotos encontradas (21 de noviembre de 2026) | se vuelve a pedir un minuto después |
| EnforcementAircraft, desde GitHub | un archivo de sumas de comprobación cada 6 horas; la lista en sí solo si ha cambiado | sumas de comprobación 91 bytes; lista 292 KB | se reintenta en la siguiente comprobación de cada hora; tu copia sigue en uso |
| EnforcementVessels, desde GitHub | un archivo de sumas de comprobación cada 6 horas; la lista en sí solo si ha cambiado | sumas de comprobación 90 bytes; lista 90 KB | lo mismo |
| Registro de aeronaves de la FAA (Estados Unidos) | se comprueba una vez al día; se descarga de `registry.faa.gov` cuando tu copia tiene 7 días | 73,1 MB | se reintenta al día siguiente; tu copia sigue en uso |

Los archivos descargados se comparten con otros módulos de Live Track, así que
cada uno se descarga una sola vez, instales los módulos que instales. Se
guardan en la carpeta `.storage` de Home Assistant con nombres que empiezan
por `saw_`. Si quitas Live Track SALT y ningún otro módulo de Live Track los
usa, puedes borrarlos a mano.

---

## Ayúdanos a hacerlo crecer

Live Track SALT sigue creciendo. Añadimos fuentes de datos a medida que las
encontramos, y queremos saber qué te gustaría a continuación.

### Sugerir algo

¿Falta tu zona o tu fuente de datos? ¿Hay algo mal, o difícil de entender?
Cuéntanoslo de la forma que te resulte más fácil:

* [**Rellena un formulario corto**](https://github.com/StrausbergAutomationWorks/LiveTrackSALT/issues/new?template=es.yml)
  en español. Necesitas una cuenta gratuita de GitHub.
* **Escribe un correo** a
  [StrausbergAutomationWorks@recordwise.org](mailto:StrausbergAutomationWorks@recordwise.org).
  No hace falta cuenta.

En cualquier caso, ayuda que nos digas:

* qué te gustaría ver, y en qué parte del mundo;
* un enlace a donde se publican los datos, si conoces uno (una página de
  datos abiertos, un canal público, la web de un servicio): no es necesario,
  pero ayuda;
* el idioma de tu Home Assistant, si el problema es la redacción o una
  traducción.

Escribe en inglés o en tu propio idioma, lo que te resulte más fácil.

Un avión que debería estar en la lista se propone en
[EnforcementAircraft](https://github.com/StrausbergAutomationWorks/EnforcementAircraft),
que mantiene la lista, no en este formulario.

### Añadirlo tú mismo, con nuestra ayuda

Si quieres añadir algo tú mismo, te ayudaremos a hacerlo, desde la primera
pregunta hasta la versión terminada. No necesitas ser desarrollador para
empezar:

* **Una traducción.** Los textos del diálogo de configuración son una lista
  corta de frases en un archivo de texto. Te mostraremos qué archivo y qué
  líneas.
* **Una nueva fuente de datos.** Dinos dónde se publican los datos. Podemos
  escribir el código juntos, o revisar el tuyo.
* **Probarlo donde vives.** Instálalo, mira tu parte del mapa y dinos qué está
  bien y qué no.
* **Una corrección de este README.** Si un paso no coincidía con lo que
  viste, dinos lo que viste.

[**Cuéntanos qué tienes en mente**](https://github.com/StrausbergAutomationWorks/LiveTrackSALT/issues/new?template=es.yml)
o escribe a
[StrausbergAutomationWorks@recordwise.org](mailto:StrausbergAutomationWorks@recordwise.org),
y te responderemos con los siguientes pasos.

---

## Idiomas

Este README: [English](README.md), **Español**. Cada README traducido está
completo. Ninguno lo ha leído todavía un hablante nativo. Si el español es tu
lengua materna, dinos si este README se lee bien: ver
[Ayúdanos a hacerlo crecer](#ayúdanos-a-hacerlo-crecer).

El diálogo de configuración y las opciones están por ahora solo en inglés, sea
cual sea el idioma de tu Home Assistant. Si hablas otro idioma, puedes
traducirlos tú mismo: es una lista corta de frases en un solo archivo, y [te
ayudaremos a hacerlo](#añadirlo-tú-mismo-con-nuestra-ayuda).

¿Has encontrado un error en una traducción, o necesitas otro idioma?
Dínoslo en <https://github.com/StrausbergAutomationWorks/LiveTrackSALT/issues>,
o [tradúcelo con nuestra ayuda](#añadirlo-tú-mismo-con-nuestra-ayuda).

---

## Créditos y licencias

* **adsb.fi** (<https://adsb.fi>): posiciones de aviones, datos abiertos solo
  para uso personal y no comercial, según las condiciones de su
  [README de datos abiertos](https://github.com/adsbfi/opendata), que piden
  citar a adsb.fi y enlazar a su página principal. Al instalar esta
  integración usas adsb.fi, y sus condiciones se aplican a ti.
* **adsb.lol** (<https://adsb.lol>): posiciones de aviones, bajo la
  [Open Database License (ODbL) 1.0](https://opendatacommons.org/licenses/odbl/).
  Al instalar esta integración usas adsb.lol, y sus condiciones se aplican a
  ti. Las dos redes las mantienen voluntarios: si puedes, apóyalas aportando
  los datos de un receptor.
* **aisstream.io** (<https://aisstream.io>): posiciones de buques, con tu
  propia cuenta y tu propia clave. aisstream.io no publica condiciones de uso;
  cada buque lo cita.
* **EnforcementAircraft** ([StrausbergAutomationWorks](https://github.com/StrausbergAutomationWorks/EnforcementAircraft)):
  la lista de aviones que se usan en el control migratorio, bajo la
  [ODbL 1.0](https://opendatacommons.org/licenses/odbl/1-0/).
* **EnforcementVessels** ([StrausbergAutomationWorks](https://github.com/StrausbergAutomationWorks/EnforcementVessels)):
  la lista de buques de la Guardia Costera nombrados en el trabajo migratorio,
  y las cuatro zonas de agua, bajo la
  [ODbL 1.0](https://opendatacommons.org/licenses/odbl/1-0/).
* **El registro de aeronaves de la FAA** (Federal Aviation Administration,
  Estados Unidos): propietarios de aviones matriculados en los Estados Unidos,
  y los aviones de las fuerzas federales del orden, datos públicos del
  gobierno de los Estados Unidos, que descarga cada instalación.
* **ADS-B Radar** (<https://adsb-radar.com>): los iconos de aviones, usados
  con permiso y según sus condiciones. Los iconos no están cubiertos por la
  licencia MIT de este repositorio. Algunos iconos, entre ellos el Beechcraft
  King Air 350 del icono de la marca, los dibujó StrausbergAutomationWorks y
  los donó a ADS-B Radar, así que también se rigen por sus condiciones. El
  anillo discontinuo que se dibuja sobre una detección es propio de esta
  integración. Los detalles están en [ATTRIBUTION.md](ATTRIBUTION.md).
* **El icono de los buques** es el casco de Live Track Ships, dibujado para
  StrausbergAutomationWorks, bajo la licencia MIT.
* **Planespotters.net** (<https://www.planespotters.net>): las fotos de los
  aviones, a través de su [API de fotos](https://www.planespotters.net/photo/api)
  y bajo sus condiciones. Cada foto es obra de su fotógrafo, cuyo nombre
  aparece a su lado, y enlaza con su página en Planespotters.net. No se copia
  ninguna foto en este repositorio, y Home Assistant no descarga, guarda ni
  reenvía ninguna imagen. Al instalar esta integración usas Planespotters.net,
  y sus condiciones se aplican a ti.
* **Wikidata** (<https://www.wikidata.org>) y **Wikimedia Commons**
  (<https://commons.wikimedia.org>): las fotos de los buques y los datos que
  permiten encontrarlas. Cada foto se muestra con su autor y su licencia, tal
  como los da Commons, y enlaza con su página allí. Los datos de Wikidata están
  bajo [CC0](https://creativecommons.org/publicdomain/zero/1.0/).
* **La tarjeta de mapa** es [LiveTrackMapCard](https://github.com/StrausbergAutomationWorks/LiveTrackMapCard),
  MIT, una copia de [ha-map-card](https://github.com/nathan-gs/ha-map-card) de
  nathan-gs, MIT. Sus teselas de mapa y sus créditos están en su README.

Ninguna de estas organizaciones ha creado ni respaldado esta integración.

**Código**: MIT, en [LICENSE](LICENSE).

**Para desarrolladores:** las entidades siguen el contrato de mapa común de
Live Track, así que cada módulo aparece en un solo mapa; los lectores de las
listas, los iconos de aviones, la petición de aviones compartida, la conexión
compartida con aisstream.io y la búsqueda de fotos están en la biblioteca
[saw-livetrack](https://pypi.org/project/saw-livetrack/). Las pruebas se
ejecutan con `python -m unittest discover -s tests`, con `saw-livetrack`
instalado.

---

## Palabras clave

Home Assistant control migratorio · ICE · ICE Air · vuelos de deportación ·
CBP · DHS · Guardia Costera · aviones de inmigración · aviones de ICE ·
inmigración · ADS-B · mapa ADS-B · AIS · seguimiento de vuelos ·
radar de aviones · immigration enforcement · deportation flights ·
Coast Guard · adsb.fi · adsb.lol · aisstream.io · EnforcementAircraft ·
EnforcementVessels · registro de la FAA · ADS-B Radar · Planespotters.net ·
fotos de aviones · Wikidata · Wikimedia Commons · geo_location ·
tarjeta de mapa · Lovelace · HACS · Marketplace · Live Track · LiveTrack ·
StrausbergAutomationWorks

---

**Reconocimiento.** StrausbergAutomationWorks reconoce a los pueblos indígenas
de todas las tierras y aguas de este mapa, en todo el mundo, y presenta sus
respetos a sus Mayores del pasado y del presente.
