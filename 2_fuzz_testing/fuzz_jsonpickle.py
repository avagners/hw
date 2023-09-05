#!/usr/bin/env python3
import json
import sys

import atheris


with atheris.instrument_imports():
    import jsonpickle as jp


@atheris.instrument_func
def TestOneInput(data):
    fdp = atheris.FuzzedDataProvider(data)
    try:
        original = fdp.ConsumeUnicodeNoSurrogates(fdp.remaining_bytes())
        thawed = jp.decode(original)
        jp.encode(thawed)
    except json.JSONDecodeError:
        return -1


def main():
    atheris.Setup(sys.argv, TestOneInput)
    atheris.Fuzz()


if __name__ == '__main__':
    main()
