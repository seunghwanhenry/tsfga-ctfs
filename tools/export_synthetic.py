"""Write a synthetic fab dataset to CSV as a schema template for the real extract.

python tools/export_synthetic.py data/synthetic_fabA.csv
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from ctfs import data as D

out = sys.argv[1] if len(sys.argv) > 1 else "data/synthetic_fabA.csv"
os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
df, meta = D.make_synthetic_fab(products_per_process=3, ops_per_product=4, records_per_combo=300)
df.to_csv(out, index=False)
print(df.shape, "->", out)
print("true features per process:", meta["true_features"])
