import Options
import csv
import os

"""
Transform the data from the default Nonroad output to a useful format. 
Update database with emissions as well as copy emissions to static files
for quick debugging and error checking.  
"""
class CombustionEmissions(Options.ScenarioOptions):
    def __init__(self, modelRunTitle):
        Options.ScenarioOptions.__init__(self, modelRunTitle)
        self.pmRatio = 0.20
       
                               
              
    def populateTables(self, run_codes, modelRunTitle):
        
        #-------Inputs Begin
        # # 1 short ton (2000 lbs) = 0.90718474 tonne ( 1 Mg)
        convert_tonne = 0.9071847  # short ton / Metric ton
        
        # # DOE conversion from BTU/gal of diesel, LHV
        self.LHV = 128450.0 / 1e6  # mmBTU / gallon --> default for diesel fuel, changed for other fuel types
                
        # # RSF2 impact analysis NH3 emission factor
        self.NH3_EF = 0.68  # gNH3 / mmBTU --> default for diesel fuel, changed for other fuel types
        
        # # Convert THC to VOC
        self.vocConversion = 1.053  # --> default for diesel fuel
        
        # # Convert PM10 to PM2.5
        self.pm10toPM25 = 0.97  # --> default for diesel fuel
        #-------Inputs End
        
        for run_code in run_codes:
            
            
            # path to results
            path = 'C:/Nonroad/%s/OUT/%s/' % (modelRunTitle, run_code)
            listing = os.listdir(path)
        
            feedstock = run_code[0:2] 
            
            
            # write data to static files for debugging purposes
            f = open('C:/Nonroad/' + modelRunTitle + '/OUT/' + run_code + '.csv', 'wb')
            writer = csv.writer(f)
            writer.writerow(('FIPS', 'SCC', 'HP', 'FuelCons_gal/yr', 'THC_exh', 'VOC_exh', 'CO_exh', 'NOx_exh',
                            'CO2_exh', 'SO2_exh', 'PM10_exh', 'PM25_exh', 'NH3_exh', 'Description'))
        
        
            cur = self.conn.cursor()
            for cur_file in listing:
                # use for debugging
#                print "Current file is: %s -- %s" % (run_code, cur_file)

                reader = csv.reader(open(path + cur_file))
         
                # account for headers in file
                for i in range(10): reader.next()
                        
                for row in reader:
                    
                    if float(row[4]) > 0.0:    
                
                # _getDescription updates the vocConversion, NH3_EF and LHV for each fuel type    
                        SCC = row[2]
                        HP = row[3]   
                        description = self.__getDescription__(run_code, SCC, HP)                
                        
                        

                        THC = float(row[5]) * convert_tonne
                        CO = float(row[6]) * convert_tonne
                        NOx = float(row[7]) * convert_tonne
                        CO2 = float(row[8]) * convert_tonne
                        SO2 = float(row[9]) * convert_tonne
                        PM10 = float(row[10]) * convert_tonne
                        PM25 = float(row[10]) * 0.97 * convert_tonne
                        FuelCons = float(row[19])  # gal/year
                        

                        
                        VOC = THC * self.vocConversion * convert_tonne                    
                        NH3 = FuelCons * self.LHV * self.NH3_EF / (1e6)  # gal/year * mmBTU/gal * gNH3/mmBTU * Mg/g
                    

                # write data to static files and the database
                        writer.writerow((row[0], SCC, HP, FuelCons, THC, VOC, CO, NOx,
                            CO2, SO2, PM10, PM25, NH3, run_code,))
                        
                        cur.execute("""INSERT INTO %s.%s_raw (FIPS, SCC, HP, THC, VOC, CO, NOX, CO2, SOx, PM10, PM25, fuel_consumption, NH3, description, run_code) 
                                               VALUES ('%s', %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, '%s', '%s')"""
                                           % (self.schema, feedstock, row[0], SCC, HP, THC, VOC, CO, NOx, CO2, SO2, PM10, PM25, FuelCons, NH3, description, run_code))
                    
        
            self.conn.commit()
            cur.close()
            
            
        print "Finished populating table for " + run_code            
            







    def __getDescription__(self, run_code, SCC, HP):
        # cast HP as a number
        HP = int(HP)
        
# Switchgrass        
        if run_code.startswith('SG_H'):
            if len(run_code) == 4: 
                description = "Year %s - Harvest" % (run_code[4])  # year 1-9
            else:
                description = "Year %s - Harvest" % (run_code[4:6])  # year 10
        
        elif run_code.startswith('SG_N'):
            if len(run_code) == 4: 
                description = "Year %s - Non-Harvest" % (run_code[4])  # year 1-9
            else:
                description = "Year %s - Non-Harvest" % (run_code[4:6])  # year 10
                
        elif run_code.startswith('SG_T'):
            if len(run_code) == 4: 
                description = "Year %s - Transport" % (run_code[4])  # year 1-9
            else:
                description = "Year %s - Transport" % (run_code[4:6])  # year 10
                        
# Forest Residue            
        elif run_code.startswith('FR'):
            if HP == 600:
                description = "Loader Emissions"
            elif HP == 175:
                description = "Chipper Emissions"
        
# Corn Stover and Wheat Straw        
        elif run_code.startswith('CS') or run_code.startswith('WS'):
        
        # get tillage    
            if run_code.endswith('RT'):
                tillage = 'Reduced Till'
            elif run_code.endswith('NT'):
                tillage = 'No Till'    
            
            if SCC.endswith('5020'):
                operation = 'Harvest'
            elif SCC.endswith('5015'):
                operation = 'Transport'
            
            description = tillage + ' - ' + operation
            
# Corn Grain
        elif run_code.startswith('CG'):
            
        # get tillage    
            if run_code.startswith('CG_R'): tillage = 'Reduced Till'
                
            elif run_code.startswith('CG_N'): tillage = 'No Till'    
                
            elif run_code.startswith('CG_C'): tillage = 'Conventional Till'
        
        # special case for irrigation    
            elif run_code.startswith('CG_I'):
        
                if run_code.endswith('D'):
                    tillage = 'Diesel Irrigation'
                    self.LHV = 128450.0 / 1e6  
                    self.NH3_EF = 0.68  
                    self.vocConversion = 1.053
                    self.pm10toPM25 = 0.97 
                                 
                elif run_code.endswith('L'):
                    tillage = 'LPG Irrigation'
                    self.LHV = 84950.0 / 1e6
                    self.NH3_EF = 0.0  # data not available
                    self.vocConversion = 0.995
                    self.pm10toPM25 = 1.0
                               
                elif run_code.endswith('C'):
                    tillage = 'CNG Irrigation'
                    self.LHV = 20268.0 / 1e6
                    self.NH3_EF = 0.0  # data not available
                    self.vocConversion = 0.004
                    self.pm10toPM25 = 1.0
                                        
                elif run_code.endswith('G'):
                    tillage = 'Gasoline Irrigation'
                    self.LHV = 116090.0 / 1e6
                    self.NH3_EF = 1.01        
                    self.vocConversion = 0.933         
                    self.pm10toPM25 = 0.92
            
        # get operation (harvest or non-harvest)                                                    
            if run_code.endswith('N') or run_code.startswith('CG_I'):
                operation = 'Non-Harvest'
                
            elif run_code.endswith('H'):
                # get operation (harvest or transport)
                if SCC.endswith('5020'):
                    operation = 'Harvest'
                elif SCC.endswith('5015'):
                    operation = 'Transport'
            
   
            description = tillage + ' - ' + operation    
         
        return description 
    
    
    
