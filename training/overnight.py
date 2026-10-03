"""Overnight sequence (SJ OK, 3 Oct). OWNER: Jabin. Decision rules fixed BEFORE results (docs/05):
1 GENDER_THRESHOLD = fit_temperature.py choice on calib (None -> keep config 0.85).
2 merge policy = v2 only if its mean accuracy over topic/family/stat on calib+messy beats v1 by >= 0.005, else v1.
3 single test run (all arms) with those values. 4 E1 plain + prompt_only (if the Llama model is pulled).
"""
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
PY = sys.executable
LOG = ROOT / "results" / "overnight.log"


def run(args):
    with LOG.open("a", encoding="utf-8") as f:
        f.write(f"\n$ {' '.join(args)}\n")
        f.flush()
        return subprocess.run([PY, *args], cwd=ROOT, stdout=f, stderr=subprocess.STDOUT).returncode


def mean_acc(arm):
    xs = []
    for s in ("calib", "messy"):
        p = ROOT / "results" / "classifier" / "dev" / f"{arm}_{s}_summary.json"
        xs += [r["acc"] for r in json.loads(p.read_text(encoding="utf-8"))["by_q_lang"] if r["q"] in ("topic", "family", "stat")]
    return sum(xs) / len(xs)


def main():
    run(["training/calibrate/fit_temperature.py"])
    th = json.loads((ROOT / "results/calibration/gender_threshold.json").read_text(encoding="utf-8"))["chosen_threshold"]
    run(["training/evaluate_classifiers.py", "--mode", "dev", "--arms", "d_shipped,d2_shipped_laya_first"])
    v1, v2 = mean_acc("d_shipped"), mean_acc("d2_shipped_laya_first")
    policy = "v2" if v2 - v1 >= 0.005 else "v1"
    decision = {"gender_threshold": th if th is not None else 0.85, "threshold_fit_found": th is not None,
                "merge_policy": policy, "dev_mean_acc_v1": v1, "dev_mean_acc_v2": v2}
    (ROOT / "results/calibration/pre_test_decision.json").write_text(json.dumps(decision, indent=1), encoding="utf-8")
    for path, old, new in (("src/mak/config.py", "GENDER_THRESHOLD = 0.85", f"GENDER_THRESHOLD = {decision['gender_threshold']}"),
                           ("src/mak/nlu/understand.py", 'MERGE_POLICY = "v1"', f'MERGE_POLICY = "{policy}"')):
        p = ROOT / path
        p.write_text(p.read_text(encoding="utf-8").replace(old, new), encoding="utf-8")
    run(["training/evaluate_classifiers.py", "--mode", "test", "--i-confirm-single-run",
         "--arms", "a_rules,b_laya_zeroshot,c_laya_ft,d_shipped,e_qwen_lora,f_xlmr_ft"])
    run(["-m", "mak.eval.run_e1", "--arms", "plain,prompt_only"])


if __name__ == "__main__":
    sys.path.insert(0, str(ROOT / "src"))
    main()
