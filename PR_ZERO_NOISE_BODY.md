Zero-noise Scaffold: clean-by-default scaffolding; TodoWidget explicit

Summary
- Enforce zero-noise scaffolding by default. Generated sites are clean, minimal, consistent.
- TodoWidget remains available as an explicit widget; scaffold does not inject noise.

What changed
- martin_framework/martin/scaffold.py: removed automatic noise blocks; scaffolding now clean by default.
- martin_framework/martin/widgets/todo.py: added TodoWidget; widget available in API.
- martin_framework/martin/widgets/__init__.py: export TodoWidget.
- scaffold_test_project: added as test scaffold with clean layout.
- Tools: added smoke test utilities (run_scaffold_smoke.py, verify_scaffold_clean.py, list_scaffold_files.py).
- REFRACTOR_PLAN.md: documentado para la versión 0.7.x.

Verification
- verify_scaffold_clean.py passes locally.
- scaffold_test_project generated; verificación manual de limpieza completada.

How to test locally
- Genera un scaffold vía render_new_project_files o run_scaffold_smoke.py.
- Abre main.py generado para confirmar una UI limpia y consistente.
- Opcional: inicia el servidor del scaffold para validar el render en http://localhost:3908.

Migration
- No hay cambios de API rompibles. Scaffold por defecto es limpio.
- TodoWidget permanece disponible como widget explícito.

Notas finales
- Este PR elimina ruido por defecto en scaffolds y documenta la nueva filosofía de diseño. TodoWidget se usa cuando el desarrollador explicitamente lo necesita.
