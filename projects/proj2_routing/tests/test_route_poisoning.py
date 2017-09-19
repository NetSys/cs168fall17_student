"""
Tests that the router performs route poisoning.

Creates a topology like the following:

h1 -- s1 -- c1 -- s2 -- s3 -- h2

After routes have converged, sends a ping from h1 to h2, which should get
through. Then disconnects s2 and s3. Then, after letting the routers exchange
messages but before routes have a chance to time out, sends another ping from h1
to h2. The test passes if the ping does not reach c1, meaning it was dropped at
s1 because the route was poisoned by s2.

"""

import sim
import sim.api as api
import sim.basics as basics
import sys

from tests.test_simple import GetPacketHost, NoPacketHost
from tests.test_link_weights import CountingHub


def launch():
    h1 = NoPacketHost.create('h1')
    h2 = GetPacketHost.create('h2')
    s1 = sim.config.default_switch_type.create('s1')
    s2 = sim.config.default_switch_type.create('s2')
    s3 = sim.config.default_switch_type.create('s3')
    c1 = CountingHub.create('c1')
    h1.linkTo(s1)
    s1.linkTo(c1)
    c1.linkTo(s2)
    s2.linkTo(s3)
    s3.linkTo(h2)

    def test_tasklet():
        yield 15

        api.userlog.debug('Sending ping from h1 to h2 - it should get through')
        h1.ping(h2)

        yield 5

        if c1.pings != 1:
            api.userlog.error("The first ping didn't get through")
            sys.exit(1)

        api.userlog.debug('Disconnecting s2 and s3')
        s2.unlinkTo(s3)

        api.userlog.debug(
            'Waiting for poison to propagate, but not long enough ' +
            'for routes to time out')
        yield 10

        api.userlog.debug(
            'Sending ping from h1 to h2 - it should be dropped at s1')
        h1.ping(h2)

        yield 5

        if c1.pings != 1:
            api.userlog.error(
                's1 forwarded the ping when it should have dropped it')
            sys.exit(1)
        else:
            api.userlog.debug('s1 dropped the ping as expected')
            sys.exit(0)

    api.run_tasklet(test_tasklet)
