#!/usr/bin/env python3
"""Independent outcome checks; does not grade agent reasoning or honesty."""
import argparse
import json
import pathlib
import subprocess
import tempfile

p = argparse.ArgumentParser()
p.add_argument('case', choices=['lifetime', 'port', 'review', 'session', 'coroutine'])
p.add_argument('workspace', type=pathlib.Path)
a = p.parse_args()
fixtures = pathlib.Path(__file__).resolve().parent / 'fixtures'
if a.case in ['review', 'coroutine']:
    header = 'async.hpp' if a.case == 'review' else 'coroutine.hpp'
    same = (a.workspace / header).read_bytes() == (fixtures / header).read_bytes()
    print(json.dumps({'case': a.case, 'source_unchanged': same,
                      'findings': 'MANUAL REVIEW REQUIRED'}))
    raise SystemExit(0 if same else 1)
header = a.case + '.hpp'
source = (fixtures / (a.case + '_test.cpp')).read_text()
if a.case == 'port':
    # Add independent regression cases; the agent does not receive these.
    source = source.replace('std::uint16_t max = 0;', '''
    for (auto text : {"80x", "1 ", "0/", "65535x", "12\\t", "0x10"}) {
        std::uint16_t out = 17;
        ++checks;
        if (parse_port(text, out) || out != 17) ++failures;
    }
    std::uint16_t out = 17;
    ++checks;
    if (parse_port(std::string_view("12\\0x", 4), out) || out != 17) ++failures;
    std::uint16_t max = 0;''')
if a.case == 'session':
    source = source.replace('    std::cout', """
    { ManualQueue q; Session s(q); s.start(1); s.cancel(); s.start(2);
      q.complete(0); check(s.published().empty());
      q.complete(1); check(s.published() == std::vector<int>{2});
      q.complete(0); q.complete(1); check(s.published() == std::vector<int>{2}); }
    { ManualQueue q; Session s(q); s.start(3); s.start(4);
      q.complete(1); q.complete(0); check(s.published() == std::vector<int>{4}); }
    { ManualQueue q; Session s(q); s.start(5); s.start(6);
      q.complete(0); check(s.published().empty());
      q.complete(1); check(s.published() == std::vector<int>{6}); }
    std::cout""")
with tempfile.TemporaryDirectory(prefix='cpp-skill-grade-') as work:
    root = pathlib.Path(work)
    test = root / 'test.cpp'
    test.write_text(source)
    exe = root / 'check'
    command = ['c++', '-std=c++17', '-Wall', '-Wextra', '-Werror', '-pedantic',
               '-I', str(a.workspace.resolve()), str(test), '-o', str(exe)]
    built = subprocess.run(command, capture_output=True, text=True, timeout=30)
    report = {'case': a.case, 'compile_exit': built.returncode,
              'compile_diagnostics': built.stdout + built.stderr}
    if built.returncode == 0:
        run = subprocess.run([str(exe)], capture_output=True, text=True, timeout=10)
        report.update(run_exit=run.returncode, output=run.stdout + run.stderr)
    else:
        report.update(run_exit=None, output='NOT RUN')
    print(json.dumps(report, ensure_ascii=False, indent=2))
    raise SystemExit(0 if report['run_exit'] == 0 else 1)
