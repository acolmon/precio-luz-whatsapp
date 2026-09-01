"""Envio de texto por WhatsApp usando la API gratuita de CallMeBot.

Requisitos previos (una sola vez, ver README):
  1. Guardar el numero del bot de CallMeBot en los contactos del movil.
  2. Enviarle por WhatsApp: "I allow callmebot to send me messages".
  3. El bot responde con tu APIKEY.

Variables de entorno:
  CALLMEBOT_PHONE    tu numero en formato internacional SIN '+', p. ej. 34612345678
  CALLMEBOT_APIKEY   la APIKEY que devuelve el bot
"""
from __future__ import annotations

import os

import requests

URL = "https://api.callmebot.com/whatsapp.php"


def enviar_texto(texto: str) -> None:
    phone = os.environ.get("CALLMEBOT_PHONE")
    apikey = os.environ.get("CALLMEBOT_APIKEY")
    faltan = [
        nombre
        for nombre, valor in (
            ("CALLMEBOT_PHONE", phone),
            ("CALLMEBOT_APIKEY", apikey),
        )
        if not valor
    ]
    if faltan:
        raise RuntimeError(f"Faltan variables de entorno: {', '.join(faltan)}")

    resp = requests.get(
        URL,
        params={"phone": phone, "text": texto, "apikey": apikey},
        timeout=30,
    )
    # CallMeBot siempre responde 200; el exito se confirma con "Message queued"
    # en el cuerpo. Cualquier otra cosa (APIKEY invalida, numero no activado, etc.)
    # se considera fallo para que el job de GitHub Actions quede en rojo.
    cuerpo = (resp.text or "").strip()
    if resp.status_code >= 400 or "queued" not in cuerpo.lower():
        raise RuntimeError(
            f"CallMeBot no confirmo el envio: HTTP {resp.status_code} - {cuerpo[:300]}"
        )
    print(f"[callmebot] {cuerpo[:200]}")
