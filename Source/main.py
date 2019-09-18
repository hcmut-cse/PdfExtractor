from __future__ import division
import argparse
import os
import json
import numpy as np
from preProcess import preProcessPdf
from processData import extractData
from posProcess import leftProcess, subfieldProcess
from connectContent import connectContent
import pdftotext

def checkFolder(string):
    currentDir = os.listdir('../')
    allFolder = [x for x in currentDir if os.path.isdir('../' + x)]
    if string in allFolder:
        return string
    else:
        # print("No folder named %s" % string)
        return -1

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--pdf_type', dest='pdf_type', type=checkFolder)
    args = parser.parse_args()

    PDF_TYPE = str(args.pdf_type)

    fileName = list(filter(lambda pdf: pdf[-3:].lower() == 'pdf' ,os.listdir('../' + PDF_TYPE)))
    # fileName = ["15.pdf"]

    for file in fileName:
        with open('../' + PDF_TYPE + '/' + PDF_TYPE + '.json', 'r', encoding='utf8') as json_file:
            ORIGINAL_CONFIG = json.load(json_file)

        print("========================================================")
        print(file)
        print("========================================================")

        print("- Pre-processing PDF for extracting...")
        CURR_CONFIG = {}
        CONFIG = {}
        HF_CONFIG = {}
        PDF_PAGES = 0

        # Preproces PDF
        fullPdf, removed, CONFIG, HF_CONFIG, PDF_PAGES = preProcessPdf('../' + PDF_TYPE + '/' + file, ORIGINAL_CONFIG)
        # for line in fullPdf:
        #     print(line)

        # Sort CONFIG from top to bottom, from left to right
        configByColumn = dict(sorted(CONFIG.items(), key=lambda kv: kv[1]['column'][0]))
        CONFIG = dict(sorted(configByColumn.items(), key=lambda kv: kv[1]['row'][0]))
        # print(CONFIG)

        # Create config for current pdf
        for key in CONFIG:
            CURR_CONFIG[key] = {}
            CURR_CONFIG[key]['row'] = CONFIG[key]['row'].copy()
            CURR_CONFIG[key]['column'] = CONFIG[key]['column'].copy()

        print("- Extracting information from PDF...")
        # Extract data from PDF
        extractedData = extractData(fullPdf, CONFIG, CURR_CONFIG, removed)

        print("- Pos-processing extracted data...")
        # Run pos-processing
        extractedData = leftProcess(CONFIG, extractedData)
        extractedData = subfieldProcess(CONFIG, extractedData)

        print("- Connecting similar contents...")
        # If pdf have multi pages, we will check similar content and connect them
        if (PDF_PAGES > 1):
            extractedData = connectContent(PDF_PAGES, extractedData)

        print("- Writting result to file...")
        # Save extracted result to file
        with open('../' + PDF_TYPE + '/' + file[:-3] + 'txt', 'w', encoding='utf8') as resultFile:
            for key in extractedData:
                resultFile.write("------------------------------------\n")
                resultFile.write("%s:\n%s\n" % (key, extractedData[key]))
                resultFile.write("------------------------------------\n")

        print("- Done!")
