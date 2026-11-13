# Gitflow automático

La creación y el merge de PR son permanentes y automáticos. `main` y `develop`
no exigen aprobación, checks ni resolución de conversaciones. El ruleset anterior
queda desactivado y auto-merge está habilitado. Las pruebas se ejecutan antes de
publicar en Railway, sin convertirse en requisitos para los merges.

| Rama publicada o actualizada | Destinos |
| --- | --- |
| `feature/*` | `develop` |
| `release/<version>` | Primero `main`; después `develop` |
| `hotfix/*` | Primero `main`; después `develop` y las `release/*` existentes |

El primer push de una release o un hotfix inicia la publicación de código. Prepara
la rama localmente antes de publicarla. Las versiones de release usan tres números,
por ejemplo `release/0.1.0`. El merge en `main` recibe la etiqueta `v0.1.0`.
Un hotfix incrementa el patch de la última etiqueta de versión y registra la versión
prevista en el PR para que los reintentos no calculen otra.

El controlador revisa todas las ramas candidatas en cada ejecución. Reutiliza los PR,
comprueba el SHA del origen y realiza commits de merge. Completa los retornos en
la misma ejecución: no depende de que los eventos del token inicien otro workflow.
Las ejecuciones están serializadas y pueden iniciarse desde Actions con
`workflow_dispatch`. Las ramas integradas por el controlador se eliminan después
de completar todos sus destinos. Las ramas que ya estaban integradas al activarlo
se conservan para revisar sus dependencias de despliegue antes de limpiarlas.

Si hay conflictos, un PR sigue en borrador, cambia el SHA o una etiqueta corresponde
a otra entrega, el workflow informa el error y conserva la rama. Resuelve el problema
y reejecuta **Gitflow automático**. No sobrescribe etiquetas ni fuerza el historial.

GitHub Actions utiliza `GITHUB_TOKEN` con `contents: write` y `pull-requests: write`
solo para este workflow. Los permisos generales permanecen en lectura. El ajuste
del repositorio que permite crear y aprobar PR está habilitado para permitir su
creación; el controlador no fabrica revisiones de aprobación.

Para comprobar el controlador con dobles REST, desde la raíz:

```powershell
node --test .github/scripts/gitflow.test.cjs
```

Railway conserva un SHA explícito de la entrega verificada. Los merges futuros
no sustituyen automáticamente ese despliegue sin una nueva verificación.
