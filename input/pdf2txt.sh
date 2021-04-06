#!/bin/bash
for file in *.pdf; do pdftotext "$file"; done
