#!/usr/bin/env python3
"""
Master Matrix Runner: run_matrix_checks.py
Exécute systématiquement la totalité des tests unitaires et de conformité
des 7 sous-skills et génère le rapport métrique de couverture.
"""

import os
import sys
import subprocess
import time
from pathlib import Path

FRAMEWORK_ROOT = Path(__file__).resolve().parent.parent

TEST_SUITES = [
    ("SK-01 Kernel Architecture", FRAMEWORK_ROOT / "sub-skills" / "SK-01-kernel-architecture" / "tests" / "test_kernel.py"),
    ("SK-02 Rules Engine", FRAMEWORK_ROOT / "sub-skills" / "SK-02-rules-engine" / "tests" / "test_rules.py"),
    ("SK-03 Skill Authoring", FRAMEWORK_ROOT / "sub-skills" / "SK-03-skill-authoring" / "tests" / "test_skill_scaffold.py"),
    ("SK-04 Plugin Packaging", FRAMEWORK_ROOT / "sub-skills" / "SK-04-plugin-packaging" / "tests" / "test_plugin_packager.py"),
    ("SK-05 Lifecycle Hooks", FRAMEWORK_ROOT / "sub-skills" / "SK-05-lifecycle-hooks" / "tests" / "test_hooks.py"),
    ("SK-06 MCP Integration", FRAMEWORK_ROOT / "sub-skills" / "SK-06-mcp-integration" / "tests" / "test_mcp.py"),
    ("SK-07 Deploy & Manifests", FRAMEWORK_ROOT / "sub-skills" / "SK-07-deployment-validation" / "tests" / "test_deploy.py"),
]

def run_suite(name: str, test_file: Path):
    if not test_file.is_file():
        return False, 0.0, f"Fichier de test introuvable : {test_file}"
        
    start = time.time()
    res = subprocess.run([sys.executable, str(test_file)], capture_output=True, text=True)
    duration = time.time() - start
    
    success = (res.returncode == 0)
    output = res.stderr if res.stderr else res.stdout
    return success, duration, output.strip()

def main():
    print("=" * 80)
    print("   EXÉCUTION DE LA MATRICE DE COUVERTURE & TESTS (AGY-CUSTOMIZATIONS)   ")
    print("=" * 80)
    
    total_suites = len(TEST_SUITES)
    passed_suites = 0
    total_time = 0.0
    
    for name, path in TEST_SUITES:
        success, duration, out = run_suite(name, path)
        total_time += duration
        status = "[PASS]" if success else "[FAIL]"
        print(f"{status} {name:28} | Durée: {duration:0.3f}s")
        if not success:
            print(f"       -> Erreur : {out}")
        else:
            passed_suites += 1

    print("-" * 80)
    coverage_pct = (passed_suites / total_suites) * 100.0
    print(f"RÉSULTAT GLOBAL : {passed_suites}/{total_suites} suites validées ({coverage_pct:0.1f}%)")
    print(f"TEMPS TOTAL D'EXÉCUTION : {total_time:0.3f}s")
    print("=" * 80)
    
    sys.exit(0 if passed_suites == total_suites else 1)

if __name__ == "__main__":
    main()
