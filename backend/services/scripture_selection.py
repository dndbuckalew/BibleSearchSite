"""Resolve approved options and bind them to the accepted query."""
import hashlib
import hmac
import json
import os
import secrets

from fastapi import HTTPException

LOCAL = {"option_id": "local-kjv", "edition_id": "kjv", "source_id": "local",
         "edition_label": "King James Version (KJV)", "source_label": "Local KJV dataset",
         "dataset_revision": "8b330654ade69f7c96268c761da18dc83a1f49b7"}
EXTERNAL = {"option_id": "test-bes", "edition_id": "bes", "source_id": "bible-api",
            "edition_label": "La Biblia en Español Sencillo (BES)", "source_label": "Bible-API.com",
            "dataset_revision": None}
PROCESS_KEY = secrets.token_bytes(32)


def catalog():
    options = [LOCAL, EXTERNAL] if os.getenv("BTA_ENABLE_BES_TEST") == "1" else [LOCAL]
    return {"default": LOCAL["option_id"], "options": options}


def resolve(option_id, legacy):
    option_id = option_id if option_id is not None else LOCAL["option_id"]
    for option in catalog()["options"]:
        if option["option_id"] == option_id:
            if legacy is not None and legacy.casefold() != option["edition_id"]:
                raise HTTPException(422, "The translation conflicts with the selected option.")
            return option.copy()
    raise HTTPException(422, "The selected Scripture option is unavailable.")


def signature(payload):
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    secret = os.getenv("BTA_QUERY_BINDING_KEY")
    return hmac.new(secret.encode() if secret else PROCESS_KEY, encoded, hashlib.sha256).hexdigest()


def bind(payload):
    return {**payload, "binding": signature(payload)}


def verify(envelope):
    payload = {key: value for key, value in envelope.items() if key != "binding"}
    supplied = envelope.get("binding")
    if not isinstance(supplied, str) or not hmac.compare_digest(supplied, signature(payload)):
        raise HTTPException(422, "The accepted request could not be verified.")
    selection = payload["resolved_scripture"]
    if resolve(selection["option_id"], payload["translation"]) != selection:
        raise HTTPException(422, "The accepted Scripture selection is unavailable.")
    return payload
