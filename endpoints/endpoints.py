from fastapi import FastAPI, APIRouter
from fastapi.responses import HTMLResponse, UJSONResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.cors import CORSMiddleware
import sys
import os

# import the excelParser
parserPath = "./service/excelParser.py"
sys.path.insert(0, os.path.dirname(os.path.abspath(parserPath)))
from excelParser import *

# import the configGenerator
configPath = "./service/configGenerator.py"
sys.path.insert(0, os.path.dirname(os.path.abspath(configPath)))
from configGenerator import * 

router = APIRouter()

templates = Jinja2Templates(directory="jinja-templates")
templates.env.autoescape = False
EXCEL_FILE = "Base.xlsx"

# initialize a parser object
parser = Parser()
# initialize a config object
config = Config()

# generating and saving config files for leafs
def generateConfig(): 
    # convert excel data into dictionary format
    dictionary = parser.toDictByRows(EXCEL_FILE)
    for currentLeafList in dictionary["leafList"]: 
        for index, leaf in enumerate(currentLeafList): 
            interfaceOutput = ""
            subinterfaceOutput = ""
            irbInterfaceOutput = ""
            macvrfInterfaceOutput = ""
            ipvrfInterfaceOutput = ""
            
            # if it's the first leaf of its name, create interface and subinterface for that leaf
            if index == 0:
                interfaceOutput = config.createInterface(leaf)
                subinterfaceOutput = config.createSubInterface(leaf)
            # if leaf with the same name already exists, check if their port numbers are same
            else: 
                if currentLeafList[0]["portNumber"] != leaf["portNumber"]: 
                    interfaceOutput = config.createInterface(leaf)
                    subinterfaceOutput = config.createSubInterface(leaf)
                # if port numbers are same, check the breakout numbers
                else: 
                    if currentLeafList[0]["breakoutNumberList"] != leaf["breakoutNumberList"]:
                        subinterfaceOutput = config.createSubInterface(leaf)
            # if leaf has IPv4 Gateway, create irb interface
            if leaf.get("IPv4 Gateway") is not None:  
                irbInterfaceOutput = config.createIRBInterface(leaf)
            # if VLAN Type is L3, create IPVRF interface, also create MACVRF interface inside the createIPVRFInterface method  
            if leaf["L2 or L3"] == "L3": 
                ipvrfInterfaceOutput = config.createIPVRFInterface(leaf)
            # if VLAN Type is L2, create MACVRF interface
            else: 
                macvrfInterfaceOutput = config.createMACVRFInterface(leaf)
            # merge all configs of the specific leaf in one file 
            config.mergeInOneFile(interfaceOutput, subinterfaceOutput, irbInterfaceOutput, macvrfInterfaceOutput, ipvrfInterfaceOutput, leaf)
    return dictionary
            
@router.get('/')
async def index():
    dictionary = generateConfig()
    return dictionary
