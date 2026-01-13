#!/bin/bash

codeql database analyze ./target/flask-db ./target/ql/detect_cwes.ql --format=sarif-latest --output=./target/report/results.sarif --threads=5 --ram=4096 --rerun

