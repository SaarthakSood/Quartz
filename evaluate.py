"""Confusion matrix on a labelled folder set.  Usage:
   python evaluate.py [data_dir=data] [threshold=0.5]
   data_dir/ai/*.jpg   data_dir/real/*.jpg   (positive class = AI)"""
import pathlib
import sys

from PIL import Image

from backend import detector

root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "data")
th = float(sys.argv[2]) if len(sys.argv) > 2 else 0.5
EXT = {".jpg", ".jpeg", ".png", ".webp"}
tp = fn = fp = tn = skipped = 0
for label in ("ai", "real"):
    files = [p for p in (root / label).glob("*") if p.suffix.lower() in EXT]
    if not files:
        sys.exit(f"No images in {root / label}")
    for p in files:
        try:
            pred_ai = detector.predict(Image.open(p).convert("RGB"))["ai_probability"] >= th
        except Exception as e:  # noqa: BLE001
            skipped += 1
            print("skip", p.name, e)
            continue
        if label == "ai":
            tp, fn = tp + pred_ai, fn + (not pred_ai)
        else:
            fp, tn = fp + pred_ai, tn + (not pred_ai)
n = tp + fn + fp + tn
div = lambda a, b: a / b if b else 0.0  # noqa: E731
print(f"\nthreshold {th}   n={n}   skipped={skipped}")
print("                 pred AI   pred real")
print(f"actual AI      {tp:9d} {fn:11d}")
print(f"actual real    {fp:9d} {tn:11d}")
print(f"accuracy  {div(tp + tn, n):.3f}")
print(f"precision {div(tp, tp + fp):.3f}")
print(f"recall    {div(tp, tp + fn):.3f}")
print(f"f1        {div(2 * tp, 2 * tp + fp + fn):.3f}")
