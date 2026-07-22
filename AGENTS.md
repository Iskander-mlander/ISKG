# ISKG — Agent Workflow

Pasos obligatorios cada vez que se hacen cambios en el proyecto.

## 1. Verificación

Siempre antes de commitear:

```bash
python -m pytest tests/ -v           # 115 tests deben pasar
python -m ruff check iskg/ tests/    # lint limpio
python -m ruff format iskg/ tests/   # formatear
```

## 2. Pre-push checklist

- [ ] `git status` y `git diff` — revisar que no haya cambios espurios
- [ ] Versión consistente en:
  - `pyproject.toml` → `version`
  - `iskg/_version.py` → `VERSION`
  - `docs/conf.py` → `release`
  - `CHANGELOG.md` → título del entry
- [ ] `CHANGELOG.md` actualizado con los cambios
- [ ] `README.md` actualizado si cambiaron: número de widgets, temas, features, ejemplos, URLs de release
- [ ] Documentación (`docs/`, docstrings) actualizada si cambió API pública (nuevos params, clases, widgets)
- [ ] `ACTUAL.md` actualizado si se corrigieron bugs
- [ ] Tests pasan después de todos los cambios

## 3. Push

```bash
git add -A
git commit -m "tipo: mensaje descriptivo"
git push
```

## 4. Release (solo si version bump)

```bash
git tag vX.Y.Z
git push origin vX.Y.Z
```

Esto dispara `.github/workflows/release.yml`: build wheel, GitHub Release, PyPI publish.

## 5. Post-push

- [ ] Verificar que CI pasa en GitHub Actions (`.github/workflows/ci.yml`)
- [ ] Verificar que Docs build pasa (`.github/workflows/docs.yml`)
- [ ] Verificar que Release workflow se completó (si aplica)

## Recordatorios

- El workflow de Release se dispara con tags `v*`, no con pushes a `main`
- `sphinx-rtd-dark-mode` debe estar tanto en `pyproject.toml` como en `.github/workflows/docs.yml`
- `_vendor.py` y `widgets/_dialogs.py` tienen formato no estándar — si se tocan, formatear con `ruff`
- No hay servidor HTTP — todo es inline HTML/JS via pywebview
