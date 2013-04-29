import Options

class NEIComparison(Options.ScenarioOptions):
    def __init__(self, modelRunTitle):
        Options.ScenarioOptions.__init__(self, modelRunTitle)
        
        self.cellulosicAllocation = 0.34
        self.cornGrainAllocation = 0.54
        
        
        query = """
CREATE TABLE summedEmissions
(
fips    char(5)    ,
feedstock    text    ,
prod    float    ,
harv_Ac    float    ,
NOX    float    DEFAULT 0.0,
NH3    float    DEFAULT 0.0,
SOX    float    DEFAULT 0.0,
VOC    float    DEFAULT 0.0,
PM10    float    DEFAULT 0.0,
PM25    float    DEFAULT 0.0,
CO    float    DEFAULT 0.0);"""

        self.__executeQuery__(query)



    def __setNEIRatioTable__(self, feedstock):
        query = """
CREATE TABLE """+feedstock+"""_NEIRatio
(
fips    char(5) ,
nox    float    ,
sox    float    ,
co    float    ,
pm10    float    ,
pm25    float    ,
voc    float    ,
nh3    float);"""
        self.__executeQuery__(query)
        
        
            
    def createSummedEmissionsTable(self, feedstock):
        
        if feedstock == 'CG':
            f = "Corn Grain"
            prod = "dat.total_prod, dat.total_harv_ac"
        elif feedstock == 'SG':
            f = "Switchgrass"
            prod = "dat.prod, dat.harv_ac"
        elif feedstock == 'WS':
            f = "Wheat Straw"
            prod = "dat.prod, dat.harv_ac"
        elif feedstock == 'CS':
            f = "Corn Stover"
            prod = "dat.prod, dat.harv_ac"
        elif feedstock == 'FR':
            f = "Forest Residue"
            prod = "dat.fed_minus_55, 0"
        
    
        query = """
    INSERT INTO summedEmissions 
    WITH
    """
    
        #populate tables that have fertilizer emissions
    #    if feedstock == 'CG' or feedstock == 'SG':
        if feedstock != 'FR':    
            query += """
    Fert as (SELECT DISTINCT fips,
                    sum(nox) as nox,
                    sum(nh3) as nh3
        FROM %s_nfert
        GROUP BY fips),
    ---------------------------------------------------------------------------------------------
    """ % (feedstock)
    
        if feedstock == 'CG' or feedstock == 'SG':
            query += """
    Chem as (SELECT DISTINCT fips,
                    sum(voc) as voc
        FROM %s_chem
        GROUP BY fips),
    ---------------------------------------------------------------------------------------------
    """ % (feedstock)
    
        query +="""
    Raw as (SELECT  DISTINCT fips,
                    sum(nox) AS nox,
                    sum(nh3) AS nh3,
                    sum(sox) AS sox,
                    sum(voc) AS voc,
                    (sum(pm10) + sum(fug_pm10)) AS pm10, 
                    (sum(pm25) + sum(fug_pm25)) AS pm25,
                    (sum(co)) AS co
        FROM %s_raw
        GROUP BY fips)
    ---------------------------------------------------------------------------------------------
    """ % (feedstock)
    
    
        if feedstock == 'CG' or feedstock == 'SG': 
            query +="""
    (SELECT dat.fips, %s, %s,
        (raw.nox + fert.nox) as nox, 
        (raw.nh3 + fert.nh3) as nh3,
        (raw.sox) as sox,
        (raw.voc + chem.voc) as voc,
        (raw.pm10) as pm10,
        (raw.pm25) as pm25,
        (raw.co) as co    
        
    FROM %s dat
    
    LEFT JOIN Fert ON fert.fips = dat.fips
    LEFT JOIN Chem ON chem.fips = dat.fips
    LEFT JOIN Raw ON raw.fips = dat.fips
    )
    ;""" % ("'"+f+"'", prod, 
            self.productionSchema +'.'+ feedstock + "_data")


        elif feedstock == 'CS' or feedstock == 'WS':
            query +="""
    (SELECT dat.fips, %s, %s,
        (raw.nox + fert.nox) as nox, 
        (raw.nh3 + fert.nh3) as nh3,
        (raw.sox) as sox,
        (raw.voc) as voc,
        (raw.pm10) as pm10,
        (raw.pm25) as pm25,
        (raw.co) as co    
        
    FROM %s dat
    
    LEFT JOIN Fert ON fert.fips = dat.fips
    LEFT JOIN Raw ON raw.fips = dat.fips
    )
    ;""" % ("'"+f+"'", prod, 
            self.productionSchema +'.'+ feedstock + "_data")    
    
    
        elif feedstock == 'FR':
            query +="""
    (SELECT dat.fips, %s, %s,
        (raw.nox) as nox, 
        (raw.nh3) as nh3,
        (raw.sox) as sox,
        (raw.voc) as voc,
        (raw.pm10) as pm10,
        (raw.pm25) as pm25,
        (raw.co) as co    
        
    FROM %s dat
    
    LEFT JOIN Raw ON raw.fips = dat.fips
    )
    ;""" % ("'"+f+"'", prod, 
            self.productionSchema +'.'+ feedstock + "_data")            


        self.__executeQuery__(query)
    
 
    
    def createNEIComparison(self, feedstock):
        if feedstock == 'CG':
            allocation = str(self.cornGrainAllocation)
        else: 
            allocation = str(self.cellulosicAllocation)
        
            
        self.__setNEIRatioTable__(feedstock)
        
        
        if feedstock == 'CG':
            f = 'Corn Grain'
        elif feedstock == 'SG':
            f = 'Switchgrass'
        elif feedstock == 'CS':
            f = 'Corn Stover'
        elif feedstock == 'WS':
            f = 'Wheat Straw'
        elif feedstock == 'FR':
            f = 'Forest Residue' 
        
        
        
        query = """
INSERT INTO """+feedstock+"""_NEIRatio
WITH
   nrel AS (select distinct fips,  sum(nox) as nox,
                   sum(sox) as sox,
                   sum(co) as co,
                   sum(pm10) as pm10,
                   sum(pm25) as pm25,
                   sum(voc) as voc,
                   sum(nh3) as nh3 from summedEmissions where feedstock ilike '%"""+f+"""%' GROUP BY fips),
   nei as (select fips, nox, sox, co, pm10, pm25, voc, nh3 from """+self.constantsSchema+""".nei_data_by_county)

   select c.fips,
            (nrel.nox * """+allocation+""") / nei.nox as nox, 
            (nrel.sox * """+allocation+""") / nei.sox as sox,
            (nrel.co * """+allocation+""") / nei.co as co,
            (nrel.pm10 * """+allocation+""") / nei.pm10 as PM10,
            (nrel.pm25 * """+allocation+""") / nei.pm25 as PM25,
            (nrel.voc * """+allocation+""") / nei.voc as VOC,
            (nrel.nh3 * """+allocation+""") / nei.nh3 as NH3

    from """+ self.productionSchema +""".cg_data c

    LEFT JOIN nrel ON c.fips = nrel.fips

    LEFT JOIN nei ON c.fips = nei.fips

"""
        
        
        
        
        
        self.__executeQuery__(query)
        
        




