"""Construye el texto del mensaje diario a partir de la lista de precios.

Dos formatos:

1. `construir_mensaje()` -> multilinea, en columna. Se usa para el log del workflow y
   para la prueba local (SOLO_TEXTO). Legible para humanos.

2. `construir_linea_plantilla()` -> texto para el parametro {{1}} de la plantilla de
   WhatsApp Cloud API. Meta NO admite saltos de linea (\\n) en las variables, asi que
   va todo en un parrafo con " . " entre trozos; en WhatsApp lo ajusta el ancho de la
   burbuja (~2 horas por linea).

En ambos, el emoji indica el tramo de precio (umbrales definidos en precios.py):
  🟢 < 0,15 €/kWh   🟡 0,15-0,20 €/kWh   🔴 > 0,20 €/kWh
"""
from __future__ import annotations

from datetime import date

from precios import PrecioHora, resumen

EMOJI = {"verde": "\U0001F7E2", "amarillo": "\U0001F7E1", "rojo": "\U0001F534"}
BOMBILLA = "\U0001F4A1"

# Separador entre trozos del parametro de la plantilla. Se probo U+2028 para forzar el
# salto de linea, pero algunos WhatsApp lo muestran como caracter roto; se usa " . ".
SEP_LINEA = " · "


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
    """Texto para el parametro {{1}} de la plantilla de WhatsApp (un parrafo, sin \\n)."""
    dia = dia or date.today()
    r = resumen(precios)
    hora_min = r["minimo"].hora
    hora_max = r["maximo"].hora

    partes = [f"{dia.strftime('%d/%m/%Y')} media {_eur(r['media'])} €/kWh"]
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
    return SEP_LINEA.join(partes)


if __name__ == "__main__":
    from precios import obtener_precios

    _precios = obtener_precios()
    print(construir_mensaje(_precios))
    print()
    print("--- parametro {{1}} de la plantilla ---")
    print(construir_linea_plantilla(_precios))
