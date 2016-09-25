import urllib
import requests
import ujson
import csv

#pubLINCS is a class of functions used for obtaining CID and Name from PubChem for some input structure in smiles format.
class pubLINCS(object):

	def __init__(self):#a "constructor" for the pubLINCS class.
		print("Verification Started")#tells you the class was instantiated.
				
	def buildSmilesList(self): #this function takes the input smiles in .tsv format since this was the common exchange format for small molecule submissions.
		with open('smiles2cid_VerifificationPipelineInputTestSet.txt', 'r') as f:
			centerCompoundIds = [] #list to hold compound Id. 
			inputCIDs = [] #list to hold input CIDs.
			centerSmiles = [] #list to hold input smiles.
			reader = csv.reader(f, delimiter='\t')#instantiate csv reader object.
			flagHdr = 1 #skip header flag, binary: 1=yes, 0=no
			#the following loop populates the CID, molecule names, and input smiles lists.
			for row in reader:
				if flagHdr == 1: #is this header test
					row = (next(reader)) #skip header
					flagHdr = 0 #set header flag to no
				centerCompoundIds.append(row[0]) #populate compuond id list. column location 0 is hardcoded, positions are fixed in input file.
				inputCIDs.append(row[1])
				centerSmiles.append(row[2]) #populate input smiles list. column location 1 is hardcoded, positions are fixed in input file.
		return centerCompoundIds, centerSmiles, inputCIDs
		#end buildSmilesList function.
		
	def getCidFromSmiles(self, smiles):#this function takes an input smiles, gets pubchem standardization, and returns CID and standard structure.
		smiles = urllib.parse.quote_plus(smiles)
		url3 = "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/smiles/record/JSON?Content-Type:%20application/x-www-form-urlencoded&smiles="+smiles
		try:#try and request standardization and records for standardized structure.
			thisResponse = requests.get(url3, timeout=90)
		except requests.exceptions.RequestException as e:#if there is a problem make a log and return some dummy values for CID and structure.
			CID = 'Error inpubchem requests. See errorLog.txt'
			isoSmiles = 'Error inpubchem requests. See errorLog.txt'
			InChi = 'Error inpubchem requests. See errorLog.txt'
			with open('errorLog.txt', 'a') as f:
				line = 'Requests Error =\n'+e+'\nBad URL =\n'+url3+'\n'
				f.write(line)
			return CID, isoSmiles, InChi
		#the following block catches invalid smiles (or other 400 code) and returns the pubchem error text. The 'None' values trigger error output in the main loop.
		if thisResponse.status_code == 400:#PubChem returns 400 status if "molecule failed standardization".
			dataTarget=ujson.loads(thisResponse.text)
			for index, key in enumerate(dataTarget['Fault']['Details']):
				if 'Warning' in dataTarget['Fault']['Details'][index]:
					CID = dataTarget['Fault']['Details'][index]#dataTarget['Fault'].get('PubChem Warning')
					isoSmiles =  None
					InChi = None
					return CID, isoSmiles, InChi#end 400 status block.
					
		else:#next block loads the json response and returns CID and structures if there is no 400 status returned. 
			dataTarget=ujson.loads(thisResponse.text)
			if dataTarget['PC_Compounds'][0]['id'] == {}:#check for an empty CID. Pubchem will return a record with no CID for all valid structures.
				CID = "Smiles is a valid structure, but does not have CID. Check returned smiles against input smiles."
				pass#go on to get the smiles without CID.
			else:#get the CID if it is there.
				CID = (dataTarget['PC_Compounds'][0]['id']['id']['cid'])
			#The position of the structure children under the properties parent will load differently in the json parser; the next loop block loops all properties children and test for correct keys.	
			for index, record in enumerate(dataTarget['PC_Compounds'][0]['props']):
				if dataTarget['PC_Compounds'][0]['props'][index]['urn']['label'] == 'InChI':
					InChi = dataTarget['PC_Compounds'][0]['props'][index]['value']['sval']
				elif dataTarget['PC_Compounds'][0]['props'][index]['urn']['label'] == 'SMILES' and dataTarget['PC_Compounds'][0]['props'][index]['urn']['name'] == 'Isomeric':
					isoSmiles = dataTarget['PC_Compounds'][0]['props'][index]['value']['sval']
			return CID, isoSmiles, InChi#end 'get CID and structures block.
		#end getCidFromSmiles function.	
						
	def getNameFromCID(self, CID):#this function takes a CID and returns the PubChem preferred or 'best match' name
		if type(CID) is str:#test for non-numerical CID to make sure it is valid CID.
			pubChemName = 'No name found. No CID input value.'
			return pubChemName#retrun a dummy value for PubChem Name if there is no valid CID.
		url3 = "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/"+str(CID)+"/synonyms/JSON"
		print(url3)
		try:#try to request a name from the CID. First name in synonym response is pubchem's preferred name.
			thisResponse = requests.get(url3, timeout=90)
		except requests.exceptions.RequestException as e:#if there is a problem make a log and return some dummy values for PubChem name.
			pubChemName = 'Error inpubchem requests. See errorLog.txt'
			with open('errorLog.txt', 'a') as f:
				line = 'Requests Error =\n'+e+'\nBad URL =\n'+url3+'\n'
				f.write(line)
		if thisResponse.status_code == 404: #PubChem returns 404 status if "no names found for valid CID"
			dataSynonyms=ujson.loads(thisResponse.text)#load request into json parser.
			pubChemName = dataSynonyms['Fault'].get('Message')
			return pubChemName#return "valid without name" value for pubChemName.
		dataSynonyms=ujson.loads(thisResponse.text)#load request into json parser.
		pubChemName = dataSynonyms['InformationList']['Information'][0]['Synonym'][0]#get first name (preferred name) from synonym list.
		return pubChemName
		#end getNameFromCID function.
		
if __name__ == "__main__":
	pB = pubLINCS()
	centerCompoundIds, centerSmiles, inputCIDs = pB.buildSmilesList()
	with open('smiles2cid_VerifificationPipelineOutput.txt', 'w') as outFile:
		line = 'CenterCompoundID\tPubChemName\tInputCID\tPubChemCID\tInputSMILES\tPubChemSMILES\n'
		outFile.write(line)
		for index, smiles in enumerate(centerSmiles):
			CID, isoSmiles, InChi = pB.getCidFromSmiles(smiles)
			if InChi == None:#this catches the 400 status and outputs the PubChem error in the CID and SMILES fields. 
				line = centerCompoundIds[index]+'\tInvalid input structure: '+CID+'\tInvalid input structure: '+CID+'\tInvalid input structure: '+CID+'\tInvalid input structure: '+CID+'\tInvalid input structure: '+CID+'\n'
				print(line)
				outFile.write(line)
			else:
				line = centerCompoundIds[index]+'\t'+pB.getNameFromCID(CID)+'\t'+inputCIDs[index]+'\t'+str(CID)+'\t'+smiles+'\t'+isoSmiles+'\n'
				print(line)
				outFile.write(line)
			