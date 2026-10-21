import json
from os import listdir
from os.path import isfile, join, dirname

def getInputList():
    referencePath = dirname(__file__)
    inputDir = join(referencePath,"Input")
    onlyfiles = [f for f in listdir(inputDir) if isfile(join(inputDir, f))]
    return(onlyfiles)

def fix_bibites():
    direcName = dirname(__file__)
    inputDir = join(direcName,"Input")
    outputDir = join(direcName,"Output")
    inputList = getInputList()

    for k in range(len(inputList)):
        inputName = join(inputDir,inputList[k])
        outputName = join(outputDir,inputList[k])
        f = open(inputName, "r")
        s = f.read()
        y = json.loads(s[3:])
        
        y["version"] = "0.4.2"
        
        # for key in y["genes"].keys():
        #     print(str(key))
        
        y["genes"]["tag"] = inputList[k]
        
        g = open(outputName, "w")
        g.write(json.dumps(y))
        g.close()
        
        #for debugging
        print(inputName)
        
    print("We gucci.")

fix_bibites()
