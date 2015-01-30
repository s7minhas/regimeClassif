#!/bin/bash

for FILE in graphics/*.pdf; do
  pdfcrop "${FILE}" "${FILE}"
done