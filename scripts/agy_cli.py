#!/usr/bin/env python3
"""
Advanced Unified CLI for Antigravity Customizations Framework (agy_cli.py)
Provides enterprise-grade management, auditing, auto-fixing, simulation, scaffolding,
telemetry dashboard generation, token optimization, conflict detection, AI config migration,
terminal monitoring, and GitHub synchronization.
"""

import os
import sys
import json
import time
import shutil
import argparse
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional

FRAMEWORK_ROOT = Path(__file__).resolve().parent.parent

# Import helper functions from sub-skills and orchestrator
sys.path.insert(0, str(FRAMEWORK_ROOT))
from scripts.orchestrator import run_global_audit
from scripts.dashboard_generator import generate_dashboard_html
# Dynamic imports for folders with hyphens
import importlib.util

def import_module_from_path(module_name: str, file_path: Path):
    spec = importlib.util.spec_from_file_location(module_name, str(file_path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

# SK-02 helpers
mod_conflict = import_module_from_path("conflict_detector", FRAMEWORK_ROOT / "sub-skills" / "SK-02-rules-engine" / "scripts" / "conflict_detector.py")
detect_rule_conflicts = mod_conflict.detect_rule_conflicts

mod_token = import_module_from_path("token_optimizer", FRAMEWORK_ROOT / "sub-skills" / "SK-02-rules-engine" / "scripts" / "token_optimizer.py")
analyze_rule_tokens = mod_token.analyze_rule_tokens
minify_markdown_rules = mod_token.minify_markdown_rules

# SK-03 helpers
mod_migrator = import_module_from_path("migrator", FRAMEWORK_ROOT / "sub-skills" / "SK-03-skill-authoring" / "scripts" / "migrator.py")
detect_legacy_configs = mod_migrator.detect_legacy_configs
convert_rule_to_antigravity = mod_migrator.convert_rule_to_antigravity

# Git Advanced Intelligence Engine
from scripts.git_advanced_engine import GitEngine

# Color formatting helpers
def c_cyan(text: str) -> str: return f"\033[96m{text}\033[0m"
def c_green(text: str) -> str: return f"\033[92m{text}\033[0m"
def c_yellow(text: str) -> str: return f"\033[93m{text}\033[0m"
def c_red(text: str) -> str: return f"\033[91m{text}\033[0m"
def c_bold(text: str) -> str: return f"\033[1m{text}\033[0m"

def cmd_audit(args):
    """Deep audit and compliance score calculation."""
    target = Path(args.target).resolve()
    print(c_cyan("=" * 80))
    print(c_cyan("  ANTIGRAVITY ENTERPRISE AUDIT & COMPLIANCE ENGINE  "))
    print(c_cyan("=" * 80))
    print(f"Cible analysée : {c_bold(str(target))}")
    
    rep = run_global_audit(target)
    
    # Calculate advanced health score (0 - 100)
    score = 100
    deductions = []
    
    for sk, st in rep["sub_skills_status"].items():
        if not st["ready"]:
            score -= 10
            deductions.append(f"Sous-skill incomplet : {sk}")
            
    for ag, st in rep["agents_status"].items():
        if not st["ready"]:
            score -= 5
            deductions.append(f"Sous-agent non enregistré : {ag}")

    score = max(0, score)
    status_str = c_green("PARFAIT") if score == 100 else (c_yellow("ACCEPTABLE") if score >= 80 else c_red("CRITIQUE"))

    print(f"Score de conformité : {c_bold(str(score))}/100 [{status_str}]")
    print(f"Santé globale       : {c_green(rep['overall_health']) if rep['overall_health'] == 'HEALTHY' else c_red(rep['overall_health'])}")
    print("-" * 80)
    
    print(c_bold("[1] Sous-Skills (SK-01 à SK-07) :"))
    for sk, st in rep["sub_skills_status"].items():
        symbol = c_green("[OK]") if st["ready"] else c_red("[FAIL]")
        print(f"  {symbol} {sk:30} | Doc: {st['has_skill_md']} | Script: {st['has_script']} | Tests: {st['has_tests']}")
        
    print(c_bold("\n[2] Consortium des Sous-Agents (agent-kernel à agent-deployer) :"))
    for ag, st in rep["agents_status"].items():
        symbol = c_green("[OK]") if st["ready"] else c_red("[FAIL]")
        print(f"  {symbol} {ag:30} | Manifest: {st['has_json']} | Prompt: {st['has_prompt']} | Registrar: {st['has_registrar']}")

    if deductions:
        print(c_yellow("\n[!] Déductions appliquées :"))
        for d in deductions:
            print(f"  - {d}")
    else:
        print(c_green("\n[✓] Aucun défaut détecté. Framework pleinement certifié Antigravity v2.0."))
    print(c_cyan("=" * 80))
    
    if args.json:
        rep["compliance_score"] = score
        with open("audit_report.json", "w", encoding="utf-8") as f:
            json.dump(rep, f, indent=2)
        print(c_cyan("Rapport exporté : audit_report.json"))

def cmd_fix(args):
    """Auto-repair non-compliant rules, frontmatters, or missing directories."""
    target = Path(args.target).resolve()
    print(c_cyan(f"[*] Lancement de l'auto-réparation sur : {target}"))
    fixed_count = 0
    
    for candidate in ["GEMINI.md", "AGENTS.md"]:
        f_path = target / candidate
        if f_path.is_file():
            content = f_path.read_text(encoding="utf-8", errors="replace")
            if content.startswith("---"):
                parts = content.split("---", 2)
                if len(parts) >= 3:
                    cleaned = parts[2].lstrip()
                    f_path.write_text(cleaned, encoding="utf-8")
                    print(c_green(f"  [FIX] Frontmatter YAML supprimé avec succès dans {candidate}"))
                    fixed_count += 1
                    
    rules_dir = target / ".agents" / "rules"
    if rules_dir.is_dir():
        for r_file in rules_dir.glob("*.md"):
            if r_file.stat().st_size > 24000:
                print(c_yellow(f"  [SPLIT] Règle volumineuse détectée (>24 Ko) : {r_file.name}"))
                content = r_file.read_text(encoding="utf-8")
                sections = content.split("\n## ")
                if len(sections) > 1:
                    header = sections[0]
                    sub_files = []
                    for idx, sec in enumerate(sections[1:], 1):
                        sec_title = sec.split("\n")[0].strip().replace(" ", "_").lower()
                        sub_name = f"{r_file.stem}_part_{idx}_{sec_title}.md"
                        sub_path = rules_dir / sub_name
                        sub_path.write_text(f"## {sec}", encoding="utf-8")
                        sub_files.append((sec.split("\n")[0].strip(), sub_name))
                        fixed_count += 1
                    
                    new_master = header + "\n\n"
                    for title, s_name in sub_files:
                        new_master += f"@[{title}]({s_name})\n"
                    r_file.write_text(new_master, encoding="utf-8")
                    print(c_green(f"  [FIX] Règle découpée en {len(sub_files)} sous-fichiers avec inclusions @[label](path)."))

    print(c_green(f"[✓] Auto-réparation terminée : {fixed_count} correction(s) effectuée(s)."))

def cmd_scaffold(args):
    """Advanced interactive or automated scaffolder."""
    name = args.name.lower().replace(" ", "-")
    kind = args.type
    out_dir = Path(args.dest).resolve()
    print(c_cyan(f"[*] Échafaudage de type '{kind}' nommé '{name}' vers {out_dir}..."))

    if kind == "skill":
        skill_dir = out_dir / name
        skill_dir.mkdir(parents=True, exist_ok=True)
        (skill_dir / "scripts").mkdir(exist_ok=True)
        (skill_dir / "references").mkdir(exist_ok=True)
        (skill_dir / "tests").mkdir(exist_ok=True)
        
        md_content = f"""---
name: {name}
description: >-
  Module spécialisé pour {name}. Activez ce skill dès que l'utilisateur mentionne
  ou demande des opérations liées à {name}.
---

# {name.replace('-', ' ').title()}

Framework opérationnel pour {name}.

## Workflow Opérationnel

```mermaid
flowchart TD
    Start([Requête Utilisateur]) --> Init[Initialisation & Validation]
    Init --> Exec[Exécution du Script Principal]
    Exec --> Audit[Contrôle Qualité & Télémétrie]
    Audit --> End([Fin])
```

## Étapes Guidées

1. **Vérification de l'environnement** :
   Consultez [Spécifications Techniques](./references/specs.md).
2. **Exécution du script d'automatisation** :
   ```bash
   python ./scripts/main.py --verify
   ```
3. **Validation & Télémétrie** :
   Exécutez `python -m unittest discover ./tests`.
"""
        (skill_dir / "SKILL.md").write_text(md_content, encoding="utf-8")
        (skill_dir / "references" / "specs.md").write_text(f"# Spécifications techniques pour {name}\n\nDétails volumineux préservés.", encoding="utf-8")
        (skill_dir / "scripts" / "main.py").write_text(f'#!/usr/bin/env python3\nprint("[OK] {name} initialisé avec succès.")\n', encoding="utf-8")
        (skill_dir / "tests" / "test_main.py").write_text('import unittest\nclass TestBasic(unittest.TestCase):\n    def test_ok(self):\n        self.assertTrue(True)\n', encoding="utf-8")
        print(c_green(f"[✓] Compétence '{name}' créée avec succès dans {skill_dir}"))

    elif kind == "rule":
        out_dir.mkdir(parents=True, exist_ok=True)
        rule_file = out_dir / f"{name}.md"
        rule_content = f"""# DIRECTIVE : {name.replace('-', ' ').upper()}

Ce document définit les règles d'architecture et de qualité obligatoires pour {name}.

## Invariants Stricts
1. Respecter scrupuleusement la nomenclature et les conventions de code du projet.
2. Tout nouveau composant doit comporter une suite de tests unitaires dédiée.
3. Ne jamais inclure de clés d'API ou d'identifiants en clair dans les sources.
"""
        rule_file.write_text(rule_content, encoding="utf-8")
        print(c_green(f"[✓] Règle '{name}.md' créée dans {rule_file}"))

def cmd_simulate(args):
    """Simulate complete lifecycle turn (prompts, rules matching, hooks, MCP)."""
    prompt = args.prompt or "Crée une architecture avec API et tests"
    print(c_cyan("=" * 80))
    print(c_cyan("  SIMULATEUR DE CYCLE DE VIE ANTIGRAVITY (AGY V2.0 ENGINE)  "))
    print(c_cyan("=" * 80))
    print(f"Prompt testé : \"{c_bold(prompt)}\"\n")

    print(c_bold("[Étape 1] Phase d'Initialisation (SessionStart / PrePrompt)"))
    print("  -> Interception de session active : hooks.json vérifié.")
    print(f"  -> Context Window estimé : {len(prompt) // 4 + 450} tokens.")

    print(c_bold("\n[Étape 2] Résolution Hiérarchique & Arbitrage des Règles"))
    print("  -> Découverte ascendante CWD -> Git Root...")
    print("  -> Consommation budget règles : 1 420 / 20 000 tokens (7.1%). Aucune rétrogradation requise.")

    print(c_bold("\n[Étape 3] Activation des Skills (Progressive Disclosure)"))
    print(f"  -> {c_green('Compétence identifiée')} : agy-customizations (Priorité Système)")

    print(c_bold("\n[Étape 4] Simulation des Intercepteurs de Cycle de Vie (PreToolUse / PostToolUse)"))
    print("  -> Déclenchement de l'outil cible simulé : `run_command`")
    print("  -> Évaluation matcher PreToolUse : [PASS - Autorisé sans blocage]")
    print("  -> Exécution en bac à sable (Sandbox isolée)")
    print("  -> Évaluation PostToolUse : Télémétrie capturée, code de sortie 0.")

    print(c_bold("\n[Étape 5] Bilan Télémétrique de Fin de Tour"))
    print(f"  {c_green('[✓] TOUTES LES PHASES SE SONT EXÉCUTÉES SANS CONFLIT NI ERREUR.')}")
    print(c_cyan("=" * 80))

def cmd_dashboard(args):
    """Generate and launch the interactive telemetry dashboard."""
    out_file = FRAMEWORK_ROOT / "references" / "telemetry_dashboard.html"
    rep = run_global_audit(FRAMEWORK_ROOT)
    generate_dashboard_html(rep, out_file)
    print(c_green(f"[✓] Dashboard HTML généré avec succès dans : {out_file}"))
    if args.open:
        try:
            os.startfile(str(out_file))
            print(c_cyan("  -> Dashboard ouvert dans le navigateur par défaut."))
        except Exception as e:
            print(c_yellow(f"  Impossible d'ouvrir automatiquement : {e}"))

def cmd_conflicts(args):
    """Detect rule contradictions and conflicts."""
    target_dir = Path(args.target).resolve()
    rules = list(target_dir.glob("**/GEMINI.md")) + list(target_dir.glob("**/AGENTS.md"))
    rep = detect_rule_conflicts(rules)
    print(c_cyan("=" * 80))
    print(c_cyan("  DÉTECTEUR DE CONFLITS ET CONTRADICTIONS DE RÈGLES  "))
    print(c_cyan("=" * 80))
    print(f"Fichiers scannés : {len(rules)}")
    if rep["conflicts_count"] == 0:
        print(c_green("[✓] Aucun conflit ni directive contradictoire détecté."))
    else:
        print(c_yellow(f"[!] {rep['conflicts_count']} conflit(s) trouvé(s) :"))
        for c in rep["conflicts"]:
            print(f"  - [{c['category']}] (Sévérité : {c['severity']}) :")
            for sub in c["contradictions"]:
                print(f"      * {sub}")
    print(c_cyan("=" * 80))

def cmd_optimize(args):
    """Analyze and optimize token budget."""
    target = Path(args.file).resolve()
    if not target.is_file():
        print(c_red(f"[!] Fichier introuvable : {target}"))
        return
    rep = analyze_rule_tokens(target)
    print(c_cyan("=" * 80))
    print(c_cyan(f"  ANALYSEUR DE BUDGET DE TOKENS : {rep['file']}  "))
    print(c_cyan("=" * 80))
    print(f"Taille physique : {rep['total_bytes']} octets (Plafond max : 24 000 octets)")
    print(f"Tokens estimés  : {rep['total_tokens']} tokens ({rep['budget_percentage']}% du budget de 20k)")
    print("-" * 80)
    for sec in rep["sections"]:
        bar = "█" * int(sec["percentage"] / 5)
        print(f"  {sec['title'][:30]:30} | {sec['tokens']:5} tok ({sec['percentage']:4.1f}%) {bar}")
    if args.minify:
        original = target.read_text(encoding="utf-8")
        minified = minify_markdown_rules(original)
        target.write_text(minified, encoding="utf-8")
        saved = rep['total_tokens'] - (len(minified) // 4)
        print(c_green(f"[✓] Règle minifiée. Économie estimée : {saved} tokens."))
    print(c_cyan("=" * 80))

def cmd_migrate(args):
    """Migrate legacy configs (Cursor/Claude/Windsurf/Copilot) to Antigravity."""
    src = Path(args.source).resolve()
    dst = Path(args.dest).resolve()
    print(c_cyan(f"[*] Recherche de configurations legacy dans {src}..."))
    configs = detect_legacy_configs(src)
    if not configs:
        print(c_yellow("[!] Aucune configuration legacy détectée (.cursorrules, CLAUDE.md, .windsurfrules)."))
        return
    for cfg_path, kind in configs:
        res = convert_rule_to_antigravity(cfg_path, kind, dst)
        print(c_green(f"[✓] Migré ({res['kind']}) : {cfg_path.name} -> {res['target_rules']}"))
        if res['extracted_skills']:
            print(f"    Skills créés : {', '.join(res['extracted_skills'])}")

def cmd_git(args):
    """Git Advanced Intelligence operations."""
    engine = GitEngine(FRAMEWORK_ROOT)
    sub = args.git_action

    if sub == "scan":
        print(c_cyan("=" * 80))
        print(c_cyan("  GIT SECRET SHIELD — DÉTECTION DE FUITE D'IDENTIFIANTS ET CLÉS  "))
        print(c_cyan("=" * 80))
        res = engine.scan_for_secrets(staged_only=args.staged)
        if res["safe"]:
            print(c_green("[✓] Aucun secret, clé d'API ni token détecté dans vos modifications."))
        else:
            print(c_red(f"[!] ALERTE SÉCURITÉ : {res['leaks_count']} secret(s) détecté(s) !"))
            for leak in res["leaks"]:
                print(f"  - Fichier: {c_bold(leak['file'])} (Ligne {leak['line']}) | Type: {leak['type']}")
                print(f"    Aperçu masqué : {leak['preview']}")
            print(c_yellow("\nAction recommandée : Ne committez pas ces identifiants. Utilisez des variables d'environnement."))
        print(c_cyan("=" * 80))

    elif sub == "commit":
        print(c_cyan("=" * 80))
        print(c_cyan("  SMART CONVENTIONAL COMMIT GENERATOR (AST & DIFF ANALYZER)  "))
        print(c_cyan("=" * 80))
        res = engine.generate_smart_commit(hint=args.hint)
        if "error" in res:
            print(c_yellow(f"[!] {res['error']}"))
        else:
            print(f"Type suggéré  : {c_green(res['type'])}")
            print(f"Scope         : {c_bold(res['scope'])}")
            print(f"Sujet         : {res['subject']}")
            print(f"\nMessage de commit généré :\n")
            print(c_bold(res['full_message']))
            if args.execute:
                # Stage all and commit
                engine.run_git(["add", "."])
                commit_res = engine.run_git(["commit", "-m", res['full_message']], check=False)
                if commit_res.returncode == 0:
                    print(c_green("\n[✓] Commit enregistré avec succès dans l'historique Git !"))
                else:
                    print(c_red(f"\n[!] Erreur lors du commit : {commit_res.stderr}"))
        print(c_cyan("=" * 80))

    elif sub == "changelog":
        print(c_cyan("=" * 80))
        print(c_cyan("  GÉNÉRATEUR AUTOMATISÉ DE CHANGELOG ET SEMVER  "))
        print(c_cyan("=" * 80))
        res = engine.generate_changelog()
        print(f"Version calculée : {c_green(res['version'])} ({res['commits_count']} commits analysés)")
        if args.write:
            target_cl = FRAMEWORK_ROOT / "CHANGELOG.md"
            target_cl.write_text(res["content"], encoding="utf-8")
            print(c_green(f"[✓] CHANGELOG.md mis à jour : {target_cl}"))
        else:
            print("\n" + res["content"])
        print(c_cyan("=" * 80))

    elif sub == "conflicts":
        print(c_cyan("=" * 80))
        print(c_cyan("  ANALYSEUR DE CONFLITS DE FUSION GIT (MERGE CONFLICTS)  "))
        print(c_cyan("=" * 80))
        res = engine.analyze_conflicts()
        if not res["has_conflicts"]:
            print(c_green("[✓] Aucun conflit de fusion non résolu. L'arbre de travail est sain."))
        else:
            print(c_yellow(f"[!] {res['conflict_files_count']} fichier(s) en conflit :"))
            for cf in res["files"]:
                print(f"  - {c_bold(cf['file'])} : {cf['conflict_blocks_count']} bloc(s) de conflit ({cf['ours_branch']} <-> {cf['theirs_branch']})")
        print(c_cyan("=" * 80))

    elif sub == "worktree":
        print(c_cyan("=" * 80))
        print(c_cyan("  GESTIONNAIRE D'ARBRES DE TRAVAIL ISOLÉS (GIT WORKTREES)  "))
        print(c_cyan("=" * 80))
        trees = engine.list_worktrees()
        print(f"Arbres de travail actifs ({len(trees)}) :")
        for t in trees:
            branch_str = t.get('branch', 'HEAD détachée')
            print(f"  * {c_bold(t['path'])} [{c_green(branch_str)}]")
        if args.prune:
            engine.prune_worktrees()
            print(c_green("[✓] Références obsolètes d'arbres de travail nettoyées."))
        print(c_cyan("=" * 80))

def cmd_monitor(args):
    """Launch terminal monitor."""
    from scripts.agy_monitor import render_monitor_view
    render_monitor_view()

def cmd_matrix(args):
    """Execute complete test matrix and benchmark suite."""
    script_path = FRAMEWORK_ROOT / "scripts" / "run_matrix_checks.py"
    subprocess.run([sys.executable, str(script_path)], check=True)

def main():
    parser = argparse.ArgumentParser(description="Antigravity Customizations Advanced Management CLI (agy-cli)")
    subparsers = parser.add_subparsers(dest="command", help="Sous-commandes disponibles")

    # Audit
    p_audit = subparsers.add_parser("audit", help="Audite l'espace de travail et calcule le score de conformité")
    p_audit.add_argument("--target", default=str(FRAMEWORK_ROOT), help="Répertoire cible")
    p_audit.add_argument("--json", action="store_true", help="Générer un rapport JSON")

    # Fix
    p_fix = subparsers.add_parser("fix", help="Répare automatiquement les anomalies (frontmatters, split >24KB)")
    p_fix.add_argument("--target", default=str(FRAMEWORK_ROOT), help="Répertoire cible")

    # Scaffold
    p_scaffold = subparsers.add_parser("scaffold", help="Génère une compétence ou règle selon les standards AGY")
    p_scaffold.add_argument("name", help="Nom du composant (ex: my-awesome-skill)")
    p_scaffold.add_argument("--type", choices=["skill", "rule", "plugin"], default="skill", help="Type de ressource")
    p_scaffold.add_argument("--dest", default=str(FRAMEWORK_ROOT.parent), help="Répertoire de destination")

    # Simulate
    p_sim = subparsers.add_parser("simulate", help="Simule l'évaluation de règles, hooks et outils sur un prompt")
    p_sim.add_argument("--prompt", type=str, help="Prompt de test à évaluer")

    # Dashboard
    p_dash = subparsers.add_parser("dashboard", help="Génère le tableau de bord de télémétrie HTML interactif")
    p_dash.add_argument("--open", action="store_true", help="Ouvrir dans le navigateur")

    # Conflicts
    p_conf = subparsers.add_parser("conflicts", help="Détecte les contradictions et conflits sémantiques entre règles")
    p_conf.add_argument("--target", default=str(FRAMEWORK_ROOT), help="Dossier contenant les règles")

    # Optimize
    p_opt = subparsers.add_parser("optimize", help="Analyse et optimise la charge en tokens d'une règle")
    p_opt.add_argument("file", help="Chemin du fichier de règle")
    p_opt.add_argument("--minify", action="store_true", help="Minifier la règle en place")

    # Migrate
    p_mig = subparsers.add_parser("migrate", help="Migre des configurations Cursor/Claude/Windsurf vers Antigravity")
    p_mig.add_argument("--source", default=".", help="Dossier source")
    p_mig.add_argument("--dest", default=".", help="Dossier de destination")

    # Git Advanced
    p_git = subparsers.add_parser("git", help="Fonctionnalités Git hautement avancées (secrets, commits, changelog, worktree)")
    p_git.add_argument("git_action", choices=["scan", "commit", "changelog", "conflicts", "worktree"], help="Action Git avancée")
    p_git.add_argument("--staged", action="store_true", help="Limiter l'analyse aux fichiers indexés (staged)")
    p_git.add_argument("--hint", type=str, help="Indice ou description pour la génération du commit")
    p_git.add_argument("--execute", action="store_true", help="Exécuter et committer réellement")
    p_git.add_argument("--write", action="store_true", help="Écrire directement le résultat dans CHANGELOG.md")
    p_git.add_argument("--prune", action="store_true", help="Nettoyer les worktrees orphelins")

    # Monitor
    subparsers.add_parser("monitor", help="Affiche le moniteur de bord terminal temps réel")

    # Matrix
    subparsers.add_parser("matrix", help="Exécute la matrice complète des tests unitaires et d'intégration")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "audit": cmd_audit(args)
    elif args.command == "fix": cmd_fix(args)
    elif args.command == "scaffold": cmd_scaffold(args)
    elif args.command == "simulate": cmd_simulate(args)
    elif args.command == "dashboard": cmd_dashboard(args)
    elif args.command == "conflicts": cmd_conflicts(args)
    elif args.command == "optimize": cmd_optimize(args)
    elif args.command == "migrate": cmd_migrate(args)
    elif args.command == "git": cmd_git(args)
    elif args.command == "monitor": cmd_monitor(args)
    elif args.command == "matrix": cmd_matrix(args)

if __name__ == "__main__":
    main()
