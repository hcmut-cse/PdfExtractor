from __future__ import division
import argparse
import os
import json
import numpy as np
from preprocess import preProcessPdf
from processData import extractData
from posProcess import posProcessData
import pdftotext

def checkFolder(string):
    currentDir = os.listdir('../')
    allFolder = [x for x in currentDir if os.path.isdir('../' + x)]
    if string in allFolder:
        return string
    else:
        print("No folder named %s" % string)
        return -1

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--pdf_type', dest='pdf_type', type=checkFolder)
    args = parser.parse_args()

    PDF_TYPE = str(args.pdf_type)

    fileName = list(filter(lambda pdf: pdf[-3:].lower() == 'pdf' ,os.listdir('../' + PDF_TYPE)))
    # fileName = ["VN102347_50.pdf"]

    with open('../' + PDF_TYPE + '/' + PDF_TYPE + '.json', 'r', encoding='utf8') as json_file:
        ORIGINAL_CONFIG = json.load(json_file)

    for file in fileName:
        print(file)

        # Reset Current CONFIG
        CONFIG = ORIGINAL_CONFIG[0].copy()
        HF_CONFIG = ORIGINAL_CONFIG[1].copy()
        CURR_CONFIG = {}

        if (PDF_TYPE == "15"):
            with open('../' + PDF_TYPE + '/' + file, "rb") as f:
                pdf = pdftotext.PDF(f)
            if (len(pdf) == 2):
                CONFIG = CONFIG["multi"]
            elif (len(pdf) == 3):
                CONFIG = CONFIG["3"]
            elif (len(pdf) == 1):
                CONFIG = CONFIG["1"]

        # Sort CONFIG from top to bottom, from left to right
        configByColumn = dict(sorted(CONFIG.items(), key=lambda kv: kv[1]['column'][0]))
        CONFIG = dict(sorted(configByColumn.items(), key=lambda kv: kv[1]['row'][0]))
        # print(CONFIG)

        # Create config for current pdf
        for key in CONFIG:
            CURR_CONFIG[key] = {}
            CURR_CONFIG[key]['row'] = CONFIG[key]['row'].copy()
            CURR_CONFIG[key]['column'] = CONFIG[key]['column'].copy()

        # Preproces PDF
        fullPdf, removed = preProcessPdf('../' + PDF_TYPE + '/' + file, HF_CONFIG)
        for line in fullPdf:
            print(line)
        # Extract data from PDF
        extractedData = extractData(fullPdf, CONFIG, CURR_CONFIG, removed)

        extractedData = posProcessData(extractedData, CURR_CONFIG, removed)

        if (PDF_TYPE == 15):
            length = len(pdf)
            if (length > 1):
                connectContent(length, extractedData)
        # for word in removed:
        #     if (removed[word])
        # Save extracted result to file
        with open('../' + PDF_TYPE + '/' + file[:-3] + 'txt', 'w', encoding='utf8') as resultFile:
            for key in extractedData:
                resultFile.write("------------------------------------\n")
                resultFile.write("%s:\n%s\n" % (key, extractedData[key]))
                resultFile.write("------------------------------------\n")
