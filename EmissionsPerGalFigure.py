from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import psycopg2 as db
from pylab import *
import matplotlib.pyplot as plt
from scipy.stats import scoreatpercentile
import Options

"""
@comments: much of this plotting utility was taken from the following URL:
http://matplotlib.org/examples/pylab_examples/boxplot_demo2.html
"""

"""
function to collect the data from the database using a query in the form of a string
"""

class EmissionsPerGallon(Options.ScenarioOptions):
    

 
    def __init__(self, modelRunTitle):
        Options.ScenarioOptions.__init__(self, modelRunTitle)
    
        self.f = open(self.path + 'FIGURES/PerGalEtOH_numerical.csv','w')
        
        self.f.write('feedstock, pollutant, max, 95, 75, median, 25, 5, min, mean \n')
        
    #define inputs/constants:  
        pollutantLabels = ['$NO_x$', '$NH_3$', '$CO$', '$SO_x$','$VOC$','$PM_{10}$','$PM_{2.5}$']
        
        feedstockList = ['Corn Grain','Switchgrass','Corn Stover','Wheat Straw','Forest Residue']
        fList = ['CG','SG','CS','WS','FR']
        pollutantList = ['NOx','NH3','CO','SOx','VOC','PM10','PM25']
        EtOHVals = [2.76, 89.6, 89.6, 89.6, 75.7] #gallons per production (bu for CG, dry short ton for everything else)    
    
        queryTable = 'summedemissions'
    
        for pNum, pollutant in enumerate(pollutantList):
    #-----------------EXTRACT DATA FROM THE DATABASE-----------------    
            dataArray = self.__collectData__(queryTable, feedstockList, pollutant, EtOHVals)
    #-----------------PART 2, PLOT DATA----------------------------------
            #pretty plotting things
            fig = plt.figure(figsize=(8,6))
            canvas = FigureCanvas(fig)        
            self.ax1 = fig.add_subplot(111)
    #adjust this value to change the plot size
    #----------------------------------------------------------------
            plt.subplots_adjust(left=0.15, right=0.99, top=0.95, bottom=0.1)
    #---------------------------------------------------------------- 

    #-------create boxplot
            bp = plt.boxplot(dataArray, notch=0, sym='', vert=1, whis=1000)
                
            plt.setp(bp['boxes'], color='black')
            plt.setp(bp['whiskers'], color='black', linestyle='-')
            plt.yscale('log')
    
            plotTitle=pollutantLabels[pNum]
            axisTitle = '%s emissions  (g/gal EtOH)' % (pollutantLabels[pNum])
            
            self.__setAxis__(plotTitle, axisTitle, dataArray, fList)    
    #plot 95% intervals 
            perc95 = self.__plotInterval__(dataArray)
    
            fig.savefig(self.path + 'Figures/PerGalEtOH_'+pollutant+'.png', format = 'png')
    
            print pollutant
        
            
        self.f.close()
        
            
    
    def __collectData__(self, queryTable, feedstockList, pollutant, EtOHVals):
        data = []
        for fNum, feedstock in enumerate(feedstockList):
            cur = self.conn.cursor()
            query = """
    SELECT (%s) / (prod * %s * 1e-6) FROM %s.%s WHERE prod > 0.0 AND feedstock ilike '%s';
    """  % (pollutant, EtOHVals[fNum], self.schema, queryTable, feedstock)
            cur.execute(query)
            data.append(cur.fetchall())
             
            cur.close()
             
        self.__writeData__(data, feedstockList, pollutant)
        return data
    
    
    
    def __plotInterval__(self, dataArray):
    
        numFeed = 5
        numArray = array([x for x in range(numFeed)]) + 1 #index starts at 1, not zero
            
        #plot 95% interval
        perc95 = array([scoreatpercentile(dataArray[0],95), scoreatpercentile(dataArray[1],95),
                        scoreatpercentile(dataArray[2],95), scoreatpercentile(dataArray[3],95), 
                        scoreatpercentile(dataArray[4],95)])
                          
        #plot 5% interval
        perc5 = array([scoreatpercentile(dataArray[0],5), scoreatpercentile(dataArray[1],5),
                        scoreatpercentile(dataArray[2],5), scoreatpercentile(dataArray[3],5), 
                        scoreatpercentile(dataArray[4],5)])
                        
        plt.plot((numArray), perc95, '_', markersize=15, color='k')                 
        plt.plot((numArray), perc5, '_', markersize=15, color='k')
        
        
        
    """
    function to set axis titles and plot titles
    """
    def __setAxis__(self, plotTitle, axisTitle, dataArray, data_labels):
    # Add a horizontal grid to the plot
        self.ax1.yaxis.grid(True, linestyle='-', which='major', color='lightgrey',
                      alpha=0.7)
                      
#        self.ax1.set_ylim(bottom=1e-04, top=0.01)                  
        
        # Hide these grid behind plot objects
        self.ax1.set_axisbelow(True)
    
        self.ax1.set_ylabel(axisTitle, size=25, style='normal')    
        
    #    ax1.set_yticklabels([1e-3,1e-2,1e-1,0,1,10,], size = 15)
    
        self.ax1.set_xticklabels(data_labels, size=25, style='normal')                         
    
    #    ax1.set_title(plotTitle+' Mg per gallon of EtOH', size=20, style='normal')
        
        minVal = min(dataArray[4])[0]
        if minVal < 1e-3:
            minString='%.0e' % (minVal)
            maxString='%.0e' % (max(dataArray[4])[0])
    
        #value            
            self.ax1.annotate(' min='+minString, xy=(4.5, 2.5e-3),size=15) 
            self.ax1.annotate('max='+maxString, xy=(4.5, 4.0e-3),size=15) 
        #arrow pointing down
            self.ax1.annotate('', xy=(4.75, 1.0e-3),
                         xytext=(4.75,1.9e-3), 
                         arrowprops=dict(arrowstyle="->"))   
    
    
    
        
        
    def __writeData__(self, dataArray, feedstockList, pollutant):
        
        
        
        for fNum, feedstock in enumerate(feedstockList):
            lines=[ feedstock, pollutant, max(dataArray[fNum])[0],
                 scoreatpercentile(dataArray[fNum],95), 
                 scoreatpercentile(dataArray[fNum],50),
                 median(dataArray[fNum]),
                 scoreatpercentile(dataArray[fNum],25), 
                 scoreatpercentile(dataArray[fNum],5),
                 min(dataArray[fNum])[0],
                 mean(dataArray[fNum]) ]             
    
            self.f.write(str(lines) + '\n')    
           
    
 
        
        
        
if __name__ == "__main__":  
    modelRunTitle = "AllFeed"
    EmissionsPerGallon(modelRunTitle)
       
