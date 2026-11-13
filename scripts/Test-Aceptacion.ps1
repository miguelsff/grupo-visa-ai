$ErrorActionPreference = 'Stop'
$testProject = 'ocd-t4-' + [guid]::NewGuid().ToString('N')
$repository = Split-Path $PSScriptRoot -Parent
$listener = [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Loopback, 0)
$listener.Start()
$testPort = $listener.LocalEndpoint.Port
$listener.Stop()
$previousPort = $env:APP_PORT
$env:APP_PORT = "$testPort"
$temporaryEnv = Join-Path ([System.IO.Path]::GetTempPath()) ($testProject + '.env')
"APP_PORT=$testPort" | Set-Content -Encoding ascii $temporaryEnv
$composeArgs = @('compose', '--project-directory', $repository, '--env-file', $temporaryEnv,
    '-p', $testProject, '-f', (Join-Path $repository 'compose.yaml'),
    '-f', (Join-Path $PSScriptRoot 'acceptance/compose.yaml'))
function Invoke-AcceptanceDocker {
    param([string[]]$Arguments)
    & docker @composeArgs @Arguments
    if ($LASTEXITCODE -ne 0) { throw "Docker finalizo con codigo $LASTEXITCODE" }
}
Write-Host "Proyecto aislado: $testProject; puerto local: $testPort"
try {
    Invoke-AcceptanceDocker @('up', '--build', '-d', '--wait', 'app', 'qdrant', 'doubles', 'ingesta')
    $health = Invoke-RestMethod "http://127.0.0.1:$testPort/api/health"
    if ($health.status -ne 'ok' -or $health.sqlite -ne 'ok') { throw 'Salud local no disponible' }
    Invoke-AcceptanceDocker @('exec', '-T', 'ingesta', 'ocd-ingestar')
    Invoke-AcceptanceDocker @('exec', '-T', 'app', 'python', '/acceptance/probe.py', 'first')
    Invoke-AcceptanceDocker @('exec', '-T', 'ingesta', 'ocd-ingestar')
    Invoke-AcceptanceDocker @('exec', '-T', 'app', 'python', '/acceptance/probe.py', 'chat')
    & docker @composeArgs exec -T ingesta ocd-ingestar
    if ($LASTEXITCODE -ne 1) { throw 'La carga con Atlassian apagado debe fallar' }
    Invoke-AcceptanceDocker @('exec', '-T', 'app', 'python', '/acceptance/probe.py', 'offline')
    Invoke-AcceptanceDocker @('up', '-d', '--force-recreate', '--wait', 'app', 'qdrant')
    Invoke-AcceptanceDocker @('exec', '-T', 'app', 'python', '/acceptance/probe.py', 'resume')
    Invoke-AcceptanceDocker @('--profile', 'test', 'run', '--build', '--rm', 'tests')
    Invoke-AcceptanceDocker @('--profile', 'test', 'run', '--rm', 'tests', 'ruff', 'check', '--no-cache', 'app', 'tests')
    Write-Host 'Aceptacion T4 aprobada; servicios externos sinteticos, Qdrant real.'
}
finally {
    $env:APP_PORT = $previousPort
    if ($testProject -notmatch '^ocd-t4-[0-9a-f]{32}$') { throw 'Proyecto inseguro' }
    Invoke-AcceptanceDocker @('down', '--volumes', '--remove-orphans')
    Remove-Item -LiteralPath $temporaryEnv -ErrorAction SilentlyContinue
}
