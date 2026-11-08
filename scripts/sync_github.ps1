<#
.SYNOPSIS
    Initialise Git et synchronise le framework agy-customizations avec GitHub via la CLI gh.
#>
[CmdletBinding()]
param (
    [string]$RepoName = "agy-customizations",
    [switch]$Private
)

$frameworkDir = Split-Path -Parent $MyInvocation.MyCommand.Path | Split-Path -Parent

Push-Location $frameworkDir

Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host " SYNCHRONISATION GITHUB (AGY-CUSTOMIZATIONS)                    " -ForegroundColor Cyan
Write-Host "=================================================================" -ForegroundColor Cyan

# 1. Vérifier si git est initialisé
if (-not (Test-Path ".git")) {
    Write-Host "[>] Initialisation du dépôt Git local..." -ForegroundColor Yellow
    git init -b main
    git config user.name "leonbathie"
    git config user.email "leonbathie@users.noreply.github.com"
}

# 2. Stage et Commit
Write-Host "[>] Ajout des fichiers au suivi Git..." -ForegroundColor Yellow
git add .
git commit -m "feat: Antigravity Customizations v2.0 Enterprise Framework release"

# 3. Vérifier gh CLI
Write-Host "[>] Vérification de l'authentification GitHub CLI..." -ForegroundColor Yellow
$authStatus = gh auth status 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Error "GitHub CLI n'est pas authentifié. Exécutez 'gh auth login'."
    Pop-Location
    exit 1
}

# 4. Vérifier si le repo existe déjà sur GitHub
$existing = gh repo view "leonbathie/$RepoName" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "[>] Création du dépôt distant leonbathie/$RepoName..." -ForegroundColor Green
    $visFlag = if ($Private) { "--private" } else { "--public" }
    gh repo create "leonbathie/$RepoName" $visFlag --source=. --remote=origin --push --description "Système maître et orchestrateur complet de personnalisation Google Antigravity (AGY v2.0 Enterprise)"
} else {
    Write-Host "[>] Le dépôt distant existe déjà. Poussée des mises à jour..." -ForegroundColor Green
    git push -u origin main
}

Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host "[✓] Dépôt synchronisé avec succès sur : https://github.com/leonbathie/$RepoName" -ForegroundColor Green
Write-Host "=================================================================" -ForegroundColor Cyan

Pop-Location
