#!/bin/bash

codeql database analyze ./test/test-codeql-db ./test/ql/detect_cwes.ql --format=sarif-latest --output=./test/report/results.sarif --threads=5 --ram=4096 --rerun
