"""Tiny existing runner with optional exact-name selection."""
import argparse
import pathlib
import subprocess
import sys

p = argparse.ArgumentParser()
p.add_argument('--name', default='port_contract')
a = p.parse_args()
if a.name != 'port_contract':
    print('tests=0')
    sys.exit(0)
pathlib.Path('build').mkdir(exist_ok=True)
subprocess.run(['c++', '-std=c++17', '-Wall', '-Wextra', '-Werror', '-pedantic',
                '-I.', 'port_test.cpp', '-o', 'build/port_test'], check=True)
r = subprocess.run(['build/port_test'], check=False)
print('tests=1')
sys.exit(r.returncode)
