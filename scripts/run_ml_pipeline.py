"""Run reproducible machine learning evaluation and update benchmark artifacts.

Usage:
    python scripts/run_ml_pipeline.py
"""
import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parents[1] / "backend"
sys.path.insert(0, str(backend_dir))

from app.ml.evaluate import run_full_ml_benchmark, REPORT_FILE


def main():
    print("=================================================================")
    print(" BIOPRESS Analytics — Machine Learning Evaluation Pipeline")
    print("=================================================================")
    print("[*] Ingesting strictly validated features from v_ml_features...")
    report = run_full_ml_benchmark()
    print(f"[+] Total Audited Opportunities: {report['total_opportunities']}")
    print(f"[+] Complied Actions: {report['total_complied']} ({report['baseline_compliance_rate']*100:.1f}%)")
    print(f"[+] Git Commit Hash: {report['git_commit']}")
    print(f"[+] Benchmarked Configurations: {len(report['benchmark_table'])}")
    print(f"[+] Computed Odds Ratios: {len(report['odds_ratios'])}")
    print(f"[+] Artifact saved to: {REPORT_FILE}")
    print("\n[+] Top Odds Ratios:")
    for o in report["odds_ratios"][:5]:
        print(f"    - {o['feature']} [{o['category']} vs {o['reference_category']}]: OR={o['odds_ratio']} (95% CI: [{o['ci_low']} – {o['ci_high']}]), p={o['p_value']}")
    print("\n[+] Recommendation Conclusion:")
    print(report["conclusion"])
    print("\n[+] Pipeline run completed successfully.")


if __name__ == "__main__":
    main()
