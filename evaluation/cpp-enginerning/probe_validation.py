#!/usr/bin/env python3
"""Reproduce false-green checks locally; these are harness probes, not agent trials."""
import json
import pathlib
import platform
import shutil
import subprocess
import tempfile

def run_command(command, **kwargs):
    try:
        return subprocess.run(command, capture_output=True, text=True, **kwargs)
    except (OSError, subprocess.TimeoutExpired) as error:
        return subprocess.CompletedProcess(command, 125, '', 'BLOCKED: ' + str(error))

result = {'platform' : platform.platform(),
          'compiler': run_command(['c++', '--version'], timeout=10).stdout.splitlines(),
          'tools': {n: shutil.which(n) for n in ['c++', 'cmake', 'ctest', 'clang++', 'clang-tidy']}}
with tempfile.TemporaryDirectory() as work:
    root = pathlib.Path(work)
    source = root / 'overflow.cpp'
    source.write_text('#include <climits>\nint main(int argc, char**) { volatile int n = INT_MAX; volatile int x = n + argc; (void)x; return 0; }\n')
    checks = []
    for mode, extra in [('recover', []), ('failfast', ['-fno-sanitize-recover=all'])]:
        exe = root / mode
        flags = ['-std=c++17', '-fsanitize=undefined', *extra]
        built = run_command(['c++', *flags, str(source), '-o', str(exe)], timeout=30)
        item = {'mode': mode, 'compile_exit': built.returncode, 'flags': flags}
        if built.returncode == 0:
            run = run_command([str(exe)], timeout=10)
            item.update(status='OBSERVED' if 'runtime error' in run.stderr else 'BLOCKED', exit_code=run.returncode, diagnostic_detected='runtime error' in run.stderr,
                        stderr=run.stderr.replace(str(root), '<temp>'))
        else:
            item.update(status='BLOCKED', stderr=built.stderr.replace(str(root), '<temp>'))
        checks.append(item)
    result['ubsan_probe'] = checks
fixtures = pathlib.Path(__file__).resolve().parent / 'fixtures'
with tempfile.TemporaryDirectory() as work:
    for name in ['run_tests.py', 'port.hpp', 'port_test.cpp']:
        shutil.copy2(fixtures / name, pathlib.Path(work) / name)
    checks = []
    for selection in ['port_unit', 'port_contract']:
        run = run_command(['python3', 'run_tests.py', '--name', selection], cwd=work, timeout=30)
        checks.append({'selection': selection, 'exit_code': run.returncode,
                       'output': run.stdout + run.stderr})
    result['test_selection_probe'] = checks
print(json.dumps(result, ensure_ascii=False, indent=2))
