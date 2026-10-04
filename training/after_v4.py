"""Runs after Laya v4 training (SJ, 4 Oct). OWNER: Jabin. Rule fixed BEFORE v4 results:
ship v4 if its post-hoc shipped mean accuracy over gender/family/stat (en, hi, ta) >= v3r's, else v3.
Steps: wait for training PID -> threshold fit (calib) -> post-hoc v4 (Laya alone + shipped) -> E4 v4 -> choose -> E1 plain+prompt_only.
"""
import json
import pathlib
import subprocess
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[1]
LOG = ROOT / "results" / "after_v4.log"
PID = int(sys.argv[1])


def alive(pid):
    out = subprocess.run(["tasklist", "/FI", f"PID eq {pid}"], capture_output=True, text=True).stdout
    return str(pid) in out


def run(args):
    with LOG.open("a", encoding="utf-8") as f:
        f.write(f"\n$ {' '.join(args)}\n")
        f.flush()
        return subprocess.run([sys.executable, *args], cwd=ROOT, stdout=f, stderr=subprocess.STDOUT).returncode


def mean(tag):
    xs = []
    for lang in ("en", "hi", "ta"):
        s = json.loads((ROOT / f"results/classifier/posthoc_{tag}/d_shipped_{lang}_summary.json").read_text(encoding="utf-8"))
        xs += [r["acc"] for r in s["by_q_lang"] if r["q"] in ("gender_signal", "family", "stat")]
    return sum(xs) / len(xs)


def main():
    while alive(PID):
        time.sleep(30)
    if not (ROOT / "models/laya-mak-v4/model.safetensors").exists():
        LOG.open("a", encoding="utf-8").write("\nv4 model missing: training failed; stopping before E1\n")
        return
    run(["training/calibrate/fit_temperature.py", "--model", "models/laya-mak-v4"])
    run(["training/evaluate_classifiers.py", "--mode", "posthoc", "--tag", "v4", "--laya", "models/laya-mak-v4",
         "--arms", "c_laya_ft,d_shipped"])
    run(["-m", "mak.eval.decision_eval", "--arm", "shipped", "--laya", "models/laya-mak-v4", "--tag", "v4_posthoc"])
    v3, v4 = mean("v3r"), mean("v4")
    choice = "laya-mak-v4" if v4 >= v3 else "laya-mak-v3"
    (ROOT / "results/calibration/model_choice.json").write_text(json.dumps(
        {"rule": "v4 if shipped mean(gender,family,stat) >= v3r", "v3r": v3, "v4": v4, "chosen": choice}, indent=1), encoding="utf-8")
    run(["-m", "mak.eval.run_e1", "--arms", "plain,prompt_only"])


if __name__ == "__main__":
    main()
