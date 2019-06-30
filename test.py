import pdftotext
import json
import numpy as np
import os
import re
from difflib import SequenceMatcher

PDF_TYPE = "VN101466"
# CURR_CONFIG = {}
#
# with open(PDF_TYPE + '/' + PDF_TYPE + '.json', 'r', encoding='utf8') as json_file:
#     CONFIG = json.load(json_file)


fileName = list(filter(lambda pdf: pdf[-3:] == 'pdf' ,os.listdir(PDF_TYPE)))
# fileName = ["SI-SGNV27883400.pdf"]

if __name__ == '__main__':
    for file in fileName:
        # Reset Current CONFIG
        with open(PDF_TYPE + '/' + PDF_TYPE + '.json', 'r', encoding='utf8') as json_file:
            CONFIG = json.load(json_file)
        CURR_CONFIG = {}

        # Load PDF
        with open(PDF_TYPE + '/' + file, "rb") as f:
            pdf = pdftotext.PDF(f)

        # Remove header & footer
        if (len(pdf) > 1):
            fullPdf = []
            for i in range(len(pdf)):
                fullPdf.append(pdf[i].split('\n'))
            # Remove header
            row = 0
            continueRemove = True
            while (True):
                for i in range(len(fullPdf) - 1):
                    if (''.join(fullPdf[0][row].split()) != ''.join(fullPdf[i+1][row].split())):
                        continueRemove = False
                        break
                if (continueRemove):
                    for i in range(len(fullPdf)):
                        del(fullPdf[i][row])
                else:
                    break

            # Remove footer
            continueRemove = True
            while (True):
                row = [len(page)-1 for page in fullPdf]
                for i in range(len(fullPdf) - 1):
                    if SequenceMatcher(None, ''.join(fullPdf[0][row[0]].split()), ''.join(fullPdf[i+1][row[i+1]].split())).ratio() < 0.8:
                        continueRemove = False
                        break
                if (continueRemove):
                    for i in range(len(fullPdf)):
                        del(fullPdf[i][row[i]])
                else:
                    break
            fullPdf = [line for page in fullPdf for line in page]
        else:
            fullPdf = pdf[0].split('\n')

        print("Number of lines in PDF: %d" % len(fullPdf))

        # Sort CONFIG from top to bottom, from left to right
        configByColumn = dict(sorted(CONFIG.items(), key=lambda kv: kv[1]['column'][0]))
        CONFIG = dict(sorted(configByColumn.items(), key=lambda kv: kv[1]['row'][0]))
        # print(CONFIG)

        # Create config for current pdf
        for key in CONFIG:
            CURR_CONFIG[key] = {}
            CURR_CONFIG[key]['row'] = CONFIG[key]['row']
            CURR_CONFIG[key]['column'] = CONFIG[key]['column']
            # CURR_CONFIG[key]['extracted'] = False

        # Display fullPdf
        for i in fullPdf:
            print(i)

        extracted = []
        # Extract data
        extractedData = {}
        for key in CONFIG:
            # print(key)
            if (not CONFIG[key]['isFlex']): # For fixxed elements
                row = CURR_CONFIG[key]['row']
                column = CURR_CONFIG[key]['column']
            else:
                for margin in CONFIG[key]['endObject']:
                    if (CONFIG[key]['endObject'][margin] == -1):
                        # If not define object for margin, it will use absolute location
                        continue
                    else:
                        print(CURR_CONFIG[key]['row'])
                        if (margin == 'top'):
                            if (len(extracted) > 0):
                                keyIndex = -1
                                minDistance = len(fullPdf)
                                for keyE in extracted:
                                    if (CONFIG[keyE]['row'][1] - 1 < CONFIG[key]['row'][0] and minDistance > abs(CONFIG[keyE]['row'][1] - CONFIG[key]['row'][0])):
                                        keyIndex = extracted.index(keyE)
                                        minDistance = abs(CONFIG[keyE]['row'][1] - CONFIG[key]['row'][0])

                                print("KEY INDEX %d" % keyIndex)
                                if (keyIndex == -1):
                                    startRow = 0
                                else:
                                # keyIndex = np.argmin([abs(CONFIG[keyE]['row'][1] - CONFIG[key]['row'][0]) for keyE in extracted])
                                # print([abs(CURR_CONFIG[keyE]['row'][1] - CURR_CONFIG[key]['row'][0]) for keyE in extracted])
                                    startRow = CURR_CONFIG[extracted[keyIndex]]['row'][1]
                            else:
                                startRow = 0

                            if (CONFIG[key]['endObject']['top'][:4] == 'same'):
                                topFinding = CONFIG[key]['endObject'][CONFIG[key]['endObject']['top'][-4:]]
                                sameLine = 0
                            else:
                                topFinding = CONFIG[key]['endObject']['top']
                                sameLine = 1

                            print(topFinding)
                            print(fullPdf[startRow])
                            while (True):
                                if (re.search(topFinding, fullPdf[startRow])):
                                    distance = startRow - CURR_CONFIG[key]['row'][0] + sameLine

                                    # for keyE in CURR_CONFIG:
                                    #     if (keyE not in extracted and CURR_CONFIG[keyE]['row'][0] >= CURR_CONFIG[key]['row'][1] and keyE != key):
                                    #         print(keyE)
                                    #         CURR_CONFIG[keyE]['row'] =  [i + distance for i in CURR_CONFIG[keyE]['row']]

                                    # CURR_CONFIG[key]['row'] =  [i + distance for i in CURR_CONFIG[key]['row']]
                                    for keyE in CURR_CONFIG:
                                        if (keyE != key and CONFIG[keyE]['row'][0] == CONFIG[key]['row'][0]):
                                            CURR_CONFIG[keyE]['row'][0] += distance
                                    CURR_CONFIG[key]['row'][0] += distance
                                    break;
                                else:
                                    startRow += 1
                                    if (startRow == len(fullPdf)):
                                        break;

                        elif (margin == 'bottom'):
                            startRow = CURR_CONFIG[key]['row'][0] + 1

                            while (True):
                                if (re.search(CONFIG[key]['endObject']['bottom'], fullPdf[startRow])):
                                    distance = startRow - CURR_CONFIG[key]['row'][1]

                                    nearestKey = key
                                    minDistance = len(fullPdf)
                                    for keyE in CURR_CONFIG:
                                        if (keyE not in extracted and keyE != key and CONFIG[keyE]['row'][0] >= CONFIG[key]['row'][1]):
                                            if abs(CURR_CONFIG[keyE]['row'][0] - CURR_CONFIG[key]['row'][1]) < minDistance:
                                                nearestKey = keyE
                                                minDistance = abs(CURR_CONFIG[keyE]['row'][0] - CURR_CONFIG[key]['row'][1])
                                    print("NEAREST " + nearestKey)

                                    if (distance > 0):
                                        # print("lon hon 0")
                                        # Find nearest under block

                                        if (CURR_CONFIG[key]['row'][1] + distance > CURR_CONFIG[nearestKey]['row'][0] + 1):
                                            distance = CURR_CONFIG[key]['row'][1] - CURR_CONFIG[nearestKey]['row'][0] + distance - 1
                                        else:
                                            break
                                    elif (distance < 0): ## Problem
                                    #Tim kiem block nam tren, co row[1] thap nhat, dich chuyen cac vung ben duoi theo no
                                        # Find nearest upper blocks
                                        print("nho hon 0, diatance %d" % distance)
                                        upperKey = key
                                        minDistance = len(fullPdf)
                                        for keyE in CURR_CONFIG:
                                            if (keyE != key  and keyE != nearestKey and CONFIG[keyE]['row'][1] <= CONFIG[nearestKey]['row'][0]):
                                                # print(keyE)
                                                if abs(CURR_CONFIG[keyE]['row'][1] - CURR_CONFIG[nearestKey]['row'][0]) < minDistance:
                                                    upperKey = keyE
                                                    minDistance = abs(CURR_CONFIG[keyE]['row'][1] - CURR_CONFIG[nearestKey]['row'][0])
                                        print("UPPER " + upperKey)

                                        if (CURR_CONFIG[upperKey]['row'][1] > CURR_CONFIG[key]['row'][1] + distance):
                                            CURR_CONFIG[key]['row'][1] += distance
                                            print(CURR_CONFIG[key]['row'][1])
                                            distance = CURR_CONFIG[upperKey]['row'][1] - CONFIG[upperKey]['row'][1]
                                            print("New distance: %d" % distance)
                                            for keyE in CURR_CONFIG:
                                                if (keyE not in extracted and CURR_CONFIG[keyE]['row'][0] >= CURR_CONFIG[upperKey]['row'][1] and keyE != upperKey):
                                                    # print(keyE)
                                                    CURR_CONFIG[keyE]['row'] =  [i + distance for i in CURR_CONFIG[keyE]['row']]
                                            break

                                    else:
                                        break

                                    for keyE in CURR_CONFIG:
                                        if (keyE not in extracted and CURR_CONFIG[keyE]['row'][0] >= CURR_CONFIG[key]['row'][1] and keyE != key):
                                            CURR_CONFIG[keyE]['row'] =  [i + distance for i in CURR_CONFIG[keyE]['row']]
                                    CURR_CONFIG[key]['row'][1] += distance

                                    break;
                                else:
                                    startRow += 1
                                    # if ('ENDPAGE' in fullPdf[startRow]):
                                    #     distance = startRow - CURR_CONFIG[key]['row'][1]
                                    #     for keyE in CURR_CONFIG:
                                    #         if (keyE not in extracted and CURR_CONFIG[keyE]['row'][0] >= CURR_CONFIG[key]['row'][1] and keyE != key):
                                    #             CURR_CONFIG[keyE]['row'] =  [i + distance for i in CURR_CONFIG[keyE]['row']]
                                    #
                                    #     CURR_CONFIG[key]['row'][1] += distance
                                    if (startRow == len(fullPdf)):
                                        break;

                        elif (margin == 'left'):
                            if (CURR_CONFIG[key]['column'][0] == None):
                                continue
                            startCol = fullPdf[CURR_CONFIG[key]['row'][0]].index(CONFIG[key]['endObject'][margin])
                            distance = startCol + len(CONFIG[key]['endObject'][margin]) - CURR_CONFIG[key]['column'][0]
                            # print("TO push left: ")
                            for keyE in CURR_CONFIG:
                                if (keyE not in extracted and keyE != key and ((CURR_CONFIG[keyE]['row'][0] < CURR_CONFIG[key]['row'][1] and CURR_CONFIG[keyE]['row'][0] >= CURR_CONFIG[key]['row'][0])
                                                                            or (CURR_CONFIG[keyE]['row'][1] <= CURR_CONFIG[key]['row'][1] and CURR_CONFIG[keyE]['row'][1] > CURR_CONFIG[key]['row'][0]))):
                                    # print(keyE)
                                    for i in range(len(CURR_CONFIG[keyE]['column'])):
                                        if (CURR_CONFIG[keyE]['column'][i] != None):
                                            CURR_CONFIG[keyE]['column'][i] += distance
                                        else:
                                            CURR_CONFIG[keyE]['column'][i] = None

                            # print(CURR_CONFIG[key]['column'])
                            for i in range(len(CURR_CONFIG[key]['column'])):
                                if (CURR_CONFIG[key]['column'][i] != None):
                                    CURR_CONFIG[key]['column'][i] += distance
                                else:
                                    CURR_CONFIG[key]['column'][i] = None

                        elif (margin == 'right'):
                            if (CURR_CONFIG[key]['column'][1] == None):
                                continue
                            startCol = fullPdf[CURR_CONFIG[key]['row'][0]].index(CONFIG[key]['endObject'][margin])
                            distance = startCol - CURR_CONFIG[key]['column'][1]

                            for keyE in CURR_CONFIG:
                                if (keyE not in extracted and keyE != key and ((CURR_CONFIG[keyE]['row'][0] < CURR_CONFIG[key]['row'][1] and CURR_CONFIG[keyE]['row'][0] >= CURR_CONFIG[key]['row'][0])
                                                                            or (CURR_CONFIG[keyE]['row'][1] <= CURR_CONFIG[key]['row'][1] and CURR_CONFIG[keyE]['row'][1] > CURR_CONFIG[key]['row'][0]))):
                                    for i in range(len(CURR_CONFIG[keyE]['column'])):
                                        if (CURR_CONFIG[keyE]['column'][i] != None):
                                            CURR_CONFIG[keyE]['column'][i] += distance
                                        else:
                                            CURR_CONFIG[keyE]['column'][i] = None

                            CURR_CONFIG[key]['column'][1] += distance


                        # print(CURR_CONFIG[key]['row'])
                        row = CURR_CONFIG[key]['row']
                        column = CURR_CONFIG[key]['column']

            lines = fullPdf[row[0]:row[1]]
            extractedData[key] = '\n'.join([x[column[0]:column[1]].strip() for x in lines])
            extracted.append(key)


        # Print data extracted
        # for key in extractedData:
        #     print("------------------------------------")
        #     print("%s: %s" % (key, extractedData[key]))
        #     print("------------------------------------")

        # Save extracted result
        with open(PDF_TYPE + '/' + file[:-3] + 'txt', 'w', encoding='utf8') as resultFile:
            for key in extractedData:
                resultFile.write("------------------------------------\n")
                resultFile.write("%s:\n%s\n" % (key, extractedData[key]))
                resultFile.write("------------------------------------\n")
