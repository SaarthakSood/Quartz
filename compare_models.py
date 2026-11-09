"""Measure each candidate detector separately on YOUR labelled images, then recommend the best combination.

    python compare_models.py [data_dir=data] [--max 300] [--models a/b,c/d]
    data_dir/ai/*.jpg   data_dir/real/*.jpg      (positive class = AI)

Use images from the generators and sources you actually care about (current Midjourney / Flux / GPT-image /
Gemini images, plus real phone photos). Public benchmark numbers on a model card do not predict this.
"""
import argparse
import pathlib
import sys

from PIL import Image

from backend import benchmark, detector

CANDIDATES = [
    "Ateeqq/ai-vs-human-image-detector",
    "haywoodsloan/ai-image-detector-deploy",
    "Smogy/SMOGY-Ai-images-detector",
    "cmckinle/sdxl-flux-detector_v1.1",
    "Heem2/AI-vs-Real-Image-Detection",
    "Organika/sdxl-detector",
]
EXT = {".jpg", ".jpeg", ".png", ".webp"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("data", nargs="?", default="data")
    ap.add_argument("--max", type=int, default=300, help="max images per class")
    ap.add_argument("--models", default=",".join(CANDIDATES))
    a = ap.parse_args()
    names = [m.strip() for m in a.models.split(",") if m.strip()]

    items = []
    for lab, cls in ((1, "ai"), (0, "real")):
        files = sorted(p for p in (pathlib.Path(a.data) / cls).glob("*") if p.suffix.lower() in EXT)[: a.max]
        if not files:
            sys.exit(f"No images in {pathlib.Path(a.data) / cls}")
        items += [(p, lab) for p in files]
    print(f"{len(items)} images ({sum(l for _, l in items)} AI, {sum(1 - l for _, l in items)} real)\\n")

    P, y, skipped = {n: [] for n in names}, [], {}
    imgs = []
    for p, lab in items:
        try:
            imgs.append((Image.open(p).convert("RGB"), lab))
        except Exception as e:  # noqa: BLE001
            print("skip", p.name, e)
    y = [l for _, l in imgs]
    for n in list(names):
        scores = [detector.score_model(n, im) for im, _ in imgs]
        bad = [s for s in scores if "ai_probability" not in s]
        if bad:
            skipped[n] = bad[0]["error"]
            names.remove(n)
            P.pop(n)
            continue
        P[n] = [s["ai_probability"] for s in scores]

    print(f"{'model':46s} {'acc':>6s} {'bal.acc':>8s} {'AUC':>6s} {'recall':>7s} {'spec.':>6s}   TP  FN  FP  TN")
    for n in names:
        m = benchmark.metrics(y, P[n])
        print(f"{n:46s} {m['accuracy']:6.3f} {m['balanced_accuracy']:8.3f} {m['auc']:6.3f} {m['recall']:7.3f} {m['specificity']:6.3f}  "
              f"{m['tp']:3d} {m['fn']:3d} {m['fp']:3d} {m['tn']:3d}")
    for n, e in skipped.items():
        print(f"{n:46s} skipped: {e}")
    if not names:
        sys.exit("No model could be evaluated.")
    best, m = benchmark.best_ensemble(P, y, names)
    print("\\nBest equal-weight ensemble:" if best else "\\nNo model beats chance on this data.")
    if best:
        print("  ", ", ".join(best))
        print(f"   accuracy {m['accuracy']:.3f}  balanced {m['balanced_accuracy']:.3f}  AUC {m['auc']:.3f}  "
              f"TP {m['tp']} FN {m['fn']} FP {m['fp']} TN {m['tn']}")
        print("\\nUse it:\\n   set QUARTZ_MODELS=" + ",".join(best) + "   (Windows)\\n   export QUARTZ_MODELS=" + ",".join(best) + "   (Mac/Linux)")
    print("\\nA model with AUC near 0.5 is guessing. AUC high but accuracy low means the 0.5 cut-off is wrong for that model.")


if __name__ == "__main__":
    main()
