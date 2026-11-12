"""lab_seconds_from_ci reads the lab times out of a Labs share's log."""

import lab_seconds_from_ci


def test_it_reads_each_labs_time_and_skips_a_retried_one() -> None:
    stamp = "2026-11-12T16:08:58.6541082Z "
    retried = "ok (on its own, after the checker gave up in the crowd)"
    lines = [
        "ok     csa.hw.disks/write-io-rate (212 s)",
        "BROKEN csa.net.dns/write-zone-health (75 s)",
        "       - after solution.sh, shop-test fails: (3 s)",
        f"{retried} csa.hw.gpus/build-x (90 s)",
        "19 of 20 labs keep their contract.",
    ]
    log = "\n".join(stamp + line for line in lines)
    assert lab_seconds_from_ci.times_in(log) == {
        "csa.hw.disks/write-io-rate": 212,
        "csa.net.dns/write-zone-health": 75,
    }
