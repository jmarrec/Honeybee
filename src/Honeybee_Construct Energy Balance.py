#
# Honeybee: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# 
# This file is part of Honeybee.
# 
# Copyright (c) 2013-2015, Chris Mackey <Chris@MackeyArchitecture.com> 
# Honeybee is free software; you can redistribute it and/or modify 
# it under the terms of the GNU General Public License as published 
# by the Free Software Foundation; either version 3 of the License, 
# or (at your option) any later version. 
# 
# Honeybee is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the 
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>


"""
This component accepst the outputs of the "Read EP Result" and the "Read EP Surface Result" components and outputs a data tree with all of the building-wide energy balance terms.  This can then be plugged into the "Ladybug_3D Chart" or "Ladybug_Monthly Bar Chart" to give a visualization of the energy balance of the whole model.

-
Provided by Honeybee 0.0.57
    
    Args:
        _HBZones: The HBZones out of any of the HB components that generate or alter zones.  Note that these should ideally be the zones that are fed into the Run Energy Simulation component.  Zones read back into Grasshopper from the Import idf component will not align correctly with the EP Result data.
        cooling_: The cooling load from the "Honeybee_Read EP Result" component.
        heating_: The heating load from the "Honeybee_Read EP Result" component.
        electricLight_: The electric lighting load from the "Honeybee_Read EP Result" component.
        electricEquip_: The electric equipment load from the "Honeybee_Read EP Result" component.
        peopleGains_: The people gains from the "Honeybee_Read EP Result" component.
        totalSolarGain_: The total solar gain from the "Honeybee_Read EP Result" component.
        infiltrationEnergy_: The infiltration heat loss (negative) or heat gain (positive) from the "Honeybee_Read EP Result" component.
        outdoorAirEnergy_: The outdoor air heat loss (negative) or heat gain (positive) from the "Honeybee_Read EP Result" component.
        natVentEnergy_: The natural ventilation heat loss (negative) or heat gain (positive) from the "Honeybee_Read EP Result" component.
        surfaceEnergyFlow_: The surface heat loss (negative) or heat gain (positive) from the "Honeybee_Read EP Surface Result" component.
    Returns:
        readMe!: ...
        modelEnergyBalance:  A data tree with the important building-wide energy balance terms.  This can then be plugged into the "Ladybug_3D Chart" or "Ladybug_Monthly Bar Chart" to give a visualization of the energy balance of the whole model.
        energyBalWithSotrage:  A data tree with the important building-wide energy balance terms plus an additional term to represent the energy being stored in the building's mass and air mass.  This can then be plugged into the "Ladybug_3D Chart" or "Ladybug_Monthly Bar Chart" to give a visualization of the energy balance of the whole model.
"""

ghenv.Component.Name = "Honeybee_Construct Energy Balance"
ghenv.Component.NickName = 'energyBalance'
ghenv.Component.Message = 'VER 0.0.57\nSEP_13_2015'
ghenv.Component.Category = "Honeybee"
ghenv.Component.SubCategory = "09 | Energy | Energy"
#compatibleHBVersion = VER 0.0.56\nMAY_02_2015
#compatibleLBVersion = VER 0.0.59\nAPR_04_2015
ghenv.Component.AdditionalHelpFromDocStrings = "0"


from System import Object
from clr import AddReference
AddReference('Grasshopper')
import Grasshopper.Kernel as gh
from Grasshopper import DataTree
from Grasshopper.Kernel.Data import GH_Path
import scriptcontext as sc



def checkCreateDataTree(dataTree, dataName, dataType):
    #Define a variable for warnings.
    w = gh.GH_RuntimeMessageLevel.Warning
    
    #Convert the data tree to a python list.
    dataPyList = []
    for i in range(dataTree.BranchCount):
        branchList = dataTree.Branch(i)
        dataVal = []
        for item in branchList:
            try: dataVal.append(float(item))
            except: dataVal.append(item)
        dataPyList.append(dataVal)
    
    #Test to see if the data has a header on it, which is necessary to know if it is the right data type.  If there's no header, the data should not be vizualized with this component.
    checkHeader = []
    dataHeaders = []
    dataNumbers = []
    for list in dataPyList:
        if str(list[0]) == "key:location/dataType/units/frequency/startsAt/endsAt":
            checkHeader.append(1)
            dataHeaders.append(list[:7])
            dataNumbers.append(list[7:])
        else:
            dataNumbers.append(list)
    
    if sum(checkHeader) == len(dataPyList):
        dataCheck1 = True
    else:
        if len(dataPyList) > 0 and dataPyList[0][0] == None: pass
        else:
            dataCheck1 = False
            warning = "Not all of the connected " + dataName + " has a Ladybug/Honeybee header on it.  This header is necessary to generate an indoor temperture map with this component."
            print warning
            ghenv.Component.AddRuntimeMessage(w, warning)
    
    try:
        #Check to be sure that the lengths of data in in the dataTree branches are all the same.
        dataLength = len(dataNumbers[0])
        dataLenCheck = []
        for list in dataNumbers:
            if len(list) == dataLength:
                dataLenCheck.append(1)
            else: pass
        if sum(dataLenCheck) == len(dataNumbers) and dataLength <8761:
            dataCheck2 = True
        else:
            dataCheck2 = False
            warning = "Not all of the connected " + dataName + " branches are of the same length or there are more than 8760 values in the list."
            print warning
            ghenv.Component.AddRuntimeMessage(w, warning)
        
        if dataCheck1 == True:
            #Check to be sure that all of the data headers say that they are of the same type.
            header = dataHeaders[0]
            
            headerUnits =  header[3]
            headerStart = header[5]
            headerEnd = header[6]
            simStep = str(header[4])
            headUnitCheck = []
            headPeriodCheck = []
            for head in dataHeaders:
                if dataType in head[2]:
                    headUnitCheck.append(1)
                if head[3] == headerUnits and str(head[4]) == simStep and head[5] == headerStart and head[6] == headerEnd:
                    headPeriodCheck.append(1)
                else: pass
            
            if sum(headPeriodCheck) == len(dataHeaders):
                dataCheck3 = True
            else:
                dataCheck3 = False
                warning = "Not all of the connected " + dataName + " branches are of the same timestep or same analysis period."
                print warning
                ghenv.Component.AddRuntimeMessage(w, warning)
            
            if sum(headUnitCheck) == len(dataHeaders):
                dataCheck4 = True
            else:
                dataCheck4 = False
                warning = "Not all of the connected " + dataName + " data is for the correct data type."
                print warning
                ghenv.Component.AddRuntimeMessage(w, warning)
            
            if 'm2' in headerUnits or 'ft2' in headerUnits:
                dataCheck5 = False
                warning = "The data from the " + dataName + " input has been normalized by an area. \n Values need to be non-normalized for the energy balance to work."
                print warning
                ghenv.Component.AddRuntimeMessage(w, warning)
            else:
                dataCheck5 = True
            
            if dataCheck1 == True and dataCheck2 == True and dataCheck3 == True and dataCheck4 == True and dataCheck5 == True: dataCheck = True
            else: dataCheck = False
        else:
            dataCheck = False
            headerUnits = 'unknown units'
            dataHeaders = []
            header = [None, None, None, None, None, None, None]
    except:
        dataCheck = True
        headerUnits = None
        dataHeaders = []
        dataNumbers = []
        header = [None, None, None, None, None, None, None]
    
    return dataCheck, headerUnits, dataHeaders, dataNumbers, [header[5], header[6]]


def getSrfNames(HBZones):
    wall = []
    window = []
    skylight =[]
    roof = []
    exposedFloor = []
    groundFloor = []
    undergroundWall = []
    
    for zone in HBZones:
        # call the objects from the lib
        hb_hive = sc.sticky["honeybee_Hive"]()
        
        zone = hb_hive.callFromHoneybeeHive([zone])[0]
        
        for srf in zone.surfaces:
            # Wall
            if srf.type == 0:
                if srf.BC.upper() == "OUTDOORS":
                    if srf.hasChild:
                        wall.append(srf.name)
                        for childSrf in srf.childSrfs:
                            window.append(childSrf.name)
                    else:
                        wall.append(srf.name)
            # underground wall
            elif srf.type == 0.5:
                if srf.BC.upper() == "GROUND":
                    undergroundWall.append(srf.name)
            # Roof
            elif srf.type == 1:
                if srf.BC.upper() == "OUTDOORS":
                    if srf.hasChild:
                        roof.append(srf.name)
                        for childSrf in srf.childSrfs:
                            skylight.append(childSrf.name)
                    else:
                        roof.append(srf.name)
            
            elif srf.type == 2.5:
                if srf.BC.upper() == "GROUND":
                    groundFloor.append(srf.name)
            elif srf.type == 2.75:
                if srf.BC.upper() == "OUTDOORS":
                    exposedFloor.append(srf.name)
        
        
    return wall, window, skylight, roof, \
           exposedFloor, groundFloor, undergroundWall

def checkList(theList, dataTree, name, branchList):
    itemFound = False
    for srf in theList:
        if srf.upper() == name:
            dataTree.append(branchList)
            itemFound = True
        else: pass
    return itemFound

def sumAllLists(tree):
    if len(tree) == 1: summedList = tree[0]
    else:
        summedList = tree[0]
        for dataCount, dataList in enumerate(tree):
            if dataCount == 0: pass
            else:
                for count, item in enumerate(dataList):
                    summedList[count] = summedList[count] + item
    
    return summedList


def main(HBZones, heatingLoad, solarLoad, lightingLoad, equipLoad, peopleLoad, surfaceEnergyFlow, infiltrationEnergy, outdoorAirEnergy, natVentEnergy, coolingLoad):
    #Check and convert the data for each of the zone data lists.
    checkData1, heatingUnits, heatingHeaders, heatingNumbers, heatingAnalysisPeriod = checkCreateDataTree(heatingLoad, "heating", "Heating")
    checkData2, solarUnits, solarHeaders, solarNumbers, solarAnalysisPeriod = checkCreateDataTree(solarLoad, "totalSolarGain_", "Solar")
    checkData3, lightingUnits, lightingHeaders, lightingNumbers, lightingAnalysisPeriod = checkCreateDataTree(lightingLoad, "electricLight_", "Lighting")
    checkData4, equipUnits, equipHeaders, equipNumbers, equipAnalysisPeriod = checkCreateDataTree(equipLoad, "electricEquip_", "Equipment")
    checkData5, peopleUnits, peopleHeaders, peopleNumbers, peopleAnalysisPeriod = checkCreateDataTree(peopleLoad, "peopleGains_", "People")
    checkData6, infiltrationUnits, infiltrationHeaders, infiltrationNumbers, infiltrationAnalysisPeriod = checkCreateDataTree(infiltrationEnergy, "infiltrationEnergy_", "Infiltration")
    checkData7, outdoorAirUnits, outdoorAirHeaders, outdoorAirNumbers, outdoorAirAnalysisPeriod = checkCreateDataTree(outdoorAirEnergy, "outdoorAirEnergy_", "Outdoor Air")
    checkData8, natVentUnits, natVentHeaders, natVentNumbers, natVentAnalysisPeriod = checkCreateDataTree(natVentEnergy, "natVentEnergy_", "Natural Ventilation")
    checkData9, coolingUnits, coolingHeaders, coolingNumbers, coolingAnalysisPeriod = checkCreateDataTree(coolingLoad, "cooling", "Cooling")
    checkData10, surfaceUnits, surfaceHeaders, surfaceNumbers, surfaceAnalysisPeriod = checkCreateDataTree(surfaceEnergyFlow, "surfaceEnergyFlow_", "Surface Energy")
    
    if checkData1 == True and checkData2 == True and checkData3 == True and checkData4 == True and checkData5 == True and checkData6 == True and checkData7 == True and checkData8 == True and checkData9 == True  and checkData10 == True:
        #Get the names of the surfaces from the HBZones.
        wall, window, skylight, roof, exposedFloor, groundFloor, undergroundWall = getSrfNames(HBZones)
        
        #Organize all of the surface data by type of surface.
        opaqueEnergyFlow = []
        glazingEnergyFlow = []
        
        if len(surfaceNumbers) > 0:
            for srfCount, srfHeader in enumerate(surfaceHeaders):
                try:srfName = srfHeader[2].split(" for ")[-1].split(": ")[0]
                except:srfName = srfHeader[2].split(" for ")[-1]
                
                itemFound = checkList(wall, opaqueEnergyFlow, srfName, surfaceNumbers[srfCount])
                if itemFound == False: itemFound = checkList(window, glazingEnergyFlow, srfName, surfaceNumbers[srfCount])
                if itemFound == False: itemFound = checkList(skylight, glazingEnergyFlow, srfName, surfaceNumbers[srfCount])
                if itemFound == False: itemFound = checkList(roof, opaqueEnergyFlow, srfName, surfaceNumbers[srfCount])
                if itemFound == False: itemFound = checkList(exposedFloor, opaqueEnergyFlow, srfName, surfaceNumbers[srfCount])
                if itemFound == False: itemFound = checkList(groundFloor, opaqueEnergyFlow, srfName, surfaceNumbers[srfCount])
                if itemFound == False: itemFound = checkList(undergroundWall, opaqueEnergyFlow, srfName, surfaceNumbers[srfCount])
        
        #Sum all of the zones and sufaces into one list for each energy balance term.
        if len(heatingNumbers) > 0: heatingNumbers = sumAllLists(heatingNumbers)
        if len(solarNumbers) > 0: solarNumbers = sumAllLists(solarNumbers)
        if len(lightingNumbers) > 0: lightingNumbers = sumAllLists(lightingNumbers)
        if len(equipNumbers) > 0: equipNumbers = sumAllLists(equipNumbers)
        if len(peopleNumbers) > 0: peopleNumbers = sumAllLists(peopleNumbers)
        if len(infiltrationNumbers) > 0: infiltrationNumbers = sumAllLists(infiltrationNumbers)
        if len(outdoorAirNumbers) > 0: outdoorAirNumbers = sumAllLists(outdoorAirNumbers)
        if len(natVentNumbers) > 0: natVentNumbers = sumAllLists(natVentNumbers)
        if len(coolingNumbers) > 0: coolingNumbers = sumAllLists(coolingNumbers)
        if len(opaqueEnergyFlow) > 0: opaqueEnergyFlow = sumAllLists(opaqueEnergyFlow)
        if len(glazingEnergyFlow) > 0: glazingEnergyFlow = sumAllLists(glazingEnergyFlow)
        
        #Subtract the solar load from the glazing energy flow to get just the heat conduction through the glazing.
        for count, val in enumerate(glazingEnergyFlow):
            glazingEnergyFlow[count] = val - solarNumbers[count]
        
        #Make sure that the cooling energy is negative.
        if len(coolingNumbers) > 0:
            for count, val in enumerate(coolingNumbers):
                coolingNumbers[count] = -val
        
        #Add headers to the data number lists
        if len(heatingNumbers) > 0: heatingHeader = heatingHeaders[0][:2] + ['Heating'] + [heatingUnits] + [heatingHeaders[0][4]] + heatingAnalysisPeriod
        if len(solarNumbers) > 0: solarHeader = solarHeaders[0][:2] + ['Solar'] + [solarUnits] + [solarHeaders[0][4]] + solarAnalysisPeriod
        if len(lightingNumbers) > 0: lightingHeader = lightingHeaders[0][:2] + ['Lighting'] + [lightingUnits] + [lightingHeaders[0][4]] + lightingAnalysisPeriod
        if len(equipNumbers) > 0: equipHeader = equipHeaders[0][:2] + ['Equipment'] + [equipUnits] + [equipHeaders[0][4]] + equipAnalysisPeriod
        if len(peopleNumbers) > 0: peopleHeader = peopleHeaders[0][:2] + ['People'] + [peopleUnits] + [peopleHeaders[0][4]] + peopleAnalysisPeriod
        if len(infiltrationNumbers) > 0: infiltrationHeader = infiltrationHeaders[0][:2] + ['Infiltration'] + [infiltrationUnits] + [infiltrationHeaders[0][4]] + infiltrationAnalysisPeriod
        if len(outdoorAirNumbers) > 0: outdoorAirHeader = outdoorAirHeaders[0][:2] + ['Outdoor Air'] + [outdoorAirUnits] + [outdoorAirHeaders[0][4]] + outdoorAirAnalysisPeriod
        if len(natVentNumbers) > 0: natVentHeader = natVentHeaders[0][:2] + ['Natural Ventilation'] + [natVentUnits] + [natVentHeaders[0][4]] + natVentAnalysisPeriod
        if len(coolingNumbers) > 0: coolingHeader = coolingHeaders[0][:2] + ['Cooling'] + [coolingUnits] + [coolingHeaders[0][4]] + coolingAnalysisPeriod
        if len(opaqueEnergyFlow) > 0: opaqueHeader = surfaceHeaders[0][:2] + ['Opaque Conduction'] + [surfaceUnits] + [surfaceHeaders[0][4]] + surfaceAnalysisPeriod
        if len(glazingEnergyFlow) > 0: glazingHeader = surfaceHeaders[0][:2] + ['Glazing Conduction'] + [surfaceUnits] + [surfaceHeaders[0][4]] + surfaceAnalysisPeriod
        
        #Put each of the terms into one master list.    
        modelEnergyBalance = []
        modelEnergyBalanceNum = []
        if len(heatingNumbers) > 0:
            modelEnergyBalance.append(heatingHeader + heatingNumbers)
            modelEnergyBalanceNum.append(heatingNumbers)
        if len(solarNumbers) > 0:
            modelEnergyBalance.append(solarHeader + solarNumbers)
            modelEnergyBalanceNum.append(solarNumbers)
        if len(lightingNumbers) > 0:
            modelEnergyBalance.append(lightingHeader + lightingNumbers)
            modelEnergyBalanceNum.append(lightingNumbers)
        if len(equipNumbers) > 0:
            modelEnergyBalance.append(equipHeader + equipNumbers)
            modelEnergyBalanceNum.append(equipNumbers)
        if len(peopleNumbers) > 0:
            modelEnergyBalance.append(peopleHeader + peopleNumbers)
            modelEnergyBalanceNum.append(peopleNumbers)
        if len(infiltrationNumbers) > 0:
            modelEnergyBalance.append(infiltrationHeader + infiltrationNumbers)
            modelEnergyBalanceNum.append(infiltrationNumbers)
        if len(outdoorAirNumbers) > 0:
            modelEnergyBalance.append(outdoorAirHeader + outdoorAirNumbers)
            modelEnergyBalanceNum.append(outdoorAirNumbers)
        if len(natVentNumbers) > 0:
            modelEnergyBalance.append(natVentHeader + natVentNumbers)
            modelEnergyBalanceNum.append(natVentNumbers)
        if len(opaqueEnergyFlow) > 0:
            modelEnergyBalance.append(opaqueHeader + opaqueEnergyFlow)
            modelEnergyBalanceNum.append(opaqueEnergyFlow)
        if len(glazingEnergyFlow) > 0:
            modelEnergyBalance.append(glazingHeader + glazingEnergyFlow)
            modelEnergyBalanceNum.append(glazingEnergyFlow)
        if len(coolingNumbers) > 0:
            modelEnergyBalance.append(coolingHeader + coolingNumbers)
            modelEnergyBalanceNum.append(coolingNumbers)
        
        #Create an energy balance list with a storage term.
        energyBalWithStorage = modelEnergyBalance[:]
        storageHeaderInit = modelEnergyBalance[0][:7]
        storageHeader = storageHeaderInit[:2] + ['Storage'] + storageHeaderInit[3:7]
        storageNumbers = sumAllLists(modelEnergyBalanceNum)
        for count, val in enumerate(storageNumbers):
            storageNumbers[count] = -val
        energyBalWithStorage.append(storageHeader + storageNumbers)
        
        
        return modelEnergyBalance, energyBalWithStorage
    else: return -1


hbCheck = True
if sc.sticky.has_key('honeybee_release') == False:
    hbCheck = False
    print "You should first let Honeybee  fly..."
    ghenv.Component.AddRuntimeMessage(w, "You should first let Honeybee fly...")



if hbCheck == True and _HBZones != []:
    if heating_.BranchCount > 0 or totalSolarGain_.BranchCount > 0 or  electricLight_.BranchCount > 0 or  electricEquip_.BranchCount > 0 or  peopleGains_.BranchCount > 0 or  surfaceEnergyFlow_.BranchCount > 0 or infiltrationEnergy_.BranchCount > 0 or outdoorAirEnergy_.BranchCount > 0 or natVentEnergy_.BranchCount > 0 or cooling_.BranchCount > 0:
        modelEnergyBalanceInit, energyBalWithStorageInit = main(_HBZones, heating_, totalSolarGain_, electricLight_, electricEquip_, peopleGains_, surfaceEnergyFlow_, infiltrationEnergy_, outdoorAirEnergy_, natVentEnergy_, cooling_)
        
        if modelEnergyBalanceInit != -1:
            modelEnergyBalance = DataTree[Object]()
            energyBalWithStorage = DataTree[Object]()
            
            for dataCount, dataList in enumerate(modelEnergyBalanceInit):
                for item in dataList: modelEnergyBalance.Add(item, GH_Path(dataCount))
            for dataCount, dataList in enumerate(energyBalWithStorageInit):
                for item in dataList: energyBalWithStorage.Add(item, GH_Path(dataCount))