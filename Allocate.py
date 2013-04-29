# Functions associated with allocation



class Allocate(object):
    """
    The 'Allocate' class is used to write spatial indicators to .alo file for the NonRoad program to use. 
    File are written on a state-level basis. 
    """

    def __init__(self,scenarioOptions):
        self.scenario = scenarioOptions
        self.path = scenarioOptions.path + 'ALLOCATE/' 


        
    def initializeAloFile(self, state, run_code):
        self.episodeYear = self.scenario.episodeYear         
        self.run_code = run_code
        self.inicatorTotal = 0.0 
               
        self.alo_file = open(self.path + state + '_' + run_code+'.alo', 'w')
        lines = """
------------------------------------------------------------------------
This is the packet that contains the allocation indicator data.  Each
indicator value is a measured or projected value such as human
population or land area.  The format is as follows.

1-3    Indicator code
6-10   FIPS code (can be global FIPS codes e.g. 06000 = all of CA)
11-15  Subregion code (blank means is entire nation, state or county)
16-20  Year of estimate or prediction
21-40  Indicator value
41-45  Blank (unused)
46+    Optional Description (unused)
------------------------------------------------------------------------
/INDICATORS/
""" 
        self.alo_file.writelines(lines)




    ## This function writes the appropriate information to each line of the file
    ## Inputs: allocation file name, fips number, and indicator value 
    ## Outputs: write lines for state leve allocation file
    def writeIndicator(self, fips, indicator):
        if self.run_code.startswith('FR'):
            #convert input -> dry ton_s into cubic feet
            # (x dry_ton) * (2000 lbs / ton) * (1 ft^3 / 30 lbs) --> BT2 Report page 18 footnote.
            indicator = float(indicator) * 2000.0 * 1.0 / 30.0
            lines = """LOG  %s      %s    %s\n""" % (fips, self.episodeYear, indicator)
            
        else:
            lines = """FRM  %s      %s    %s\n""" % (fips, self.episodeYear, indicator)
        
        self.alo_file.writelines(lines)

#        print indicator, fips
        self.inicatorTotal += float(indicator)




    ## This function finishes off the .alo file
    def writeSumAndClose(self, fips):
        if self.run_code.startswith('FR'):
            lines = """LOG  %s000      %s    %s\n/END/""" % (fips[0:2], self.episodeYear, self.inicatorTotal)

        else:
            lines = """FRM  %s000      %s    %s \n/END/""" % (fips[0:2], self.episodeYear, self.inicatorTotal)
            
        self.alo_file.writelines(lines)
        
        self.alo_file.close()
        
        


        
        
