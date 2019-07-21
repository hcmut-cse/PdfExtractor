import numpy as np
import re
from difflib import SequenceMatcher

def subfieldProcess(CONFIG, extractedData):
    # Process the subfields
    for key in CONFIG:
        if ('hasSubfield' in CONFIG[key]):
            if (CONFIG[key]['hasSubfield']):
                for subs in CONFIG[key]['subfields']:
                    pos = 0
                    reg = CONFIG[key]['subfields'][subs]
                    if (reg != 10):
                        result = re.search(reg, extractedData[key]).span()
                        extractedData[key + '_' + subs] = extractedData[key][result[0]:result[1]]
                        pos = result[1]
                    else:
                        extractedData[key+'_'+subs] = extractedData[key][pos:]
                del extractedData[key]

    return extractedData

def extractData(fullPdf, CONFIG, CURR_CONFIG):
    extracted = []
    # Extract data
    extractedData = {}
    for key in CONFIG:
        print(key)
        print('--------------')
        if (not CONFIG[key]['isFlex']): # For fixxed elements
            row = CURR_CONFIG[key]['row']
            column = CURR_CONFIG[key]['column']
        else:
            for margin in CONFIG[key]['endObject']:
                if (CONFIG[key]['endObject'][margin] == -1):
                    # If not define object for margin, it will use absolute location
                    continue
                else:
                    if (margin == 'top'):
                        # print("running top")
                        # Find nearest upper block
                        if (len(extracted) > 0):
                            keyIndex = -1
                            minDistance = len(fullPdf)
                            for keyE in extracted:
                                if (CONFIG[keyE]['row'][1] - 1 < CONFIG[key]['row'][0] and minDistance > abs(CONFIG[keyE]['row'][1] - CONFIG[key]['row'][0])):
                                    keyIndex = extracted.index(keyE)
                                    minDistance = abs(CONFIG[keyE]['row'][1] - CONFIG[key]['row'][0])

                            if (keyIndex == -1):
                                startRow = 0
                            else:
                                startRow = CURR_CONFIG[extracted[keyIndex]]['row'][1]
                        else:
                            startRow = 0

                        # Get keyword
                        if (CONFIG[key]['endObject']['top'][:4] == 'same'):
                            topFinding = CONFIG[key]['endObject'][CONFIG[key]['endObject']['top'][-4:]]
                            sameLine = 0
                        else:
                            topFinding = CONFIG[key]['endObject']['top']
                            sameLine = 1

                        # Find first row that has keyword from startRow
                        while (True):
                            if (re.search(topFinding, fullPdf[startRow])):
                                distance = startRow - CURR_CONFIG[key]['row'][0] + sameLine

                                for keyE in CURR_CONFIG:
                                    if (keyE != key and CONFIG[keyE]['row'][0] == CONFIG[key]['row'][0]):
                                        CURR_CONFIG[keyE]['row'][0] += distance

                                # Move current block
                                # for keyE in CURR_CONFIG:
                                #     if (keyE not in extracted and CURR_CONFIG[keyE]['row'][0] >= CURR_CONFIG[key]['row'][1] and keyE != key):
                                #         CURR_CONFIG[keyE]['row'] =  [i + distance for i in CURR_CONFIG[keyE]['row']]
                                # CURR_CONFIG[key]['row'][1] += distance
                                CURR_CONFIG[key]['row'][0] += distance
                                break;

                            else:
                                startRow += 1
                                if (startRow == len(fullPdf)):
                                    break
                        if (startRow == len(fullPdf)):
                            break


                            # Raise error
                    elif (margin == 'bottom'):
                        # Bottom object is under Top object
                        # print("running bottom")
                        startRow = CURR_CONFIG[key]['row'][0]
                        # print(CURR_CONFIG[key]['row'])
                        # Find first row that has keyword from startRow
                        while (True):
                            # print(CONFIG[key]['endObject']['bottom'])
                            # print(fullPdf[startRow])
                            if (re.search(CONFIG[key]['endObject']['bottom'], fullPdf[startRow])):
                                # print(startRow)
                                distance = startRow - CURR_CONFIG[key]['row'][1]
                                nearestKey = key
                                minDistance = len(fullPdf)

                                for keyE in CURR_CONFIG:
                                    if (keyE not in extracted and keyE != key and CONFIG[keyE]['row'][0] >= CONFIG[key]['row'][1]):
                                        if abs(CURR_CONFIG[keyE]['row'][0] - CURR_CONFIG[key]['row'][1]) < minDistance:
                                            nearestKey = keyE
                                            minDistance = abs(CURR_CONFIG[keyE]['row'][0] - CURR_CONFIG[key]['row'][1])
                                # print(nearestKey)

                                upperKey = key
                                minDistance = len(fullPdf)

                                for keyE in CURR_CONFIG:
                                    if (CONFIG[keyE]['row'][1] == None):
                                        continue
                                    if (keyE != key and keyE != nearestKey and CONFIG[keyE]['row'][1] <= CONFIG[nearestKey]['row'][0]):
                                        if abs(CURR_CONFIG[keyE]['row'][1] - CURR_CONFIG[nearestKey]['row'][0]) < minDistance:
                                            upperKey = keyE
                                            minDistance = abs(CURR_CONFIG[keyE]['row'][1] - CURR_CONFIG[nearestKey]['row'][0])

                                # print(distance)
                                # Find distance to move down
                                if (distance > 0):
                                    # print(CURR_CONFIG[upperKey]['row'][1] > CURR_CONFIG[key]['row'][0])
                                    if (CURR_CONFIG[upperKey]['row'][1] >= CURR_CONFIG[key]['row'][1] and CONFIG[upperKey]['row'][1] > CONFIG[key]['row'][0] and CURR_CONFIG[upperKey]['row'][1] < CURR_CONFIG[key]['row'][1] + distance):
                                        distance = CURR_CONFIG[key]['row'][1] + distance - CURR_CONFIG[upperKey]['row'][1]
                                    else:
                                        CURR_CONFIG[key]['row'][1] += distance
                                        break

                                # Find distance to move up and move under block up
                                elif (distance < 0):

                                    if (CURR_CONFIG[upperKey]['row'][1] > CURR_CONFIG[key]['row'][1] + distance):
                                        CURR_CONFIG[key]['row'][1] += distance
                                        distance = CURR_CONFIG[upperKey]['row'][1] - CONFIG[nearestKey]['row'][0]
                                        for keyE in CURR_CONFIG:
                                            if (keyE not in extracted and CURR_CONFIG[keyE]['row'][0] >= CURR_CONFIG[upperKey]['row'][1] and keyE != upperKey):

                                                CURR_CONFIG[keyE]['row'] =  [i + distance for i in CURR_CONFIG[keyE]['row']]
                                        break

                                else:
                                    break

                                print(distance)

                                # Move current block
                                for keyE in CURR_CONFIG:
                                    if (keyE not in extracted and CURR_CONFIG[keyE]['row'][0] >= CURR_CONFIG[key]['row'][1] and keyE != key):
                                        CURR_CONFIG[keyE]['row'] =  [i + distance for i in CURR_CONFIG[keyE]['row']]
                                CURR_CONFIG[key]['row'][1] += distance

                                break
                            else:
                                startRow += 1
                                if (startRow == len(fullPdf)):
                                    break

                    elif (margin == 'left'):
                        if (CURR_CONFIG[key]['column'][0] == None):
                            continue

                        # Get startRow to find left keyword
                        startRow = CURR_CONFIG[key]['row'][0]
                        leftFinding = CONFIG[key]['endObject'][margin]
                        # if (CONFIG[key]['endObject']['top'][:4] != 'same' and leftFinding.strip() != ""):
                        #     startRow -= 1

                        # Find first row that has key word
                        while (True):
                            if (re.search(leftFinding, fullPdf[startRow])):
                                break;
                            else:
                                startRow += 1
                                if (startRow == len(fullPdf)):
                                    break
                        if (startRow == len(fullPdf)):
                            continue

                        # Get startCol to find left keyword
                        if (len(extracted) > 0):
                            startCol = 0

                            for keyE in extracted:
                                if (CURR_CONFIG[keyE]['row'][0] > startRow):
                                    if (CURR_CONFIG[keyE]['column'][1] > startCol):
                                        startCol = CURR_CONFIG[keyE]['column'][1]

                        else:
                            startCol = 0

                        # print(key)
                        # Find left keyword and calculate distance
                        startCol = startCol + re.search(CONFIG[key]['endObject'][margin], fullPdf[startRow][startCol:]).span(0)[0]
                        distance = startCol + len(CONFIG[key]['endObject'][margin]) - CURR_CONFIG[key]['column'][0]

                        # Move other right block
                        for keyE in CURR_CONFIG:
                            if (keyE not in extracted and keyE != key and ((CURR_CONFIG[keyE]['row'][0] < CURR_CONFIG[key]['row'][1] and CURR_CONFIG[keyE]['row'][0] >= CURR_CONFIG[key]['row'][0])
                                                                        or (CURR_CONFIG[keyE]['row'][1] <= CURR_CONFIG[key]['row'][1] and CURR_CONFIG[keyE]['row'][1] > CURR_CONFIG[key]['row'][0]))):

                                for i in range(len(CURR_CONFIG[keyE]['column'])):
                                    if (CURR_CONFIG[keyE]['column'][i] != None):
                                        CURR_CONFIG[keyE]['column'][i] += distance
                                    else:
                                        CURR_CONFIG[keyE]['column'][i] = None

                        # Move current block
                        for i in range(len(CURR_CONFIG[key]['column'])):
                            if (CURR_CONFIG[key]['column'][i] != None):
                                CURR_CONFIG[key]['column'][i] += distance
                            else:
                                CURR_CONFIG[key]['column'][i] = None

                    elif (margin == 'right'):
                        if (CURR_CONFIG[key]['column'][1] == None):
                            continue

                        # Get startRow to find right keyword
                        startRow = CURR_CONFIG[key]['row'][0]
                        rightFinding = CONFIG[key]['endObject'][margin]
                        if (CONFIG[key]['endObject']['top'][:4] != 'same' and rightFinding.strip() != ""):
                            startRow -= 1

                        # Find first row that has key word
                        while (True):
                            if (re.search(rightFinding, fullPdf[startRow])):
                                break;
                            else:
                                startRow += 1
                                if (startRow == len(fullPdf)):
                                    break

                        if (startRow == len(fullPdf)):
                            continue

                        print(fullPdf[startRow][CURR_CONFIG[key]['column'][0]:])
                        # Find right keyword and calculate distance
                        startCol = CURR_CONFIG[key]['column'][0] + re.search(CONFIG[key]['endObject'][margin], fullPdf[startRow][CURR_CONFIG[key]['column'][0]:]).span(0)[0]
                        distance = startCol - CURR_CONFIG[key]['column'][1]

                        # Move other right block
                        for keyE in CURR_CONFIG:
                            if (keyE not in extracted and keyE != key and ((CURR_CONFIG[keyE]['row'][0] < CURR_CONFIG[key]['row'][1] and CURR_CONFIG[keyE]['row'][0] >= CURR_CONFIG[key]['row'][0])
                                                                        or (CURR_CONFIG[keyE]['row'][1] <= CURR_CONFIG[key]['row'][1] and CURR_CONFIG[keyE]['row'][1] > CURR_CONFIG[key]['row'][0]))):
                                for i in range(len(CURR_CONFIG[keyE]['column'])):
                                    if (CURR_CONFIG[keyE]['column'][i] != None):
                                        CURR_CONFIG[keyE]['column'][i] += distance
                                    else:
                                        CURR_CONFIG[keyE]['column'][i] = None

                        # Move current block
                        CURR_CONFIG[key]['column'][1] += distance

        # Get row and column
        row = CURR_CONFIG[key]['row']
        column = CURR_CONFIG[key]['column']

        # print(key)
        print(row)
        print(column)
        print(CURR_CONFIG)
        # Extract data and mark it as 'extracted'
        lines = fullPdf[row[0]:row[1]]
        dataBlock = []
        formalLeft = False
        formalRight = False
        # Correct column + get information
        for inform in lines:
            if (column[0] > 0 and len(inform[column[0]:column[1]]) > 0):
                if (inform[column[0]] != ' ' and inform[column[0] -1] == ' '):
                    formalLeft = True

                if (formalLeft and inform[column[0]] != ' ' and inform[column[0] - 1] != ' '):
                    # print(key)
                    i = 1
                    while (inform[column[0] - i] == ' '):
                        i += 1
                    dataBlock.append(inform[column[0] - i - 1:column[1]].strip())
                    continue
            # print(key)
            if (column[1] != None and len(inform[column[0]:column[1]]) > 0):
                if (column[1] < len(inform)):
                    # print(len(inform))
                    # print(column[1])
                    if (inform[column[1] - 1] == ' ' and inform[column[1]] != ' '):
                        formalRight = True

                    if (formalRight and inform[column[1]] != ' ' and inform[column[1] - 1] != ' '):
                        # print(key)
                        i = 1
                        while (inform[column[1] - i] == ' '):
                            i += 1
                        dataBlock.append(inform[column[0]:column[1] - i - 1].strip())
                        continue


            dataBlock.append(inform[column[0]:column[1]].strip())

        extractedData[key] = '\n'.join(dataBlock)
        print(extractedData[key])
        extracted.append(key)

    extractedData = subfieldProcess(CONFIG, extractedData)

    return extractedData
