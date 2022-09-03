import pandas as pd
import re
import os
import sys

rootFolderPath = os.path.abspath("./")
EXCEL_FILE = "Base.xlsx"

class Parser: 
    def __init__(self): 
        os.chdir(rootFolderPath)
    
    # reads the first sheet of the excel file
    def readExcelRaw(self, fileName): 
        df = pd.read_excel(fileName)
        return df
    
    # reads the excel sheet by its name, if sheet name is not provided, it reads the first sheet.
    def readExcelBySheet(self, fileName, sheetName): 
        sdf = pd.read_excel(fileName, sheetName)
        return sdf
    
    def readTopology(self, df):
        df["Topology"]
    
    # this methods get each row and converts them to dictionaries in the dictionary.
    def toDictByRows(self, fileName): 
        # get the data frame from excel
        df = pd.read_excel(fileName)
        df = df.fillna(" ")
        
        # create structure of dictionary
        leafsDict = {
            "leafList": []
        }

        # hold the keys of data frame in a list
        featureList = []
        for key in df.keys(): 
            if key != "Topology":
                featureList.append(key)
        
        # iterate over rows and columns of the rows        
        for index in range(1, df.shape[0]-2): # range starts from 1 bc row 0 is just an explanation.

            # get the leaf structures from Topology string by splitting it by (";")
            if isinstance(df.loc[index]["Topology"], str):
                leafStructureList = df.loc[index]["Topology"].split(";")
                # leaf structure consists of "leaf_name", "port_number" and "breakout_number" for each leaf structure in the list 
                for leafStructure in leafStructureList: # iterate over leaf structures to get the "leaf name" "port number" and "breakout number" for each 
                    # get the leaf name 
                    splittedLeafStructure = re.split("_|/", leafStructure) # leafName[0] is the name of the leaf
                    # create a dictionary for this leaf
                    
                    # check if breakout numbers have a range
                    if "-" in splittedLeafStructure[2]:
                        # separate breakout range by "-"
                        breakoutStart = int(splittedLeafStructure[2][0:splittedLeafStructure[2].find("-")])
                        breakoutEnd = int(splittedLeafStructure[2][splittedLeafStructure[2].find("-")+1: len(splittedLeafStructure[2])])
                        doesExists = False
                        leafList = []
                        leafDict = {}
                        leafDict["name"] = splittedLeafStructure[0]
                        leafDict["portNumber"] = splittedLeafStructure[1]
                        breakoutNumberList = []
                        # append breakout numbers to the list
                        for breakoutNumber in range(breakoutStart, breakoutEnd+1): 
                            breakoutNumberList.append(breakoutNumber)
                        leafDict["breakoutNumberList"] = breakoutNumberList
                        # if cell value is empty, do not append it 
                        for feature in featureList: 
                            if df.loc[index][feature] != " ":
                                leafDict[feature] = df.loc[index][feature] 
                        # check if VLAN ID is in range or not
                        try: 
                            assert df.loc[index]["VLAN ID"] >= 0 and df.loc[index]["VLAN ID"] <= 4094, "VLAN ID is not in range"
                        # VLAN ID is out of range, terminate the program
                        except AssertionError as msg:
                            print(msg)
                            sys.exit()
                        # check if VLAN is L2 or L3 or not
                        try: 
                            assert df.loc[index]["L2 or L3"] == "L2" or df.loc[index]["L2 or L3"] == "L3", "Wrong Network Name"
                        # Wrong network name, terminate the program
                        except AssertionError as msg:
                            print(msg)
                            sys.exit()
                        
                        # if leaf with same name already exists, put them in the same list  
                        if len(leafsDict["leafList"]) != 0: 
                            for currentLeafList in leafsDict["leafList"]:
                                if len(currentLeafList) != 0: 
                                    if currentLeafList[0]["name"] == leafDict["name"]:
                                        doesExists = True
                                        currentLeafList.append(leafDict) 
                                else:   
                                    leafList.append(leafDict)
                        # if leaf name is new, create new list for that
                        if doesExists is False: 
                            leafList.append(leafDict)
                            leafsDict["leafList"].append(leafList)
                    
                    # leaf has only one breakout number 
                    else:   
                        doesExists = False
                        leafList = []              
                        leafDict = {}
                        leafDict["name"] = splittedLeafStructure[0]
                        leafDict["portNumber"] = splittedLeafStructure[1]
                        leafDict["breakoutNumberList"] = [int(splittedLeafStructure[2])]
                        
                        # if cell value is empty, do not append it 
                        for feature in featureList: 
                            if df.loc[index][feature] != " ":
                                leafDict[feature] = df.loc[index][feature]
                        
                        # check if VLAN ID is in range or not
                        try: 
                            assert df.loc[index]["VLAN ID"] >= 0 and df.loc[index]["VLAN ID"] <= 4094, "VLAN ID is not in range"
                        # VLAN ID is out of range, terminate the prograM
                        except AssertionError as msg:
                            print(msg)
                            sys.exit()
                        # check if VLAN is L2 or L3 or not 
                        try: 
                            assert df.loc[index]["L2 or L3"] == "L2" or df.loc[index]["L2 or L3"] == "L3", "Wrong Network Name"
                        # Wrong network name, terminate the program
                        except AssertionError as msg:
                            print(msg)
                            sys.exit()
                        
                        # if leaf with same name already exists, put them in the same list  
                        if len(leafsDict["leafList"]) != 0: 
                            for currentLeafList in leafsDict["leafList"]:
                                if len(currentLeafList) != 0: 
                                    if currentLeafList[0]["name"] == leafDict["name"]: 
                                        doesExists = True
                                        currentLeafList.append(leafDict)
                                else: 
                                    leafList.append(leafDict)
                        
                        # if leaf name is new, create new list for that
                        if doesExists is False:
                            leafList.append(leafDict)
                            leafsDict["leafList"].append(leafList)  
        return leafsDict