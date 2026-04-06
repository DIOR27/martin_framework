# Refactor Plan — Martin Framework (0.7.0)

Objetivo
- Hacer el framework limpio, simple y consistente. Que al generar un scaffold, el sitio resultante sea elegante con una sintaxis Python clara y coherente.
- Convertir el concepto de TODO en un widget, alineando la filosofía de que TODO es una representación visual dentro del sitio generado.

Principios
- Minimalismo: API y estilos simples, sin ruido.
- Consistencia: convención de nombres, estructuras y props a través de widgets.
- Elegancia: sintaxis clara, legible y expresiva en Python.
- Todo como widget: cada pieza de contenido o placeholder debe ser representable como un widget (o composición de widgets).

Plan de acción (fases)
1) Preparación y reglas de desarrollo
 - Crear rama de desarrollo (dev) y rama de lanzamiento (0.7.0) ya creada en este repo.
 - Documentar normas básicas de refactorización y pruebas mínimas esperadas.

2) Refactorización gradual (ambos planos, código y scaffolding)
 - Centralizar creación de estilo: usar un único camino para estilos (resolve_styles) y props universales.
 - Normalizar la API de Widgets: revisar el Widget base para asegurar consistencia de render y atributos.
 - Introducir TodoWidget básico: un widget que renderiza una etiqueta de TODO; habilitar ello para que el scaffold lo use cuando detecte TODOs.
 - Ajustar scaffold para producir sitios limpios: plantillas simples, markup claro, y defaults elegantes.

3) Consistencia y ergonomía
 - Extender tests existentes para cubrir la nueva semántica de TODO como widget y el rendering limpio.
 - Asegurar compatibilidad de API: cambios no rompibles para usuarios existentes cuando sea posible, con notas de migración.

4) Verificación y entrega
 - Ejecutar suite de tests y validaciones de scaffold.
 - Documentar cambios y ejemplos de uso en la docs.

Salida esperada al finalizar la fase 0.7.0
- Rama 0.7.0 con refactor inicial: core de widgets más limpio, TodoWidget disponible, scaffold más directo, y plan de migración/documentación.
