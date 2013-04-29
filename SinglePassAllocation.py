import Options


class SinglePassAllocation(Options.ScenarioOptions):
    def __init__(self, modelRunTitle):
        Options.ScenarioOptions.__init__(self, modelRunTitle)
        
        self.residueAllocation = str(380.0 / 540.0)
        self.cornGrainAllocation = str(160.0 / 540.0)
        
        self.allocateCG = False
        
        residues = ['cs','ws']
        
        for r in residues: 
            #define corn stover query - 380/540
            query = """
                UPDATE """+r+"""_raw
                SET
                    fuel_consumption = fuel_consumption * """+self.residueAllocation+""",
                    thc = thc * """+self.residueAllocation+""",
                    voc = voc * """+self.residueAllocation+""",
                    co = co * """+self.residueAllocation+""",
                    nox = nox * """+self.residueAllocation+""",
                    co2 = co2 * """+self.residueAllocation+""",
                    sox = sox * """+self.residueAllocation+""",
                    pm10 = pm10 * """+self.residueAllocation+""",
                    pm25 = pm25 * """+self.residueAllocation+""",
                    nh3 = nh3 * """+self.residueAllocation+""",
                    fug_pm10 = fug_pm10 * """+self.residueAllocation+""",
                    fug_pm25 = fug_pm10 * """+self.residueAllocation+"""
                WHERE description ilike '%Harvest%';
            """             
            self.__executeQuery__(query)
            
       
        if self.allocateCG:
            #define corn grain query
            query = """
                UPDATE """+r+"""_raw
                SET
                    fuel_consumption = fuel_consumption * """+self.cornGrainAllocation+""",
                    thc = thc * """+self.cornGrainAllocation+""",
                    voc = voc * """+self.cornGrainAllocation+""",
                    co = co * """+self.cornGrainAllocation+""",
                    nox = nox * """+self.cornGrainAllocation+""",
                    co2 = co2 * """+self.cornGrainAllocation+""",
                    sox = sox * """+self.cornGrainAllocation+""",
                    pm10 = pm10 * """+self.cornGrainAllocation+""",
                    pm25 = pm25 * """+self.cornGrainAllocation+""",
                    nh3 = nh3 * """+self.cornGrainAllocation+""",
                    fug_pm10 = fug_pm10 * """+self.cornGrainAllocation+""",
                    fug_pm25 = fug_pm10 * """+self.cornGrainAllocation+"""
                WHERE 
                    description NOT ilike '%Conventional%' AND
                    description ilike '% Harvest%';
            """            
            self.__executeQuery__(query)
        
        
        
        
        
    
