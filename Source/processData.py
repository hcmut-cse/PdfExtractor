import numpy as np
import re
from difflib import SequenceMatcher
from posProcess import posProcessData

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

def extractData(fullPdf, CONFIG, CURR_CONFIG, removed):
    extracted = []
    # Extract data
    extractedData = {}
    synonymUsing={}
    for key in CONFIG:
        foundSynonym=0
        # if ('alias' in CONFIG[key]):
        #     for synonym in CONFIG[key]['alias']:
        #         name = CONFIG[key]['alias'][synonym]['name']
        #
        #         nearestKey = key
        #         minDistance = len(fullPdf)
        #
        #         for keyE in CURR_CONFIG:
        #             if (keyE not in extracted and keyE != key and CONFIG[keyE]['row'][0] >= CONFIG[key]['row'][1]):
        #                 if abs(CURR_CONFIG[keyE]['row'][0] - CURR_CONFIG[key]['row'][1]) < minDistance:
        #                     nearestKey = keyE
        #                     minDistance = abs(CURR_CONFIG[keyE]['row'][0] - CURR_CONFIG[key]['row'][1])
        #         # print(nearestKey)
        #
        #         upperKey = key
        #         minDistance = len(fullPdf)
        #
        #         for keyE in CURR_CONFIG:
        #             if (CONFIG[keyE]['row'][1] == None):
        #                 continue
        #             if (keyE != key and keyE != nearestKey and CONFIG[keyE]['row'][1] <= CONFIG[nearestKey]['row'][0]):
        #                 if abs(CURR_CONFIG[keyE]['row'][1] - CURR_CONFIG[nearestKey]['row'][0]) < minDistance:
        #                     upperKey = keyE
        #                     minDistance = abs(CURR_CONFIG[keyE]['row'][1] - CURR_CONFIG[nearestKey]['row'][0])
        #
        #
        #         upperLine = CURR_CONFIG[upperKey]['row'][1]
        #         lowerLine = CURR_CONFIG[nearestKey]['row'][0]
        #         # print(upperKey)
        #         # print(nearestKey)
        #         # print(fullPdf[upperLine:lowerLine])
        #         for line in fullPdf[upperLine:lowerLine]:
        #             if line.find(name)!=-1:
        #                 if (CONFIG[key]['endObject']['top'][:4] == "same"):
        #                     CONFIG[key]['endObject'][CONFIG[key]['endObject']['top'][5:]] = name
        #                     CURR_CONFIG[key]['endObject'][CONFIG[key]['endObject']['top'][5:]] = name
        #                 else:
        #                     CONFIG[key]['endObject']['top'] = name
        #                     CURR_CONFIG[key]['endObject']['top'] = name
        #                 foundSynonym=1
        #                 break
        #         if (foundSynonym):
        #             break
        error = False
        # print(key)
        # print('-----------------------------------------')
        # print(CURR_CONFIG)
        if (not CONFIG[key]['isFlex']): # For fixxed elements
            row = CURR_CONFIG[key]['row']
            column = CURR_CONFIG[key]['column']

        elif ("isCenter" in CONFIG[key]):

            key_top = -1

            for margin in CONFIG[key]['endObject']:
                if (CONFIG[key]['endObject'][margin] == -1):
                    # If not define object for margin, it will use absolute location
                    continue
                else:
                    if (margin == 'top'):
                        # print("running top")
                        # Find nearest upper block
                        nearestKey = key
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
                                nearestKey = extracted[keyIndex]
                                startRow = CURR_CONFIG[nearestKey]['row'][1]
                        else:
                            startRow = 0

                        # print(startRow)
                        # Get keyword
                        if (CONFIG[key]['endObject']['top'][:4] == 'same'):
                            topFinding = CONFIG[key]['endObject'][CONFIG[key]['endObject']['top'][5:]]
                            sameLine = 0
                        else:
                            topFinding = CONFIG[key]['endObject']['top']
                            sameLine = 1

                        # Find first row that has keyword from startRow
                        while (True):
                            # print(fullPdf[startRow])
                            key_top = re.search(topFinding, fullPdf[startRow])
                            if (key_top):
                                # print(startRow)
                                # if (startRow > CURR_CONFIG[nearestKey]['row'][0] and nearestKey != key):
                                    # print("DCM startrow")
                                    # break
                                distance = startRow - CURR_CONFIG[key]['row'][0] + sameLine
                                # print("top distance " + str(distance))
                                for keyE in CURR_CONFIG:
                                    if (keyE != key and keyE not in extracted and CURR_CONFIG[keyE]['row'][0] == CURR_CONFIG[key]['row'][0]):
                                        CURR_CONFIG[keyE]['row'][0] += distance
                                        if (CURR_CONFIG[keyE]['row'][1] != None):
                                            CURR_CONFIG[keyE]['row'][1] += distance

                                # Move current block
                                if (CURR_CONFIG[key]['row'][1] != None):
                                    for keyE in CURR_CONFIG:
                                        if (keyE not in extracted and CURR_CONFIG[keyE]['row'][0] >= CURR_CONFIG[key]['row'][1] and keyE != key and CURR_CONFIG[keyE]['row'][0] != CURR_CONFIG[key]['row'][0] + distance):
                                            for i, val in enumerate(CURR_CONFIG[keyE]['row']):
                                                if val != None:
                                                    CURR_CONFIG[keyE]['row'][i] =  val + distance
                                                else:
                                                    CURR_CONFIG[keyE]['row'][i] = None
                                    CURR_CONFIG[key]['row'][1] += distance
                                CURR_CONFIG[key]['row'][0] += distance
                                break;

                            else:
                                startRow += 1
                                if (startRow == len(fullPdf)):
                                    break
                        # print(startRow - CURR_CONFIG[nearestKey]['row'][1])
                        # if (CURR_CONFIG[key]['row'][1] != None):
                        #     if (startRow > CURR_CONFIG[key]['row'][1]):


                        # print("TOP " + str(CURR_CONFIG[key]['row'][0]))

                            # Raise error

                    elif (margin == 'bottom'):
                        # Bottom object is under Top object
                        # print("running bottom")
                        startRow = CURR_CONFIG[key]['row'][0]
                        if (re.search(CONFIG[key]['endObject']['bottom'], fullPdf[startRow - (CONFIG[key]['endObject']['top'][:4] != 'same')])):
                            error = True
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
                                            if (keyE not in extracted and CURR_CONFIG[keyE]['row'][0] >= CURR_CONFIG[upperKey]['row'][1] and keyE != upperKey and CONFIG[keyE]['row'][0] != CONFIG[key]['row'][0]):
                                                for i, val in enumerate(CURR_CONFIG[keyE]['row']):
                                                    if val != None:
                                                        CURR_CONFIG[keyE]['row'][i] =  val + distance
                                                    else:
                                                        CURR_CONFIG[keyE]['row'][i] = None
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

            # Đã xong top vaf bottom
            key_left = CONFIG[key]['endObject']['left']
            key_right = CONFIG[key]['endObject']['right']

            # print("CURR_CONFIG[key]['row'][0]:",CURR_CONFIG[key]['row'][0])
            # print("CURR_CONFIG[key]['row'][1]:",CURR_CONFIG[key]['row'][1])
            # Đã có row mới, lúc này chưa cập nhật column
            # Xử lý center
            start_row, end_row = CURR_CONFIG[key]['row']
            column_temp = []
            column_temp.append(key_top.start())
            column_temp.append(key_top.end())


            # Find position of current, left and right key
            min_column = 0
            max_column_t = 0
            max_column = 0

            temp_pdf = fullPdf
            for line in temp_pdf:
                if not (key_left == -1):
                    kl = re.search(key_left, line)
                    if (kl):
                        min_column = kl.end()
                else:
                    min_column = 0

                if not (key_right == -1):
                    kr = re.search(key_right, line)
                    if (kr):
                        max_column = kr.start()
                else:
                    max_column_t = "max"

            #take datablock
            multilines = fullPdf[start_row:end_row]

            #take datablock
            lines = []
            for line in multilines:
                if (max_column_t == "max"):
                    temp = line[min_column:]
                else:
                    temp = line[min_column:max_column]

                temp = re.sub("[\s]+","",temp)
                if temp == "":
                    continue

                if (max_column_t == "max"):
                    lines.append(line[min_column:])
                else:
                    lines.append(line[min_column:max_column])

            num = 1
            # print(min_column,column_temp,max_column)

            rights = []
            lefts = []
            for line in lines:

                # print("line:","|",line,"|")
                if (max_column_t == "max"):
                    temp = re.sub("[\s]+","",line[column_temp[1] - min_column:len(line)])
                    if not temp == "":
                        rights.append(line[column_temp[1] - min_column:len(line)])

                    #print("right:","|",line[column_temp[1] - min_column:len(line)],"|")
                else:
                    temp = re.sub("[\s]+","",line[column_temp[1] - min_column:max_column - min_column])
                    if not temp == "":
                        rights.append(line[column_temp[1] - min_column:max_column - min_column])

                    #print("right:","|",line[column_temp[1] - min_column:max_column - min_column],"|")
                temp = re.sub("[\s]+","",line[:column_temp[1] - min_column])
                if not temp == "":
                    lefts.append(line[:column_temp[1] - min_column])

                #print("left:","|",line[min_column - min_column:column_temp[1] - min_column],"|")
            max_length = column_temp[1] - min_column
            for line in lefts:
                #print(len(line))
                if (len(line) > max_length):
                    max_length = len(line)
            #print("max:",max_length)

            for line,i in zip(lefts,range(len(lefts))):
                if len(line) < max_length:
                    lefts[i] = line + " "*(max_length - len(line))
            # for right in rights:
            #     print("right:","|", right)
            #
            # for left in lefts:
            #     print("left:","|", left,"|")
            #
            # for left in lefts:
            #     print("re_left:","|", left[::-1],"|")

            max_left_column = 0
            max_right_column = 0

            #find max_left_column
            if (len(lefts) != 0):
                for left in lefts:
                    reverse_left_string = left[::-1]
                    x = re.search("[^\s]+(\s\s)", reverse_left_string)
                    if(x):
                        if(x.end() > max_left_column):
                            max_left_column = x.end()
            else:
                max_left_column = 0

            #find max_right_column
            if (len(rights) != 0):
                for right in rights:
                    reverse_right_string = right[::-1]
                    x = re.search("[^\s]+(\s\s)", reverse_right_string)
                    if(x):
                        if(x.end() > max_right_column):
                            max_right_column = x.end()
            else:
                if (max_column_t == "max"):
                    max_right_column = None
                else:
                    max_right_column = 0

            #update column
            #update column[0]
            if (min_column == 0):
                column_temp[0] = 0
            else:
                column_temp[0] = column_temp[1] - max_left_column

            #update column[1]
            if (max_column_t == "max"):
                column_temp[1] = None
            else:
                column_temp[1] = max_column - max_right_column


            CURR_CONFIG[key]['column'][0] = column_temp[0]
            CURR_CONFIG[key]['column'][1] = column_temp[1]

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
                                if (((CONFIG[keyE]['row'][1] - 1 < CONFIG[key]['row'][0] and CONFIG[key]['endObject']['top'][:4] == 'same')
                                    or (CONFIG[keyE]['row'][1] < CONFIG[key]['row'][0] and CONFIG[key]['endObject']['top'][:4] != 'same'))
                                    and minDistance > tempDis and CONFIG[keyE]['row'][0] != CONFIG[key]['row'][0]):
                                    keyIndex = extracted.index(keyE)
                                    minDistance = tempDis

                            if (keyIndex == -1):
                                startRow = 0
                            else:
                                # print(extracted[keyIndex])
                                nearestUpperKey = extracted[keyIndex]
                                # print(nearestUpperKey)
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
                                if (nearestLowerKey != key and startRow > CURR_CONFIG[nearestLowerKey]['row'][0] + 1 and len(extracted) > 0):
                                    # print(startRow)
                                    # print(nearestLowerKey)
                                    # print(CURR_CONFIG[nearestLowerKey]['row'][0])
                                    if (CURR_CONFIG[nearestLowerKey]['row'][1]):
                                        if (CURR_CONFIG[nearestLowerKey]['row'][1] - CURR_CONFIG[nearestLowerKey]['row'][0] > 1):
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
                                # print(CURR_CONFIG)
                                break;

                            else:
                                startRow += 1
                                if (startRow == len(fullPdf)):
                                    break

                        if (someProblem or startRow == len(fullPdf)):
                            toFind = [k for k in removed]
                            keyList = [key]
                            if ("alias" in CURR_CONFIG[key]):
                                for each in CURR_CONFIG[key]["alias"]:
                                    keyList.append(CURR_CONFIG[key]["alias"][each]["name"])
                            # print(keyList)

                            for tf in toFind:
                                runXxx = False
                                for eachKey in keyList:
                                    if eachKey in tf:
                                        runXxx = True
                                        break

                                if runXxx:
                                    # print("Recover key: " + key)
                                    startRow = removed[tf][0] + 1

                                    distance = startRow - CURR_CONFIG[key]['row'][0] - (not  sameLine)
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
                                print('  + Key \"%s\" error!' % key)
                                error = 1

                        # print(error)
                    elif (margin == 'bottom'):
                        if (error): continue
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
                        if (CURR_CONFIG[key]['column'][0] == None or error):
                            continue

                        # Get startRow to find left keyword
                        if (len(extracted) > 0):
                            keyIndex = -1
                            minDistance = len(fullPdf)
                            for keyE in extracted:
                                if CONFIG[keyE]['row'][1] == None:
                                    continue
                                tempDis = abs(CONFIG[keyE]['row'][1] - CONFIG[key]['row'][0])
                                if (((CONFIG[keyE]['row'][1] - 1 < CONFIG[key]['row'][0] and CONFIG[key]['endObject']['top'][:4] == 'same')
                                    or (CONFIG[keyE]['row'][1] < CONFIG[key]['row'][0] and CONFIG[key]['endObject']['top'][:4] != 'same'))
                                    and minDistance > tempDis and CONFIG[keyE]['row'][0] != CONFIG[key]['row'][0]):
                                    keyIndex = extracted.index(keyE)
                                    minDistance = tempDis

                            if (keyIndex == -1):
                                startRow = 0
                            else:
                                # print(extracted[keyIndex])
                                startRow = CURR_CONFIG[extracted[keyIndex]]['row'][1]
                        else:
                            startRow = 0
                        # startRow = CURR_CONFIG[key]['row'][0]
                        leftFinding = CONFIG[key]['endObject'][margin]
                        # if (CONFIG[key]['endObject']['top'][:4] != 'same' and leftFinding.strip() != ""):
                        #     startRow -= 1
                        # print(startRow)
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
                                # print(keyE)
                                # print(CURR_CONFIG[keyE]['row'])
                                if CURR_CONFIG[keyE]['row'][1] == None:
                                    # print("RUNNNNNNNNNNNNNNNNN++++++++++++++++++++++++++++++")
                                    if (CURR_CONFIG[keyE]['column'][1] != None):
                                        if (CURR_CONFIG[keyE]['column'][1] > startCol):
                                            startCol = CURR_CONFIG[keyE]['column'][1]
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
                        tempLeft = re.search(CONFIG[key]['endObject'][margin], fullPdf[startRow][:startCol])
                        if (leftObj != None and tempLeft == None):
                            startCol = startCol + leftObj.span(0)[0] + len(CONFIG[key]['endObject'][margin])
                            # print("startCol: "+str(startCol))
                        distance = startCol - CURR_CONFIG[key]['column'][0]



                        # Move other right block
                        for keyE in CURR_CONFIG:
                            if (CURR_CONFIG[keyE]['row'][1] != None and CURR_CONFIG[key]['row'][1] != None):
                                # if (CONFIG[keyE]['column'][1] != None and CONFIG[key]['column'][1] != None):
                                if (keyE not in extracted and keyE != key and ((CONFIG[keyE]['row'][0] < CONFIG[key]['row'][1] and CONFIG[keyE]['row'][0] >= CONFIG[key]['row'][0])
                                                                            or (CONFIG[keyE]['row'][1] <= CONFIG[key]['row'][1] and CONFIG[keyE]['row'][1] > CONFIG[key]['row'][0]))):
                                                                            # and CONFIG[key]['column'][1] <= CONFIG[keyE]['column'][1]):

                                    for i in range(len(CURR_CONFIG[keyE]['column'])):
                                        if (CURR_CONFIG[keyE]['column'][i] != None):
                                            CURR_CONFIG[keyE]['column'][i] += distance
                                            if (CURR_CONFIG[keyE]['column'][i] < 0):
                                                CURR_CONFIG[keyE]['column'][i] = 0
                                        else:
                                            CURR_CONFIG[keyE]['column'][i] = None


                        # Move current block
                        for i in range(len(CURR_CONFIG[key]['column'])):
                            if (CURR_CONFIG[key]['column'][i] != None):
                                CURR_CONFIG[key]['column'][i] += distance
                            else:
                                CURR_CONFIG[key]['column'][i] = None

                        # If top = same_left
                        if (CONFIG[key]['endObject']['top'] != -1):
                            if (CONFIG[key]['endObject']['top'][:4] == 'same'):
                                for line in fullPdf[startRow:]:
                                    if line.find(key)!=-1:
                                        CURR_CONFIG[key]['column'][0] = line.find(key)
                                        break

                    elif (margin == 'right'):
                        if (CURR_CONFIG[key]['column'][1] == None or error):
                            continue

                        # Get startRow to find right keyword
                        if (len(extracted) > 0):
                            keyIndex = -1
                            minDistance = len(fullPdf)
                            for keyE in extracted:
                                if CONFIG[keyE]['row'][1] == None:
                                    continue
                                tempDis = abs(CONFIG[keyE]['row'][1] - CONFIG[key]['row'][0])
                                if (((CONFIG[keyE]['row'][1] - 1 < CONFIG[key]['row'][0] and CONFIG[key]['endObject']['top'][:4] == 'same')
                                    or (CONFIG[keyE]['row'][1] < CONFIG[key]['row'][0] and CONFIG[key]['endObject']['top'][:4] != 'same'))
                                    and minDistance > tempDis and CONFIG[keyE]['row'][0] != CONFIG[key]['row'][0]):
                                    keyIndex = extracted.index(keyE)
                                    minDistance = tempDis

                            if (keyIndex == -1):
                                startRow = 0
                            else:
                                # print(extracted[keyIndex])
                                startRow = CURR_CONFIG[extracted[keyIndex]]['row'][1]
                        else:
                            startRow = 0
                        # startRow = CURR_CONFIG[key]['row'][0]
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

                        if (re.search(rightFinding, fullPdf[startRow][CURR_CONFIG[key]['column'][0]:]) == None):
                            break
                        # Find right keyword and calculate distance
                        startCol = CURR_CONFIG[key]['column'][0] + re.search(rightFinding, fullPdf[startRow][CURR_CONFIG[key]['column'][0]:]).span(0)[0]
                        distance = startCol - CURR_CONFIG[key]['column'][1]
                        # Move' other right block
                        for keyE in CURR_CONFIG:
                            # print(CURR_CONFIG[keyE]['row'][1])
                            if (CURR_CONFIG[keyE]['row'][1] != None and CURR_CONFIG[key]['row'][1] != None):
                                if (keyE not in extracted and keyE != key and ((CONFIG[keyE]['row'][0] < CONFIG[key]['row'][1] and CONFIG[keyE]['row'][0] >= CONFIG[key]['row'][0])
                                                                            or (CONFIG[keyE]['row'][1] <= CONFIG[key]['row'][1] and CONFIG[keyE]['row'][1] > CONFIG[key]['row'][0]))):
                                                                            # and (CONFIG[key]['column'][1] <= CONFIG[keyE]['column'][1])):
                                    # print(keyE)
                                    for i in range(len(CURR_CONFIG[keyE]['column'])):
                                        if (CURR_CONFIG[keyE]['column'][i] != None):
                                            CURR_CONFIG[keyE]['column'][i] += distance
                                            if (CURR_CONFIG[keyE]['column'][i] < 0):
                                                CURR_CONFIG[keyE]['column'][i] = 0
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
        # print(row)
        # print(column)
        # print(CURR_CONFIG)
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

                    if (CONFIG[key]['endObject']['right'] == -1):
                        continue

                    if (formalRight and CONFIG[key]['endObject']['right'].strip() != '' and ((inform[column[1]] != ' ' and inform[column[1] - 1] != ' ')
                                    or  inform[column[1]] == ' ' and inform[column[1] - 1] != ' ')):
                        i = 1
                        # print(inform[column[1]])
                        while (inform[column[1] - i] != ' '):
                            i += 1
                            if column[1] - i == 0:
                                break
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
        # dataBlock = [line[column[0]:column[1]].strip() for line in lines]
        dataBlock = posProcessData([line[column[0]:column[1]] for line in lines], CURR_CONFIG[key], removed)

        if(column[1] != None):
            linehavedata = 0
            for i, line in enumerate(dataBlock):
                str_temp = re.sub(" ","",line)
                if (len(str_temp) > 0):
                    linehavedata += 1


                
            if (linehavedata > 1):
                for i, line in enumerate(dataBlock):
                    print("l",line)
                    if (len(line) < (column[1] - column[0])):
                        continue

                    print("pass1")
                    if (line[::-1][0:2] == "  "):
                        continue
                    print("pass2")
                    fullLine = lines[i]

                    threshhold = int(column[1] - column[0])
                    spaceFinding = re.search("  ",fullLine[column[1]:])
                    spaceFinding2 = re.search("  ",fullLine[column[1]:column[1] + threshhold])
                    print(fullLine[column[1]:])


                    if spaceFinding:
                        if spaceFinding2:
                            newdata = fullLine[column[0]:spaceFinding.start() + column[1]]
                            dataBlock[i] = newdata

                            list_temp = list(fullPdf[row[0] + i])
                            list_temp[column[1]:spaceFinding.start() + column[1]] = " "*len(list_temp[column[1]:spaceFinding.start() + column[1]])
                            fullPdf[row[0] + i] = ''.join(list_temp)

                    else:
                        newdata = fullLine[column[0]:]
                        dataBlock[i] = newdata

                        list_temp = list(fullPdf[row[0] + i])
                        list_temp[column[1]:] = " "*len(list_temp[column[1]:])
                        fullPdf[row[0] + i] = ''.join(list_temp)



        dataBlock = [x.strip() for  x in dataBlock]
        # print(CURR_CONFIG)

        # Process for payment
        paymentList = ['payment','bill','type']

        paymentCheck = True
        for item in paymentList:
            keyCheck = key.lower()
            if(re.search(item,keyCheck)):
                paymentCheck = False

        if (paymentCheck):
            for l, lineInBlock in enumerate(dataBlock):
                temp = lineInBlock.lower()
                isPayment = re.search("freight", temp)

                if(isPayment):
                    # print("RUN PAYMENTS")
                    prepaid = "prepaid"
                    collect = "collect"

                    payment = re.search("freight " + prepaid, temp)
                    if (payment):
                        start = payment.start()
                        end = payment.end()

                        PaymentData = lineInBlock[start:end]


                        case = "freight " + prepaid
                        case_sub0 = "\s\s\s+" + case + "\s\s\s+"
                        case_sub1 = "\s\s\s+" + case + "$"
                        case_sub2 = "^" + case + "\s\s\s+"
                        case_sub3 = "^" + case + "$"
                        iscase_sub0 = re.search(case_sub0, temp)
                        iscase_sub1 = re.search(case_sub1, temp)
                        iscase_sub2 = re.search(case_sub2, temp)
                        iscase_sub3 = re.search(case_sub3, temp)
                        if(iscase_sub0 or iscase_sub1 or iscase_sub2 or iscase_sub3):
                            space = " " * len(lineInBlock[start:end])
                            list_temp = list(lineInBlock)
                            list_temp[start:end] = space
                            dataBlock[l] = ''.join(list_temp)
                        
                        extractedData["Payment"] = PaymentData

                    payment = re.search("freight " + collect, temp)
                    if (payment):
                        start = payment.start()
                        end = payment.end()

                        PaymentData = lineInBlock[start:end]

                        case = "freight " + collect
                        case_sub0 = "\s\s\s+" + case + "\s\s\s+"
                        case_sub1 = "\s\s\s+" + case + "$"
                        case_sub2 = "^" + case + "\s\s\s+"
                        case_sub3 = "^" + case + "$"
                        iscase_sub0 = re.search(case_sub0, temp)
                        iscase_sub1 = re.search(case_sub1, temp)
                        iscase_sub2 = re.search(case_sub2, temp)
                        iscase_sub3 = re.search(case_sub3, temp)
                        if(iscase_sub0 or iscase_sub1 or iscase_sub2 or iscase_sub3):
                            space = " " * len(lineInBlock[start:end])
                            list_temp = list(lineInBlock)
                            list_temp[start:end] = space
                            dataBlock[l] = ''.join(list_temp)

                        extractedData["Payment"] = PaymentData


        dataBlock = [x.strip() for  x in dataBlock]

        remarkList = ['remark','remarks','bill','type']

        remarkCheck = True
        for item in remarkList:
            keyCheck = key.lower()
            if(re.search(item,keyCheck)):
                remarkCheck = False

        if (remarkCheck):
            for l, lineInBlock in enumerate(dataBlock):
                temp = lineInBlock.lower()
                isSeaway = re.search("sea[ ]?way", temp)

                if(isSeaway):
                    case = "sea[ ]*way[ ]*((hold[ ]*cargo)|(bill.*hold cargo)|(bill))?"
                    isCase = re.search(case, temp)

                    if(isCase):
                        start = isCase.start(0)
                        end = isCase.end(0)
                        SeawayData = lineInBlock[start:end]

                        case_sub0 = "\s\s\s+" + case + "\s\s\s+"
                        case_sub1 = "\s\s\s+" + case + "$"
                        case_sub2 = "^" + case + "\s\s\s+"
                        case_sub3 = "^" + case + "$"
                        iscase_sub0 = re.search(case_sub0, temp)
                        iscase_sub1 = re.search(case_sub1, temp)
                        iscase_sub2 = re.search(case_sub2, temp)
                        iscase_sub3 = re.search(case_sub3, temp)
                        if(iscase_sub0 or iscase_sub1 or iscase_sub2 or iscase_sub3):
	                        space = " " * len(lineInBlock[start:end])
	                        list_temp = list(lineInBlock)
	                        list_temp[start:end] = space
                        	dataBlock[l] = ''.join(list_temp)
                        extractedData["Remark"] = SeawayData



        # Process for temperature notation
        for l, lineInBlock in enumerate(dataBlock):
            temp = lineInBlock.lower()
            rows = len(dataBlock)
            notation = re.search("^o$", temp)

            if (notation and l >= (rows - 2)):
                dataBlock.remove(lineInBlock)

            temperature = re.search("(([+]|[-]|)([0-9]+)([\s]|[\s\s])(c|f))([^a-zA-Z])", temp)

            if (temperature):
                # print(temperature.group(2))
                # print(temperature.group(3))
                # print(temperature.group(4))
                list_temp = list(lineInBlock)
                list_temp[temperature.start(4):temperature.end(4)] = " degrees "
                dataBlock[l] = ''.join(list_temp)



        extractedData[key] = '\n'.join(dataBlock)
        # print(extractedData[key])
        extracted.append(key)

    return extractedData
