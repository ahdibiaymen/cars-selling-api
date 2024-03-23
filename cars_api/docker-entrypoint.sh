#!/bin/sh
set -e
set -u

if [ -n "${MODE}" ] && [ "${MODE}" != "dev" ]; then
  uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
else
  uvicorn app.main:app --host 0.0.0.0 --port 8000
fi
