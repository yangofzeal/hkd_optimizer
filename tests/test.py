from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hkd_optimizer import EDITION, get_backend

logical_rows = 100000
def delta():
    return 123456789

res = get_backend().active_state(logical_rows, 1, delta)
assert res.result == 123456789
print("HKD_OPTIMIZER")
print("edition=%s" % EDITION)
print("logical_rows=%d" % logical_rows)
print("exact=True")
print("structural_reduction_x={:,.0f}".format(res.logical_reduction_x))
print("PASS")
