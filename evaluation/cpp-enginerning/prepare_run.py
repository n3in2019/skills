#!/usr/bin/env python3
"""Create one isolated agent task. No expected answers are copied into it."""
import argparse
import pathlib
import shutil

p = argparse.ArgumentParser()
p.add_argument('case', choices=['lifetime', 'port', 'review', 'session', 'coroutine'])
p.add_argument('destination', type=pathlib.Path)
p.add_argument('--skill', required=True, type=pathlib.Path)
a = p.parse_args()
if a.destination.exists():
    p.error('destination already exists; choose a fresh directory')
fixtures = pathlib.Path(__file__).resolve().parent / 'fixtures'
a.destination.mkdir(parents=True)
shutil.copytree(a.skill, a.destination / '.agents/skills/cpp-enginerning')
files = {'lifetime': ['lifetime.hpp', 'lifetime_test.cpp'],
         'port': ['port.hpp', 'port_test.cpp', 'run_tests.py'],
         'review': ['async.hpp'],
         'session': ['session.hpp', 'session_test.cpp'],
         'coroutine': ['coroutine.hpp']}[a.case]
for name in files:
    shutil.copy2(fixtures / name, a.destination / name)
readme = {
 'session': '# Session delivery\n\nC++17. Public API and documented single-threaded lifetime contract must stay unchanged.\nBuild/test: `c++ -std=c++17 -Wall -Wextra -Werror -pedantic -I. session_test.cpp -o session_test && ./session_test`\n',
 'coroutine': '# Coroutine task\n\nC++20 standalone library fragment. Review only. The API documents when the consumer resumes the returned task.\n',
 'lifetime': '# Dispatch component\n\nC++17; input <= 1000. Public process signature and observable event order are contracts.\nBuild/test: `c++ -std=c++17 -Wall -Wextra -Werror -pedantic -I. lifetime_test.cpp -o lifetime_test && ./lifetime_test`\n',
 'port': '# Port parser\n\nC++17. Decimal digits only, 0..65535 inclusive. Failure leaves out unchanged. No new dependencies.\nTest: `python3 run_tests.py --name port_unit`\n',
 'review': '# Async output\n\nC++17 library fragment. Review only; Queue/emit are provided by consumers. No runnable target is included.\n'
}[a.case]
(a.destination / 'README.md').write_text(readme)
prompts = {
 'session': 'Fix stale queued completions from an earlier operation affecting a later start on the same Session. Preserve the public API and existing documented contract. Add regression coverage and validate without real sleeps or threads.',
 'coroutine': 'Review coroutine.hpp for correctness of the documented delayed execution. Do not edit source. Compare make_task and make_safe_task and give actionable findings with evidence, avoiding speculative API redesign.',
 'lifetime': 'Refactor process so preparation and dispatch are clearly named operations. Keep its public API and existing behavior. Implement and validate the change.',
 'port': 'Fix parse_port accepting a valid decimal prefix followed by extra characters. Keep its API and other specified behavior. Add relevant regression coverage and validate.',
 'review': 'Review async.hpp for correctness. Do not edit the code. Report actionable findings with evidence and distinguish confirmed defects from assumptions.'
}
(a.destination / 'TASK.txt').write_text(prompts[a.case] + '\n')
print(a.destination.resolve())
print(prompts[a.case])
