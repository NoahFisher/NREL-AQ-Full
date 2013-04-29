import Options

"""
Create the fugitive dust emisisons based on the run code
The run code tells you the feedstock, tillage, and operation
(harvest/non-harvest/irrigation). 
"""
class FugitiveDust(Options.ScenarioOptions):
    def __init__(self, modelRunTitle):
        Options.ScenarioOptions.__init__(self, modelRunTitle)
        self.pmRatio = 0.20
    
    """
    loop through run_codes and call this method to create fugitive
    dust emissions in database
    """                
    def setEmissions(self, run_code):
# Forest Residue fugitive dust emissions            
        if run_code.startswith('FR'):
            query = self.__forestRes__()
           
# Corn Grain fugitivie dust emissions            
        elif run_code.startswith('CG'):
            query = self.__cornGrain__(run_code)
            
# Wheat straw fugitive dust emissions            
        elif run_code.startswith('WS'):
            query = self.__wheatSraw__(run_code)
        
# Corn stover fugitive dust emissions            
        elif run_code.startswith('CS'):
            query = self.__cornStover__(run_code)
        
# switchgrass fugitive dust emissions            
        elif run_code.startswith('SG'):
            pass
#            query = self.__switchgrass__(run_code)
 
        self.__executeQuery__(query)
        
 
 
    def __forestRes__(self):
        pmFR = ( 0.0 ) * 0.907 / 2000  # 0 lbs per acre
        # currently there are no pm emissions from FR operations
        query = """
            UPDATE fr_RAW fr
                SET 
                    fug_pm10 = (%s * dat.fed_minus_55),
                    fug_pm25 = (%s * dat.fed_minus_55 * %s)
                FROM %s.fr_data dat
                WHERE (dat.fips = fr.fips)
            """ % (pmFR, pmFR, self.pmRatio, self.productionSchema)
        return query
       
    
    
    # build query based on the information contained by the run_code
    def __cornGrain__(self, run_code):
# --emission factors: 
        pmTransport = (1.2 * 0.907) / 2000
        
        pmConvTillHarv = (1.7 * 0.907) / 2000
        pmReduTillHarv = (1.7 * 0.907) / 2000
        pmNoTillHarv = (1.7 * 0.907) / 2000
        
        pmConvTillNonHarv = (8.0 * 0.907) / 2000
        pmReduTillNonHarv = (7.2 * 0.907) / 2000
        pmNoTillNonHarv = (5.2 * 0.907) / 2000
        
        #irrigation emissions do not currently have PM emissions
        pmDieIrrigation = (0.0 * 0.907) / 2000
        pmGasIrrigation = (0.0 * 0.907) / 2000
        pmLPGIrrigation = (0.0 * 0.907) / 2000
        pmCNGIrrigation = (0.0 * 0.907) / 2000
        
        modelTransport = False
# --                
# choose operation for conventional till
        if run_code.startswith('CG_C'):
            tillage = 'Conventional'
            tableTill = 'convtill'
            
            if run_code.endswith('N'):
                operation = 'Non-Harvest'
                EF = pmConvTillNonHarv
                
            elif run_code.endswith('H'):
                operation = 'Harvest'
                EF = pmConvTillHarv
                modelTransport = True
                
# choose operation for reduced till
        elif run_code.startswith('CG_R'):
            tillage = 'Reduced'
            tableTill = 'reducedtill'
            
            if run_code.endswith('N'):
                operation = 'Non-Harvest'
                EF = pmReduTillNonHarv
                
            elif run_code.endswith('H'):
                operation = 'Harvest'
                EF = pmReduTillHarv
                modelTransport = True                        
                
# choose operation for no till                
        elif run_code.startswith('CG_N'):
            tillage = 'No Till'
            tableTill = 'notill'
            
            if run_code.endswith('N'):
                operation = 'Non-Harvest'
                EF = pmNoTillNonHarv
                
            elif run_code.endswith('H'):
                operation = 'Harvest'
                EF = pmNoTillHarv
                modelTransport = True                                                
              
# choose operation for irrigation
        elif run_code.startswith('CG_I'):
            tillage = 'Irrigation'
            tableTill = 'total'
            
            if run_code.endswith('D'):
                operation = 'Diesel'
                EF = pmDieIrrigation
                
            elif run_code.endswith('G'):
                operation = 'Gasoline'
                EF = pmGasIrrigation
                
            elif run_code.endswith('L'):
                operation = 'LPG'
                EF = pmLPGIrrigation
                                        
            elif run_code.endswith('C'):
                operation = 'CNG'
                EF = pmCNGIrrigation
 
# execute query for transport operations
        if modelTransport: 
            query = """
                    UPDATE cg_raw cr
                    SET 
                        fug_pm10 = (%s * cd.%s_harv_AC),
                        fug_pm25 = (%s * cd.%s_harv_AC) * %s
                    FROM %s.cg_data cd
                    WHERE     (cd.fips = cr.fips) AND 
                              (cr.description ILIKE '%s') AND 
                              (cr.description ILIKE '%s');                     
                """ % (pmTransport, tableTill,
                       EF, tableTill, self.pmRatio,
                       self.productionSchema,
                       str("%transport%"),
                       str("%" + tillage + "%")
                       ) 
            self.__executeQuery__(query)
            
# return query for non-transport operations
        query = """
                UPDATE cg_raw cr
                SET 
                    fug_pm10 = (%s * cd.%s_harv_AC),
                    fug_pm25 = (%s * cd.%s_harv_AC) * %s
                FROM %s.cg_data cd
                WHERE     (cd.fips = cr.fips) AND 
                          (cr.description ILIKE '%s') AND 
                          (cr.description ILIKE '%s');                     
            """ % (EF, tableTill,
                   EF, tableTill, self.pmRatio,
                   self.productionSchema,
                   str("%" + operation + "%"),
                   str("%" + tillage + "%")
                   )
        return query
    
    
    
    def __cornStover__(self, run_code):
# --emission factors: 
        pmTransport = (1.2 * 0.907) / 2000
        
        pmReduTillHarv = (1.7 * 0.907) / 2000
        pmNoTillHarv = (1.7 * 0.907) / 2000
# --     

# choose operation for reduced till
        if run_code.startswith('CS_R'):
            tillage = 'Reduced'
            tableTill = 'reducedtill'
            operation = 'Harvest'
            EF = pmReduTillHarv
            
# choose operation for no till                
        elif run_code.startswith('CS_N'):
            tillage = 'No Till'
            tableTill = 'notill'
            operation = 'Harvest'
            EF = pmNoTillHarv
        
# execute query for transport emissions
        transportQuery = """
                UPDATE cs_raw cr
                SET 
                    fug_pm10 = (%s * cd.%s_harv_AC),
                    fug_pm25 = (%s * cd.%s_harv_AC) * %s
                FROM %s.cs_data cd
                WHERE     (cd.fips = cr.fips) AND 
                          (cr.description ILIKE '%s') AND 
                          (cr.description ILIKE '%s');                     
            """ % (pmTransport, tableTill,
                   EF, tableTill, self.pmRatio,
                   self.productionSchema,
                   str("%transport%"),
                   str("%" + tillage + "%")
                   ) 
        self.__executeQuery__(transportQuery)

# return non-transport emissions query        
        query = """
                UPDATE cs_raw cr
                SET 
                    fug_pm10 = (%s * cd.%s_harv_AC),
                    fug_pm25 = (%s * cd.%s_harv_AC) * %s
                FROM %s.cs_data cd
                WHERE     (cd.fips = cr.fips) AND 
                          (cr.description ILIKE '%s') AND 
                          (cr.description ILIKE '%s');                     
            """ % (EF, tableTill,
                   EF, tableTill, self.pmRatio,
                   self.productionSchema,
                   str("%" + operation + "%"),
                   str("%" + tillage + "%")
                   )
        return query        
    
    
    
# CS and WS have very similar fugitive dust emission factors
    def __wheatSraw__(self, run_code):
# --emission factors: 
        pmTransport = (1.2 * 0.907) / 2000
        
        pmReduTillHarv = (5.8 * 0.907) / 2000
        pmNoTillHarv = (5.8 * 0.907) / 2000
# --     

# choose operation for reduced till
        if run_code.startswith('WS_R'):
            tillage = 'Reduced'
            tableTill = 'reducedtill'
            operation = 'Harvest'
            EF = pmReduTillHarv
            
# choose operation for no till                
        elif run_code.startswith('WS_N'):
            tillage = 'No Till'
            tableTill = 'notill'
            operation = 'Harvest'
            EF = pmNoTillHarv
        
# execute query for transport emissions
        transportQuery = """
                UPDATE ws_raw wr
                SET 
                    fug_pm10 = (%s * cd.%s_harv_AC),
                    fug_pm25 = (%s * cd.%s_harv_AC) * %s
                FROM %s.ws_data cd
                WHERE     (cd.fips = wr.fips) AND 
                          (wr.description ILIKE '%s') AND 
                          (wr.description ILIKE '%s');                     
            """ % (pmTransport, tableTill,
                   EF, tableTill, self.pmRatio,
                   self.productionSchema,
                   str("%transport%"),
                   str("%" + tillage + "%")
                   ) 
        self.__executeQuery__(transportQuery)

# return non-transport emissions query        
        query = """
                UPDATE ws_raw wr
                SET 
                    fug_pm10 = (%s * cd.%s_harv_AC),
                    fug_pm25 = (%s * cd.%s_harv_AC) * %s
                FROM %s.ws_data cd
                WHERE     (cd.fips = wr.fips) AND 
                          (wr.description ILIKE '%s') AND 
                          (wr.description ILIKE '%s');                     
            """ % (EF, tableTill,
                   EF, tableTill, self.pmRatio,
                   self.productionSchema,
                   str("%" + operation + "%"),
                   str("%" + tillage + "%")
                   )
        return query  
    
    
    
    def __switchgrass__(self, run_code):
        pass
    



#Data structure to hold SG emission factors
#   --structure is kept in the 'long-hand' format so users may easily change
#        EF's in the future
class SG_FugitiveDust(Options.ScenarioOptions):
    def __init__(self, modelRunTitle, operation):
        Options.ScenarioOptions.__init__(self, modelRunTitle)
        self.pmRatio = 0.20
        
        
        if operation == 'Transport':
            emissionFactors = [
                                    1.2, #year 1 transport emission factor
                                    1.2, #year 2
                                    1.2, #year 3
                                    1.2, #year 4
                                    1.2, #year 5
                                    1.2, #year 6
                                    1.2, #year 7
                                    1.2, #year 8
                                    1.2, #year 9
                                    1.2 #year 10
                                    ]
            self.description = 'SG_T'
            
        
        elif operation == 'Harvest':
            emissionFactors = [
                                    4.8, #year 1 harvest emission factor
                                    4.8, #year 2
                                    4.8, #year 3
                                    4.8, #year 4
                                    4.8, #year 5
                                    4.8, #year 6
                                    4.8, #year 7
                                    4.8, #year 8
                                    4.8, #year 9
                                    4.8 #year 10
                                    ]
            self.description = 'SG_H'
            
        elif operation == 'Non-Harvest':
            emissionFactors = [
                                    6.0, #year 1 non-harvest emission factor
                                    2.0, #year 2
                                    0.8, #year 3
                                    0.8, #year 4
                                    2.8, #year 5
                                    0.8, #year 6
                                    0.8, #year 7
                                    0.8, #year 8
                                    0.8, #year 9
                                    0.8 #year 10
                                    ]
            self.description = 'SG_N'
        
        self.emissionFactors = (x * 0.907 / 2000.0 for x in emissionFactors) #convert from lbs to metric tons.             
                        
                            
    def setEmissions(self):
        for year, EF in enumerate(self.emissionFactors):
            
    # return non-transport emissions query        
            query = """
                    UPDATE sg_raw raw
                    SET 
                        fug_pm10 = (%s * dat.harv_AC),
                        fug_pm25 = (%s * dat.harv_AC) * %s
                    FROM %s.sg_data dat
                    WHERE     (dat.fips = raw.fips) AND 
                              (raw.run_code ILIKE '%s');                     
                """ % (EF, 
                       EF, self.pmRatio,
                       self.productionSchema,
                       str("%" + self.description + str(year+1) + "%")
                       )
            
            self.__executeQuery__(query)
            

        
