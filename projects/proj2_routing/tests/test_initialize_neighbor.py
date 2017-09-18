"""
Tests that routers eagerly initialize new neighbors.

Creates a topology like:

h1 -- s1    s2 -- h2

After routes have converged, links s1 and s2 and quickly sends a ping from h1 to
h2. The test passes if h2 gets the ping, which would mean that s1 and s2 shared
routing tables immediately, without waiting for a timeout.

"""

import sim
import sim.api as api
import sim.basics as basics
import sim.cable as cable

from tests.test_simple import GetPacketHost, NoPacketHost


def launch():
    h1 = NoPacketHost.create("h1")
    h2 = GetPacketHost.create("h2")

    s1 = sim.config.default_switch_type.create('s1')
    s2 = sim.config.default_switch_type.create('s2')

    h1.linkTo(s1)
    h2.linkTo(s2)

    def test_tasklet():
        yield 5

        api.userlog.debug('Linking s1 and s2')
        def test_cable():
            c = cable.BasicCable()
            c.tx_time = 0
            return c
        s1.linkTo(s2, cable=(test_cable(), test_cable()))
        yield 0.1
        api.userlog.debug('Sending ping from h1 to h2')
        h1.ping(h2)

        yield 5

        if h2.pings != 1:
            api.userlog.error("h2 got %s pings instead of 1", h2.pings)
            good = False
        else:
            api.userlog.debug('h2 successfully received the ping')
            good = True

        import sys
        sys.exit(0 if good else 1)

    api.run_tasklet(test_tasklet)
