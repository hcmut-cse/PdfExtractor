def posProcessData(data, CURR_CONFIG, removedData):
    for word in removedData:
        for key in CURR_CONFIG:
            if (CURR_CONFIG[key]['row'][1] == None):
                CURR_CONFIG[key]['row'][1] = removedData[word][0] + 1
            if (removedData[word][0] in range(CURR_CONFIG[key]['row'][0], CURR_CONFIG[key]['row'][1])):
                if (CURR_CONFIG[key]['column'][1] == None):
                    CURR_CONFIG[key]['column'][1] = removedData[word][2] + 1
                if (removedData[word][1] in range(CURR_CONFIG[key]['column'][0], CURR_CONFIG[key]['column'][1])
                and removedData[word][2] in range(CURR_CONFIG[key]['column'][0], CURR_CONFIG[key]['column'][1])):
                    newData = data[key].split('\n')
                    row = removedData[word][0] - CURR_CONFIG[key]['row'][0]
                    colL = removedData[word][1] - CURR_CONFIG[key]['column'][0]
                    colR = len(newData[row]) - (CURR_CONFIG[key]['column'][1] - removedData[word][2])
                    newData[row] = newData[row].replace(newData[row][colL:colR], word)
                    data[key] = '\n'.join(newData)
    return data
