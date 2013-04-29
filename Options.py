import os
import psycopg2 as db


class ScenarioOptions:
    """
    The 'ScenarioOptions' object is used to query production (harvested acres and production) from a database. 
    It also contains other useful information such as a scenario title, path to write outputs, and the year
     of interest for the data inputs. 
    """
    def __init__(self, modelRunTitle):
        #credentials for connecting to the database -- superuser
        self.conn = db.connect("dbname=biofuel user=**** password=****")
        # schema name for production data
        self.productionSchema = 'BTS2dat_55'
        # schema name for stored constants (n application rates, n distribution, etc...)
        self.constantsSchema = 'constantvals'        
        # schema name for the scenario
        self.schema = modelRunTitle
        
        self.modelRunTitle = modelRunTitle
        
        self.path = 'C:/Nonroad/%s/' % (self.modelRunTitle)  # non-dev directory
        
    

    def __executeQuery__(self, query):   
        print query     
        cur = self.conn.cursor()
        cur.execute("SET search_path to %s" % (self.schema))
        cur.execute(query)
        cur.close()
        self.conn.commit()
        
        
             
    def initialize(self, modelRunTitle, run_codes):
# TODO: place username and password credentials here.
#        self.conn = db.connect("dbname=biofuel user=nfisher password=nfisher")
        
        self.run_codes = run_codes
        
        # schema title for future emissions inventory
        self.modelRunTitle = modelRunTitle 
        self.schema = modelRunTitle
        
        
        if os.path.exists(self.path):
            # path already exists
            pass
        else:
            # path does not exist
            os.makedirs(self.path)
                   
            os.makedirs(self.path + "ALLOCATE/")
            os.makedirs(self.path + "POP/")
            os.makedirs(self.path + "OPT/")
            os.makedirs(self.path + "OUT/")
            os.makedirs(self.path + "FIGURES/")
      
        # break flag used to ensure switchgrass database query only happens once. (all other feedstocks need multiple pulls from the database).
        self.querySG = True
                
        # create scenario level batch file
        self.scenarioBatchFile = open(self.path + 'OPT/' + self.modelRunTitle + '.bat', 'w')




        
    # Create Batch File for each run_code                
    def initializeBatch(self):
        self.scenarioBatchFile.write('\n')
        self.batchFile = open(self.path + 'OPT/' + self.run_code + '.bat', 'w')
        self.batchFile.write("cd C:\\NonRoad\n")

        self.batchPath = self.path + 'OPT/'    
        self.batchPath = self.batchPath.replace('/', '\\')



    
    
    # add states to the batch file
    def appendBatch(self, state):
        lines = "NONROAD.exe " + self.batchPath + self.run_code + '\\' + state + ".opt\n"
        self.batchFile.writelines(lines)





    # finish the batch file and add the finished batch file to the full 'Scenario' batch file 
    def finishBatch(self):
        self.batchFile.close()        
        self.scenarioBatchFile.write("CALL " + "\"" + self.batchPath + self.run_code + '.bat\"\n')
        
        
        
        
        
        
    def getData(self, run_code):
        self.run_code = run_code
        
        # model all years as 2022 except corn grain = 2011
        if run_code.startswith('CG'): self.episodeYear = '2011'
        else: self.episodeYear = '2022' 
                     
        self.__getQuery__()
        self.__getProdData__()
       

        # create output directories
        if os.path.exists(self.path + '/OUT/' + run_code):
            # path already exists, existing data will be replaced. 
            pass
    
        else:
            # path does not exist
            os.makedirs(self.path + '/OPT/' + run_code)
            os.makedirs(self.path + '/OUT/' + run_code)
                   
                  
                  
                   
    def __getProdData__(self):      
            
        cur = self.conn.cursor()
        
        cur.execute("SET search_path TO %s" % (self.productionSchema))           
        # extract data
        cur.execute(self.query)
    
        self.data = list(cur.fetchall())
        
        cur.close()
        
        
        
        # the number of extracted data must be 3109 with no null (blank) returned results.  
#        print len(self.data)

 
 
 
    # query database for appropriate production data based on run_code            
    def __getQuery__(self):
        if self.run_code.startswith('CG'):
            
            if self.run_code.startswith('CG_C'):
                self.query = """select ca.fips, ca.st, dat.convtill_harv_ac, dat.convtill_prod, dat.convtill_yield
                from cg_data dat, """ + self.constantsSchema + """.county_attributes ca where dat.fips = ca.fips order by ca.fips asc"""
            
            elif self.run_code.startswith('CG_R'):
                self.query = """select ca.fips, ca.st, dat.reducedtill_harv_ac, dat.reducedtill_prod, dat.reducedtill_yield
                from cg_data dat, """ + self.constantsSchema + """.county_attributes ca where dat.fips = ca.fips order by ca.fips asc"""
            
            elif self.run_code.startswith('CG_N'):
                self.query = """select ca.fips, ca.st, dat.notill_harv_ac, dat.notill_prod, dat.notill_yield 
                from cg_data dat, """ + self.constantsSchema + """.county_attributes ca where dat.fips = ca.fips order by ca.fips asc"""
                
            elif self.run_code.startswith('CG_I'):
                
                if self.run_code.endswith('D'): fuel_type = 'A'
                elif self.run_code.endswith('G'): fuel_type = 'B'
                elif self.run_code.endswith('L'): fuel_type = 'C'
                elif self.run_code.endswith('C'): fuel_type = 'D'
                self.query = """
                Set search_path to %s; 
                WITH
                    IRR AS (
                    SELECT 
                        A.state,
                        %s.fuel as fuel, %s.hp as hp, %s.percent as perc, %s.hrsperacre as hpa
                    FROM
                        cg_irrigated_states A JOIN
                        cg_irrigated_states B ON (A.state = B.state) JOIN
                        cg_irrigated_states C ON (B.state = C.state) JOIN
                        cg_irrigated_states D ON (C.state = D.state)
                    WHERE
                        A.fuel ilike 'Diesel' AND
                        B.fuel ilike 'Gasoline' AND
                        C.fuel ilike 'LPG' AND
                        D.fuel ilike 'natgas'
                    )
                    
                select ca.fips, ca.st, dat.total_harv_ac * irr.perc, dat.total_prod, 
                        irr.fuel, irr.hp, irr.perc, irr.hpa
                        
                            from county_attributes ca
                            left join %s.cg_data dat on ca.fips = dat.fips
                            left join irr on irr.state ilike ca.st
                            
                            where ca.st ilike irr.state
                            order by ca.fips asc
                    """ % (self.constantsSchema, fuel_type, fuel_type, fuel_type, fuel_type, self.productionSchema)
    
    
               
                  
        elif self.run_code.startswith('CS'):
            
            if self.run_code == 'CS_RT':
                self.query = """select ca.fips, ca.st, dat.reducedtill_harv_ac, dat.reducedtill_prod, dat.reducedtill_yield
                from cs_data dat, """ + self.constantsSchema + """.county_attributes ca where dat.fips = ca.fips order by ca.fips asc"""
            
            elif self.run_code == 'CS_NT':
                self.query = """select ca.fips, ca.st, dat.notill_harv_ac, dat.notill_prod, dat.notill_yield 
                from cs_data dat, """ + self.constantsSchema + """.county_attributes ca where dat.fips = ca.fips  order by ca.fips asc"""
                
          
          
                         
        elif self.run_code.startswith('WS'):
            self.queryTable = 'ws_data'

            if self.run_code == 'WS_RT':
                self.query = """select ca.fips, ca.st, dat.reducedtill_harv_ac, dat.reducedtill_prod, dat.reducedtill_yield
                from ws_data dat, """ + self.constantsSchema + """.county_attributes ca where dat.fips = ca.fips order by ca.fips asc"""
            
            elif self.run_code == 'WS_NT':
                self.query = """select ca.fips, ca.st, dat.notill_harv_ac, dat.notill_prod, dat.notill_yield 
                from ws_data dat, """ + self.constantsSchema + """.county_attributes ca where dat.fips = ca.fips  order by ca.fips asc"""
        
        
                
                 
        elif self.run_code.startswith('SG'):
            
            if self.querySG:
                self.query = """select ca.fips, ca.st, dat.harv_ac, dat.prod
                from sg_data dat, """ + self.constantsSchema + """.county_attributes ca where dat.fips = ca.fips order by ca.fips asc"""
                
                # we have 30 scenarios for SG to run, but only want one to query the database once
                self.querySG = False
                    
         
         
            
        elif self.run_code.startswith('FR'):
            
            if self.run_code == 'FR':
                self.query = """select ca.fips, ca.st, dat.fed_minus_55 
                from """ + self.constantsSchema + """.county_attributes ca, fr_data dat where dat.fips = ca.fips"""









# functions associated with nonroad input files (*.opt files)

class NROptionFile:
    """
    The 'NROptionFile' is used to creat .opt files to run the Nonroad program. 
    """

    def __init__(self, scenarioOptions, allocate, state, fips):
        
        self.run_code = scenarioOptions.run_code
        
        self.path = scenarioOptions.path + 'OPT/' + scenarioOptions.run_code + '/'
        
        self.outPathNR = self.path.replace('/', '\\')
        self.outPathPopAlo = scenarioOptions.path.replace('/', '\\')
        
#        self.outPath = scenarioOptions.path + 'OPT/'
#        self.outPath = self.outPath.replace('/','\\')
        
        self.episodeYear = scenarioOptions.episodeYear
        
        self.state = state
        
        self.tempMin = 50.0
        self.tempMax = 68.8
        self.tempMean = 60.0
        
        self.__NRoptions__(fips)



    
    def __NRoptions__(self, fips):
        
        with open(self.path + self.state + ".opt", 'w') as self.opt_file:
        
            lines = """
------------------------------------------------------
                  PERIOD PACKET
1  - Char 10  - Period type for this simulation.
                  Valid responses are: ANNUAL, SEASONAL, and MONTHLY
2  - Char 10  - Type of inventory produced.
                  Valid responses are: TYPICAL DAY and PERIOD TOTAL
3  - Integer  - year of episode (4 digit year)
4  - Char 10  - Month of episode (use complete name of month)
5  - Char 10  - Type of day
                  Valid responses are: WEEKDAY and WEEKEND
------------------------------------------------------
/PERIOD/
Period type        : Annual
Summation type     : Period total
Year of episode    : """ + self.episodeYear + """
Season of year     :
Month of year      :
Weekday or weekend : Weekday
Year of growth calc:
Year of tech sel   :
/END/

------------------------------------------------------
                  OPTIONS PACKET
1  -  Char 80  - First title on reports
2  -  Char 80  - Second title on reports
3  -  Real 10  - Fuel RVP of gasoline for this simulation
4  -  Real 10  - Oxygen weight percent of gasoline for simulation
5  -  Real 10  - Percent sulfur for gasoline
6  -  Real 10  - Percent sulfur for diesel
7  -  Real 10  - Percent sulfur for LPG/CNG
8  -  Real 10  - Minimum daily temperature (deg. F)
9  -  Real 10  - maximum daily temperature (deg. F)
10 -  Real 10  - Representative average daily temperature (deg. F)
11 -  Char 10  - Flag to determine if region is high altitude
                      Valid responses are: HIGH and LOW
12 -  Char 10  - Flag to determine if RFG adjustments are made
                      Valid responses are: YES and NO
------------------------------------------------------
/OPTIONS/
Title 1            : 2011 current corn grain scenario
Title 2            : All scripts written by Noah Fisher
Fuel RVP for gas   : 8.0
Oxygen Weight %    : 2.62
Gas sulfur %       : 0.0339
Diesel sulfur %    : 0.0011
Marine Dsl sulfur %: 0.0435
CNG/LPG sulfur %   : 0.003
Minimum temper. (F): """ + str(self.tempMin) + """
Maximum temper. (F): """ + str(self.tempMax) + """
Average temper. (F): """ + str(self.tempMean) + """
Altitude of region : LOW
EtOH Blend % Mkt   : 78.8
EtOH Vol %         : 9.5
/END/

------------------------------------------------------
                  REGION PACKET
US TOTAL   -  emissions are for entire USA without state
              breakout.

50STATE    -  emissions are for all 50 states
              and Washington D.C., by state.

STATE      -  emissions are for a select group of states
              and are state-level estimates

COUNTY     -  emissions are for a select group of counties
              and are county level estimates.  If necessary,
              allocation from state to county will be performed.

SUBCOUNTY  -  emissions are for the specified sub counties
              and are subcounty level estimates.  If necessary,
              county to subcounty allocation will be performed.

US TOTAL   -  Nothing needs to be specified.  The FIPS
              code 00000 is used automatically.

50STATE    -  Nothing needs to be specified.  The FIPS
              code 00000 is used automatically.

STATE      -  state FIPS codes

COUNTY     -  state or county FIPS codes.  State FIPS
              code means include all counties in the
              state.

SUBCOUNTY  -  county FIPS code and subregion code.
------------------------------------------------------
/REGION/
Region Level       : COUNTY
All STATE          : """ + fips[0:2] + """000
/END/

or use -
Region Level       : STATE
Michigan           : 26000
------------------------------------------------------

              SOURCE CATEGORY PACKET

This packet is used to tell the model which source
categories are to be processed.  It is optional.
If used, only those source categories list will
appear in the output data file.  If the packet is
not found, the model will process all source
categories in the population files.
------------------------------------------------------
/SOURCE CATEGORY/
                   :2260005000
                   :2265005000
                   :2267005000
                   :2268005000
                   :2270005000
                   :2270007015
/END/
------------------------------------------------------
/RUNFILES/
ALLOC XREF         : data\\allocate\\allocate.xrf
ACTIVITY           : c:\\nonroad\\data\\activity\\activity.dat
EXH TECHNOLOGY     : data\\tech\\tech-exh.dat
EVP TECHNOLOGY     : data\\tech\\tech-evp.dat
SEASONALITY        : data\\season\\season.dat
REGIONS            : data\\season\\season.dat
REGIONS            : data\\season\\season.dat
MESSAGE            : c:\\nonroad\\outputs\\""" + self.state + """.msg
OUTPUT DATA        : """ + self.outPathPopAlo + 'OUT\\' + self.run_code + '\\' + self.state + """.out
EPS2 AMS           :
US COUNTIES FIPS   : data\\allocate\\fips.dat
RETROFIT           :
/END/

------------------------------------------------------
This is the packet that defines the equipment population
files read by the model.
------------------------------------------------------
/POP FILES/
Population File    : """ + self.outPathPopAlo + 'POP\\' + self.state + '_' + self.run_code + """.pop
/END/

------------------------------------------------------
This is the packet that defines the growth files
files read by the model.
------------------------------------------------------
/GROWTH FILES/
National defaults  : data\\growth\\nation.grw
/END/


/ALLOC FILES/
Harvested acres    : """ + self.outPathPopAlo + 'ALLOCATE\\' + self.state + '_' + self.run_code + """.alo
/END/
------------------------------------------------------
This is the packet that defines the emssions factors
files read by the model.
------------------------------------------------------
/EMFAC FILES/
THC exhaust        : data\\emsfac\\exhthc.emf
CO exhaust         : data\\emsfac\\exhco.emf
NOX exhaust        : data\\emsfac\\exhnox.emf
PM exhaust         : data\\emsfac\\exhpm.emf
BSFC               : data\\emsfac\\bsfc.emf
Crankcase          : data\\emsfac\\crank.emf
Spillage           : data\\emsfac\\spillage.emf
Diurnal            : data\\emsfac\\evdiu.emf
Tank Perm          : data\\emsfac\\evtank.emf
Non-RM Hose Perm   : data\\emsfac\\evhose.emf
RM Fill Neck Perm  : data\\emsfac\\evneck.emf
RM Supply/Return   : data\\emsfac\\evsupret.emf
RM Vent Perm       : data\\emsfac\\evvent.emf
Hot Soaks          : data\\emsfac\\evhotsk.emf
RuningLoss         : data\\emsfac\\evrunls.emf
/END/

------------------------------------------------------
This is the packet that defines the deterioration factors
files read by the model.
------------------------------------------------------
/DETERIORATE FILES/
THC exhaust        : data\\detfac\\exhthc.det
CO exhaust         : data\\detfac\\exhco.det
NOX exhaust        : data\\detfac\\exhnox.det
PM exhaust         : data\\detfac\\exhpm.det
Diurnal            : data\\detfac\\evdiu.det
Tank Perm          : data\\detfac\\evtank.det
Non-RM Hose Perm   : data\\detfac\\evhose.det
RM Fill Neck Perm  : data\\detfac\\evneck.det
RM Supply/Return   : data\\detfac\\evsupret.det
RM Vent Perm       : data\\detfac\\evvent.det
Hot Soaks          : data\\detfac\\evhotsk.det
RuningLoss         : data\\detfac\\evrunls.det
/END/

Optional Packets - Add initial slash "/" to activate

/STAGE II/
Control Factor     : 0.0
/END/
Enter percent control: 95 = 95% control = 0.05 x uncontrolled
Default should be zero control.

/MODELYEAR OUT/
EXHAUST BMY OUT    :
EVAP BMY OUT       :
/END/

SI REPORT/
SI report file-CSV :OUTPUTS\NRPOLLUT.CSV
/END/

/DAILY FILES/
DAILY TEMPS/RVP    :
/END/

PM Base Sulfur
 cols 1-10: dsl tech type;
 11-20: base sulfur wt%; or '1.0' means no-adjust (cert= in-use)
/PM BASE SULFUR/
T2        0.0350    0.02247
T3        0.2000    0.02247
T3B       0.0500    0.02247
T4A       0.0500    0.02247
T4B       0.0015    0.02247
T4        0.0015    0.30
T4N       0.0015    0.30
T2M       0.0350    0.02247
T3M       1.0       0.02247
T4M       1.0       0.02247
/END/
"""
            self.opt_file.writelines(lines)
            
            self.opt_file.close()

