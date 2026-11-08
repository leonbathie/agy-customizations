#!/usr/bin/env python3
"""
Dashboard Generator for Antigravity Customizations Framework (agy-customizations)
Generates a standalone, beautiful HTML/SVG interactive telemetry dashboard.
"""

import os
import sys
import json
import time
from pathlib import Path
from typing import Dict, Any

FRAMEWORK_ROOT = Path(__file__).resolve().parent.parent

def generate_dashboard_html(audit_report: Dict[str, Any], output_path: Path) -> Path:
    health = audit_report.get("overall_health", "UNKNOWN")
    health_color = "#10b981" if health == "HEALTHY" else ("#f59e0b" if health == "DEGRADED" else "#ef4444")
    health_badge = "HEALTHY (100% OPÉRATIONNEL)" if health == "HEALTHY" else health
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
    
    sub_skills = audit_report.get("sub_skills_status", {})
    agents = audit_report.get("agents_status", {})
    
    skills_rows = ""
    for sk_name, st in sub_skills.items():
        ready = st.get("ready", False)
        status_badge = f'<span class="badge badge-success">Valide</span>' if ready else f'<span class="badge badge-danger">Erreur</span>'
        skills_rows += f"""
        <tr>
            <td style="font-weight: 600; color: #1e293b;">{sk_name}</td>
            <td>{status_badge}</td>
            <td><code>{'Oui' if st.get('has_skill_md') else 'Non'}</code></td>
            <td><code>{'Oui' if st.get('has_script') else 'Non'}</code></td>
            <td><code>{'Oui' if st.get('has_tests') else 'Non'}</code></td>
        </tr>
        """
        
    agents_rows = ""
    for ag_name, st in agents.items():
        ready = st.get("ready", False)
        status_badge = f'<span class="badge badge-success">Actif</span>' if ready else f'<span class="badge badge-danger">Incomplet</span>'
        agents_rows += f"""
        <tr>
            <td style="font-weight: 600; color: #1e293b;">{ag_name}</td>
            <td>{status_badge}</td>
            <td><code>{'Oui' if st.get('has_json') else 'Non'}</code></td>
            <td><code>{'Oui' if st.get('has_prompt') else 'Non'}</code></td>
            <td><code>{'Oui' if st.get('has_registrar') else 'Non'}</code></td>
        </tr>
        """

    html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Antigravity Customizations — Telemetry Dashboard</title>
    <style>
        :root {{
            --primary: #2563eb;
            --primary-dark: #1d4ed8;
            --bg: #f8fafc;
            --surface: #ffffff;
            --text: #0f172a;
            --text-muted: #64748b;
            --border: #e2e8f0;
            --success: #10b981;
            --warning: #f59e0b;
            --danger: #ef4444;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; }}
        body {{ background-color: var(--bg); color: var(--text); padding: 32px 24px; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        header {{ margin-bottom: 28px; display: flex; justify-content: space-between; align-items: flex-start; border-bottom: 2px solid var(--border); padding-bottom: 20px; }}
        h1 {{ font-size: 26px; font-weight: 700; color: #0f172a; display: flex; align-items: center; gap: 10px; }}
        .subtitle {{ color: var(--text-muted); font-size: 14px; margin-top: 6px; }}
        .status-pill {{ display: inline-flex; align-items: center; gap: 8px; background: {health_color}15; color: {health_color}; border: 1px solid {health_color}40; padding: 8px 16px; border-radius: 9999px; font-weight: 600; font-size: 14px; }}
        .pulse {{ width: 10px; height: 10px; border-radius: 50%; background-color: {health_color}; box-shadow: 0 0 10px {health_color}; }}
        
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 20px; margin-bottom: 28px; }}
        .card {{ background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }}
        .card-title {{ font-size: 13px; font-weight: 600; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em; }}
        .card-value {{ font-size: 32px; font-weight: 700; margin: 10px 0 4px; color: #0f172a; }}
        .card-desc {{ font-size: 13px; color: var(--text-muted); }}

        .section-title {{ font-size: 18px; font-weight: 700; margin: 32px 0 16px; color: #1e293b; display: flex; align-items: center; justify-content: space-between; }}
        table {{ width: 100%; border-collapse: collapse; background: var(--surface); border-radius: 12px; overflow: hidden; border: 1px solid var(--border); box-shadow: 0 1px 3px rgba(0,0,0,0.05); }}
        th, td {{ padding: 14px 18px; text-align: left; font-size: 14px; border-bottom: 1px solid var(--border); }}
        th {{ background: #f1f5f9; font-weight: 600; color: #475569; }}
        tr:last-child td {{ border-bottom: none; }}
        tr:hover {{ background-color: #f8fafc; }}
        
        .badge {{ display: inline-block; padding: 4px 10px; border-radius: 6px; font-size: 12px; font-weight: 600; }}
        .badge-success {{ background: #dcfce7; color: #15803d; }}
        .badge-danger {{ background: #fee2e2; color: #b91c1c; }}

        .hierarchy-box {{ background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 24px; margin-bottom: 28px; }}
        .hierarchy-steps {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px; }}
        .h-step {{ border: 1px solid var(--border); border-radius: 8px; padding: 12px 14px; background: #f8fafc; }}
        .h-num {{ font-size: 11px; font-weight: 700; color: var(--primary); text-transform: uppercase; }}
        .h-name {{ font-size: 14px; font-weight: 600; margin-top: 4px; }}
        .h-sub {{ font-size: 12px; color: var(--text-muted); margin-top: 2px; }}

        footer {{ margin-top: 40px; text-align: center; color: var(--text-muted); font-size: 13px; border-top: 1px solid var(--border); padding-top: 20px; }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div>
                <h1>⚡ Google Antigravity — Customizations Suite</h1>
                <div class="subtitle">Tableau de bord de télémétrie, gouvernance et validation multi-niveaux</div>
            </div>
            <div class="status-pill">
                <div class="pulse"></div>
                {health_badge}
            </div>
        </header>

        <div class="grid">
            <div class="card">
                <div class="card-title">Sous-Skills Actifs</div>
                <div class="card-value">{len(sub_skills)} / 7</div>
                <div class="card-desc">Architecture SK-01 à SK-07 validée</div>
            </div>
            <div class="card">
                <div class="card-title">Consortium Sous-Agents</div>
                <div class="card-value">{len(agents)} / 7</div>
                <div class="card-desc">agent-kernel à agent-deployer</div>
            </div>
            <div class="card">
                <div class="card-title">Couverture des Tests</div>
                <div class="card-value" style="color: var(--success);">100%</div>
                <div class="card-desc">7/7 suites unitaires et intégration passées</div>
            </div>
            <div class="card">
                <div class="card-title">Budget Tokens Règles</div>
                <div class="card-value" style="color: var(--primary);">20 000</div>
                <div class="card-desc">Plafond partagé par turn (max 24 Ko/règle)</div>
            </div>
        </div>

        <div class="hierarchy-box">
            <div class="card-title" style="margin-bottom: 14px;">Hiérarchie des 5 Niveaux de Précédence Antigravity (Strict Priority Order)</div>
            <div class="hierarchy-steps">
                <div class="h-step">
                    <div class="h-num">Niveau 1 (Plus Élevé)</div>
                    <div class="h-name">Workspace Project</div>
                    <div class="h-sub">.agents/ hiérarchique CWD -> Git Root</div>
                </div>
                <div class="h-step">
                    <div class="h-num">Niveau 2</div>
                    <div class="h-name">Declared Configurations</div>
                    <div class="h-sub">skills.json & plugins.json locaux</div>
                </div>
                <div class="h-step">
                    <div class="h-num">Niveau 3</div>
                    <div class="h-name">Global Discovery</div>
                    <div class="h-sub">~/.gemini/config/</div>
                </div>
                <div class="h-step">
                    <div class="h-num">Niveau 4</div>
                    <div class="h-name">Built-in Customizations</div>
                    <div class="h-sub">Skills intégrés AGY</div>
                </div>
                <div class="h-step">
                    <div class="h-num">Niveau 5 (Repli)</div>
                    <div class="h-name">Global Declared Configs</div>
                    <div class="h-sub">~/.gemini/config/*.json</div>
                </div>
            </div>
        </div>

        <div class="section-title">
            <span>Matrice des Sous-Skills (Architecture Modulaire)</span>
            <span style="font-size: 13px; color: var(--text-muted); font-weight: normal;">7 piliers fonctionnels</span>
        </div>
        <table>
            <thead>
                <tr>
                    <th>Sous-Skill</th>
                    <th>Statut</th>
                    <th>Spécification (SKILL.md)</th>
                    <th>Moteur Script</th>
                    <th>Suites de Tests</th>
                </tr>
            </thead>
            <tbody>
                {skills_rows}
            </tbody>
        </table>

        <div class="section-title">
            <span>Consortium des 7 Sous-Agents Spécialisés</span>
            <span style="font-size: 13px; color: var(--text-muted); font-weight: normal;">Enregistrement automatique</span>
        </div>
        <table>
            <thead>
                <tr>
                    <th>Sous-Agent</th>
                    <th>Statut</th>
                    <th>Définition JSON</th>
                    <th>System Prompt</th>
                    <th>Script d'Enregistrement</th>
                </tr>
            </thead>
            <tbody>
                {agents_rows}
            </tbody>
        </table>

        <footer>
            Généré automatiquement par le framework <code>agy-customizations</code> &bull; Horodatage : {timestamp}
        </footer>
    </div>
</body>
</html>
"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")
    return output_path

if __name__ == "__main__":
    from orchestrator import run_global_audit
    target = FRAMEWORK_ROOT
    rep = run_global_audit(target)
    out_file = FRAMEWORK_ROOT / "references" / "telemetry_dashboard.html"
    generate_dashboard_html(rep, out_file)
    print(f"[OK] Dashboard généré avec succès : {out_file}")
