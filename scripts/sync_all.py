import sys
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def main():
    print("=" * 60)
    print("ArunCore Master Data Sync (GitHub + LinkedIn)")
    print("=" * 60)

    print("\n--- 1. Syncing GitHub Repositories & READMEs ---")
    subprocess.run([sys.executable, str(BASE_DIR / "scripts" / "sync_github.py")], check=False)

    print("\n--- 2. Syncing LinkedIn Posts & Insights ---")
    subprocess.run([sys.executable, str(BASE_DIR / "scripts" / "sync_linkedin.py")], check=False)

    print("\n=" * 60)
    print("[COMPLETED] All GitHub repos and LinkedIn posts synced to data/!")
    print("=" * 60)


if __name__ == "__main__":
    main()
