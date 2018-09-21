import os

FList = os.listdir(os.getcwd())
FListC = FList[:]

m = 3585
for i in FListC:
    fileName = os.path.splitext(i)[0]
    fileExtension = os.path.splitext(i)[1]
    if fileExtension == '.py':
        continue
    else:
        if m < 10:
            os.rename(i, '00000' + str(m) + fileExtension)
        elif m < 100:
            os.rename(i, '0000' + str(m) + fileExtension)
        elif m < 1000:
            os.rename(i, '000' + str(m) + fileExtension)
        elif m < 10000:
            os.rename(i, '00' + str(m) + fileExtension)
        elif m < 100000:
            os.rename(i, '0' + str(m) + fileExtension)
        elif m < 1000000:
            os.rename(i, str(m) + fileExtension)
    m += 1