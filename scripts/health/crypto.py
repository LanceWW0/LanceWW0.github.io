"""Passphrase encryption for the private /health data file.

AES-256-GCM with a key derived by PBKDF2-SHA256 (600k iterations), the same
primitives the browser's Web Crypto API provides, so the page can decrypt
without any library.

- The salt stays the same while the passphrase does, so a browser that
  remembers the derived key keeps working day to day.
- The IV is fresh and random on every write. It is never reused or derived
  from anything.
- The plaintext is padded to a multiple of 4 KB, so the file size doesn't
  hint at what changed.
- The associated data binds the ciphertext to this format version.

The encrypted file sits in public git history forever, so the passphrase
must be long and random (5+ words).
"""
from __future__ import annotations

import base64
import os
from typing import Any

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

FORMAT = 1
ALG = "AES-256-GCM"
KDF = "PBKDF2-SHA256"
ITERATIONS = 600_000
AAD = b"health-v1"
PAD_TO = 4096
SALT_BYTES, IV_BYTES = 16, 12
_ITERATION_RANGE = (1_000, 10_000_000)
_KEYS = {"enc", "alg", "kdf", "iter", "salt", "iv", "data"}


class CryptoError(ValueError):
    pass


def is_envelope(obj: Any) -> bool:
    return isinstance(obj, dict) and "enc" in obj


def encrypt(plaintext: bytes, passphrase: str, *, salt: bytes | None = None, iterations: int = ITERATIONS) -> dict:
    if not passphrase:
        raise CryptoError("empty passphrase")
    salt = salt if salt is not None else os.urandom(SALT_BYTES)
    if len(salt) != SALT_BYTES:
        raise CryptoError("bad salt length")
    iv = os.urandom(IV_BYTES)
    padded = plaintext + b" " * (-len(plaintext) % PAD_TO)  # JSON ignores trailing spaces
    ciphertext = AESGCM(_derive(passphrase, salt, iterations)).encrypt(iv, padded, AAD)
    return {
        "enc": FORMAT,
        "alg": ALG,
        "kdf": KDF,
        "iter": iterations,
        "salt": _b64(salt),
        "iv": _b64(iv),
        "data": _b64(ciphertext),
    }


def decrypt(envelope: Any, passphrase: str) -> bytes:
    _check(envelope)
    try:
        ciphertext = _unb64(envelope["data"])
    except ValueError:
        raise CryptoError("bad data encoding") from None
    key = _derive(passphrase, salt_of(envelope), envelope["iter"])
    try:
        padded = AESGCM(key).decrypt(_unb64(envelope["iv"]), ciphertext, AAD)
    except InvalidTag:
        raise CryptoError("wrong passphrase or damaged file") from None
    return padded.rstrip(b" ")


def salt_of(envelope: Any) -> bytes:
    _check(envelope)
    return _unb64(envelope["salt"])


def _check(envelope: Any) -> None:
    if not isinstance(envelope, dict) or set(envelope) != _KEYS:
        raise CryptoError("not an encrypted health file")
    if envelope["enc"] != FORMAT or envelope["alg"] != ALG or envelope["kdf"] != KDF:
        raise CryptoError("unsupported encryption format")
    iterations = envelope["iter"]
    if type(iterations) is not int or not _ITERATION_RANGE[0] <= iterations <= _ITERATION_RANGE[1]:
        raise CryptoError("unsupported iteration count")
    try:
        if len(_unb64(envelope["salt"])) != SALT_BYTES or len(_unb64(envelope["iv"])) != IV_BYTES:
            raise CryptoError("bad salt or IV length")
    except (TypeError, ValueError) as exc:
        if isinstance(exc, CryptoError):
            raise
        raise CryptoError("bad salt or IV encoding") from None


def _derive(passphrase: str, salt: bytes, iterations: int) -> bytes:
    if not passphrase:
        raise CryptoError("empty passphrase")
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=iterations)
    return kdf.derive(passphrase.encode("utf-8"))


def _b64(raw: bytes) -> str:
    return base64.b64encode(raw).decode("ascii")


def _unb64(text: Any) -> bytes:
    if not isinstance(text, str):
        raise ValueError("expected base64 text")
    return base64.b64decode(text, validate=True)
