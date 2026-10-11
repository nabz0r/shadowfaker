#!/usr/bin/env python3
"""Pilot, resume and publish only counts from the private IoC evidence ledger."""
import json

from shadowfaker.config import CONFIG
from shadowfaker.ioc_corpus import build, publish_aggregate


def main() -> None:
    pilot = build(pilot=True, path=CONFIG.root / "data" / "pilot_ioc" / "faker_ioc.sqlite")
    if pilot["errors"] or pilot["tables"]["games"] != 5:
        raise RuntimeError(f"IoC pilot failed: {pilot['errors']}")
    full = build()
    if full["errors"]:
        raise RuntimeError(f"IoC build errors: {full['errors']}")
    public = publish_aggregate()
    print(json.dumps({"pilot": pilot["tables"], "full": full["tables"],
                      "by_split": public["windows_by_split"]}, indent=2))


if __name__ == "__main__":
    main()
