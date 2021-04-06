#!/bin/bash
cd pdf
for file in *.pdf; do pdftotext "$file"; done
mv *.txt ../txt/
