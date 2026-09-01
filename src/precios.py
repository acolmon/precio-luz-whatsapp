"""Obtiene el precio PVPC (tarifa 2.0TD) hora a hora desde la API pública de REE.

Fuente: https://apidatos.ree.es/es/datos/mercados/precios-mercados-tiempo-real
No requiere token ni registro. Devuelve la serie "PVPC" (id 1001) con 24 valores
horarios en euros/MWh; aqui se normaliza a euros/kWh.

El PVPC es el precio regulado que factura Curenergia (comercializadora de ultimo
recurso). La potencia contratada (3,45 kW) NO influye en este precio horario de la
energia: solo afecta al termino fijo de potencia del recibo.
"""
from __future__ import annotations

import time
from dataclasses import dataclass
from datetime import date

import requests

# --- Umbrales de color, en euros/kWh (ajustables) ---
UMBRAL_VERDE = 0.15   # precio < 0,15  -> verde
UMBRAL_ROJO = 0.20    # precio > 0,20  -> rojo ; entre ambos -> amarillo

API_URL = "https://apidatos.ree.es/es/datos/mercados/precios-mercados-tiempo-real"
REINTENTOS = 3
ESPERA_REINTENTO_S = 10


@dataclass
class PrecioHora:
    hora: int          # 0..23
    precio_kwh: float   # euros/kWh

    @property
    def color(self) -> str:
        return color_por_precio(self.precio_kwh)


def color_por_precio(precio_kwh: float) -> str:
    """Devuelve 'verde' | 'amarillo' | 'rojo' segun el umbral de precio absoluto."""
    if precio_kwh < UMBRAL_VERDE:
        return "verde"
    if precio_kwh > UMBRAL_ROJO:
        return "rojo"
    return "amarillo"


def obtener_precios(dia: date | None = None) -> list[PrecioHora]:
    """24 PrecioHora en orden cronologico (00 -> 23) para `dia` (hoy si es None)."""
    dia = dia or date.today()
    params = {
        "start_date": f"{dia.isoformat()}T00:00",
        "end_date": f"{dia.isoformat()}T23:59",
        "time_trunc": "hour",
    }
    datos = _get_con_reintentos(params)

    serie = None
    for incluido in datos.get("included", []):
        if str(incluido.get("id")) == "1001" or incluido.get("type") == "PVPC":
            serie = incluido.get("attributes", {}).get("values")
            break
    if not serie:
        raise RuntimeError("La respuesta de REE no contiene la serie PVPC (id 1001).")

    precios: list[PrecioHora] = []
    for punto in serie:
        # datetime tipo "2026-09-01T00:00:00.000+02:00" -> tomamos la hora local
        hora = int(str(punto["datetime"])[11:13])
        precio_kwh = float(punto["value"]) / 1000.0  # euros/MWh -> euros/kWh
        precios.append(PrecioHora(hora=hora, precio_kwh=precio_kwh))

    precios.sort(key=lambda p: p.hora)
    if len(precios) != 24:
        raise RuntimeError(f"Se esperaban 24 horas y se recibieron {len(precios)}.")
    return precios


def resumen(precios: list[PrecioHora]) -> dict:
    """Minimo, maximo, media y las 3 horas mas baratas (en orden cronologico)."""
    minimo = min(precios, key=lambda p: p.precio_kwh)
    maximo = max(precios, key=lambda p: p.precio_kwh)
    media = sum(p.precio_kwh for p in precios) / len(precios)
    baratas = sorted(precios, key=lambda p: p.precio_kwh)[:3]
    return {
        "minimo": minimo,
        "maximo": maximo,
        "media": media,
        "horas_baratas": sorted(baratas, key=lambda p: p.hora),
    }


def _get_con_reintentos(params: dict) -> dict:
    ultimo_error: Exception | None = None
    for intento in range(1, REINTENTOS + 1):
        try:
            resp = requests.get(
                API_URL,
                params=params,
                headers={"Accept": "application/json", "Content-Type": "application/json"},
                timeout=25,
            )
            resp.raise_for_status()
            return resp.json()
        except Exception as exc:  # noqa: BLE001
            ultimo_error = exc
            print(f"[precios] intento {intento}/{REINTENTOS} fallido: {exc}")
            if intento < REINTENTOS:
                time.sleep(ESPERA_REINTENTO_S)
    raise RuntimeError(f"No se pudo obtener el precio de la luz: {ultimo_error}")


if __name__ == "__main__":
    for p in obtener_precios():
        print(f"{p.hora:02d}:00  {p.precio_kwh:.4f} EUR/kWh  [{p.color}]")
    print(resumen(obtener_precios()))
