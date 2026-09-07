"""Construye el texto del mensaje diario a partir de la lista de precios.

Dos formatos:

1. `construir_mensaje()` -> multilinea, en columna. Se usa para el log del workflow y
   para la prueba local (SOLO_TEXTO). Legible para humanos.

2. `construir_linea_plantilla()` -> texto para el parametro {{1}} de la plantilla de
   WhatsApp Cloud API. Meta rechaza el salto de linea normal (\\n) en las variables, asi
   que se usa el separador Unicode U+2028 (LINE SEPARATOR): el filtro de Meta lo deja
   pasar y la mayoria de versiones de WhatsApp lo pintan como salto de linea, con lo
   que se ve en columna (una hora por linea). Si algun WhatsApp no lo respeta, se veria
   como un parrafo (no rompe nada).

En ambos, el emoji indica el tramo de precio (umbrales definidos en precios.py):
  🟢 < 0,15 €/kWh   🟡 0,15-0,20 €/kWh   🔴 > 0,20 €/kWh
"""
from __future__ import annotations

from datetime import date

from precios import PrecioHora, resumen

EMOJI = {"verde": "\U0001F7E2", "amarillo": "\U0001F7E1", "rojo": "\U0001F534"}
BOMBILLA = "\U0001F4A1"

# Separador de linea para el parametro de la plantilla. NO es "\n" (Meta lo rechaza):
# es U+2028 LINE SEPARATOR, que su validador deja pasar y WhatsApp suele mostrar como
# salto de linea.
SEP_LINEA = " "


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
    """Texto para el parametro {{1}} de la plantilla de WhatsApp.

    Sin \\n, \\t ni mas de 4 espacios seguidos (Meta lo rechazaria). Usa U+2028 entre
    lineas para que se vea en columna.
    """
    dia = dia or date.today()
    r = resumen(precios)
    hora_min = r["minimo"].hora
    hora_max = r["maximo"].hora

    lineas = [f"{dia.strftime('%d/%m/%Y')} · media {_eur(r['media'])} €/kWh"]
    for p in precios:
        if p.hora == hora_min:
            marca = "  (min)"
        elif p.hora == hora_max:
            marca = "  (max)"
        else:
            marca = ""
        lineas.append(
            f"{p.hora:02d}:00  {EMOJI[p.color]} {_eur(p.precio_kwh)} €/kWh{marca}"
        )

    baratas = ", ".join(f"{p.hora:02d}h" for p in r["horas_baratas"])
    lineas.append(f"Mas baratas: {baratas}")
    return SEP_LINEA.join(lineas)


if __name__ == "__main__":
    from precios import obtener_precios

    _precios = obtener_precios()
    print(construir_mensaje(_precios))
    print()
    print("--- version plantilla (parametro {{1}}, con U+2028 entre lineas) ---")
    linea = construir_linea_plantilla(_precios)
    print(repr(linea))
    print()
    print(linea)
