import Options

"""
Input run_codes in study and create appropriate tables
"""
class UpdateDatabase(Options.ScenarioOptions): 
    def __init__(self, modelRunTitle):
        Options.ScenarioOptions.__init__(self, modelRunTitle)
         
        cur = self.conn.cursor()
        # create schema, drop schema if it already existed        
        cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % (modelRunTitle))
        cur.execute("CREATE SCHEMA %s" % (modelRunTitle))
        self.conn.commit()    
        
        

    def createTables(self, feedstock):
# create tables (based on feedstock)
# TODO: Insert Primary Keys  
        query = """
                        CREATE TABLE %s_raw
                        (
                        FIPS    char(5)    ,
                        SCC    char(10)    ,
                        HP    int    ,
                        fuel_consumption float    ,
                        THC    float    ,
                        VOC    float    ,
                        CO    float    ,
                        NOx    float    ,
                        CO2    float    ,
                        SOx    float    ,
                        PM10    float    ,
                        PM25    float    ,
                        NH3    float    ,
                        Description    text    ,
                        run_code    text    ,
                        fug_pm10    float    , 
                        fug_pm25    float)""" % (feedstock)
        self.__executeQuery__(query)


        
        if feedstock != 'FR':
            query = """
                            CREATE TABLE %s_NFert
                            (
                            FIPS    char(5)    ,
                            NOx    float    ,
                            NH3    float    ,
                            SCC    char(10)    ,
                            description    text)""" % (feedstock)
            self.__executeQuery__(query)
            
            
        
        if feedstock == 'SG' or feedstock == 'CG':
            query = """
                           CREATE TABLE %s_CHEM
                           (
                           FIPS    char(5),
                           SCC    char(10)    ,
                           VOC    float    ,
                           description    text)""" % (feedstock)
            self.__executeQuery__(query)
