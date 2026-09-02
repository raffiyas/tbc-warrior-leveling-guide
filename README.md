# TBC Warrior Fury Leveling Guide

Guía interactiva y no oficial para subir un Warrior Fury en **WoW: The Burning Crusade Anniversary**.

## Producción

https://tbc-warrior-leveling-guide.vercel.app/

GitHub sigue siendo la fuente del proyecto y Vercel despliega automáticamente cada cambio de `main`.

## V3.1 — My Warrior Companion

La guía principal ahora incluye un perfil local de **Xhena** y el comparador de armas integrado dentro de la misma experiencia.

- Perfil My Warrior con nombre, nivel, spec, región y realm.
- Nivel sincronizado con el selector de talentos.
- Próximo hito y estado de Dual Wield calculados desde el nivel actual.
- Arma registrada reutilizada desde los datos guardados por el comparador.
- Comparador V3 integrado en la guía mediante `compare.html`, con opción de abrirlo en pantalla completa.
- Datos persistentes mediante `localStorage`.
- Botón de búsqueda en la nueva WoW Armory Classic.

## Backend Vercel

El proyecto ya tiene su primera Vercel Function:

`/api/health`

Actualmente solo verifica que el backend esté operativo. La siguiente fase será preparar una ruta segura para Blizzard/Armory sin exponer credenciales en el frontend.

## Qué incluye

- Talentos nivel por nivel de 10 a 70 con selector interactivo.
- Hitos importantes: Defensive Stance, Overpower, Dual Wield, Berserker Stance, Sweeping Strikes, Whirlwind, Bloodthirst, Rampage, Victory Rush y Spell Reflection.
- Comparación práctica **2H vs Dual Wield** desde nivel 20.
- Enfoque Fury con flexibilidad para tankear dungeons.
- Rotación práctica y prioridades del trainer.
- Addons útiles para leveling, tanking, economía y dungeons.
- Macros de Warrior con botón Copiar.
- Comparador de armas con weapon DPS, daño, velocidad, STR/AGI/STA, costo y valor estimado.
- Wowhead Powered Tooltips en el módulo de comparación.

## Arquitectura

- **GitHub**: código y versionado.
- **Vercel**: producción, previews y funciones backend.
- **Wowhead**: tooltips y referencias de ítems.
- **Blizzard / WoW Armory**: integración prevista para la siguiente fase.

## Fuentes principales

- Icy Veins — Fury Warrior Leveling Guide 1–70
- Icy Veins — Warrior Leveling Guide 1–70
- Icy Veins — Warrior Macros / Addons
- Wowhead — TBC Classic Fury Warrior Leveling
- Wowhead — Powered Tooltips
- Warcraft Tavern — Warrior Leveling / Addons & Macros

> Proyecto personal y no oficial. World of Warcraft y sus marcas pertenecen a Blizzard Entertainment.
