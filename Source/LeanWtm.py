from __future__ import division
import os
import re
import json
import numpy as np
import pdftotext
from removeHeaderFooter import removeHeaderAndFooter
from removeWatermark import removeWatermark
from preprocess import preProcessPdf

def leanWtm(fullPdf, wtmList):
	count = 0
	for line in fullPdf:
		for i in range (0, len(line)):
			if (ord(line[i]) > 32 and ord(line[i]) < 127):
				count = count + 1
		if (count < 4):
			wtmList.append(line)	
		count = 0
	return wtmList
def detectWtm(wtmList, wtmDict):
	# for wtm in wtmList:
	# 	for i in range (0, len(wtm)):
	# 		w = ord(wtm[i])
	# 		if (w >= 48 and w <= 57):
	# 			break
	# 		else:
	# 			if (w != 32):
	# 				print(wtm[i])
	line = 1
	for wtm in wtmList:
		i = 1
		while (i < len(wtm) - 1):
			while(ord(wtm[i]) == 32):
				i = i + 1
			if (i == len(wtm) - 1):
				print(wtm[i])
				print(line)
				print(i)
				#wtmDict[wtm[i]] = i
				break
			if (ord(wtm[i + 1]) == 32):
				print(wtm[i])
				print(line)
				print(i)
				#wtmDict[wtm[i]] = i
			if (i == len(wtm)-1): break
			while ((ord(wtm[i + 1]) != 32) and (i < len(wtm) - 2)):
				i = i + 1
			i = i + 1
		line = line + 1
	return wtmDict
if __name__ == '__main__':
	PDF_TYPE = '15'
	filename = list(filter(lambda pdf: pdf[-3:].lower() == 'pdf' ,os.listdir('../' + PDF_TYPE)))
	for file in filename:
		with open('../' + PDF_TYPE + '/' + PDF_TYPE + '.json', 'r', encoding='utf8') as json_file:
			ORIGINAL_CONFIG = json.load(json_file)
		print(file)

		CONFIG = ORIGINAL_CONFIG[0].copy()
		HF_CONFIG = ORIGINAL_CONFIG[1].copy()

		fullPdf = preProcessPdf('../' + PDF_TYPE + '/' + file, HF_CONFIG)
		wtmList = []
		wtmDict = {}
		wtmList = leanWtm(fullPdf, wtmList)
		wtmDict = detectWtm(wtmList, wtmDict)
		with open('../' + PDF_TYPE + '/' + file[:-3] + 'txt', 'w', encoding='utf8') as resultFile:
			for i in wtmDict:
				resultFile.write("%s:\n%s\n" % (i, wtmDict[i]))

