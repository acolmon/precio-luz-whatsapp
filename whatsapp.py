"""Envio por la API oficial de Meta (WhatsApp Cloud API).

Los mensajes programados (fuera de una conversacion abierta) exigen una PLANTILLA
aprobada por Meta. Aqui se envia la plantilla `precio_luz_diario` con un unico
parametro de texto {{1}} en el cuerpo (la linea que genera mensaje.py).

Variables de entorno:
  WHATSAPP_TOKEN             token permanente del usuario de sistema de Meta
  WHATSAPP_PHONE_NUMBER_ID   ID del numero emisor (panel WhatsApp > API Setup)
  WHATSAPP_RECIPIENT         numero destino en formato internacional sin '+', p. ej. 34600222847
Opcionales:
  WHATSAPP_TEMPLATE          nombre de la plantilla (por defecto: precio_luz_diario)
  WHATSAPP_TEMPLATE_LANG     idioma de la plantilla (por defecto: es)
"""
from __future__ import annotations

import os

import requests

API_VERSION = "v21.0"


def enviar_plantilla(variable_texto: str) -> None:
    # .strip() por si el secret se pego con espacios o un salto de linea al final
    token = (os.environ.get("WHATSAPP_TOKEN") or "").strip()
    phone_id = (os.environ.get("WHATSAPP_PHONE_NUMBER_ID") or "").strip()
    destino = (os.environ.get("WHATSAPP_RECIPIENT") or "").strip()
    faltan = [
        nombre
        for nombre, valor in (
            ("WHATSAPP_TOKEN", token),
            ("WHATSAPP_PHONE_NUMBER_ID", phone_id),
            ("WHATSAPP_RECIPIENT", destino),
        )
        if not valor
    ]
    if faltan:
        raise RuntimeError(f"Faltan variables de entorno: {', '.join(faltan)}")

    plantilla = os.environ.get("WHATSAPP_TEMPLATE", "precio_luz_diario")
    idioma = os.environ.get("WHATSAPP_TEMPLATE_LANG", "es")

    url = f"https://graph.facebook.com/{API_VERSION}/{phone_id}/messages"
    payload = {
        "messaging_product": "whatsapp",
        "to": destino,
        "type": "template",
        "template": {
            "name": plantilla,
            "language": {"code": idioma},
            "components": [
                {
                    "type": "body",
                    "parameters": [{"type": "text", "text": variable_texto}],
                }
            ],
        },
    }
    resp = requests.post(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=30,
    )
    if resp.status_code >= 400:
        raise RuntimeError(
            f"WhatsApp Cloud API fallo: HTTP {resp.status_code} - {resp.text[:600]}"
        )
    print(f"[whatsapp] enviado: {resp.text[:300]}")
