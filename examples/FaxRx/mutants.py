"""
Mutation suite for FaxRx's verify.py (see harness/mutation.py).

Each mutant plants one realistic bug in executable_model and names the checks
that must go red. `python verify.py --mutants` proves every check still bites.
"""

from __future__ import annotations

from harness.mutation import Mutant, drop_every_nth, patch_result

CONSERVATION = "Tier-1: work conservation (ledger balance)"
NO_OVERLOAD = "Tier-1: no congestion loss without saturation (PSTN blocking allowed)"
NONNEG = "Tier-1: non-negative ledger, success_rate in [0,1]"
PARTITION = "Tier-1 (multi-class): plain + ocr partition the system totals"
CHANNELS = "Tier-2 (metamorphic): adding SIP channels removes PSTN blocking"
OCR_SLOWER = "Tier-2 (structural): OCR path is slower than the plain path"


def _lose_requests(m):
    drop_every_nth(m.Server, "handle_request", 10)


def _ok_marked_timeout(m):
    def edit(cfg, r):
        # consistent across system and classes, so only the congestion law sees it
        for cls in ("plain", "ocr"):
            moved = r[f"{cls}_ok"] // 10
            r[f"{cls}_ok"] -= moved
            r[f"{cls}_timeout"] += moved
            r["completed_ok"] -= moved
            r["dropped_timeout"] += moved
    patch_result(m, edit)


def _double_count(m):
    def edit(cfg, r):
        for key in ("completed_ok", "plain_ok", "ocr_ok"):
            r[key] *= 2
        r["success_rate"] = r["completed_ok"] / r["total_arrivals"]
    patch_result(m, edit)


def _plain_counts_all(m):
    def edit(cfg, r):
        r["plain_ok"] = r["completed_ok"]      # bug: class filter forgotten for plain
    patch_result(m, edit)


def _no_pstn_limit(m):
    original = m.Server.__init__

    def init(self, env, cfg):
        original(self, env, cfg)
        # bug: SIP pool built from a constant; sip_channels never read
        self.sip_pool = m.simpy.Resource(env, capacity=100000)
    m.Server.__init__ = init


def _inverted_ocr_routing(m):
    original = m.Server._serve

    def _serve(self, rec):
        # bug: routing condition inverted - plain faxes get the OCR step, OCR ones skip it
        rec.ocr = not rec.ocr
        try:
            yield from original(self, rec)
        finally:
            rec.ocr = not rec.ocr
    m.Server._serve = _serve


MUTANTS = [
    Mutant("lose-requests", "every 10th fax vanishes without an outcome",
           (CONSERVATION,), _lose_requests),
    Mutant("ok-marked-timeout", "delivered faxes also recorded as SLA timeouts",
           (NO_OVERLOAD,), _ok_marked_timeout),
    Mutant("double-count-ok", "each delivery counted twice",
           (NONNEG,), _double_count),
    Mutant("plain-counts-all", "plain-class counter forgets the class filter",
           (PARTITION,), _plain_counts_all),
    Mutant("no-pstn-limit", "SIP pool sized from a constant; Erlang-B blocking never happens",
           (CHANNELS,), _no_pstn_limit),
    Mutant("inverted-ocr-routing", "OCR routing condition inverted",
           (OCR_SLOWER,), _inverted_ocr_routing),
]
