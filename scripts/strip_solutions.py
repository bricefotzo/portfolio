#!/usr/bin/env python3
"""Retire les blocs solution des fichiers pour produire la version étudiante.

Usage:
    python scripts/strip_solutions.py                    # dry-run (affiche les fichiers)
    python scripts/strip_solutions.py --apply            # modifie les fichiers en place
    python scripts/strip_solutions.py --output dist/     # copie dans dist/ (sans toucher l'original)

Les blocs encadrés par les marqueurs suivants sont remplacés par
un ``raise NotImplementedError`` :

    # ✂️ SOLUTION START
    <code solution>
    # ✂️ SOLUTION END

Les imports ajoutés uniquement pour la solution (lignes entre marqueurs)
sont aussi retirés. Les imports existants hors blocs sont conservés.
"""

from __future__ import annotations

import argparse
import re
import shutil
import textwrap
from pathlib import Path

MARKER_START = "# ✂️ SOLUTION START"
MARKER_END = "# ✂️ SOLUTION END"

# Fichiers à scanner (relatifs à la racine du projet)
TARGET_DIRS = [
    "packages/backend/src/backend/repositories",
    "packages/backend/src/backend/services",
]


def find_target_files(root: Path) -> list[Path]:
    """Trouve tous les .py contenant au moins un bloc solution."""
    files = []
    for d in TARGET_DIRS:
        target = root / d
        if target.is_dir():
            for f in sorted(target.rglob("*.py")):
                content = f.read_text(encoding="utf-8")
                if MARKER_START in content:
                    files.append(f)
    return files


def strip_file(content: str) -> str:
    """Remplace chaque bloc SOLUTION par raise NotImplementedError."""
    lines = content.splitlines(keepends=True)
    result = []
    inside_block = False
    block_indent = ""

    for line in lines:
        stripped = line.rstrip()

        if MARKER_START in stripped:
            inside_block = True
            # Détecter l'indentation du marqueur
            block_indent = re.match(r"^(\s*)", line).group(1)
            # Écrire le raise à la place
            result.append(f"{block_indent}raise NotImplementedError\n")
            continue

        if MARKER_END in stripped:
            inside_block = False
            continue

        if inside_block:
            # Supprimer la ligne (fait partie de la solution)
            continue

        result.append(line)

    return "".join(result)


def main():
    parser = argparse.ArgumentParser(description="Strip solution blocks for student distribution")
    parser.add_argument(
        "--apply", action="store_true", help="Modify files in place"
    )
    parser.add_argument(
        "--output", type=str, default=None,
        help="Copy project to OUTPUT dir and strip there (leaves original untouched)",
    )
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]

    if args.output:
        dest = Path(args.output).resolve()
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(root, dest, ignore=shutil.ignore_patterns(
            ".venv", "__pycache__", ".git", "*.pyc", ".pytest_cache", "uv.lock",
        ))
        root = dest
        apply = True
        print(f"Copié dans {dest}")
    else:
        apply = args.apply

    files = find_target_files(root)

    if not files:
        print("Aucun fichier avec des blocs solution trouvé.")
        return

    for f in files:
        rel = f.relative_to(root)
        original = f.read_text(encoding="utf-8")
        stripped = strip_file(original)

        n_blocks = original.count(MARKER_START)
        changed = original != stripped

        if apply and changed:
            f.write_text(stripped, encoding="utf-8")
            print(f"  ✂️  {rel} — {n_blocks} bloc(s) retiré(s)")
        elif changed:
            print(f"  [dry-run] {rel} — {n_blocks} bloc(s) à retirer")
        else:
            print(f"  [skip] {rel} — aucun bloc")

    if not apply:
        print("\nAjouter --apply pour modifier en place, ou --output <dir> pour copier.")


if __name__ == "__main__":
    main()
