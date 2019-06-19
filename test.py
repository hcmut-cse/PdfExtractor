import pdftotext
import json
import os
import re

PDF_TYPE = "VN101466"
CURR_CONFIG = {}

with open(PDF_TYPE + '/' + PDF_TYPE + '.json', 'r', encoding='utf8') as json_file:
    CONFIG = json.load(json_file)


fileName = list(filter(lambda pdf: pdf[-3:] == 'pdf' ,os.listdir(PDF_TYPE)))
fileName = ["SI_HANV08177300.pdf"]

if __name__ == '__main__':
    for file in fileName:
        # Reset Current CONFIG
        CURR_CONFIG = {}

        # Load PDF
        with open(PDF_TYPE + '/' + file, "rb") as f:
            pdf = pdftotext.PDF(f)


        fullPdf = '\n***ENDPAGE***\n'.join(pdf)
        fullPdf = fullPdf.split("\n")

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
        # for i in fullPdf:
        #     print(i)

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
                        # Kiểm tra tất cả trường đã extract (dùng filter với lambda)
                        # Tìm vị trí của 'top' margin bên dưới các trường đã extract
                        # Từ vị trí 'top' margin đã có, chạy xuống tìm 'bottom margin'
                        # Tương tự với left right
                        # Các thông số vị trí mới update lại vào CURR_CONFIG
                        if (margin == 'top'):
                            if (len(extracted) > 0):
                                rowIndex = min([abs(CURR_CONFIG[keyE]['row'][1] - CURR_CONFIG[key]['row'][0]) for keyE in extracted])
                            else:
                                rowIndex = 0
                            startRow = CURR_CONFIG[extracted[rowIndex]]['row'][1] + 1
                            while (True):
                                if (re.search(CONFIG[key]['endObject']['top'], fullPdf[startRow])):
                                    distance = startRow - CURR_CONFIG[key]['row'][0] + 1

                                    for keyE in CURR_CONFIG:
                                        if (keyE not in extracted and CURR_CONFIG[keyE]['row'][0] >= CURR_CONFIG[key]['row'][1] and keyE != key):
                                            CURR_CONFIG[keyE]['row'] =  [i + distance for i in CURR_CONFIG[keyE]['row']]

                                    CURR_CONFIG[key]['row'] =  [i + distance for i in CURR_CONFIG[key]['row']]
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

                                    for keyE in CURR_CONFIG:
                                        if (keyE not in extracted and CURR_CONFIG[keyE]['row'][0] >= CURR_CONFIG[key]['row'][1] and keyE != key):
                                            CURR_CONFIG[keyE]['row'] =  [i + distance for i in CURR_CONFIG[keyE]['row']]

                                    CURR_CONFIG[key]['row'][1] += distance
                                    break;
                                else:
                                    startRow += 1
                                    if ('***ENDPAGE***' in fullPdf[startRow]):
                                        distance = startRow - CURR_CONFIG[key]['row'][1]
                                        for keyE in CURR_CONFIG:
                                            if (keyE not in extracted and CURR_CONFIG[keyE]['row'][0] >= CURR_CONFIG[key]['row'][1] and keyE != key):
                                                CURR_CONFIG[keyE]['row'] =  [i + distance for i in CURR_CONFIG[keyE]['row']]

                                        CURR_CONFIG[key]['row'][1] += distance
                                        break;

                        elif (margin == 'left'):
                            if (CURR_CONFIG[key]['column'][0] == None):
                                continue
                            startCol = fullPdf[CURR_CONFIG[key]["row"][0]].index(CONFIG[key]['endObject'][margin])
                            distance = startCol - CURR_CONFIG[key]['column'][0]

                            for keyE in CURR_CONFIG:
                                if (keyE not in extracted and keyE != key
                                    and (CURR_CONFIG[keyE]['row'][0] <= CURR_CONFIG[key]['row'][1]
                                    or CURR_CONFIG[keyE]['row'][1] >= CURR_CONFIG[key]['row'][0])):
                                    CURR_CONFIG[keyE]['column'] = [i + distance for i in CURR_CONFIG[keyE]['column'] if i != None]

                            CURR_CONFIG[key]['column'] =  [i + distance for i in CURR_CONFIG[key]['column'] if i != None]
                        elif (margin == 'right'):
                            if (CURR_CONFIG[key]["row"][1] == None):
                                continue
                            startCol = fullPdf[CURR_CONFIG[key]["row"][1]].index(CONFIG[key]['endObject'][margin])
                            distance = startCol - CURR_CONFIG[key]['column'][1]

                            for keyE in CURR_CONFIG:
                                if (keyE not in extracted and keyE != key
                                    and (CURR_CONFIG[keyE]['row'][0] <= CURR_CONFIG[key]['row'][1]
                                    or CURR_CONFIG[keyE]['row'][1] >= CURR_CONFIG[key]['row'][0])):
                                    CURR_CONFIG[keyE]['column'] = [i + distance for i in CURR_CONFIG[keyE]['column'] if i != None]

                            CURR_CONFIG[key]['column'][1] += distance

                        row = CURR_CONFIG[key]['row']
                        column = CURR_CONFIG[key]['column']

            lines = fullPdf[row[0]:row[1]]
            extractedData[key] = '\n'.join([x[column[0]:column[1]] for x in lines])
            extracted.append(key)


        # Print data extracted
        # for key in extractedData:
        #     print("------------------------------------")
        #     print("%s: %s" % (key, extractedData[key]))
        #     print("------------------------------------")

        # Save extracted result
        # with open(PDF_TYPE + '/' + file[:-3] + 'txt', 'w+', encoding='utf8') as resultFile:
        #     for key in extractedData:
        #         resultFile.write("------------------------------------\n")
        #         resultFile.write("%s:\n%s\n" % (key, extractedData[key]))
        #         resultFile.write("------------------------------------\n")
