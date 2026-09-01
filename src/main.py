"""Punto de entrada del bot.

Flujo:
  1. Comprueba que en Espana (Europe/Madrid) son las 08:00 (salvo FORZAR=1).
  2. Descarga el PVPC horario del dia desde REE.
  3. Construye el texto con las 24 horas y su precio.
  4. Lo envia por WhatsApp con CallMeBot.

Variables de entorno utiles:
  FORZAR=1       omite la comprobacion de la hora (para pruebas / workflow_dispatch)
  SOLO_TEXTO=1   imprime el mensaje pero NO lo envia (para pruebas locales)
  CALLMEBOT_PHONE / CALLMEBOT_APIKEY   credenciales de envio (ver callmebot.py)
"""
from __future__ import annotations

import os
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

from callmebot import enviar_texto
from mensaje import construir_mensaje
from precios import obtener_precios

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
    texto = construir_mensaje(precios, dia)

    print("[main] Mensaje:")
    print(texto)

    if os.environ.get("SOLO_TEXTO") == "1":
        print("\n[main] SOLO_TEXTO=1: no se envia WhatsApp.")
        return 0

    enviar_texto(texto)
    print("\n[main] WhatsApp enviado correctamente.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
