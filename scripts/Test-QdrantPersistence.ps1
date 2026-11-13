# Ejecutar desde cualquier directorio. Solo elimina el proyecto temporal que crea.
$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$composeFile = Join-Path $repoRoot 'compose.yaml'
$probePath = Join-Path $PSScriptRoot 'qdrant_probe.py'
$testProject = 'ocd-t1-' + [guid]::NewGuid().ToString('N').Substring(0, 12)

function Invoke-Docker {
    param([string[]]$DockerArguments)
    & docker @DockerArguments
    if ($LASTEXITCODE -ne 0) { throw "Docker terminó con código $LASTEXITCODE" }
}

function Invoke-Probe {
    param([string]$Mode)
    Invoke-Docker -DockerArguments @(
        'run', '--rm', '--network', "${testProject}_default",
        '--mount', "type=bind,source=$probePath,target=/probe.py,readonly",
        'python:3.14-slim', 'python', '/probe.py', $Mode
    )
}

Write-Host "Proyecto aislado: $testProject"
try {
    Invoke-Docker -DockerArguments @('compose', '-f', $composeFile, '-p', $testProject, 'up', '-d', 'qdrant')
    # La imagen Qdrant no incluye curl; la sonda Python espera /readyz con plazo limitado.
    Invoke-Probe -Mode seed
    Invoke-Docker -DockerArguments @('compose', '-f', $composeFile, '-p', $testProject, 'up', '-d', '--force-recreate', 'qdrant')
    Invoke-Probe -Mode verify
}
finally {
    # Excepción deliberada: únicamente el proyecto aleatorio de esta prueba.
    Invoke-Docker -DockerArguments @('compose', '-f', $composeFile, '-p', $testProject, 'down', '--volumes')
}
