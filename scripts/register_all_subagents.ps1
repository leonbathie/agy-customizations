<#
.SYNOPSIS
    Enregistre et vérifie l'ensemble des 7 sous-agents Antigravity (agent-kernel à agent-deployer).
#>
[CmdletBinding()]
param ()

$frameworkRoot = Split-Path -Parent $MyInvocation.MyCommand.Path | Split-Path -Parent
$agentsDir = Join-Path $frameworkRoot "agents"

$agents = @(
    "agent-kernel",
    "agent-rules",
    "agent-skill",
    "agent-plugin",
    "agent-hook",
    "agent-mcp",
    "agent-deployer"
)

Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host " INITIALISATION DU CONSORTIUM DES 7 SOUS-AGENTS ANTIGRAVITY     " -ForegroundColor Cyan
Write-Host "=================================================================" -ForegroundColor Cyan

$successCount = 0

foreach ($ag in $agents) {
    $agPath = Join-Path $agentsDir $ag
    $regScript = Join-Path $agPath "registrar.ps1"
    
    if (Test-Path $regScript) {
        Write-Host "[>] Exécution du registrar pour : $ag" -ForegroundColor Yellow
        & $regScript
        if ($LASTEXITCODE -eq 0 -or $? -eq $true) {
            $successCount++
        }
    } else {
        Write-Error "Registrar introuvable pour : $ag"
    }
}

Write-Host "-----------------------------------------------------------------" -ForegroundColor Cyan
Write-Host "Sous-agents opérationnels : $successCount / $($agents.Count)" -ForegroundColor Green
Write-Host "=================================================================" -ForegroundColor Cyan
