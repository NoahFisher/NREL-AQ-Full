import Options

class Chemical(Options.ScenarioOptions):
    def __init__(self, modelRunTitle):
        Options.ScenarioOptions.__init__(self, modelRunTitle)
         
    
    
    def setChemical(self, feed):
        
        if feed == 'CG' or feed == 'SG': 
            if feed == 'CG':
                query = self.__cornGrain__()
                
            elif feed == 'SG':
                query = self.__switchgrass__()
                
            self.__executeQuery__(query)
            
        
        
    def __cornGrain__(self):

        chemQuery = """
INSERT INTO cg_chem
    (

    SELECT cg.fips, (2461850051) AS "SCC", 

    ((cg.total_harv_ac * pest.EF * 0.9 * 0.835) * 0.907018474 / 2000.0) AS "VOC", 

    ('Pesticide Emissions') AS "Description"

    FROM """+self.productionSchema+""".cg_data cg, """ + self.constantsSchema + """.CG_pest_app_factor pest

    WHERE substr(fips, 1, 2) = pest.STFIPS
    )"""
        return chemQuery
    

                                         
    def __switchgrass__(self):
        
        chemQuery = """
INSERT INTO sg_chem 
    (
        SELECT sg.fips, (2461850099) AS "SCC",  
        (
            (
            sg.harv_ac * 0.1 * (0.5) + 
            sg.harv_ac * 0.1 * (1.0) + 
            sg.harv_ac * 0.1 * (1.0) + 
            sg.harv_ac * 0.1 * (1.5)
            ) * 0.9 * 0.835
        ) * 0.90718474 / 2000.0 AS "VOC", 
     
        ('Establishment Year: quinclorac + Atrazine + 2-4-D-Amine') AS "Description"

        FROM """+self.productionSchema+""".sg_data sg
    )"""
        return chemQuery
          
        
