from __future__ import division
import os
import json
import numpy as np
from preprocess import preProcessPdf
<<<<<<< HEAD
from processData import extractData

if __name__ == '__main__':
    PDF_TYPE = "1"
    fileName = list(filter(lambda pdf: pdf[-3:] == 'pdf' ,os.listdir('../' + PDF_TYPE)))
    # fileName = ["SGNV33817500.pdf"]
=======
from processData import extractData, connectContent
from posProcess import posProcessData
import pdftotext

if __name__ == '__main__':
    PDF_TYPE = "15"
    fileName = list(filter(lambda pdf: pdf[-3:].lower() == 'pdf' ,os.listdir('../' + PDF_TYPE)))
    # fileName = ["HANV06329700_6_mbl_swb.pdf"]

    with open('../' + PDF_TYPE + '/' + PDF_TYPE + '.json', 'r', encoding='utf8') as json_file:
        ORIGINAL_CONFIG = json.load(json_file)
>>>>>>> a622fea951ea90d7f49c43929d976a2f8e8b9315

    for file in fileName:
        print(file)
        # Reset Current CONFIG
        with open('../' + PDF_TYPE + '/' + PDF_TYPE + '.json', 'r', encoding='utf8') as json_file:
            CONFIG = json.load(json_file)
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
            CURR_CONFIG[key]['row'] = CONFIG[key]['row']
            CURR_CONFIG[key]['column'] = CONFIG[key]['column']

        # Preproces PDF
<<<<<<< HEAD
        fullPdf = preProcessPdf('../' + PDF_TYPE + '/' + file)
        # for line in fullPdf:
        #     print(line)
        # Extract data from PDF
        extractedData = extractData(file, fullPdf, CONFIG, CURR_CONFIG)
=======
        fullPdf, removed = preProcessPdf('../' + PDF_TYPE + '/' + file, HF_CONFIG)
        # for line in fullPdf:
        #     print(line)
        # Extract data from PDF
        extractedData = extractData(fullPdf, CONFIG, CURR_CONFIG, removed)
>>>>>>> a622fea951ea90d7f49c43929d976a2f8e8b9315

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
