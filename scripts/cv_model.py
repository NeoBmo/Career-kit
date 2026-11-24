#!/usr/bin/env python3
"""Load and validate a person's cv.json without external dependencies.

Formato: specs/001-single-source/plan.md, sección «Formato de `cv.json`».
Un texto traducible es un objeto {"es": "...", "en": "..."}; una cadena simple
vale igual en todos los idiomas (útil para nombres propios como la organización).
Las listas traducibles (logros, keywords) siguen la misma regla.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class CvError(ValueError):
    """cv.json inválido. El mensaje lleva la ruta exacta de cada campo que falla."""

    def __init__(self, errors: list[str]) -> None:
        self.errors = errors
        super().__init__("cv.json inválido:\n" + "\n".join(f"  - {e}" for e in errors))


def load_cv(path: str | Path) -> dict[str, Any]:
    """Lee y valida un cv.json. Lanza CvError si algo no cumple el formato."""
    path = Path(path)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise CvError([f"{path}: JSON inválido en la línea {exc.lineno}: {exc.msg}"]) from exc
    validate(data)
    return data


def text(value: Any, lang: str) -> Any:
    """Devuelve el valor en `lang`: una cadena o lista simple vale para todos los idiomas."""
    return value[lang] if isinstance(value, dict) else value


def validate(data: Any) -> None:
    """Valida estructura y traducciones. Junta todos los errores en un solo CvError."""
    errors: list[str] = []
    _Validator(errors).check(data)
    if errors:
        raise CvError(errors)


class _Validator:
    def __init__(self, errors: list[str]) -> None:
        self.errors = errors

    def fail(self, path: str, message: str) -> None:
        self.errors.append(f"{path}: {message}")

    # ---------- Tipos básicos ----------

    def obj(self, data: Any, path: str) -> bool:
        if isinstance(data, dict):
            return True
        self.fail(path, "debe ser un objeto")
        return False

    def field(self, data: dict[str, Any], key: str, path: str) -> Any:
        """Devuelve data[key] o registra que falta. None indica ausencia."""
        if key not in data:
            self.fail(f"{path}.{key}" if path else key, "falta el campo")
            return None
        return data[key]

    def string(self, value: Any, path: str, nullable: bool = False) -> None:
        if value is None and nullable:
            return
        if not isinstance(value, str) or not value.strip():
            expected = "una cadena no vacía o null" if nullable else "una cadena no vacía"
            self.fail(path, f"debe ser {expected}")

    def string_list(self, value: Any, path: str) -> None:
        if not isinstance(value, list):
            self.fail(path, "debe ser una lista de cadenas")
            return
        for i, item in enumerate(value):
            self.string(item, f"{path}[{i}]")

    def translatable(self, value: Any, path: str, is_list: bool = False) -> None:
        """Cadena (o lista) simple, o un objeto {idioma: cadena o lista}."""
        check = self.string_list if is_list else self.string
        if isinstance(value, dict):
            if not value:
                self.fail(path, "el objeto traducible está vacío")
            for lang, item in value.items():
                check(item, f"{path}.{lang}")
        else:
            check(value, path)

    def required(self, data: dict[str, Any], path: str, spec: dict[str, str]) -> None:
        """Comprueba cada campo según su tipo: text, list, str, str?, tr, tr-list."""
        for key, kind in spec.items():
            if key not in data:
                self.fail(f"{path}.{key}" if path else key, "falta el campo")
                continue
            value, sub = data[key], f"{path}.{key}" if path else key
            if kind == "str":
                self.string(value, sub)
            elif kind == "str?":
                self.string(value, sub, nullable=True)
            elif kind == "tr":
                self.translatable(value, sub)
            elif kind == "tr-list":
                self.translatable(value, sub, is_list=True)

    def items(self, data: dict[str, Any], key: str, spec: dict[str, str], non_empty: bool = False) -> list[dict[str, Any]]:
        value = self.field(data, key, "")
        if value is None:
            return []
        if not isinstance(value, list) or (non_empty and not value):
            self.fail(key, "debe ser una lista no vacía" if non_empty else "debe ser una lista")
            return []
        valid = []
        for i, item in enumerate(value):
            if self.obj(item, f"{key}[{i}]"):
                self.required(item, f"{key}[{i}]", spec)
                valid.append(item)
        return valid

    # ---------- Documento ----------

    def check(self, data: Any) -> None:
        if not self.obj(data, "(raíz)"):
            return

        person = self.field(data, "person", "")
        if person is not None and self.obj(person, "person"):
            self.required(person, "person", {"name": "str", "location": "tr", "phone": "str", "email": "str"})

        more = self.field(data, "more", "")
        if more is not None and self.obj(more, "more"):
            self.required(more, "more", {"label": "tr", "url": "str"})

        profiles = self.field(data, "profiles", "")
        if profiles is not None and self.obj(profiles, "profiles"):
            if not profiles:
                self.fail("profiles", "debe tener al menos un perfil")
            for name, profile in profiles.items():
                if self.obj(profile, f"profiles.{name}"):
                    self.required(profile, f"profiles.{name}",
                                  {"title": "tr", "summary": "tr", "keywords": "tr-list"})

        # start admite null: hay experiencias con una sola fecha («2021»).
        experience = self.items(data, "experience", {"role": "tr", "organization": "tr", "start": "str?",
                                                     "end": "str?", "highlights": "tr-list"})
        for i, entry in enumerate(data["experience"] if experience else []):
            # Una experiencia sin logros dejaría un ckitems vacío, que no compila.
            highlights = entry.get("highlights") if isinstance(entry, dict) else None
            for lang, items in (highlights.items() if isinstance(highlights, dict) else [("", highlights)]):
                if isinstance(items, list) and not items:
                    path = f"experience[{i}].highlights" + (f".{lang}" if lang else "")
                    self.fail(path, "debe tener al menos un logro")

        self.items(data, "skills", {"label": "tr", "items": "tr"})
        self.items(data, "education", {"title": "tr", "organization": "tr", "start": "str?",
                                       "end": "str?", "details": "tr"})
        # Subtítulo opcional de una entrada («Proyecto X»), que va tras la organización.
        for section in ("experience", "education"):
            entries = data.get(section)
            for i, entry in enumerate(entries if isinstance(entries, list) else []):
                if isinstance(entry, dict) and "subtitle" in entry:
                    self.translatable(entry["subtitle"], f"{section}[{i}].subtitle")
        variants = self.items(data, "variants", {"lang": "str", "profile": "str"}, non_empty=True)

        # Sólo se comprueban las traducciones si la estructura es válida.
        if not self.errors:
            for i, variant in enumerate(variants):
                self.variant(data, i, variant)

    def variant(self, data: dict[str, Any], index: int, variant: dict[str, str]) -> None:
        lang, profile = variant["lang"], variant["profile"]
        label = f"variante {lang}/{profile}"
        if profile not in data["profiles"]:
            self.fail(f"variants[{index}].profile", f"el perfil '{profile}' no existe en profiles")
            return

        used: list[tuple[str, Any]] = [
            ("person.location", data["person"]["location"]),
            ("more.label", data["more"]["label"]),
        ]
        for key in ("title", "summary", "keywords"):
            used.append((f"profiles.{profile}.{key}", data["profiles"][profile][key]))
        for section, keys in (("experience", ("role", "organization", "highlights")),
                              ("skills", ("label", "items")),
                              ("education", ("title", "organization", "details"))):
            for i, entry in enumerate(data[section]):
                for key in keys:
                    used.append((f"{section}[{i}].{key}", entry[key]))
                if "subtitle" in entry:
                    used.append((f"{section}[{i}].subtitle", entry["subtitle"]))

        for path, value in used:
            if isinstance(value, dict) and lang not in value:
                self.fail(f"{path}.{lang}", f"falta el texto en '{lang}' ({label})")
