from __future__ import division
import os
import re
import numpy as np
import pdftotext
from removeHeaderFooter import removeHeaderAndFooter
from removeWatermark import removeWatermark

def preProcessPdf(filename, ORIGINAL_CONFIG):
    # Covert PDF to string by page
    with open(filename, "rb") as f:
        pdf = pdftotext.PDF(f)

    PDF_PAGES = len(pdf)

    # Check annotation and raise

    # Check multi config
    if ("Multipages" in ORIGINAL_CONFIG[0]):
        if (not ORIGINAL_CONFIG[0]['Multipages']):
            ORIGINAL_CONFIG[0] = ORIGINAL_CONFIG[0].get('1', '')

        if (str(PDF_PAGES) not in ORIGINAL_CONFIG[0]):
            print("You are using multi configs for multi pages. This file has a different page number than your configuration.")
            print("Would you like to continue extracting or edit config? (C: Continue extracting, E: Edit config)")
            choice = input("Your choice: ")
            while choice != "C" and choice != "E":
                print("You have entered a wrong option! Please choose one C: Continue extracting, E: Edit config.")
                choice = input("Your choice: ")

            if choice == 'C':
                pageConfigs = list(filter(lambda x: x != "Multipages", ORIGINAL_CONFIG[0].keys()))
                maxPages = max(pageConfigs, key=lambda x: int(x) < PDF_PAGES)
                print("We will use %s pages config for this file (%d pages)." % (maxPages, PDF_PAGES))
                ORIGINAL_CONFIG[0] = ORIGINAL_CONFIG[0][maxPages]

            elif choice == 'E':
                print("Please edit this config...")
                # Function for editting
                ORIGINAL_CONFIG[0] = {}

        else:
            ORIGINAL_CONFIG[0] = ORIGINAL_CONFIG[0][str(PDF_PAGES)]


    # Reset Current CONFIG
    CONFIG = ORIGINAL_CONFIG[0].copy()
    HF_CONFIG = ORIGINAL_CONFIG[1].copy()

    # Remove header & footer
    fullPdf = removeHeaderAndFooter(pdf, HF_CONFIG)

    # Join PDF
    fullPdf = [line for page in fullPdf for line in page if line != '']

    # Remove watrermark
    fullPdf, removed = removeWatermark(filename, fullPdf)
    # for line in fullPdf:
    #     print(line)
    return fullPdf, removed, CONFIG, HF_CONFIG, PDF_PAGES

if __name__ == '__main__':
    file = os.listdir()
    file = list(filter(lambda ef: ef[0] != "." and ef[-3:] == "pdf", file))
    # file = ["SBL_FDS_FDSLSGN190223OS.190219164902.pdf"]
    for filename in file:
        fullPdf = preProcessPdf(filename)

        if (fullPdf[0] != ""):
            with open(filename[:-3]+"txt", "w+") as f:
                for line in fullPdf:
                    f.write(line + '\n')
