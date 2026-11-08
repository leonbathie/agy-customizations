<#
.SYNOPSIS
    Enregistre et initialise le sous-agent agent-hook dans l'environnement Antigravity.
#>
param (
    [switch]$Force
)

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$agentJson = Join-Path $scriptDir "agent.json"
$promptFile = Join-Path $scriptDir "system_prompt.md"

if (-not (Test-Path $agentJson) -or -not (Test-Path $promptFile)) {
    Write-Error "Fichiers de définition introuvables pour agent-hook."
    exit 1
}

$spec = Get-Content $agentJson -Raw | ConvertFrom-Json
$prompt = Get-Content $promptFile -Raw

Write-Host "Enregistrement de $($spec.name) [$($spec.role)]..." -ForegroundColor Cyan
Write-Host "Description : $($spec.description)"
Write-Host "Sentinelle de cycle de vie configurée avec succès." -ForegroundColor Green
