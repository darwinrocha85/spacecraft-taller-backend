"""Catálogo de daños del taller — taxonomía cerrada, migrada literal desde
spacecraftSystem/.../model/DamageCategory.java (enum Java, leído directo del repo del usuario
el 2026-09-18). Es la misma fuente única de verdad que antes exponía Java en
GET /api/repairs/damage-catalog; ahora vive acá.

OJO: la cantidad de subtipos NO es uniforme (varía entre 2 y 4 según la categoría) — así está
en el Java real, no se fuerza a "3 por categoría".
"""
from __future__ import annotations

DAMAGE_CATALOG: dict[str, dict[str, object]] = {
    "CASCO_ESTRUCTURA": {
        "label": "Casco y Estructura",
        "subtypes": ["Abolladura", "Grieta", "Perforacion", "Dano termico"],
    },
    "PROPULSION": {
        "label": "Propulsion",
        "subtypes": [
            "Motor principal",
            "Propulsores RCS",
            "Sistema de combustible",
            "Sobrecalentamiento",
        ],
    },
    "ELECTRICO_AVIONICA": {
        "label": "Electrico y Avionica",
        "subtypes": [
            "Cableado",
            "Computadora de vuelo",
            "Sensores",
            "Falla de energia/baterias",
        ],
    },
    "SOPORTE_VITAL": {
        "label": "Soporte Vital",
        "subtypes": ["Oxigeno", "Presurizacion", "Control de temperatura"],
    },
    "COMUNICACIONES": {
        "label": "Comunicaciones",
        "subtypes": ["Antena/transmisor", "Sistema de navegacion"],
    },
}


def is_valid_damage(category: str, subtype: str) -> bool:
    entry = DAMAGE_CATALOG.get(category)
    if entry is None:
        return False
    return subtype in entry["subtypes"]
