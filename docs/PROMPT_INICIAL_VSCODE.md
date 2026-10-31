# Prompt para empezar en Visual Studio Code

Copia y pega esto en tu primera conversación con Claude dentro de VS Code (abre la carpeta del repo para que lea `CLAUDE.md`):

---
Lee `CLAUDE.md` y `docs/ROADMAP.md`. Vamos a trabajar en este proyecto durante meses; las reglas de CLAUDE.md son obligatorias (sin APIs externas de IA, seguridad antes del modelo, privacidad).

Mi equipo: RAM = ___ GB, GPU = ___ (o "sin GPU"). Primer usuario objetivo: ___.

Empieza así:
1. Corre `pytest` en `backend/` y confirma que todo pasa.
2. Haz la Fase 1 del roadmap en ramas pequeñas: primero Dockerfile + docker-compose con PostgreSQL/pgvector, luego Alembic, luego CI.
3. Propón (sin implementar aún) 2–3 modelos locales candidatos para mi hardware, con licencia y cómo probaríamos su español.
Antes de cada cambio grande, explícame el plan en pocas líneas.
---
