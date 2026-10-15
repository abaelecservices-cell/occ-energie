"""Reconstruction locale/CI complète, sans modification de Git ni accès réseau."""
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def run(*arguments):
    subprocess.run([sys.executable, *arguments], cwd=ROOT, check=True)


def main():
    run('tools/build_data.py', 'build/excel.json', 'build/data.json')
    run('tools/build_plans.py')
    run('tools/build_app.py')
    run('tools/build_app.py', '--lite')
    for name in ('OCC_ENERGIE_TS8.html', 'OCC_ENERGIE_VECTORIEL_MOBILE.html'):
        run('tools/build_app.py', '--output', name)
    run('tools/build_docs.py')
    for test in sorted((ROOT / 'tests').glob('test_*.py')):
        run(str(test))
    print('Reconstruction complète et tests documentaires : OK')


if __name__ == '__main__':
    main()
