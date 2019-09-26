# def posProcessData(data, CURR_CONFIG, removedData):
#     for word in removedData:
#         for key in CURR_CONFIG:
#             if (CURR_CONFIG[key]['row'][1] == None):
#                 CURR_CONFIG[key]['row'][1] = removedData[word][0] + 1
#             if (removedData[word][0] in range(CURR_CONFIG[key]['row'][0], CURR_CONFIG[key]['row'][1])):
#                 if (CURR_CONFIG[key]['column'][1] == None):
#                     CURR_CONFIG[key]['column'][1] = removedData[word][2] + 1
#                 if (removedData[word][1] in range(CURR_CONFIG[key]['column'][0], CURR_CONFIG[key]['column'][1])
#                 and removedData[word][2] in range(CURR_CONFIG[key]['column'][0], CURR_CONFIG[key]['column'][1])):
#                     newData = data[key].split('\n')
#                     row = removedData[word][0] - CURR_CONFIG[key]['row'][0]
#                     colL = removedData[word][1] - CURR_CONFIG[key]['column'][0]
#                     colR = len(newData[row]) - (CURR_CONFIG[key]['column'][1] - removedData[word][2])
#                     newData[row] = newData[row].replace(newData[row][colL:colR], word)
#                     data[key] = '\n'.join(newData)
#                     print(word)
#     return data
import copy
import re

def posProcessData(data, _config, removedData):
    newData = data.copy()
    config = copy.deepcopy(_config)
    for word in removedData:
        if (config['row'][1] == None):
            config['row'][1] = removedData[word][0] + 1
        # print("WATERMARKINGGGGGGGG>>>>>>")
        # print([config['row'][0], config['row'][1]])
        # print(removedData[word][0])
        if (removedData[word][0] in range(config['row'][0], config['row'][1])):
            if (config['column'][1] == None):
                config['column'][1] = removedData[word][2] + 1
            if (removedData[word][1] in range(config['column'][0], config['column'][1])
            and removedData[word][2] in range(config['column'][0], config['column'][1])):
                row = removedData[word][0] - config['row'][0]
                colL = removedData[word][1] - config['column'][0]
                colR = len(newData[row]) - (config['column'][1] - removedData[word][2]) + 1
                # toBeReplaced = '%s' % newData[row][colL:colR]
                # dataToReplace = '%s' % newData[row]
                list_temp = list(newData[row])
                list_temp[colL:colR] = word
                newData[row] = ''.join(list_temp)
                # newData[row] = dataToReplace.replace(toBeReplaced, word)
    return newData


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
        if ('subfields' in CONFIG[key]):
            # print(extractedData[key])
            for subs in CONFIG[key]['subfields']:
                # print(subs)
                reg = CONFIG[key]['subfields'][subs]
                if (reg != 10):
                    result1 = re.search(reg, extractedData[key])
                    if (result1 is not None):
                        result = re.search(reg, extractedData[key]).span()
                        extractedData[subs] = extractedData[key][result[0]:result[1]]
                        if key not in CONFIG[key]['subfields']:
                            extractedData[key] = extractedData[key][0:result[0]] + extractedData[key][result[1]:]
                else:
                    extractedData[subs] = extractedData[key]
            if key not in CONFIG[key]['subfields']:
                del extractedData[key]
    return extractedData
