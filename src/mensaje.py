"""Construye el texto del mensaje diario a partir de la lista de precios.

Formato (solo texto, pensado para WhatsApp):

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

Cada linea empieza con un emoji segun el umbral de precio definido en precios.py:
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


if __name__ == "__main__":
    from precios import obtener_precios

    print(construir_mensaje(obtener_precios()))
