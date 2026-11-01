"""Rebuild the Italian .tra files from an original copy of The Shivah.

Usage: python strumenti/genera.py "<path to Shivah.exe>" <output_dir>

Extracts the strings from the game, applies traduzione/italiano.tsv and writes
Italiano.tra and Italiano_senza_accenti.tra into <output_dir>.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TSV = os.path.join(HERE, "..", "traduzione", "italiano.tsv")


def run(*args):
    subprocess.run([sys.executable, *args], check=True)


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    game, out = sys.argv[1], sys.argv[2]
    project = os.path.join(out, "progetto")
    if os.path.exists(os.path.join(project, "cands.json")):
        sys.exit(f"{project} already exists: delete it or choose another output folder")
    run(os.path.join(HERE, "extract.py"), game, project, "--skip-script", "Keyboard.asc")
    run(os.path.join(HERE, "tsv.py"), "import", project, TSV)
    run(os.path.join(HERE, "build.py"), project, os.path.join(out, "Italiano"))
    run(os.path.join(HERE, "build.py"), project, os.path.join(out, "Italiano_senza_accenti"), "--ascii")


if __name__ == "__main__":
    main()
