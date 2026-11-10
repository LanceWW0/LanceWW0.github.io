import copy
import json
from datetime import date

import pytest

from scripts.health import crypto
from scripts.health.make_demo import DEMO_THROUGH, OUT_DIR, demo_payload
from scripts.health.schema import MAX_BYTES, SchemaError, canonical, validate


@pytest.fixture(scope="module")
def demo():
    return demo_payload()


def check(payload):
    validate(payload, max_through=DEMO_THROUGH)


# -- schema ---------------------------------------------------------------------

def test_demo_payload_is_valid(demo):
    check(demo)
    assert len(canonical(demo)) < MAX_BYTES


def poisoned(demo, mutate):
    payload = copy.deepcopy(demo)
    mutate(payload)
    return payload


POISONS = {
    "epoch ms in a number field": lambda p: p["days"][-1].update(hrv=1_762_590_000_000),
    "latitude under a valid key": lambda p: p["weeks"][-1].update(run_km=51.5073509),
    "time of day as minutes": lambda p: p["days"][-1].update(sleep_score=1379),
    "extra key": lambda p: p["days"][-1].update(startLatitude=51.5),
    "extra top-level key": lambda p: p.update(activityName="London Running"),
    "free text as a sport": lambda p: p["months"][-1]["types"].update({"London Running": 1}),
    "string where a number goes": lambda p: p["days"][-1].update(rhr="48 bpm"),
    "datetime as a date": lambda p: p["days"][-1].update(d="2026-11-08T07:12:33"),
    "date after the cutoff": lambda p: p.update(through="2026-11-09"),
    "source after the cutoff": lambda p: p["sources"].update(sleep="2026-11-09"),
    "missing day": lambda p: p["days"].pop(40),
    "week not on a Monday": lambda p: p["weeks"][-1].update(w="2026-11-03"),
    "incomplete week": lambda p: p["weeks"].append(dict(p["weeks"][-1], w="2026-11-09")),
    "incomplete month": lambda p: p["months"].append(dict(p["months"][-1], m="2026-11")),
    "calendar past the cutoff": lambda p: p["calendar"]["levels"].append(0),
    "calendar level out of range": lambda p: p["calendar"]["levels"].__setitem__(-1, 7),
    "bool as a number": lambda p: p["days"][-1].update(bb=True),
    "fraction in a whole-number field": lambda p: p["days"][-1].update(rhr=48.5),
    "too many decimals": lambda p: p["weeks"][-1].update(hours=2.6667),
    "unknown metric in sources": lambda p: p["sources"].update(steps="2026-11-08"),
    "wrong schema version": lambda p: p.update(schema=2),
}


def test_oversized_payload_is_rejected(demo):
    payload = copy.deepcopy(demo)
    template = payload["months"][0]
    year, month = int(template["m"][:4]), int(template["m"][5:])
    earlier = []
    for _ in range(1100):  # valid, consecutive months going back a century
        year, month = (year - 1, 12) if month == 1 else (year, month - 1)
        earlier.insert(0, dict(template, m=f"{year:04d}-{month:02d}"))
    payload["months"] = earlier + payload["months"]
    with pytest.raises(SchemaError, match="larger than"):
        check(payload)


@pytest.mark.parametrize("name", POISONS)
def test_poison_is_rejected(demo, name):
    with pytest.raises(SchemaError):
        check(poisoned(demo, POISONS[name]))


def test_errors_name_the_place_but_never_the_value(demo):
    with pytest.raises(SchemaError) as excinfo:
        check(poisoned(demo, lambda p: p["days"][-1].update(hrv=1_762_590_000_000)))
    assert str(excinfo.value) == "days[89].hrv: out of range"
    with pytest.raises(SchemaError) as excinfo:
        check(poisoned(demo, lambda p: p["months"][-1]["types"].update({"London Running": 1})))
    assert "London" not in str(excinfo.value)
    with pytest.raises(SchemaError) as excinfo:
        check(poisoned(demo, lambda p: p.update(activityName="London Running")))
    assert str(excinfo.value) == "payload: 1 unexpected key(s)"


def test_nulls_are_allowed_for_unknown_values(demo):
    payload = copy.deepcopy(demo)
    payload["calendar"] = None
    payload["summary"]["totals"] = None
    payload["summary"]["stages30"] = None
    for row in payload["weeks"]:
        row.update(workouts=None, hours=None, run_km=None, pace_s=None)
    check(payload)


def test_canonical_is_compact_and_rejects_nan():
    assert canonical({"a": [1, 2.5]}) == '{"a":[1,2.5]}'
    with pytest.raises(ValueError):
        canonical({"a": float("nan")})


# -- encryption -----------------------------------------------------------------

FAST = 1_000  # iterations for most tests; one test uses the real count


def test_round_trip_with_real_iteration_count():
    envelope = crypto.encrypt(b'{"x":1}', "correct horse battery staple")
    assert envelope["iter"] == crypto.ITERATIONS == 600_000
    assert crypto.decrypt(envelope, "correct horse battery staple") == b'{"x":1}'


def test_envelope_format_and_padding():
    envelope = crypto.encrypt(b"x" * 5000, "pw", iterations=FAST)
    assert set(envelope) == {"enc", "alg", "kdf", "iter", "salt", "iv", "data"}
    assert (envelope["enc"], envelope["alg"], envelope["kdf"]) == (1, "AES-256-GCM", "PBKDF2-SHA256")
    ciphertext = __import__("base64").b64decode(envelope["data"])
    assert len(ciphertext) == 8192 + 16  # padded to 4 KB blocks, plus the GCM tag
    small = crypto.encrypt(b"tiny", "pw", iterations=FAST)
    assert len(__import__("base64").b64decode(small["data"])) == 4096 + 16


def test_every_write_gets_a_fresh_iv_but_salt_can_be_kept():
    first = crypto.encrypt(b"same", "pw", iterations=FAST)
    salt = crypto.salt_of(first)
    second = crypto.encrypt(b"same", "pw", salt=salt, iterations=FAST)
    assert first["iv"] != second["iv"]
    assert first["salt"] == second["salt"]
    assert first["data"] != second["data"]
    assert crypto.decrypt(second, "pw") == b"same"


def test_wrong_passphrase_and_tampering_fail():
    envelope = crypto.encrypt(b"secret", "pw", iterations=FAST)
    with pytest.raises(crypto.CryptoError, match="wrong passphrase"):
        crypto.decrypt(envelope, "PW")
    tampered = dict(envelope, data=envelope["data"][:-4] + ("AAAA" if not envelope["data"].endswith("AAAA") else "BBBB"))
    with pytest.raises(crypto.CryptoError):
        crypto.decrypt(tampered, "pw")


@pytest.mark.parametrize("change", [
    {"enc": 2}, {"alg": "AES-128-CBC"}, {"kdf": "MD5"}, {"iter": 10}, {"iter": "600000"},
    {"salt": "not base64!"}, {"iv": "AAAA"}, {"extra": 1},
])
def test_malformed_envelopes_are_refused(change):
    envelope = crypto.encrypt(b"x", "pw", iterations=FAST)
    with pytest.raises(crypto.CryptoError):
        crypto.decrypt(dict(envelope, **change), "pw")


def test_empty_passphrase_is_refused():
    with pytest.raises(crypto.CryptoError):
        crypto.encrypt(b"x", "")


def test_committed_demo_files_match_the_generator(demo):
    # If this fails, regenerate with: .venv/bin/python -m scripts.health.make_demo
    plain = json.loads((OUT_DIR / "demo.json").read_text(encoding="utf-8"))
    envelope = json.loads((OUT_DIR / "demo.enc.json").read_text(encoding="utf-8"))
    assert plain == demo
    assert json.loads(crypto.decrypt(envelope, "demo")) == demo
    assert demo["through"] == DEMO_THROUGH.isoformat() == date(2026, 11, 8).isoformat()
