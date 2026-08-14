#!/bin/zsh
set -e
cd "${0:A:h}"
exec .venv/bin/python -m app.main
