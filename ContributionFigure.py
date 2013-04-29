"""
@author: nfisher
"""
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from pylab import median
import matplotlib
import psycopg2 as db
from ContributionTests import ChooseSQL
#import time
import Options

class ContributionAnalysis(Options.ScenarioOptions):
    def __init__(self, modelRunTitle):
        Options.ScenarioOptions.__init__(self, modelRunTitle)
    #    startTime = time.time()
    #-----------inputs begin
        fig = Figure( figsize=(7,5), dpi=200) 
        canvas = FigureCanvas(fig)
            
        fColor = ['r','b','g','k','c']
        fMarker = ['o','o','o','o','o']
    
        feedstockList = ['CG','SG','CS','WS','FR']
        pollutantList = ['NH3','NOx','VOC','PM25','PM10','CO','SOx']
        pollutantLabels = ['$NH_3$','$NO_x$','$VOC$','$PM_{2.5}$','$PM_{10}$','$CO$','$SO_x$'] 
        activityList = ['Non-Harvest','Fertilizer','Chemical','Harvest','Transport']
        activityLabels = ['Non-Harvest','N-Fertilizer','Pesticide','Harvest','Transport']
        
        self.f = open(self.path + 'Figures/Contribution_numerical.csv','w') 
    #-----------inputs end
    
    
        
        index = 0
        for yLabel, activity in enumerate(activityList):
            print activity
        
            for titleLabel, pollutant in enumerate(pollutantList):
                
                ax = fig.add_subplot( 5, 7, index+1 )
                ax.set_xlim([-1,5])
                ax.set_ylim([-0.1, 1.1])
          
                #show y labels on first column only
                if index % 7 == 0   :
                    matplotlib.rcParams.update({'font.size': 8})
                    ax.set_ylabel(activityLabels[yLabel])
                else: 
                    ax.set_yticklabels([])
                
                #show pollutant labels above first row of plots
                if index < 7:
                    ax.set_title(pollutantLabels[titleLabel])
                
                #show x labels below last row only
                if index < 28:
                    ax.set_xticklabels([])
                else:
                    ax.set_xticklabels(([''] + feedstockList), rotation='vertical')
        
                index+=1
                self.f.write(pollutant+','+activity+'\n')
                for fNum, feedstock in enumerate(feedstockList):
    
                    x = ChooseSQL(activity, pollutant, feedstock, self.schema)
                    self.makePlots(ax, x, fNum, 
                              fColor[fNum], fMarker[fNum], feedstock)  
         
                self.f.write('\n')
        
    #    print figure to a .png file (small file size)
    #    canvas.print_figure('Contribution Analysis.tiff')      
        fig.savefig(self.path + 'Figures/Contribution_Figure.png', format = 'png')
           
        self.f.close()
    #    print time.time() - startTime, ' seconds'
        
        
    
    
    
    
    """
    This section of code formats the plots
    """
    def makePlots(self, ax, x, fNum, fColor, fMarker, feedstock):
        
        x.getQuery()
        
        if x.queryString.startswith('No'):
            pass    
        
        elif x.queryString.startswith('FR'):
            data = [1,1]
            ax.plot([fNum]*2,[1,1],fColor,marker=fMarker,markersize=2)
            
        else:
            cur = self.conn.cursor()
            print x.queryString
            cur.execute(x.queryString)
            #[all data]
            data = cur.fetchall()
            cur.close()
            medVal = median(data)
            maxVal = max(data)
            minVal = min(data)
            
            ax.plot([fNum],medVal,fColor,marker='_', markersize=7)
    
            #Plot the max/min values
            ax.plot([fNum]*2,[maxVal, minVal],fColor,marker=fMarker, markersize=2)    
            
            self.writeResults(feedstock, str(maxVal[0]), str(medVal), str(minVal[0]))
    
    
    """
    This section writes the results to a file in a readable format. 
    """
    def writeResults(self, feedstock, maxVal, medVal, minVal):
        self.f.write(feedstock+','+maxVal+','+medVal+','+minVal+'\n')
    



if __name__ == "__main__":  
    modelRunTitle = "AllFeed"
    ContributionAnalysis(modelRunTitle)
       
