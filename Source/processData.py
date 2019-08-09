import numpy as np
import re
from difflib import SequenceMatcher

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()
def longestSubstringFinder(string1, string2):
    answer = ""
    len1, len2 = len(string1), len(string2)
    for i in range(len1):
        match = ""
        for j in range(len2):
            if (i + j < len1 and string1[i + j] == string2[j]):
                match += string2[j]
            else:
                if (len(match) > len(answer)): answer = match
                match = ""
    return answer
def connectContent(length, extractedData):
    count = 0
    string = {}
    stringValue = []
    if (length == 2):
        for key1 in list(extractedData):
            for key2 in list(extractedData):
                if (". . . . . . ." not in key2):
                    if (len(key1) > 4):
                        ratio = similar(key1, key2)
                        if (ratio >= 0.9 and ratio < 1):
                            count = count + 1
                            commonString = longestSubstringFinder(key1, key2)
                            content = extractedData[key1] + extractedData[key2]
                            extractedData[commonString] = content
                            del extractedData[key1]
                            del extractedData[key2]
                    elif (2 < len(key1) <= 4):
                        ratio = similar(key1, key2)
                        if (ratio >= 0.75):
                            count = count + 1
                            commonString = longestSubstringFinder(key1, key2)
                            content = extractedData[key1] + extractedData[key2]
                            extractedData[commonString] = content
                            #del extractedData[key1]
                            #del extractedData[key2]
            if (count == 6):
                break

def leftProcess(CONFIG, extractedData):
    #Process data with top = same_left
    for key in CONFIG:
        if (CONFIG[key]['endObject']['top'] == 'same_left' and key in extractedData):
            # Delete keyword at the beggining of the string
            length = len(key)
            # print(extractedData[key][0:length])
            if (extractedData[key][0:length] == key):
                extractedData[key] = extractedData[key][length:]
            # Delete potential blanks
            extractedData[key] = extractedData[key].lstrip()
            # Delete colon ":" if exist
            if (extractedData[key][:1] == ":"):
                extractedData[key] = extractedData[key][1:]
            # Delete leftover blanks
            extractedData[key] = extractedData[key].lstrip()
    return extractedData

def subfieldProcess(CONFIG, extractedData):
    # Process the subfields
    for key in CONFIG:
        if ('hasSubfield' in CONFIG[key]):
            if (CONFIG[key]['hasSubfield']):
                for subs in CONFIG[key]['subfields']:
                    pos = 0
                    reg = CONFIG[key]['subfields'][subs]
                    if (reg != 10):
                        result1 = re.search(reg, extractedData[key])
                        if (result1 is not None):
                            result = re.search(reg, extractedData[key]).span()
                            extractedData[key + '_' + subs] = extractedData[key][result[0]:result[1]]
                            pos = result[1]
                    else:
                        extractedData[key+'_'+subs] = extractedData[key][pos:]
                del extractedData[key]

    return extractedData

def extractData(fullPdf, CONFIG, CURR_CONFIG, removed):
    extracted = []
    # Extract data
    extractedData = {}
    for key in CONFIG:
        error = False
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
                        nearestUpperKey = key
                        if (len(extracted) > 0):
                            keyIndex = -1
                            minDistance = len(fullPdf)
                            for keyE in extracted:
                                if CONFIG[keyE]['row'][1] == None:
                                    continue
                                tempDis = abs(CONFIG[keyE]['row'][1] - CONFIG[key]['row'][0])
                                if (CONFIG[keyE]['row'][1] - 1 < CONFIG[key]['row'][0] and minDistance > tempDis and CONFIG[keyE]['row'][0] != CONFIG[key]['row'][0]):
                                    keyIndex = extracted.index(keyE)
                                    minDistance = tempDis

                            if (keyIndex == -1):
                                startRow = 0
                            else:
                                # print(extracted[keyIndex])
                                nearestUpperKey = extracted[keyIndex]
                                startRow = CURR_CONFIG[nearestUpperKey]['row'][1]
                        else:
                            startRow = 0

                        nearestLowerKey = key
                        minDistance = len(fullPdf)
                        for keyE in CURR_CONFIG:
                            if CONFIG[key]['row'][1] == None:
                                continue
                            if (keyE not in extracted and keyE != key and CONFIG[keyE]['row'][0] >= CONFIG[key]['row'][1]):
                                if abs(CURR_CONFIG[keyE]['row'][0] - CURR_CONFIG[key]['row'][1]) < minDistance:
                                    nearestLowerKey = keyE
                                    minDistance = abs(CURR_CONFIG[keyE]['row'][0] - CURR_CONFIG[key]['row'][1])

                        # print(startRow)
                        # Get keyword
                        if (CONFIG[key]['endObject']['top'][:4] == 'same'):
                            topFinding = CONFIG[key]['endObject'][CONFIG[key]['endObject']['top'][5:]]
                            sameLine = 0
                        else:
                            topFinding = CONFIG[key]['endObject']['top']
                            sameLine = 1

                        someProblem = False
                        # Find first row that has keyword from startRow
                        while (True):
                            # print(fullPdf[startRow])
                            if (re.search(topFinding, fullPdf[startRow])):
                                # print("TOPFOUNED")
                                # print(startRow)
                                if (nearestLowerKey != key and startRow > CURR_CONFIG[nearestLowerKey]['row'][0] + 1):
                                    print(startRow)
                                    print(nearestLowerKey)
                                    print(CURR_CONFIG[nearestLowerKey]['row'][0])
                                    someProblem = True
                                    break

                                distance = startRow - CURR_CONFIG[key]['row'][0] + sameLine
                                # print("top distance " + str(distance))
                                for keyE in CURR_CONFIG:
                                    if (keyE != key and keyE not in extracted and CURR_CONFIG[keyE]['row'][0] == CURR_CONFIG[key]['row'][0]):
                                        CURR_CONFIG[keyE]['row'][0] += distance
                                        if (CURR_CONFIG[keyE]['row'][1] != None):
                                            CURR_CONFIG[keyE]['row'][1] += distance

                                # Move current block
                                if (CURR_CONFIG[key]['row'][1] != None):
                                    # print(distance)
                                    for keyE in CURR_CONFIG:
                                        if (keyE not in extracted and keyE != key and CURR_CONFIG[keyE]['row'][0] != CURR_CONFIG[key]['row'][0] + distance):
                                            # print(keyE and CURR_CONFIG[keyE]['row'][0] >= CURR_CONFIG[key]['row'][1]
                                            for i, val in enumerate(CURR_CONFIG[keyE]['row']):
                                                if val != None:
                                                    CURR_CONFIG[keyE]['row'][i] =  val + distance
                                                else:
                                                    CURR_CONFIG[keyE]['row'][i] = None
                                    CURR_CONFIG[key]['row'][1] += distance
                                CURR_CONFIG[key]['row'][0] += distance
                                print(CURR_CONFIG)
                                break;

                            else:
                                startRow += 1
                                if (startRow == len(fullPdf)):
                                    break
                        # print(startRow - CURR_CONFIG[nearestKey]['row'][1])
                        if (someProblem):
                            toFind = [k for k in removed]
                            for tf in toFind:
                                if key in tf:
                                    startRow = removed[tf][0] + 1

                                    distance = startRow - CURR_CONFIG[key]['row'][0] + sameLine
                                    for keyE in CURR_CONFIG:
                                        if (keyE != key and keyE not in extracted and CURR_CONFIG[keyE]['row'][0] == CURR_CONFIG[key]['row'][0]):
                                            CURR_CONFIG[keyE]['row'][0] += distance
                                            if (CURR_CONFIG[keyE]['row'][1] != None):
                                                CURR_CONFIG[keyE]['row'][1] += distance

                                    # Move current block
                                    if (CURR_CONFIG[key]['row'][1] != None):
                                        for keyE in CURR_CONFIG:
                                            if (keyE not in extracted and keyE != key and CURR_CONFIG[keyE]['row'][0] != CURR_CONFIG[key]['row'][0] + distance):
                                                for i, val in enumerate(CURR_CONFIG[keyE]['row']):
                                                    if val != None:
                                                        CURR_CONFIG[keyE]['row'][i] =  val + distance
                                                    else:
                                                        CURR_CONFIG[keyE]['row'][i] = None
                                        CURR_CONFIG[key]['row'][1] += distance
                                    CURR_CONFIG[key]['row'][0] += distance

                                    break
                            if (startRow > CURR_CONFIG[nearestLowerKey]['row'][0] + 1):
                                error = 1

                        print(error)
                    elif (margin == 'bottom'):
                        # Bottom object is under Top object
                        # print("running bottom")
                        startRow = CURR_CONFIG[key]['row'][0]
                        # if (re.search(CONFIG[key]['endObject']['bottom'], fullPdf[startRow - (CONFIG[key]['endObject']['top'][:4] != 'same')])):
                        #     error = True
                        # print(startRow)
                        # Find first row that has keyword from startRow
                        while (True):
                            # print(CONFIG[key]['endObject']['bottom'])
                            # print(fullPdf[startRow])
                            if (re.search(CONFIG[key]['endObject']['bottom'], fullPdf[startRow])):
                                # print("BOTFOUNDED")
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
                                    elif (CURR_CONFIG[upperKey]['row'][1] < CURR_CONFIG[key]['row'][1]):
                                        pass
                                    else:
                                        # print("DCMMMMMMM")
                                        CURR_CONFIG[key]['row'][1] += distance
                                        break

                                # Find distance to move up and move under block up
                                elif (distance < 0):
                                    # print('UPPER: ' + upperKey)
                                    # print(CURR_CONFIG[upperKey]['row'][1])
                                    # print(CURR_CONFIG[key]['row'][1] + distance)
                                    if (CURR_CONFIG[upperKey]['row'][1] < CURR_CONFIG[key]['row'][1] + distance):
                                        CURR_CONFIG[key]['row'][1] += distance
                                        distance = CURR_CONFIG[upperKey]['row'][1] - CONFIG[nearestKey]['row'][0]
                                        for keyE in CURR_CONFIG:
                                            if (keyE not in extracted and CURR_CONFIG[keyE]['row'][0] >= CURR_CONFIG[upperKey]['row'][1] and keyE != upperKey and CONFIG[keyE]['row'][0] != CONFIG[key]['row'][0]):
                                                # print(keyE)
                                                for i, val in enumerate(CURR_CONFIG[keyE]['row']):
                                                    if val != None:
                                                        CURR_CONFIG[keyE]['row'][i] =  val + distance
                                                    else:
                                                        CURR_CONFIG[keyE]['row'][i] = None
                                        # print(CURR_CONFIG)
                                        break

                                else:
                                    break

                                # print(distance)

                                # Move current block
                                for keyE in CURR_CONFIG:
                                    if (keyE not in extracted and CURR_CONFIG[keyE]['row'][0] >= CURR_CONFIG[key]['row'][1] and keyE != key):
                                        for i, val in enumerate(CURR_CONFIG[keyE]['row']):
                                            if val != None:
                                                CURR_CONFIG[keyE]['row'][i] =  val + distance
                                            else:
                                                CURR_CONFIG[keyE]['row'][i] = None
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
                                break
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
                                if CURR_CONFIG[keyE]['row'][1] == None:
                                    continue
                                if (CURR_CONFIG[keyE]['row'][1] > CURR_CONFIG[key]['row'][0]):
                                    if (CURR_CONFIG[keyE]['column'][1] != None):
                                        if (CURR_CONFIG[keyE]['column'][1] > startCol):
                                            startCol = CURR_CONFIG[keyE]['column'][1]

                        else:
                            startCol = 0

                        # print("startCol: " + str(startCol))
                        # print(fullPdf[startRow][startCol:])
                        # Find left keyword and calculate distance
                        # startCol = startCol + re.search(CONFIG[key]['endObject'][margin], fullPdf[startRow][startCol:]).span(0)[0]
                        leftObj = re.search(CONFIG[key]['endObject'][margin], fullPdf[startRow][startCol:])
                        if (leftObj != None):
                            startCol = startCol + leftObj.span(0)[0] + len(CONFIG[key]['endObject'][margin])
                            # print("startCol: "+str(startCol))
                            distance = startCol - CURR_CONFIG[key]['column'][0]
                        # else:
                        #     distance = startCol -

                        # Move other right block
                        for keyE in CURR_CONFIG:
                            if (CURR_CONFIG[keyE]['row'][1] != None and CURR_CONFIG[key]['row'][1] != None):
                                if (keyE not in extracted and keyE != key and ((CONFIG[keyE]['row'][0] < CONFIG[key]['row'][1] and CONFIG[keyE]['row'][0] >= CONFIG[key]['row'][0])
                                                                            or (CONFIG[keyE]['row'][1] <= CONFIG[key]['row'][1] and CONFIG[keyE]['row'][1] > CONFIG[key]['row'][0]))):

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
                        # If top = same_left
                        if (CONFIG[key]['endObject']['top'][:4] == 'same'):
                            for line in fullPdf:
                                if line.find(key)!=-1:
                                    CURR_CONFIG[key]['column'][0] = line.find(key)
                                    break

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

                        if (re.search(CONFIG[key]['endObject'][margin], fullPdf[startRow][CURR_CONFIG[key]['column'][0]:]) == None):
                            break
                        # Find right keyword and calculate distance
                        startCol = CURR_CONFIG[key]['column'][0] + re.search(CONFIG[key]['endObject'][margin], fullPdf[startRow][CURR_CONFIG[key]['column'][0]:]).span(0)[0]
                        distance = startCol - CURR_CONFIG[key]['column'][1]

                        # Move other right block
                        for keyE in CURR_CONFIG:
                            # print(CURR_CONFIG[keyE]['row'][1])
                            if (CURR_CONFIG[keyE]['row'][1] != None and CURR_CONFIG[key]['row'][1] != None):
                                if (keyE not in extracted and keyE != key and ((CONFIG[keyE]['row'][0] < CONFIG[key]['row'][1] and CONFIG[keyE]['row'][0] >= CONFIG[key]['row'][0])
                                                                            or (CONFIG[keyE]['row'][1] <= CONFIG[key]['row'][1] and CONFIG[keyE]['row'][1] > CONFIG[key]['row'][0]))):
                                    # print(keyE)
                                    for i in range(len(CURR_CONFIG[keyE]['column'])):
                                        if (CURR_CONFIG[keyE]['column'][i] != None):
                                            CURR_CONFIG[keyE]['column'][i] += distance
                                        else:
                                            CURR_CONFIG[keyE]['column'][i] = None

                        # Move current block
                        CURR_CONFIG[key]['column'][1] += distance


        if (error):
            del CURR_CONFIG[key]
            extractedData[key] = "ERROR"
            continue
        # Get row and column
        row = CURR_CONFIG[key]['row']
        column = CURR_CONFIG[key]['column']

        # print(key)
        print(row)
        print(column)
        print(CURR_CONFIG)
        # Extract data and mark it as 'extracted'
        lines = fullPdf[row[0]:row[1]]
        # print(lines[column[0]:column[1]])
        dataBlock = []
        formalLeft = True
        formalRight = True
        distance = 0
        # Correct column + get information
        for inform in lines:
            if (column[0] > 0 and len(inform[column[0]:column[1]]) > 0):
                if (inform[column[0]] != ' ' and inform[column[0] - 1] == ' '):
                    formalLeft = True

                if (formalLeft and inform[column[0]] != ' ' and inform[column[0] - 1] != ' '):
                    # print(key)
                    i = 1
                    while (inform[column[0] - i] != ' '):
                        if i == column[0]:
                            i = 0
                            break
                        i += 1
                    column[0] = column[0] - i - 1
                    CURR_CONFIG[key]['column'][0] = column[0]
                    # dataBlock.append(inform[column[0]:column[1]].strip())
                    # continue
            # print(key)
            if (column[1] != None and len(inform[column[0]:column[1]]) > 0):
                if (column[1] < len(inform)):
                    # print(len(inform))
                    # print(column[1])
                    if (inform[column[1] - 1] == ' ' and inform[column[1]] != ' '):
                        formalRight = True

                    if (formalRight and inform[column[1]] != ' ' and inform[column[1] - 1] != ' '):
                        i = 1
                        # print(inform[column[1]])
                        while (inform[column[1] - i] != ' '):
                            i += 1
                            # if column[1] - i == column[0]:
                            #     break
                        # print(i)
                        column[1] = column[1] - i
                        CURR_CONFIG[key]['column'][1] = column[1]
                        distance += i

        for keyE in CURR_CONFIG:
            if (CURR_CONFIG[keyE]['row'][1] != None and CURR_CONFIG[key]['row'][1] != None):
                if (keyE not in extracted and keyE != key and ((CURR_CONFIG[keyE]['row'][0] < CURR_CONFIG[key]['row'][1] and CURR_CONFIG[keyE]['row'][0] >= CURR_CONFIG[key]['row'][0])
                                                            or (CURR_CONFIG[keyE]['row'][1] <= CURR_CONFIG[key]['row'][1] and CURR_CONFIG[keyE]['row'][1] > CURR_CONFIG[key]['row'][0]))):
                    # print(keyE)
                    for k in range(len(CURR_CONFIG[keyE]['column'])):
                        if (CURR_CONFIG[keyE]['column'][k] != None):
                            CURR_CONFIG[keyE]['column'][k] -= distance
                        else:
                            CURR_CONFIG[keyE]['column'][k] = None
                        # dataBlock.append(inform[column[0]:column[1]].strip())
                        # continue

            # print(column)
            # dataBlock.append(inform[column[0]:column[1]].strip())
        dataBlock = [line[column[0]:column[1]].strip() for line in lines]

        # print(CURR_CONFIG)

        extractedData[key] = '\n'.join(dataBlock)
        print(extractedData[key])
        extracted.append(key)

    extractedData = leftProcess(CONFIG, extractedData)
    extractedData = subfieldProcess(CONFIG, extractedData)

    return extractedData
