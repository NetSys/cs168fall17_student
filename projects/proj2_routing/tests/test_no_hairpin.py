"""
Tests that routers don't hairpin packets.

Creates a topology like:

h1 -- s1

After routes have converged, sends a packet from h1 to itself. The test passes
if h1 does *not* get the packet: s1 should drop the packet rather than send it
backwards.

"""

import sim
import sim.api as api
import sim.basics as basics

from tests.test_simple import GetPacketHost, NoPacketHost


def launch():
    h1 = NoPacketHost.create('h1')
    s1 = sim.config.default_switch_type.create('s1')
    h1.linkTo(s1)

    def test_tasklet():
        yield 5

        api.userlog.debug('Sending ping from h1 to itself')
        h1.ping(h1)

        yield 5

        if h1.bad_pings > 0:
            api.userlog.error('h1 got a hairpinned packet')
            good = False
        else:
            api.userlog.debug('As expected, h1 did not get a ping')
            good = True

        import sys
        sys.exit(0 if good else 1)

    api.run_tasklet(test_tasklet)
