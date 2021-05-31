# Imports pyRoot, which requires a manual compile as defaut ROOT binary comes with a python2 support
from math import sqrt,fabs
import h5py
import numpy as np
import awkward as ak
import json
import ROOT
from ROOT import TLorentzVector

# Imports the required libDelphes, which is used to 
# identify the objects in the ROOT file generated by delphes
ROOT.gSystem.Load("libDelphes.so")

class GenDataset:
    ''' 
    Gives methods to generate datasets from the root file made in delphes. 
    This module helps in taking the required information from the ROOT file
     and dump it into a HDF5 file

    Attributes :
    ------------
    delphesFile : str
        Path to the input ROOT file

    isRapid : bool
        Decides the definition of the rotational data

    totalEvents : int
        Number of Total Events

    datasetDict : List
        A list of dictionary that stores 4-momenta and the rotational information of every event

    Methods :
    ---------
    createArrays()
        Populates the datasetDict from the ROOT file for further operation

    createDataset()
        Generates the .h5 file from the datasetDict, reuires the 
        createArray function to be run before

    getArraysFromFile()
        Accessor to get the dataset back from the .h5 file

    printPretty()
        Prints tables for the 4-momenta and the azimuthal angle for an event
    '''
    def __init__(self,delphesRootFile : str,isRapid : bool = True):
        '''
        Enter the required ROOT file

        Parameters :
        ------------
        delphesRootFile : str, required
            A valid path to the delphes generated ROOT file

        isRapid : bool
            True if the Delta R definition is to be take, 
            False for absolute difference in azimuthal angle

        Returns :
        --------
        Nothing
        '''
        self.delphesFile = delphesRootFile
        self.isRapid = isRapid
        self.totalEvents = 0
        self.datasetDict = None

    def createArrays(self):
        '''
        Generate and populate the datasetDict list. The list consists of a 
        dictionary that contatins the 4-momenta and the azimuthal angle of an event.

        Parameters :
        ------------
        Nothing

        Returns :
        ---------
        Nothing
        '''
        File = ROOT.TChain("Delphes;1")
        File.Add(self.delphesFile)
        self.totalEvents = File.GetEntries()

        print("INFO : Started Filtering Particles")
        eventDict = []
        for i in range(self.totalEvents):
        	Entry = File.GetEntry(i)

        	epArray = []
        	ezArray = []
        	az_angle = [] # Azimuthal Angle
        	ra_angle = [] # Rapidity

        	EntryFromBranch = File.Photon.GetEntries()	
        	for j in range(EntryFromBranch):
        		particleArray = [1,0,0,0,File.GetLeaf("Photon.PT").GetValue(j),
                                 File.GetLeaf("Photon.E").GetValue(j),0]
        		epArray.append(particleArray)

        		az_angle.append(File.GetLeaf("Photon.Phi").GetValue(j))
        		ra_angle.append(File.GetLeaf("Photon.Eta").GetValue(j))


        	EntryFromBranch = File.Jet.GetEntries()
        	for j in range(EntryFromBranch):
            
        		Jet = TLorentzVector()
        		Jet.SetPtEtaPhiM(File.GetLeaf("Jet.PT").GetValue(j),
                                 File.GetLeaf("Jet.Eta").GetValue(j),
                                 File.GetLeaf("Jet.Phi").GetValue(j),
                                 File.GetLeaf("Jet.Mass").GetValue(j))

        		particleArray = [0,0,1 if int(File.GetLeaf("Jet.BTag").GetValue(j)) == 1 else -1,
                                 0,File.GetLeaf("Jet.PT").GetValue(j),Jet.Energy(),
                                 File.GetLeaf("Jet.Mass").GetValue(j)]
        		epArray.append(particleArray)

        		az_angle.append(File.GetLeaf("Jet.Phi").GetValue(j))
        		ra_angle.append(File.GetLeaf("Jet.Eta").GetValue(j))

        	EntryFromBranch = File.Electron.GetEntries()
        	for j in range(EntryFromBranch):
        		Electron = TLorentzVector()
        		Electron.SetPtEtaPhiM(File.GetLeaf("Electron.PT").GetValue(j),
                                      File.GetLeaf("Electron.Eta").GetValue(j),
                                      File.GetLeaf("Electron.Phi").GetValue(j),
                                      0)

        		particleArray = [0,int(File.GetLeaf("Electron.Charge").GetValue(j)),0,0,
                                 File.GetLeaf("Electron.PT").GetValue(j),Electron.Energy(),0]
        		epArray.append(particleArray)

        		az_angle.append(File.GetLeaf("Electron.Phi").GetValue(j))
        		ra_angle.append(File.GetLeaf("Electron.Eta").GetValue(j))


        	EntryFromBranch = File.MissingET.GetEntries()
        	for j in range(EntryFromBranch):
        		particleArray = [0,0,0,1,File.GetLeaf("MissingET.MET").GetValue(j),
                                 File.GetLeaf("MissingET.MET").GetValue(j),0]	
        		epArray.append(particleArray)

        		az_angle.append(File.GetLeaf("MissingET.Phi").GetValue(j))
        		ra_angle.append(File.GetLeaf("MissingET.Eta").GetValue(j))


        	EntryFromBranch = File.Muon.GetEntries()
        	for j in range(EntryFromBranch):
            
        		Muon = TLorentzVector()
        		Muon.SetPtEtaPhiM(File.GetLeaf("Muon.PT").GetValue(j),
                                  File.GetLeaf("Muon.Eta").GetValue(j),
                                  File.GetLeaf("Muon.Phi").GetValue(j),
                                  0)

        		particleArray = [0,int(File.GetLeaf("Muon.Charge").GetValue(j)),0,0,
                                 File.GetLeaf("Muon.PT").GetValue(j),Muon.Energy(),0]
        		epArray.append(particleArray)

        		az_angle.append(File.GetLeaf("Muon.Phi").GetValue(j))
        		ra_angle.append(File.GetLeaf("Muon.Eta").GetValue(j))


        	# Getting the Angular Angle Distance
        	noPart = len(az_angle) # Number of particles in the event

        	if self.isRapid:
        		for i in range(noPart):
        			tempAng = []
        			for j in range(noPart):
        				tempAng.append(sqrt((az_angle[i] - az_angle[j])**2 + (ra_angle[i] - ra_angle[j])**2))
        			ezArray.append(tempAng)

        	else:
        		for i in range(noPart):
        			tempAng = []
        			for j in range(noPart):
        				tempAng.append(fabs(az_angle[i] - az_angle[j]))
        			ezArray.append(tempAng)

        	eventDict.append({"fourMomenta" : epArray,"azimuthalAngle" : ezArray,
                              "phiList" : az_angle,"etaList" : ra_angle})

        self.datasetDict = eventDict
        print("INFO : Done Filtering Particles")

    def createDataset(self,outputFile : str):
        '''
        Generate a HDF5 file from the datasetDict list. The first conversion is to split the 
        dictionary into 2 arrays, which are then converted to Awkward Arrays due to variable 
        sizes of the particles in an event. For the conversion from Awkward to HDF5, the 
        default method provided by Awkward is used.

        Parameters :
        ------------
        outputFile : str, required
            Filepath/Filename of the output file

        Returns :
        ---------
        Nothing
        '''

        if self.datasetDict == None:
            self.createArrays()
        
        print("INFO : Started Creating Database")

        xArray = []
        for i in range(self.totalEvents):
            xArray.append(self.datasetDict[i]["fourMomenta"])

        azArray = []
        for i in range(self.totalEvents):
            azArray.append(self.datasetDict[i]["azimuthalAngle"])

        eta = []
        for i in range(self.totalEvents):
            eta.append(self.datasetDict[i]["etaList"])

        phi = []
        for i in range(self.totalEvents):
            phi.append(self.datasetDict[i]["phiList"])

        hf = h5py.File(outputFile,'w')
        partArray = hf.create_group("ParticleArray")
        azimuthalArray = hf.create_group("AzimuthalAngle")
        etaArray = hf.create_group("EtaAngle")
        phiArray = hf.create_group("PhiAngle")

        # Convert Particle Array to HDF5 Group

        print("INFO : Adding n-tuple")
        ak_array = ak.from_iter(xArray)
        form, length, container = ak.to_buffers(ak_array,container=partArray)
        partArray.attrs["form"] = form.tojson()
        partArray.attrs["length"] = json.dumps(length)
        partArray.keys()

        # Convert Azimuthal Angle Array to HDF5 Group

        print("INFO : Adding weights")
        ak_array = ak.from_iter(azArray)
        form, length, container = ak.to_buffers(ak_array,container=azimuthalArray)
        azimuthalArray.attrs["form"] = form.tojson()
        azimuthalArray.attrs["length"] = json.dumps(length)
        azimuthalArray.keys()

        print("INFO : Adding eta angle")
        ak_array = ak.from_iter(eta)
        form, length, container = ak.to_buffers(ak_array,container=etaArray)
        etaArray.attrs["form"] = form.tojson()
        etaArray.attrs["length"] = json.dumps(length)
        etaArray.keys()

        print("INFO : Adding phi angle")
        ak_array = ak.from_iter(phi)
        form, length, container = ak.to_buffers(ak_array,container=phiArray)
        phiArray.attrs["form"] = form.tojson()
        phiArray.attrs["length"] = json.dumps(length)
        phiArray.keys()

        hf.close()

        print("INFO : Done Creating Database")
        print("INFO : Database stored at " + str(outputFile))

    def getArraysFromFile(self,inputFile : str):
        '''
        Accessor function that gives back lists from hdf5 file. Due to the various conversions from 
        List --> Awkward --> HDF5 file, this function is made as to make the conversion back to list 
        simple.

        Parameters :
        ------------
        inputFile : str, required
            The hdf5 file with the converted list

        Returns :
        ---------
        particleArray : list
            The list that contains the 4-momenta of every particle in every event.

        azArray : list
            The list that contains the azimuthal angle of every particle in every event.
        '''

        print("INFO : Started Getting Data From File")

        hf = h5py.File(inputFile,'r')
        partArray = hf.get("ParticleArray")
        azimuthalArray = hf.get("AzimuthalAngle")
        etaArray = hf.get("EtaAngle")
        phiArray = hf.get("PhiAngle")

        reconstitutedPartArray = ak.from_buffers(
        ak.forms.Form.fromjson(partArray.attrs["form"]),
        json.loads(partArray.attrs["length"]),
        {k: np.asarray(v) for k, v in partArray.items()},
    )

        reconstitutedAzAngle = ak.from_buffers(
            ak.forms.Form.fromjson(azimuthalArray.attrs["form"]),
            json.loads(azimuthalArray.attrs["length"]),
            {k: np.asarray(v) for k, v in azimuthalArray.items()},
        )

        reconstitutedEtaAngle = ak.from_buffers(
            ak.forms.Form.fromjson(etaArray.attrs["form"]),
            json.loads(etaArray.attrs["length"]),
            {k: np.asarray(v) for k, v in etaArray.items()},
        )

        reconstitutedPhiAngle = ak.from_buffers(
            ak.forms.Form.fromjson(phiArray.attrs["form"]),
            json.loads(phiArray.attrs["length"]),
            {k: np.asarray(v) for k, v in phiArray.items()},
        )

        particleArray = ak.to_list(reconstitutedPartArray)
        azArray = ak.to_list(reconstitutedAzAngle)
        etaArray = ak.to_list(reconstitutedEtaAngle)
        phiArray = ak.to_list(reconstitutedPhiAngle)

        print("INFO :  Done Getting Data from File")

        return particleArray,azArray,etaArray,phiArray

    def printPretty(self, record):
        '''
        Prints any 4-momenta record in a tabular manner.

        Parameters :
        ------------
        Nothing

        Returns :
        ---------
        Nothing
        '''
        print(" Photon | Lepton | Jet  | MET |  pt   |   E   |  mass ")
        print("------------------------------------------------------")
        for i in record:
            print("   "+ str(i[0]) + "    |" + "   " 
                  +str('%2d' % i[1]) + "   |" + "  "
                  +str('%2d'%i[2])+"  |" + "  "+ str(i[3]) 
                  + "  |" + str('%7.3f' % i[4]) + "|" 
                  + str('%7.3f' % i[5]) + "|" + str('%7.3f' % i[6]))

    def printPretty(self,arrayType : str,recordNo : int = 0):
        '''
        Print any record of the dataset in a tabular format

        Parameters :
        ------------
        arrayType : str, required
            Specify which data is to be printed. "fourMomenta" for 4-momenta 
            and "azimuthalAngle" for the azimuthal angle

        recordNo : int
            The event number for which the data is to be printed

        Returns :
        ---------
        Nothing
        '''

        if self.datasetDict is None:
            self.createArrays()

        if arrayType == 'fourMomenta':    
            print(" Photon | Lepton | Jet  | MET |  pt   |   E   |  mass ")
            print("------------------------------------------------------")
            for i in self.datasetDict[recordNo]["fourMomenta"]:
                print("   "+ str(i[0]) + "    |" + "   " +str('%2d' % i[1]) + "   |" 
                      + "  "+str('%2d'%i[2])+"  |" + "  "+ str(i[3]) + "  |" 
                      + str('%7.3f' % i[4]) + "|" + str('%7.3f' % i[5]) 
                      + "|" + str('%7.3f' % i[6]))

        else :
            partNo = len(self.datasetDict[recordNo]["azimuthalAngle"])
            print(" "*10 + "|",end="")
            for i in range(partNo):
                print('%5d'%i + "     |",end="")
            print()
            print("-----------"*(partNo+1))
            for i in range(partNo):
                print('%5d'%i + "     |",end="")
                for j in range(partNo):
                    print('%10.5f'%self.datasetDict[recordNo]["azimuthalAngle"][i][j] + "|",end="")
                print()
    
    def baselineCuts(self):
        '''
        Applying baseline cuts to the events. There cuts are meant to 
        increase the signal significance.

        Parameters :
        ------------
        Nothing

        Returns :
        ---------
        Nothing
        '''

        if self.datasetDict == []:
            self.createArrays()

        print("INFO : Applying Baseline Cuts")
        # The dictionary where events that survive the cuts are added
        tempDictList = []

        for i in self.datasetDict:
            
            ptJetsb = []        # List containing b-tagged Jets
            ptAllJets = []      # List of all the Jets

            totChargeLepton = 0 # Sum of the charge of the Leptons
            leptonIndex = []    # Index of all the Leptons

            flag = True         # Flag that True -> Survive the Cut,
                                # False -> Does not Survive the Cut

            for momenta in i["fourMomenta"]:
                
                # Getting a List of Jets to  
                # compute cuts on them
            
                # B-Tagged Jet
                if momenta[2] == 1:
                    ptJetsb.append(momenta[4])
                    ptAllJets.append(momenta[4])

                # Non B-Tagged Jet    
                elif momenta[2] == -1:
                    ptAllJets.append(momenta[4])

                # Getting a List of Leptons to  
                # compute cuts on them

                if momenta[1] != 0:
                    totChargeLepton += momenta[1]
                    leptonIndex.append(i["fourMomenta"].index(momenta))
                    
                    # PT of any Lepton has to be greater than 20 GeV
                    if momenta[4] <= 20:
                        flag = False
            
                # Modulus of ETmiss > 20
                if momenta[3] == 1:
                    if momenta[4] <= 20:
                        flag = False

            # Remove all the invalid records to save time by not computing when not required
            if not flag:
                continue
            
            # Record invalid is less than 2 b-tagged Jets
            if len(ptJetsb) < 2:
                continue

            # Record invalid if the two leading momenta are not of b-tagged Jets
            ptAllJets.sort(reverse=True)
            if ptAllJets[0] not in ptJetsb or ptAllJets[1] not in ptJetsb or ptAllJets[1] < 30:
                continue

            # Getting the Index of Leading Jets
            jetIndex = []
            for momenta in i["fourMomenta"]:
                for j in range(2):
                    if momenta[2] == 1 and momenta[4] == ptAllJets[j]:
                        jetIndex.append(i["fourMomenta"].index(momenta))

            # Delta R_{bb} < 1.3 Cut
            if i['azimuthalAngle'][jetIndex[0]][jetIndex[1]] >= 1.3:
                flag = False

            # Mass Invariant Cut (95 GeV < M_{bb} < 140 GeV)
            Jet1 = TLorentzVector()
            Jet2 = TLorentzVector()

            Jet1.SetPtEtaPhiM(i['fourMomenta'][jetIndex[0]][4],
                              i['etaList'][jetIndex[0]],
                              i['phiList'][jetIndex[0]],
                              i['fourMomenta'][jetIndex[0]][-1])

            Jet2.SetPtEtaPhiM(i['fourMomenta'][jetIndex[1]][4],
                              i['etaList'][jetIndex[1]],
                              i['phiList'][jetIndex[1]],
                              i['fourMomenta'][jetIndex[1]][-1])

            if (Jet1 + Jet2).M() >= 140 or (Jet1 + Jet2).M() <= 95:
                flag = False

            # Cuts for Number of Leptons being two
            # And both having opposite charge
            if len(leptonIndex) != 2 or totChargeLepton != 0:
                continue

            # Delta R_{ll} < 1.0 is the cut applied
            if i['azimuthalAngle'][leptonIndex[0]][leptonIndex[1]] >= 1.0:
                flag = False  
            
            # The Mass Invariance Cut (M_{ll} < 65 GeV)
            Lepton1 = TLorentzVector()
            Lepton2 = TLorentzVector()

            Lepton1.SetPtEtaPhiM(i['fourMomenta'][leptonIndex[0]][4],
                                 i['etaList'][leptonIndex[0]],
                                 i['phiList'][leptonIndex[0]],
                                 i['fourMomenta'][leptonIndex[0]][-1])
                                 
            Lepton2.SetPtEtaPhiM(i['fourMomenta'][leptonIndex[1]][4],
                                 i['etaList'][leptonIndex[1]],
                                 i['phiList'][leptonIndex[1]],
                                 i['fourMomenta'][leptonIndex[1]][-1])
            
            if (Lepton1 + Lepton2).M() >= 65:
                flag = False
            
            if not flag:
                continue

            tempDictList.append(i)

        self.datasetDict = tempDictList
        self.totalEvents = len(tempDictList)
        print("INFO : Done Applying Baseline Cuts")

    def getEta(self):
        eta = []
        for i in range(self.totalEvents):
            eta.append(self.datasetDict[i]["etaList"])
        
        return eta

    def getPhi(self):
        phi = []
        for i in range(self.totalEvents):
            phi.append(self.datasetDict[i]["phiList"])

        return phi

    def getTuple(self):
        array = []
        for i in range(self.totalEvents):
            array.append(self.datasetDict[i]["fourMomenta"])

        return array


if __name__ == "__main__":
    process  = ['ttV']
    for i in process:
        print("INFO : The process running is : " + i)
        s1 = GenDataset("/home/blizzard/Tests/bbWW/"+ i + "_10k/Events/run_01/tag_1_delphes_events.root")
        s1.createDataset('../../datasets/partonCuts/'+i+'_10k.h5')
        print("INFO : The amount of events generated are : " + str(len(s1.datasetDict)))
        s1.baselineCuts()
        s1.createDataset('../../datasets/baselineCuts/'+i+'_10k.h5')
        print("INFO : The amount of events that survived are " + str(len(s1.datasetDict)))