#!/bin/bash

pre-commit install

source /build/package/venv/bin/activate
uv sync --dev --active
