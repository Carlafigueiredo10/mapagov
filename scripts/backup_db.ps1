<#
 Script de backup lógico do MapaGov
 Agende via Agendador de Tarefas (Executar se usuário logado ou não).
#>

param(
  [string]$Tag = '',
  [switch]$Pretty,
  [switch]$NoSnapshots,
  [switch]$NoChangelog
)

$ErrorActionPreference = 'Stop'
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Resolve-Path (Join-Path $ScriptDir '..')
$VenvPython = Join-Path $RepoRoot 'venv/Scripts/python.exe'
$ManagePy = Join-Path $RepoRoot 'manage.py'

if (-not (Test-Path $VenvPython)) {
  Write-Host 'ATENÇÃO: Python do venv não encontrado, usando python global.' -ForegroundColor Yellow
  $VenvPython = 'python'
}

$cmdArgs = @('manage.py','backup_db')
if ($Tag) { $cmdArgs += @('--tag', $Tag) }
if ($Pretty) { $cmdArgs += '--pretty' }
if ($NoSnapshots) { $cmdArgs += '--no-snapshots' }
if ($NoChangelog) { $cmdArgs += '--no-changelog' }

Push-Location $RepoRoot
try {
  & $VenvPython $cmdArgs
  if ($LASTEXITCODE -ne 0) { throw "Backup retornou código $LASTEXITCODE" }
  Write-Host 'Backup finalizado com sucesso.' -ForegroundColor Green
}
catch {
  Write-Host "Falha no backup: $_" -ForegroundColor Red
}
finally {
  Pop-Location
}
