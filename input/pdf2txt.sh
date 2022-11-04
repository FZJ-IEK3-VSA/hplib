#!/bin/bash
cd pdf_07_22
for file in *.pdf; do pdftotext "$file"; done
mv *.txt ../txt_07_22/
