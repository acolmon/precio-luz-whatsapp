# Bot de WhatsApp: precio de la luz por horas

Cada dia a las **08:00 (hora de Espana)** recibes por WhatsApp un mensaje de **texto**
con el precio PVPC (tarifa 2.0TD) de las **24 horas del dia**, en orden cronologico
(00:00 -> 23:00). Cada linea lleva un emoji segun el precio:

- 🟢 `< 0,15 EUR/kWh`
- 🟡 `0,15 - 0,20 EUR/kWh`
- 🔴 `> 0,20 EUR/kWh`

Ademas marca la hora mas barata y la mas cara del dia y un resumen con la media.

Ejemplo del mensaje:

```
💡 Precio de la luz — 02/09/2026
Media del dia: 0,1897 €/kWh

🟡 00:00  0,1814 €/kWh
🟡 01:00  0,1821 €/kWh
...
🟢 14:00  0,0513 €/kWh  (minimo)
...
🔴 20:00  0,3434 €/kWh  (maximo)
...
🔴 23:00  0,2252 €/kWh

🟢 Horas mas baratas: 14h, 15h, 16h
```

**Fuente de datos:** API publica de Red Electrica de Espana (`apidatos.ree.es`), serie
`PVPC` (id 1001). Es el precio regulado que factura Curenergia. No necesita token.
La potencia contratada (3,45 kW) no afecta a este precio horario: solo al termino fijo
de potencia del recibo.

**Envio:** [CallMeBot](https://www.callmebot.com/blog/free-api-whatsapp-messages/), un
servicio gratuito para mandarte mensajes de WhatsApp a ti mismo. Solo para uso personal.

**Ejecucion:** gratis en **GitHub Actions** (no necesitas servidor).

---

## Estructura

```
precio-luz-whatsapp/
├── .github/workflows/precio-luz.yml   cron (06:00 y 07:00 UTC) + ejecucion manual
├── src/
│   ├── main.py       comprueba la hora y orquesta todo
│   ├── precios.py     descarga y normaliza el PVPC de REE
│   ├── mensaje.py     construye el texto (24 horas + emojis + resumen)
│   └── callmebot.py   envia el texto por CallMeBot
└── requirements.txt
```

---

## Fase A · Probarlo en tu ordenador (sin enviar nada)

En esta maquina, `python` / `py` del PATH NO funcionan (son accesos de la Microsoft
Store). Usa la ruta completa del Python instalado.

1. Abre **PowerShell** y entra en la carpeta del proyecto:

   ```powershell
   cd "c:\Users\a-cm2\OneDrive - Universitat Jaume I\Escritorio\Codigo creado\precio-luz-whatsapp"
   ```

2. Crea el entorno virtual e instala las dependencias:

   ```powershell
   & "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe" -m venv .venv
   .\.venv\Scripts\python.exe -m pip install -r requirements.txt
   ```

3. Genera el mensaje **sin enviarlo** (solo lo imprime en pantalla):

   ```powershell
   $env:SOLO_TEXTO = "1"; $env:FORZAR = "1"
   .\.venv\Scripts\python.exe src\main.py
   ```

   Deberias ver el mensaje completo con las 24 horas. Si se ve bien, pasa a la fase B.

---

## Fase B · Activar CallMeBot (unos 2 minutos)

1. En el movil donde tienes WhatsApp, **guarda un contacto nuevo** con el numero del
   bot de CallMeBot. Copia el numero **de la pagina oficial** (cambia cada cierto tiempo):
   <https://www.callmebot.com/blog/free-api-whatsapp-messages/>
   *(en el momento de escribir esto figura `+34 684 72 39 62`; confirmalo en la web).*

2. Abre WhatsApp y envia a ese contacto **exactamente** este texto (en ingles):

   ```
   I allow callmebot to send me messages
   ```

3. En hasta 2 minutos te responde con algo como:
   `API Activated for your phone number. Your APIKEY is 123456`.
   **Apunta esa APIKEY.**

4. Prueba el envio real desde tu ordenador:

   ```powershell
   $env:CALLMEBOT_PHONE = "34XXXXXXXXX"   # tu numero, con 34 y sin el signo +
   $env:CALLMEBOT_APIKEY = "tu_apikey"
   $env:FORZAR = "1"
   Remove-Item Env:SOLO_TEXTO -ErrorAction SilentlyContinue
   .\.venv\Scripts\python.exe src\main.py
   ```

   Te debe llegar el WhatsApp con la lista. Si el simbolo `€` se ve raro, avisame y lo
   cambio por `EUR`.

---

## Fase C · Automatizarlo con GitHub Actions

1. Crea una cuenta en <https://github.com> si no tienes.
2. Crea un repositorio **privado** (boton **New**), por ejemplo `precio-luz-whatsapp`.
3. Sube el contenido de esta carpeta. Lo mas facil sin instalar nada: en la pagina del
   repo vacio, enlace **"uploading an existing file"**, y arrastra `src/`, `.github/`,
   `requirements.txt`, `README.md` y `.gitignore`.
   - *Alternativa con Git:* instala <https://git-scm.com/download/win> y ejecuta en la
     carpeta:
     ```powershell
     git init; git add .; git commit -m "Bot precio de la luz"
     git branch -M main
     git remote add origin https://github.com/TU_USUARIO/precio-luz-whatsapp.git
     git push -u origin main
     ```
4. En el repo: **Settings -> Secrets and variables -> Actions -> New repository secret**.
   Crea estos dos:

   | Name | Secret |
   |---|---|
   | `CALLMEBOT_PHONE` | tu numero, formato internacional sin `+` (p. ej. `34612345678`) |
   | `CALLMEBOT_APIKEY` | la APIKEY de la fase B |

5. Pestana **Actions** -> **Precio de la luz diario** -> **Run workflow** (deja "forzar"
   marcado). En ~1 minuto debe llegarte el WhatsApp. Si falla, abre la ejecucion y mira
   el log del paso "Construir y enviar".

A partir de aqui funciona solo cada dia a las **08:00 hora de Espana**.

---

## Mantenimiento y notas

- **Haz algun commit cada menos de 60 dias** (aunque sea editar este README). GitHub
  desactiva los workflows programados tras 60 dias sin actividad; avisa por email antes.
- La APIKEY de CallMeBot **no caduca**.
- Los cron de GitHub Actions pueden **retrasarse 5-15 min** en horas punta.
- El workflow se lanza a las 06:00 y 07:00 UTC; `main.py` solo continua si en
  `Europe/Madrid` son las 08:00, asi que la ejecucion "que no toca" termina enseguida
  con un mensaje tipo "Son las 07:00 en Madrid...". Esto cubre el cambio verano/invierno
  sin tocar nada.
- Si algun dia no llega el mensaje: normalmente sera una caida puntual de CallMeBot
  (servicio gratuito de terceros) o un cambio en la API de REE. La ejecucion aparecera
  en rojo en **Actions** y GitHub te avisa por email.
- **Fuente alternativa de datos:** ESIOS de REE, indicador `1001`
  (`https://api.esios.ree.es/indicators/1001`); requiere un token gratuito que dan por
  email.

### Variables de entorno (resumen)

| Variable | Uso |
|---|---|
| `CALLMEBOT_PHONE`, `CALLMEBOT_APIKEY` | credenciales de envio |
| `FORZAR=1` | omite la comprobacion de las 08:00 |
| `SOLO_TEXTO=1` | imprime el mensaje pero no lo envia |

### Consejo: OneDrive

La carpeta esta dentro de OneDrive, que sincroniza todo. El entorno `.venv` (miles de
archivos) hace trabajar mucho a OneDrive e incluso puede "resucitar" tras borrarlo.
Opciones: excluir la carpeta `.venv` en la configuracion de OneDrive, o mover el
proyecto fuera de OneDrive (p. ej. a `C:\proyectos\precio-luz-whatsapp`).
