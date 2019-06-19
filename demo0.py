from __future__ import division
import os
import re
import numpy as np
import pdftotext

if __name__ == '__main__':
    # file = os.listdir()
    # file = list(filter(lambda ef: ef[0] != "." and ef[-3:] == "pdf", file))

    file = ["VN101466/SI_HANV07496600.pdf"]
    for filename in file:
        # Covert PDF to string by page
        print(filename)

        with open(filename, "rb") as f:
        #     for i in f:
        #         print(i)
            pdf = pdftotext.PDF(f)
        if (pdf[0] != ""):
            with open(filename[:-3]+"txt", "w+") as f:
                for page in pdf:
                    f.write(page)
