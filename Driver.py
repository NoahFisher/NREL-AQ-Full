from subprocess import Popen

import Options as Opt
import Allocate as Alo
import Population as Pop
import UpdateDatabase
import FugitiveDust
import Chemical
import CombustionEmissions 
import Fertilizer
import SinglePassAllocation 
import NEIComparison
import EmissionsPerGalFigure
import RatioToNEIFigure
"""
"""

class Driver: 
    
    
    if __name__ == "__main__":     

#---------------------------------------------------------------------------------------------------------------------        
        #Nonroad can only load files with 8 characters, so run_codes can be 5 characters at MOST. 
        #uncomment the scenarios you would like to run. 
        run_codes = [
                     'SG_H1','SG_H2','SG_H3','SG_H4','SG_H5','SG_H6','SG_H7','SG_H8','SG_H9','SG_H10',
                     'SG_N1','SG_N2','SG_N3','SG_N4','SG_N5','SG_N6','SG_N7','SG_N8','SG_N9','SG_N10',
                     'SG_T1','SG_T2','SG_T3','SG_T4','SG_T5','SG_T6','SG_T7','SG_T8','SG_T9','SG_T10',
                     'FR',
                     'CS_RT','CS_NT',
                     'WS_RT','WS_NT',
                     'CG_CH','CG_CN',
                     'CG_RH','CG_RN',
                     'CG_NH','CG_NN',
                     'CG_ID','CG_IL',
                     'CG_IC','CG_IG'
                    ]
        
        #scenario title cannot contain spaces and must start with a letter.
        #scenario title cannot be a run_code title 
        #scenario title cannot be more than 8 characters
        #               '--------'
        modelRunTitle = 'AllFeed'
        runNRRuns = False
#---------------------------------------------------------------------------------------------------------------------        
        
        
        #initialize objects
        scenario = Opt.ScenarioOptions(modelRunTitle)
        scenario.initialize(modelRunTitle, run_codes)
        alo = Alo.Allocate(scenario)
        
        
        if runNRRuns:
            for run_code in run_codes:
                
                print run_code
                
                scenario.getData(run_code)
                   
                #initialize variables
                state = scenario.data[0][1]
                fips_prior = str(scenario.data[0][0])
                
            #New population object created for each run_code    
                if run_code.startswith('CG_I'): pop = Pop.CornGrainIrrigationPop(scenario, alo)
                elif run_code.startswith('SG'): pop = Pop.SwitchgrassPop(scenario)
                elif run_code.startswith('FR'): pop = Pop.ForestPop(scenario)
                elif run_code.startswith('CS'): pop = Pop.ResiduePop(scenario)
                elif run_code.startswith('WS'): pop = Pop.ResiduePop(scenario)    
                elif run_code.startswith('CG'): pop = Pop.CornGrainPop(scenario)
                
                alo.initializeAloFile(state, run_code)
                pop.initializePop(scenario.data[0])
                scenario.initializeBatch()
                
                for dat in scenario.data:
                    fips = str(dat[0])
                                  
                    if dat[1] == state:
                        indicator = dat[2]
                        alo.writeIndicator(fips, indicator)
                        pop.append_Pop(fips, dat)
            
                    else:
            #write *.opt file, close allocation file, close *.pop file            
                        Opt.NROptionFile(scenario, alo, state, fips_prior)
                        alo.writeSumAndClose(fips_prior)
                        pop.finishPop()
                        scenario.appendBatch(state)
                        
    #                    print fips_prior, state
            
                        fips_prior = fips
                        state = dat[1]   
            
            #initialize new pop and allocation files.                      
                        alo.initializeAloFile(state, run_code)
                        pop.initializePop(dat)
                        indicator = dat[2]
                        alo.writeIndicator(fips, indicator)
                        pop.append_Pop(fips, dat)            
                     
            #close allocation files    
                Opt.NROptionFile(scenario, alo, state, fips)        
                alo.writeSumAndClose(fips_prior)
                pop.finishPop()
                scenario.appendBatch(state)
                scenario.finishBatch()
            
            #close scenariobatchfile
            scenario.scenarioBatchFile.close()
            
    #----------------------------------------------        
            #call BATCH file here
            p = Popen(scenario.path+'opt/'+modelRunTitle+'.bat')
            #write values to a file to record assumptions. 
            #wait for batch file to complete 
            p.wait()            
    #----------------------------------------------        










#----------------------------------------------
        #the following commands create and populate the schema with the emissions inventory.
#----------------------------------------------        
        #initialize database objects
        Fert = Fertilizer.Fertilizer(modelRunTitle)
        Chem = Chemical.Chemical(modelRunTitle)
        Comb = CombustionEmissions.CombustionEmissions(modelRunTitle)
        Update = UpdateDatabase.UpdateDatabase(modelRunTitle)
        FugDust = FugitiveDust.FugitiveDust(modelRunTitle)
        NEI = NEIComparison.NEIComparison(modelRunTitle)
        
  
  
        # get feedstocks from the run_codes
        feedstockList = []
        for run_code in run_codes:
            if run_code[0:2] in feedstockList:
                pass
            else:
                feedstockList.append(run_code[0:2])
        
        
#----------------------------------------------------------------
        #Create tables, Populate Fertilizer & Chemical tables.  
        for feedstock in feedstockList:
            Update.createTables(feedstock)
            Fert.setFertilizer(feedstock)
            Chem.setChemical(feedstock)
            print "Fertilizer and Chemical complete for " + feedstock
#----------------------------------------------------------------
        
        
#----------------------------------------------------------------    
        #Populate Combustion Emissions Tables
        print "Populating tables with combustion emissions..."
        Comb.populateTables(run_codes, modelRunTitle)
        print "...COMPLETED populating tables with combustion emissions."
#----------------------------------------------------------------
        
        
#----------------------------------------------------------------
        #Fugitive Dust Emissions
        modelSG = False
        for run_code in run_codes:
            if not run_code.startswith('SG'):
                FugDust.setEmissions(run_code) 
                print "Fugitive Dust Emissions complete for " + run_code  
            else: 
                modelSG = True
                
        if modelSG:
            #It makes more sense to create fugitive dust emissions using a separate method
            operations = ['Transport', 'Harvest', 'Non-Harvest']
            for operation in operations:
                sgFugDust = FugitiveDust.SG_FugitiveDust(modelRunTitle, operation)
                sgFugDust.setEmissions()
#----------------------------------------------------------------            
        
        
#----------------------------------------------------------------
        #allocate emissions for single pass methodology - see constructor for ability to allocate CG emissions
        print "Allocate single pass emissions between corn stover and wheat straw."
        SinglePassAllocation.SinglePassAllocation(modelRunTitle)
#----------------------------------------------------------------
        
        
#----------------------------------------------------------------
        #Create NEI comparison
        
        #create a single table that has all emissions in this inventory
        for feedstock in feedstockList:
            NEI.createSummedEmissionsTable(feedstock)
            
        #create tables that contain a ratio to NEI
        for feedstock in feedstockList:
            NEI.createNEIComparison(feedstock)
#----------------------------------------------------------------


#----------------------------------------------------------------
        #create graphics and numerical summary 
        
        #Contribution Analysis
        
        #Emissions Per Gallon
        EmissionsPerGalFigure.EmissionsPerGallon(modelRunTitle)
        
        #Ratio to NEI
        ratioNEI = RatioToNEIFigure.RatioToNEIFig(modelRunTitle)
        for feedstock in feedstockList:
            pass
        
        #create all feedstock and cellulosic NEI ratios
        if len(feedstock) == 5:
            pass
        
        ratioNEI.f.close()
#----------------------------------------------------------------
        
        print 'Successful completion of model run.'
