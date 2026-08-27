from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hkd_optimizer import EDITION
from benchmarks.semiconductor_large import run

OPS = 5000000

if EDITION == "free":
    try:
        run(ops=OPS, block=32, events=2)
    except RuntimeError as e:
        msg = str(e)
        assert "HKD_OPTIMIZER_PAID_REQUIRED" in msg
        print(msg)
        print("test_large: PASS (free paywall)")
    else:
        raise AssertionError("free edition unexpectedly allowed large benchmark")
else:
    result = run(ops=OPS, block=32, events=4)
    assert result["exact"] is True
    print("test_large: PASS (paid)")
