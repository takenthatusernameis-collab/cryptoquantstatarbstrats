import subprocess, sys, time
from pathlib import Path

DONE_FILE = Path(".c441_sweep_done")

def sweep_still_running():
    try:
        out = subprocess.check_output(
            ["pgrep", "-af", "run_c441_tda_xsec_oos.py"],
            stderr=subprocess.DEVNULL, text=True,
        )
        lines = [l for l in out.splitlines() if l.strip()]
        return len(lines) > 0
    except subprocess.CalledProcessError:
        return False

def main():
    if DONE_FILE.exists():
        print("sweep already done (.c441_sweep_done present)")
        return 0
    if sweep_still_running():
        print("sweep still running (run_c441_tda_xsec_oos.py processes present)")
        return 1
    DONE_FILE.write_text(
        f"sweep_done_utc={time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}\n"
    )
    print("sweep processes exited; wrote .c441_sweep_done")
    return 0

if __name__ == "__main__":
    sys.exit(main())
