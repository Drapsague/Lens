#!/bin/bash

# codeql database analyze flask-db ./ql/externalApis.ql --format=csv --output=results.csv --threads=5 --ram=4096
echo "Query Run"
codeql query run --database=./test/test-codeql-db ./test/ql/internalFunc.ql --threads=5 --ram=4096 --output=/tmp/test_internalFunc.bqrs
codeql query run --database=./test/test-codeql-db ./test/ql/externalApis.ql --threads=5 --ram=4096 --output=/tmp/test_externalAPIs.bqrs

echo "Decoding to CSV"
codeql bqrs decode /tmp/test_internalFunc.bqrs --format=csv --output=./test/report/test_internalFunc.csv
codeql bqrs decode /tmp/test_externalAPIs.bqrs --format=csv --output=./test/report/test_externalAPIs.csv
