#!/bin/bash
py.test --cov=rocket tests/
export CODACY_PROJECT_TOKEN=1c53c95f42a841d7bf112453fe6755aa
coverage xml
python-codacy-coverage -r coverage.xml

