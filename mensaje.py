"""Construye el texto del mensaje diario a partir de la lista de precios.

Dos formatos:

1. `construir_mensaje()` -> multilinea, en columna. Se usa para el log del workflow y
   para la prueba local (SOLO_TEXTO). Legible para humanos.

2. `construir_linea_plantilla()` -> UNA sola linea (sin saltos de linea). Es lo que se
   pasa como parametro {{1}} de la plantilla de WhatsApp Cloud API, que NO admite
   saltos de linea en las variables. En WhatsApp se ve como un parrafo que se ajusta
   solo.

En ambos, el emoji indica el tramo de precio (umbrales definidos en precios.py):
  🟢 < 0,15 €/kWh   🟡 0,15-0,20 €/kWh   🔴 > 0,20 €/kWh
"""
from __future__ import annotations

from datetime import date

from precios import PrecioHora, resumen

EMOJI = {"verde": "\U0001F7E2", "amarillo": "\U0001F7E1", "rojo": "\U0001F534"}
BOMBILLA = "\U0001F4A1"


def _eur(x: float) -> str:
    """0.1234 -> '0,1234' (coma decimal)."""
    return f"{x:.4f}".replace(".", ",")


def construir_mensaje(precios: list[PrecioHora], dia: date | None = None) -> str:
    dia = dia or date.today()
    r = resumen(precios)
    hora_min = r["minimo"].hora
    hora_max = r["maximo"].hora

    lineas = [
        f"{BOMBILLA} Precio de la luz — {dia.strftime('%d/%m/%Y')}",
        f"Media del dia: {_eur(r['media'])} €/kWh",
        "",
    ]
    for p in precios:
        if p.hora == hora_min:
            marca = "  (minimo)"
        elif p.hora == hora_max:
            marca = "  (maximo)"
        else:
            marca = ""
        lineas.append(
            f"{EMOJI[p.color]} {p.hora:02d}:00  {_eur(p.precio_kwh)} €/kWh{marca}"
        )

    baratas = ", ".join(f"{p.hora:02d}h" for p in r["horas_baratas"])
    lineas += ["", f"{EMOJI['verde']} Horas mas baratas: {baratas}"]
    return "\n".join(lineas)


def construir_linea_plantilla(precios: list[PrecioHora], dia: date | None = None) -> str:
    """Una sola linea para el parametro {{1}} de la plantilla de WhatsApp.

    Sin saltos de linea, sin tabuladores y sin mas de 4 espacios seguidos (Meta
    rechaza el parametro si los tiene). En WhatsApp se muestra como un parrafo.
    """
    dia = dia or date.today()
    r = resumen(precios)
    hora_min = r["minimo"].hora
    hora_max = r["maximo"].hora

    partes = [
        f"{dia.strftime('%d/%m/%Y')}",
        f"media {_eur(r['media'])} €/kWh",
    ]
    for p in precios:
        if p.hora == hora_min:
            marca = " min"
        elif p.hora == hora_max:
            marca = " max"
        else:
            marca = ""
        partes.append(f"{p.hora:02d}h {EMOJI[p.color]} {_eur(p.precio_kwh)}{marca}")

    baratas = ",".join(f"{p.hora:02d}h" for p in r["horas_baratas"])
    partes.append(f"mas baratas: {baratas}")
    # separador " · " (punto medio) entre trozos; no lleva saltos de linea
    return " · ".join(partes)


if __name__ == "__main__":
    from precios import obtener_precios

    _precios = obtener_precios()
    print(construir_mensaje(_precios))
    print()
    print("--- version plantilla (una linea, parametro {{1}}) ---")
    print(construir_linea_plantilla(_precios))
