#! python3
# -*- coding: utf-8 -*-


import clr
import Autodesk.Revit.DB as DB
import sys
#sys.path.append(r'C:\Users\Asus\anaconda3\envs\PyRevit\Lib\site-packages')
#import pandas as pd
import json
import csv
import os.path
from Autodesk.Revit.DB import Transaction

clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')

doc = __revit__.ActiveUIDocument.Document

categories = [
    DB.BuiltInCategory.OST_Walls,
    DB.BuiltInCategory.OST_Floors,
    DB.BuiltInCategory.OST_Roofs,
    DB.BuiltInCategory.OST_StructuralColumns,
    DB.BuiltInCategory.OST_StructuralFraming,
    DB.BuiltInCategory.OST_Columns,
    DB.BuiltInCategory.OST_Doors,
    DB.BuiltInCategory.OST_Windows,
    DB.BuiltInCategory.OST_CurtainWallPanels,
    DB.BuiltInCategory.OST_Stairs,
    DB.BuiltInCategory.OST_StructuralFoundation,
]

data = []

for category in categories:
    elements = DB.FilteredElementCollector(doc).OfCategory(category).WhereElementIsNotElementType().ToElements()
    for element in elements:
        element_type = doc.GetElement(element.GetTypeId()) # para propriedades do tipo
        family_name = element_type.FamilyName # para propriedades do elemet o tipo
        element_Id = element.Id.ToString()
        #type_name = element_type.ToDSType(False).Name
        type_name = element.Name
        #DB.ElementType.Name.GetValue(element)
        volume = 0

        try:
            volume= element.get_Parameter(DB.BuiltInParameter.HOST_VOLUME_COMPUTED).AsDouble() * 0.0283168 #HOST_VOLUME_COMPUTED convert cubic feet to cubic meters
        except:
            pass

        try:
            area = element.get_Parameter(
                DB.BuiltInParameter.HOST_AREA_COMPUTED).AsDouble() * 0.092903  # convert square feet to square meters
            length = element.get_Parameter(
                DB.BuiltInParameter.CURVE_ELEM_LENGTH).AsDouble() * 0.3048  # convert feet to meters
        except:
            pass
       #SECCLASS CODES
        shared_parameter = element_type.LookupParameter("ClassificacaoSecclassSsNumero")
        if shared_parameter:
            shared_parameter_value = shared_parameter.AsString()
        else:
            shared_parameter_value = None

        shared_parameter2 = element_type.LookupParameter("ClassificacaoSecclassSsDescricao")
        if shared_parameter2:
            shared_parameter_value2 = shared_parameter2.AsString()
        else:
            shared_parameter_value2 = None

        phase_parameter = element.LookupParameter("Phase Created")
        if phase_parameter:
            phase_parameter_value2 = None
        else:
            phase_parameter_value2 = None
        #classificacao_parameter = element.get_Parameter("04466190-35a1-4404-82d0-898f32b92ec4")
        #classificacao_value = classificacao_parameter.AsString() if classificacao_parameter else None

        Export_BIM_data = {
            "ElementID": element_Id,
            "SECClasS_Code": shared_parameter_value,
            "SECClasS_Title": shared_parameter_value2,
            "Family and Type": "{} - {}".format(family_name, type_name),
            "Volume": round(volume, 2),
            "Area": round(area, 2),
            "Length": round(length, 2),
            "Phase_Created": phase_parameter_value2
        }
        data.append(Export_BIM_data)





####### Tabela csv #### SEC-WBS #######
script_dir = os.path.dirname(__file__) # path do script a correr
parentDirectory = os.path.dirname(script_dir) # path pai do script
SEC_WBS_file_path = os.path.join(parentDirectory, 'FileCreator.pushbutton', 'SEC_WBS.csv') # path da pasta e nome do cdv a abrir
with open(SEC_WBS_file_path, mode='r', encoding='utf-8-sig') as SEC_WBS:
    SEC_WBS_table = csv.DictReader(SEC_WBS, delimiter=";")
    SEC_WBS_data = list(SEC_WBS_table)
for i in range(len(SEC_WBS_data)):
    for key in SEC_WBS_data[i]:
        SEC_WBS_data[i][key] = SEC_WBS_data[i][key].replace(',', '.')


###### Tabela csv #### Co2Value ######
Co2Value_file_path = os.path.join(parentDirectory, 'FileCreator.pushbutton', 'Co2Value.csv')
with open(Co2Value_file_path, mode='r', encoding='utf-8-sig') as SEC_WBS:
    Co2Value_table = csv.DictReader(SEC_WBS, delimiter=";")
    Co2Value_data = list(Co2Value_table)
for i in range(len(Co2Value_data)):
    for key in Co2Value_data[i]:
        Co2Value_data[i][key] = Co2Value_data[i][key].replace(',', '.')

#print(Co2Value_data)
#2 MAPEAMENTO SECCLASS WBS E MEDIDAS
for i in range(len(data)):
  for row in SEC_WBS_data:
    if data[i]['SECClasS_Code'] is None:
        pass
    else:
        if data[i]['SECClasS_Code'] == row['SECClasS_Code']:
          data[i]['Quantity of elements'] = None
          data[i]['WBS_L1'] = row['WBS_L1']
          data[i]['WBS_Title_L1'] = row['WBS_Title_L1']
          data[i]['WBS_L2'] = row['WBS_L2']
          data[i]['WBS_Title_L2'] = row['WBS_Title_L2']
          data[i]['WBS_L3'] = row['WBS_L3']
          data[i]['WBS_Title_L3'] = row['WBS_Title_L3']
          data[i]['WBS_Code'] = row['WBS_Code']
          data[i]['Expected_lifespan'] = row['Expected_lifespan']
          data[i]['Mass'] = None
          data[i]['Co2_Total'] = None
          data[i]['BLC_Mass_Total'] = None
          data[i]['BLC_Co2_Total'] = None
          data[i]['Normalised requirement factor over building lifetime'] = None
          data[i]['Measure'] = row['Measure']
          data[i]['Conversion_Factor'] = row['Conversion Factor (Kg/m3, Kg/m2;kg/m;k/U)']
          data[i]['Unit_Cost'] = row['Unit_Cost']
          data[i]['Cost'] = None
          data[i]['GWP_A1-A3'] = row['GWP A1-A3 (Kg/m3, Kg/m2;kg/m;k/U)']

#3 Filtro Phase Created
list_new = []
list_existing = []
for row in data:
  if row['Phase_Created'] == "New Construction":
    list_new.append(row)
  elif row['Phase_Created'] == "Existing":
    list_existing.append(row)
  else:
    list_new.append(row) # ver isto mais tarde
data = list_new #passa a ser data


#3 Filtro só classificados
list_classified= []
list_notclassified= []
for row in data:
  if row['SECClasS_Code'] is not None:
    list_classified.append(row)
  else:
    list_notclassified.append(row)

data = list_classified #passa a ser data

## add ao Export BIM coluna do id
for id in range(len(data)):
    data[id]["id"] = id
#### Contagem de elementos ####
count_dict = {}

for row in data:
    if 'SECClasS_Code' in row:
        code = row['SECClasS_Code']
        if code in count_dict:
            count_dict[code] += 1
        else:
            count_dict[code] = 1
for row in data:
    if 'SECClasS_Code' in row:
        code = row['SECClasS_Code']
        if code in count_dict:
            row['Quantity of elements'] = count_dict[code]

#############



# lê o documento da informação do utilizador
script_dir = os.path.dirname(__file__) # path do script a correr
parentDirectory = os.path.dirname(script_dir) # path pai do script
csv_file_path = os.path.join(parentDirectory, 'FileCreator.pushbutton', 'Building_Elements_Information.csv') # path da pasta e nome do cdv a abrir

column_names = ["ref",
      "SECClasS_Code",
      "SECClasS_Title",
      "Quantity of elements",
      "Measure",
      "Conversion Factor (kg/m3, kg/m2, kg/m, kg/u)",
      "GWP A1-A3 (kgCo2e/m3, kgCo2e/m2, kgCo2e/m, kgCo2e/u)",
      "Unit Cost (€/unit of measure)",
      "Concrete (%)",
      "Bricks (%)",
      "Tiles (%)",
      "Ceramics (%)",
      "Wood (%)",
      "Glass (%)",
      "Plastic (%)",
      "Bituminous mixtures (%)",
      "Copper/bronze/brass (%)",
      "Aluminium (%)",
      "Iron/steel (%)",
      "Other metal (%)",
      "Soil and stones (%)",
      "Dredging spoil (%)",
      "Track ballast (%)",
      "Insulation materials (%)",
      "Asbestos containing materials (%)",
      "Gypsum-based materials (%)",
      "Electrical and Electronic Equipment (%)",
      "Cables (%)",
      "Total (must be 100%)"]

with open(csv_file_path, mode='r', encoding='utf-8-sig') as file:
    reader = csv.DictReader(file, delimiter=';', fieldnames=column_names)
    EI = list(reader)[1:]
for i in range(len(EI)):
    for key in EI[i]:
        EI[i][key] = EI[i][key].replace(',', '.')


########################################

# lê o documento da informação do utilizador
#path = "SECAPP.extension\SECC.tab\ByElement.panel\FileCreator.pushbutton\Building_Information.csv"
#csv_file_path1 = os.path.dirname(path)
csv_file_path1 = os.path.join(parentDirectory, 'FileCreator.pushbutton', 'Building_Information.csv') # path da pasta e nome do cdv a abrir
column_names2 = ["Project Number",
      "Project Name",
      "Building Name",
      "Building GFA (m2)*",
      "Building lifespan (years)*"]

with open(csv_file_path1, mode='r', encoding='utf-8-sig') as file:
    reader = csv.DictReader(file, delimiter=';', fieldnames=column_names2)
    BI = list(reader)[1]
for key in BI:
    BI[key] = BI[key].replace(',', '.')


#print(BI)
#print("EI", EI)

Project_Number = BI.get('Project Number')[0]
Project_Name = BI.get('Project Name')[0]
Building_Name = BI.get('Building Name')[0]
Building_GFA = float(str(BI.get('Building GFA (m2)*')[0]).replace(',','.'))
Building_lifespan = float(str(BI.get('Building lifespan (years)*')[0]).replace(',','.'))
####################################

#print("data", data)

###########  Cascata  ###########

for i in range(len(data)):
    mass = 0
    row = data[i]
    temp = []
    for key in range(len(EI)):
        if data[i]["SECClasS_Code"] == EI[key]["SECClasS_Code"]:
            #print(EI[key]["Conversion Factor (kg/m3, kg/m2, kg/m, kg/u)"])
            data[i]["Conversion_Factor"] = float(EI[key]["Conversion Factor (kg/m3, kg/m2, kg/m, kg/u)"])
            data[i]["Quantity of elements"] = int(EI[key]["Quantity of elements"])
        else:
            pass

    if 'Measure' in row:
        if row["Conversion_Factor"] is None:
            mass = 0
            cost = 0
        else:
            if row['Measure'] == "V":
                mass = float(str(row['Volume'])) * float(row["Conversion_Factor"])
                cost = float(str(row['Volume'])) * float(row["Unit_Cost"])

            elif row['Measure'] == "A":
                mass = float(str(row['Area'])) * float(row["Conversion_Factor"])
                cost = float(str(row['Area'])) * float(row["Unit_Cost"])

            elif row['Measure'] == "L":
                mass = float(str(row['Length'])) * float(row["Conversion_Factor"])
                cost = float(str(row['Length'])) * float(row["Unit_Cost"])

            elif row['Measure'] == "U":
                mass = row["Conversion_Factor"]
                cost = row["Unit_Cost"]
            else:
                pass

    # Adicionar os valores ao MASS do data
    data[i]['Mass'] = mass
    data[i]['Cost'] = cost


#print(data[0])
#print(data[0]['Mass'])

#Calculo das Massa por material e add no data
for key in range(len(EI)):
  #if "Concrete (%)" in list(EI):
    for lists in data:
      #print(EI.get("SECClasS_Code")[key])
      if EI[key]["SECClasS_Code"] == lists['SECClasS_Code']:
        GWP = float(str(EI[key]['GWP A1-A3 (kgCo2e/m3, kgCo2e/m2, kgCo2e/m, kgCo2e/u)']).replace(',','.'))

        if GWP > 0 or GWP is None:
          data[lists['id']]["GWP_A1-A3"] = GWP
        else:
            Mass = data[lists['id']]['Mass']
            if Mass is not None:
                data[lists['id']].update({
                    'Mass_Concrete': float(str(EI[key]['Concrete (%)']).replace(',', '.')) * Mass,
                    'Mass_Bricks': float(str(EI[key]['Bricks (%)']).replace(',', '.')) * Mass,
                    'Mass_Tiles': float(str(EI[key]['Tiles (%)']).replace(',', '.')) * Mass,
                    'Mass_Ceramics': float(str(EI[key]['Ceramics (%)']).replace(',', '.')) * Mass,
                    'Mass_Wood': float(str(EI[key]['Wood (%)']).replace(',', '.')) * Mass,
                    'Mass_Glass': float(str(EI[key]['Glass (%)']).replace(',', '.')) * Mass,
                    'Mass_Plastic': float(str(EI[key]['Plastic (%)']).replace(',', '.')) * Mass,
                    'Mass_Bituminous_mixtures': float(str(EI[key]['Bituminous mixtures (%)']).replace(',', '.')) * Mass,
                    'Mass_Copper_bronze_brass': float(str(EI[key]['Copper/bronze/brass (%)']).replace(',', '.')) * Mass,
                    'Mass_Aluminium': float(str(EI[key]['Aluminium (%)']).replace(',', '.')) * Mass,
                    'Mass_Iron_steel': float(str(EI[key]['Iron/steel (%)']).replace(',', '.')) * Mass,
                    'Mass_Other_metal': float(str(EI[key]['Other metal (%)']).replace(',', '.')) * Mass,
                    'Mass_Soil_stones': float(str(EI[key]['Soil and stones (%)']).replace(',', '.')) * Mass,
                    'Mass_Dredging_spoil': float(str(EI[key]['Dredging spoil (%)']).replace(',', '.')) * Mass,
                    'Mass_Track_ballast': float(str(EI[key]['Track ballast (%)']).replace(',', '.')) * Mass,
                    'Mass_Insulation_materials': float(
                        str(EI[key]['Insulation materials (%)']).replace(',', '.')) * Mass,
                    'Mass_Asbestos_containing_materials': float(
                        str(EI[key]['Asbestos containing materials (%)']).replace(',', '.')) * Mass,
                    'Mass_Gypsum_based_materials': float(
                        str(EI[key]['Gypsum-based materials (%)']).replace(',', '.')) * Mass,
                    'Mass_Electrical_electronic_equipment': float(
                        str(EI[key]['Electrical and Electronic Equipment (%)']).replace(',', '.')) * Mass,
                    'Mass_Cables': float(str(EI[key]['Cables (%)']).replace(',', '.')) * Mass,
                })
            else:
                pass

# Calculo Co2
for row in data:
  if "Mass" in row and (row["GWP_A1-A3"] is None or float(row["GWP_A1-A3"]) == 0):
      Co2_temp = {
          'Co2_Concrete': float(Co2Value_data[0]['A1_A3']) * float(row['Mass_Concrete']),
          'Co2_Bricks': float(Co2Value_data[1]['A1_A3']) * float(row['Mass_Bricks']),
          'Co2_Tiles': float(Co2Value_data[2]['A1_A3']) * float(row['Mass_Tiles']),
          'Co2_Ceramics': float(Co2Value_data[3]['A1_A3']) * float(row['Mass_Ceramics']),
          'Co2_Wood': float(Co2Value_data[4]['A1_A3']) * float(row['Mass_Wood']),
          'Co2_Glass': float(Co2Value_data[5]['A1_A3']) * float(row['Mass_Glass']),
          'Co2_Plastic': float(Co2Value_data[6]['A1_A3']) * float(row['Mass_Plastic']),
          'Co2_Bituminous_mixtures': float(Co2Value_data[7]['A1_A3']) * float(row['Mass_Bituminous_mixtures']),
          'Co2_Copper_bronze_brass': float(Co2Value_data[8]['A1_A3']) * float(row['Mass_Copper_bronze_brass']),
          'Co2_Aluminium': float(Co2Value_data[9]['A1_A3']) * float(row['Mass_Aluminium']),
          'Co2_Iron_steel': float(Co2Value_data[10]['A1_A3']) * float(row['Mass_Iron_steel']),
          'Co2_Other_metal': float(Co2Value_data[11]['A1_A3']) * float(row['Mass_Other_metal']),
          'Co2_Soil_stones': float(Co2Value_data[12]['A1_A3']) * float(row['Mass_Soil_stones']),
          'Co2_Dredging_spoil': float(Co2Value_data[13]['A1_A3']) * float(row['Mass_Dredging_spoil']),
          'Co2_Track_ballast': float(Co2Value_data[14]['A1_A3']) * float(row['Mass_Track_ballast']),
          'Co2_Insulation_materials': float(Co2Value_data[15]['A1_A3']) * float(row['Mass_Insulation_materials']),
          'Co2_Asbestos_containing_materials': float(Co2Value_data[16]['A1_A3']) * float(
              row['Mass_Asbestos_containing_materials']),
          'Co2_Gypsum_based_materials': float(Co2Value_data[17]['A1_A3']) * float(row['Mass_Gypsum_based_materials']),
          'Co2_Electrical_electronic_equipment': float(Co2Value_data[18]['A1_A3']) * float(
              row['Mass_Electrical_electronic_equipment']),
          'Co2_Cables': float(Co2Value_data[19]['A1_A3']) * float(row['Mass_Cables']),
      }
      data[row['id']].update(Co2_temp)
      sum_Co2 = sum(Co2_temp.values())
      data[row['id']]['Co2_Total'] = sum_Co2


    # Calculo Co2_GWP
  elif float(row["GWP_A1-A3"]) > 0 or not None:
    if row["Measure"] == "V" and float(row["GWP_A1-A3"]) > 0:
      Co2_GWP = row['Volume'] * row["GWP_A1-A3"]
    elif row["Measure"] == "A" and float(row["GWP_A1-A3"]) > 0:
      Co2_GWP = row['Area'] * float(row["GWP_A1-A3"])
    elif row["Measure"] == "L" and float(row["GWP_A1-A3"]) > 0:
      Co2_GWP = row['Length'] * float(row["GWP_A1-A3"])
    elif row["Measure"] == "U" and float(row["GWP_A1-A3"]) > 0:
      Co2_GWP = float(row["GWP_A1-A3"])
    else:
      Co2_GWP = 0
    data[row['id']]['Co2_Total'] = Co2_GWP
    #print(row['id'], row['SECClasS_Code'], "Co2_GWP=", Co2_GWP)

# LP * Expected_lifespan e add vari LP_factor * mass
for row in data:
  BLC = float(Building_lifespan) / float(row['Expected_lifespan'])
  data[row['id']]['Normalised requirement factor over building lifetime'] = BLC
  data[row['id']]['BLC_Mass_Total'] = float(row['Mass']) * float(BLC)
  if row["Co2_Total"] is not None:
    data[row['id']]['BLC_Co2_Total'] = row['Co2_Total'] * BLC
  if "Mass_Concrete" in row:
    data[row['id']].update({
              'BLC_Mass_Concrete': BLC * row['Mass_Concrete'],
              'BLC_Mass_Bricks': BLC * row['Mass_Bricks'],
              'BLC_Mass_Tiles': BLC * row['Mass_Tiles'],
              'BLC_Mass_Ceramics': BLC * row['Mass_Ceramics'],
              'BLC_Mass_Wood': BLC * row['Mass_Wood'],
              'BLC_Mass_Glass': BLC * row['Mass_Glass'],
              'BLC_Mass_Plastic': BLC * row['Mass_Plastic'],
              'BLC_Mass_Bituminous_mixtures': BLC * row['Mass_Bituminous_mixtures'],
              'BLC_Mass_Copper_bronze_brass': BLC * row['Mass_Copper_bronze_brass'],
              'BLC_Mass_Aluminium': BLC * row['Mass_Aluminium'],
              'BLC_Mass_Iron_steel': BLC * row['Mass_Iron_steel'],
              'BLC_Mass_Other_metal': BLC * row['Mass_Other_metal'],
              'BLC_Mass_Soil_stones': BLC * row['Mass_Soil_stones'],
              'BLC_Mass_Dredging_spoil': BLC * row['Mass_Dredging_spoil'],
              'BLC_Mass_Track_ballast': BLC * row['Mass_Track_ballast'],
              'BLC_Mass_Insulation_materials': BLC * row['Mass_Insulation_materials'],
              'BLC_Mass_Asbestos_containing_materials': BLC * row['Mass_Asbestos_containing_materials'],
              'BLC_Mass_Gypsum_based_materials': BLC * row['Mass_Gypsum_based_materials'],
              'BLC_Mass_Electrical_electronic_equipment':BLC * row['Mass_Electrical_electronic_equipment'],
              'BLC_Mass_Cables': BLC * row['Mass_Cables'],
              })
  if "Co2_Concrete" in row:
    data[row['id']].update({
            'BLC_Co2_Concrete': BLC * row['Co2_Concrete'],
            'BLC_Co2_Bricks': BLC * row['Co2_Bricks'],
            'BLC_Co2_Tiles': BLC * row['Co2_Tiles'],
            'BLC_Co2_Ceramics': BLC * row['Co2_Ceramics'],
            'BLC_Co2_Wood': BLC * row['Co2_Wood'],
            'BLC_Co2_Glass': BLC * row['Co2_Glass'],
            'BLC_Co2_Plastic': BLC * row['Co2_Plastic'],
            'BLC_Co2_Bituminous_mixtures': BLC * row['Co2_Bituminous_mixtures'],
            'BLC_Co2_Copper_bronze_brass': BLC * row['Co2_Copper_bronze_brass'],
            'BLC_Co2_Aluminium': BLC * row['Co2_Aluminium'],
            'BLC_Co2_Iron_steel': BLC * row['Co2_Iron_steel'],
            'BLC_Co2_Other_metal': BLC * row['Co2_Other_metal'],
            'BLC_Co2_Soil_stones': BLC * row['Co2_Soil_stones'],
            'BLC_Co2_Dredging_spoil': BLC * row['Co2_Dredging_spoil'],
            'BLC_Co2_Track_ballast': BLC * row['Co2_Track_ballast'],
            'BLC_Co2_Insulation_materials': BLC * row['Co2_Insulation_materials'],
            'BLC_Co2_Asbestos_containing_materials': BLC * row['Co2_Asbestos_containing_materials'],
            'BLC_Co2_Gypsum_based_materials': BLC * row['Co2_Gypsum_based_materials'],
            'BLC_Co2_Electrical_electronic_equipment':BLC * row['Co2_Electrical_electronic_equipment'],
            'BLC_Co2_Cables': BLC * row['Co2_Cables'],
            })
###############################################################################

############# Somatorio de Mass, Co2, Mass_BLC and Co2_BLC
TOTAL_MASS = 0
TOTAL_CO2 = 0
TOTAL_MASS_BLC = 0
TOTAL_CO2_BLC = 0
TOTAL_COST = 0
for row in data:
  TOTAL_MASS = TOTAL_MASS + row['Mass']
  TOTAL_CO2 = TOTAL_CO2 + row['Co2_Total']
  TOTAL_MASS_BLC = TOTAL_MASS_BLC + row['BLC_Mass_Total']
  TOTAL_CO2_BLC = TOTAL_CO2_BLC + row['BLC_Co2_Total']
  TOTAL_COST = float(TOTAL_COST)+ float(row['Cost'])
  SOCIAL_COST = float((TOTAL_CO2 / 1000)) * 50
Normalized_Co2 = float(TOTAL_CO2) / float(Building_GFA)
Normalized_2 = (Normalized_Co2 / Building_lifespan)
#########
# Define a separator line
separator = "_______________________________________________________________________________________________________________________________"

# Define a header for the program
header = "........................................................SECCALCULATOR.........................................................."
header_centered = header.center(len(separator))



# Print the formatted text
print(separator)
print(header_centered)
print(separator)
print("                 TOTALS   ", end=" ")
print(separator)
print("Mass Global = {:.2f} kg".format(TOTAL_MASS))
print("GWP Global = {:.2f} kgCo2e".format(TOTAL_CO2))
print("Normalized GWP = {:.2f} kgCo2e/m2".format(Normalized_Co2), end=" ")
print("Social Cost of Carbon = {:.2f} €".format(SOCIAL_COST), end=" ")
print("Mass Global considering Building Life Cycle  = {:.2f} kg".format(TOTAL_MASS_BLC), end=" ")
print("Co2 Global considering Building Life Cycle = {:.2f} kgCo2e".format(TOTAL_CO2_BLC))
print("Budget Estimate = {:.2f} €".format(TOTAL_COST))
print(separator)
print("The CSV and json files were created in the ../ByElement.panel/SECCalculator.pushbutton/SECCalculator.pushbutton: "
      "output_data.csv and output_data.json.  ")
print(separator)

###################################
json_file_path = os.path.join(os.path.dirname(__file__), "output_data.json")
csv3_file_path = os.path.join(os.path.dirname(__file__), "output_data.csv")
Output_APP = json.dumps(data)

jsonFile = open(json_file_path, mode='w', newline='')
jsonFile.write(Output_APP)
jsonFile.close()
with open(json_file_path) as json_file:
    data_json = json.load(json_file)

data_csv = open(csv3_file_path, mode='w', newline='', encoding='utf-8')
csv_writer = csv.writer(data_csv)

count = 0
for item in data_json:
    if count == 0:
        header = item.keys()
        csv_writer.writerow(header)
        count += 1

    csv_writer.writerow(item.values())

data_csv.close()

# Iniciando uma transação no Revit
transaction = Transaction(doc, "Atualizar parâmetro GWP(kgCo2e)")
transaction.Start()

for category in categories:
    elements = DB.FilteredElementCollector(doc).OfCategory(category).WhereElementIsNotElementType().ToElements()
    for element in elements:
        element_Id = element.Id.ToString()

        # Procurando o valor de CO2 correspondente na lista de dados
        data_item = next((item for item in data if item["ElementID"] == element_Id), None)

        # Verificando se foi encontrado um valor de CO2 correspondente
        if data_item is not None:
            #print(data_item["Co2_Total"])
            # Verificando se o parâmetro "GWP(kgCo2e)" existe no elemento
            if element.LookupParameter("GWP(kgCo2e)"):
                # Obtendo o parâmetro "GWP(kgCo2e)"
                parameter = element.LookupParameter("GWP(kgCo2e)")
                #print(type(parameter))
                # Atualizando o valor do parâmetro "GWP(kgCo2e)" com o valor de CO2 correspondente
                parameter.Set(data_item["Co2_Total"])

    # Finalizando a transação
transaction.Commit()