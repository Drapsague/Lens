#!/bin/bash

# codeql database analyze flask-db ./ql/externalApis.ql --format=csv --output=results.csv --threads=5 --ram=4096
echo "Query Run"
codeql query run --database=./target/flask-db ./target/ql/internalFunc.ql --threads=5 --ram=4096 --output=/tmp/internalFunc.bqrs
codeql query run --database=./target/flask-db ./target/ql/externalApis.ql --threads=5 --ram=4096 --output=/tmp/externalAPIs.bqrs
# codeql query run --database=flask-db ./ql/detect_cwe639.ql --threads=5 --ram=4096 --output=/tmp/cwe639_findings.bqrs

echo "Decoding to CSV"
codeql bqrs decode /tmp/internalFunc.bqrs --format=csv --output=./target/report/internalFunc.csv
codeql bqrs decode /tmp/externalAPIs.bqrs --format=csv --output=./target/report/externalAPIs.csv
# codeql bqrs decode /tmp/cwe639_findings.bqrs --format=csv --output=./report/cwe639_findings.csv
