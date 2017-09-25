#!/usr/bin/env python
"""
Test runner for dv_router.py and learning_switch.py.

Add your own tests by creating new files in tests/ and updating main
below.

"""

from __future__ import print_function

import os
import select
import subprocess
import time


def main():
    t = TestSuite()

    t.test('learning_switch', 'tests.test_learning')
    t.test('dv_router', 'tests.test_simple')
    t.test('dv_router', 'tests.test_failure')
    t.test('dv_router', 'tests.test_initialize_neighbor')
    t.test('dv_router', 'tests.test_no_hairpin')
    t.test('dv_router', 'tests.test_link_weights')
    t.test('dv_router', 'tests.test_expire_routes')
    t.test(
        'dv_router',
        'tests.test_route_poisoning',
        extra_args=['--poison-mode'])

    # Add your own tests here.

    t.finish()


GREEN = '\033[92m'
RED = '\033[91m'
CLEAR = '\033[0m'


class TestSuite:
    num_passed = 0
    num_failed = 0

    def test(self, router, test_name, extra_args=None):
        cmd = ['python', 'simulator.py', '--no-interactive', '--virtual-time',
               '--default-switch-type=%s' % router]
        if extra_args:
            cmd += extra_args
        cmd += [test_name]
        interactive_cmd = [
            arg for arg in cmd
            if arg not in [
                '--no-interactive', '--virtual-time'
            ]
        ]
        r = subprocess.call(cmd)
        if r is False:
            self.fail(router, test_name, interactive_cmd, 'Timed out')
        elif r is None:
            self.fail(router, test_name, interactive_cmd, 'Could not run')
        elif r == 0:
            self.succeed(router, test_name)
        else:
            self.fail(router, test_name, interactive_cmd)

    def succeed(self, router, testname):
        print('%s*** %s: %s passed ***%s' % (GREEN, router, testname, CLEAR))
        self.num_passed += 1

    def fail(self, router, testname, cmd, message=None):
        if message:
            print('%s*** %s: %s failed: %s ***%s' % (RED, router, testname,
                                                     message, CLEAR))
        else:
            print('%s*** %s: %s failed ***%s' % (RED, router, testname, CLEAR))
        print('%sCommand: %s%s' % (RED, ' '.join(cmd), CLEAR))
        self.num_failed += 1

    def finish(self):
        if self.num_failed == 0:
            print('%sAll tests passed.%s' % (GREEN, CLEAR))
        else:
            print('Tests: %d passed, %s%d failed%s.' %
                  (self.num_passed, RED, self.num_failed, CLEAR))


if __name__ == '__main__':
    main()
