"""Punto de entrada del bot.

Flujo:
  1. Comprueba que en Espana (Europe/Madrid) son las 08:00 (salvo FORZAR=1).
  2. Descarga el PVPC horario del dia desde REE.
  3. Construye el mensaje.
  4. Lo envia por la API oficial de Meta (WhatsApp Cloud API), como plantilla.

Variables de entorno utiles:
  FORZAR=1       omite la comprobacion de la hora (para pruebas / workflow_dispatch)
  SOLO_TEXTO=1   imprime el mensaje pero NO lo envia (para pruebas locales)
  WHATSAPP_TOKEN / WHATSAPP_PHONE_NUMBER_ID / WHATSAPP_RECIPIENT  (ver whatsapp.py)
"""
from __future__ import annotations

import os
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

from mensaje import construir_linea_plantilla, construir_mensaje
from precios import obtener_precios
from whatsapp import enviar_plantilla

TZ_ESPANA = ZoneInfo("Europe/Madrid")
HORA_ENVIO = 8  # 08:00 hora peninsular


def main() -> int:
    forzar = os.environ.get("FORZAR") == "1"
    ahora = datetime.now(TZ_ESPANA)

    if not forzar and ahora.hour != HORA_ENVIO:
        print(
            f"[main] Son las {ahora:%H:%M} en Madrid, no las {HORA_ENVIO:02d}:00. "
            "Salgo sin enviar."
        )
        return 0

    dia = ahora.date()
    precios = obtener_precios(dia)

    # Version multilinea, solo para dejar constancia legible en el log.
    print("[main] Mensaje (vista en columna):")
    print(construir_mensaje(precios, dia))

    linea = construir_linea_plantilla(precios, dia)
    print(f"\n[main] Parametro de la plantilla ({len(linea)} caracteres):")
    print(linea)

    if os.environ.get("SOLO_TEXTO") == "1":
        print("\n[main] SOLO_TEXTO=1: no se envia WhatsApp.")
        return 0

    enviar_plantilla(linea)
    print("\n[main] WhatsApp enviado correctamente.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
