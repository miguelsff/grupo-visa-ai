$ErrorActionPreference = 'Stop'
$testProject = 'ocd-t2-' + [guid]::NewGuid().ToString('N')
$composeFile = Join-Path $PSScriptRoot 'compose.test.yaml'
function Invoke-TestDocker {
    param([string[]]$Arguments)
    & docker @Arguments
    if ($LASTEXITCODE -ne 0) { throw "Docker terminó con código $LASTEXITCODE" }
}
Write-Host "Proyecto aislado: $testProject"
try {
    Invoke-TestDocker @('compose', '-f', $composeFile, '-p', $testProject, 'up', '-d', 'qdrant')
    Invoke-TestDocker @('compose', '-f', $composeFile, '-p', $testProject, 'run', '--build',
        '--rm', 'tests')
    Invoke-TestDocker @('compose', '-f', $composeFile, '-p', $testProject, 'run', '--rm',
        'tests', 'ruff', 'check', '--no-cache', 'ocd_ingesta', 'tests')
}
finally {
    # El nombre aleatorio se crea aquí; solo su volumen temporal puede eliminarse.
    if ($testProject -notmatch '^ocd-t2-[0-9a-f]{32}$') { throw 'Proyecto inseguro' }
    Invoke-TestDocker @('compose', '-f', $composeFile, '-p', $testProject,
        'down', '--volumes', '--remove-orphans')
}
