from jinja2 import Environment, FileSystemLoader
import os # to create folders and new paths for generated config files
import re # regex library to split the string

jinjaTemplatesPath = "./jinja-templates"
rootFolderPath = os.path.abspath("./")
configFolderPath = os.path.abspath("./configs")

class Config: 
    def __init__(self): 
        pass

    def createInterface(self, leafDict): 
        env = Environment(loader=FileSystemLoader(jinjaTemplatesPath))
        os.chdir(rootFolderPath)
        template = env.get_template("interface.j2")
        # pass the params to jinja and generate the jinja output
        jinjaOutput = template.render(
            portid = leafDict["portNumber"] 
        )
        return jinjaOutput
    
    def createSubInterface(self, leafDict): 
        env = Environment(loader=FileSystemLoader(jinjaTemplatesPath))
        os.chdir(rootFolderPath)
        template = env.get_template("subinterface.j2")
        # pass the params to jinja and generate the jinja output
        jinjaOutput = template.render(
            portid = leafDict["portNumber"], 
            breakoutidList = leafDict["breakoutNumberList"], 
            vlanid = leafDict["VLAN ID"]    
        )
        return jinjaOutput
      
    def createIRBInterface(self, leafDict): 
        env = Environment(loader=FileSystemLoader(jinjaTemplatesPath))
        os.chdir(rootFolderPath)
        template = env.get_template("irb_interface.j2")
        
        irb_v6_address = ""
        irb_v6_mask = ""

        # split IPv4 Gateway string into address and mask 
        splittedIPv4 = re.split("/", leafDict["IPv4 Gateway"])
        irb_v4_address = splittedIPv4[0]
        irb_v4_mask = splittedIPv4[1]

        # check if leaf has IPv6 Gateway
        if leafDict.get("IPv6 Gateway") is not None: 
            # split IPv6 Gateway string into address and mask
            splittedIPv6 = re.split("/", leafDict["IPv6 Gateway"])
            irb_v6_address = splittedIPv6[0]
            irb_v6_mask = splittedIPv6[1]
            # pass the params to jinja and generate the jinja output
            jinjaOutput = template.render(
                irb_v4_address = irb_v4_address,
                irb_v4_mask = irb_v4_mask,  
                irb_v6_address = irb_v6_address,
                irb_v6_mask = irb_v6_mask,  
                macvrf_name = leafDict["Network Name"], 
                index = leafDict["Parameter"] 
            )
            return jinjaOutput
        else: 
            # pass the params to jinja and generate the jinja output 
            jinjaOutput = template.render(
                irb_v4_address = irb_v4_address,
                irb_v4_mask = irb_v4_mask,  
                macvrf_name = leafDict["Network Name"], 
                index = leafDict["Parameter"] 
            )
            return jinjaOutput
       
    def createIPVRFInterface(self, leafDict):
        # list that hold irbs for MACVRF
        macvrfIrbList = []
        # list that holds irbs for IPVRF
        ipvrfIrbList = []
        ipvrfVxlanInterface = "vxlan1." + str(leafDict["Parameter"])
        
        env = Environment(loader=FileSystemLoader(jinjaTemplatesPath))
        os.chdir(rootFolderPath)
        template = env.get_template("ipvrf.j2")

        irb = "irb1." + str(leafDict["Parameter"]) 
        if irb not in ipvrfIrbList:
            ipvrfIrbList.append(irb)

        if irb not in macvrfIrbList:
            macvrfIrbList.append(irb)
        
        # create MACVRF jinja output
        macvrfJinjaOutput = self.createMACVRFInterface(leafDict, macvrfIrbList)

        # pass the params to jinja and generate the jinja output 
        jinjaOutput = template.render(
            index = leafDict["Parameter"],
            ipvrf_name = leafDict["IP VRF Name"],
            netins_name = leafDict["Network Name"], 
            irb_interface_list = ipvrfIrbList, 
            vxlan_interface = ipvrfVxlanInterface
        )

        # return MACVRF + IPVRF jinja output 
        return "\n" + macvrfJinjaOutput + "\n" + jinjaOutput + "\n"
  

    def createMACVRFInterface(self, leafDict, macvrfIrbList=[]):
        # list that holds ethernets for MACVRF
        macvrfEthernetList = []
        macvrfVxlanInterface = "vxlan2." + str(leafDict["Parameter"])
        
        env = Environment(loader=FileSystemLoader(jinjaTemplatesPath))
        os.chdir(rootFolderPath)
        template = env.get_template("macvrf.j2")

        # append ethernet to the ethernet list
        ethernet = ""
        for breakoutNumber in leafDict["breakoutNumberList"]:
            ethernet = str(leafDict["portNumber"]) + "/" + str(breakoutNumber)
            macvrfEthernetList.append(ethernet) 
        
        if ethernet not in macvrfEthernetList: 
            macvrfEthernetList.append(ethernet)

        # pass the params to jinja and get the jinja output 
        jinjaOutput = template.render(
            index = leafDict["Parameter"],
            subnet_name = leafDict["Network Name"], 
            irb_interface_list = macvrfIrbList, 
            edge_interface_list = macvrfEthernetList,
            vxlan_interface = macvrfVxlanInterface
        )
        # return MACVRF jinja output
        return jinjaOutput
  
    def mergeInOneFile(self, interfaceFile, subinterfaceFile, irbInterfaceFile, macvrfInterfaceFile, ipvrfInterfaceFile, leafDict):
        # merge all jinja outputs for each leaf in 1 variable
        jinjaOutput = interfaceFile + "\n \n" + subinterfaceFile + "\n \n" + irbInterfaceFile + "\n \n" + macvrfInterfaceFile + "\n \n" + ipvrfInterfaceFile + "\n \n"
        print("Generating a config file for ", leafDict["name"])
        outputFileName = leafDict["name"] + ".cfg"
        
        # create config folder if it doesn't already exist
        if os.path.isdir("./configs") is False: 
            os.mkdir("./configs")
        
        # change dir to configs folder
        os.chdir(configFolderPath)
        
        # check if interfaces dir exists
        if os.path.isdir("./interfaces") is False: 
            os.mkdir("./interfaces")
        
        # change dir to interfaces folder
        os.chdir("./interfaces")
        
        # get the absolute path of interfaces folder to write into a file
        InterfacesConfigsPath = os.path.abspath("./")
        
        # create a path by appending the file path to directory path
        outputFilePath = os.path.join(InterfacesConfigsPath, outputFileName) # ... / ... / .. / leafXX.cfg
        
        # if leaf with same name exists, append new one to the existing one
        if os.path.exists(outputFileName): 
            with open(outputFilePath, "a") as configFile: 
                configFile.write(jinjaOutput)
            os.chdir(rootFolderPath)
        # if leaf with same name doesn't exist already, create new config file with the corresponding name
        else: 
            with open(outputFilePath, "w") as configFile: 
                configFile.write(jinjaOutput)
            os.chdir(rootFolderPath)