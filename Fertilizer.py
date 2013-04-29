import Options

class Fertilizer(Options.ScenarioOptions): 
    def __init__(self, modelRunTitle):
        Options.ScenarioOptions.__init__(self, modelRunTitle)
           
    def setFertilizer(self, feed):
#table format in database        
#    FIPS    char(5)    ,
#    NOx    float    ,
#    NH3    float    ,
#    SCC    char(10)    ,
#    description    text   
        if feed != 'FR':
             
            if feed == 'CS':
                query = self.__cornStover__(feed)
        
            elif feed == 'WS':
                query = self.__wheatStraw__(feed)
                
            elif feed == 'CG':
                query = self.__cornGrain__()
                
            elif feed == 'SG':
                query = self.__switchgrass__()
              
            self.__executeQuery__(query)
        
        
        
    def __cornStover__(self, feed):
        fertQuery = """        
INSERT INTO """ + feed + """_nfert
    (
        --------------------------------------------------------------------------
        --This query returns the urea component 
        --------------------------------------------------------------------------
        SELECT feed.fips, 

        ((N_app.""" + feed + """ / 2000.0) * (n_dist.urea * nfert.nox_ur) * 0.90718474 / 2000.0 * feed.prod) AS "NOX", 

        ((N_app.""" + feed + """ * 0.90718474 / 2000.0) * (n_dist.urea * nfert.nh3_ur) * feed.prod * 17.0 / 14.0) AS "NH3",

        (2801700004) AS SCC,

        'Urea Fertilizer Emissions' AS "Description"

        FROM """ + self.productionSchema + '.' + feed + """_data feed, """ + self.constantsSchema + """.N_fert_EF nfert, 
        """ + self.constantsSchema + """.CS_WS_SG_Napp N_app, """ + self.constantsSchema + """.n_fert_distribution n_dist

        GROUP BY feed.fips, 
        nfert.nox_ur, nfert.nox_nsol, nfert.nox_as, nfert.nox_an, nfert.nox_aa,
        nfert.nh3_ur, nfert.nh3_nsol, nfert.nh3_as, nfert.nh3_an, nfert.nh3_aa,
        feed.prod, N_APP.""" + feed + """, n_dist.urea
    )
    UNION 
    (
        --------------------------------------------------------------------------
        --This query contains the Nitrogen Solutions Component
        --------------------------------------------------------------------------

        SELECT feed.fips, 

        ((N_app.""" + feed + """ / 2000.0) * (n_dist.nsol * nfert.nox_nsol) * 0.90718474 / 2000.0 * feed.prod) AS "NOX", 

        ((N_app.""" + feed + """ * 0.90718474 / 2000.0) * (n_dist.nsol * nfert.nh3_nsol) * feed.prod * 17.0 / 14.0) AS "NH3",

        (2801700003) AS SCC,

        'Nitrogen Solutions Fertilizer Emissions' AS "Description"

        FROM """ + self.productionSchema + '.' + feed + """_data feed, """ + self.constantsSchema + """.N_fert_EF nfert, 
        """ + self.constantsSchema + """.CS_WS_SG_Napp N_app, """ + self.constantsSchema + """.n_fert_distribution n_dist

        GROUP BY feed.fips, 
        nfert.nox_ur, nfert.nox_nsol, nfert.nox_as, nfert.nox_an, nfert.nox_aa,
        nfert.nh3_ur, nfert.nh3_nsol, nfert.nh3_as, nfert.nh3_an, nfert.nh3_aa,
        feed.prod, N_APP.""" + feed + """, n_dist.nsol
    )
    UNION
    (
        --------------------------------------------------------------------------
        --This query contains the Anhydrous Ammonia Component
        --------------------------------------------------------------------------

        SELECT feed.fips, 

        ((N_app.""" + feed + """ / 2000.0) * (n_dist.anhydrous_ammonia * nfert.nox_aa) * 0.90718474 / 2000.0 * feed.prod) AS "NOX", 

        ((N_app.""" + feed + """ * 0.90718474 / 2000.0) * (n_dist.anhydrous_ammonia * nfert.nh3_aa) * feed.prod * 17.0 / 14.0) AS "NH3",

        (2801700001) AS SCC,

        'Anhydrous Ammonia Fertilizer Emissions' AS "Description"

        FROM """ + self.productionSchema + '.' + feed + """_data feed, """ + self.constantsSchema + """.N_fert_EF nfert, 
        """ + self.constantsSchema + """.CS_WS_SG_Napp N_app, """ + self.constantsSchema + """.n_fert_distribution n_dist

        GROUP BY feed.fips, 
        nfert.nox_ur, nfert.nox_nsol, nfert.nox_as, nfert.nox_an, nfert.nox_aa,
        nfert.nh3_ur, nfert.nh3_nsol, nfert.nh3_as, nfert.nh3_an, nfert.nh3_aa,
        feed.prod, N_APP.""" + feed + """, n_dist.anhydrous_ammonia
    )
    UNION
    (
        --------------------------------------------------------------------------
        --This query contains the Ammonium Nitrate component
        --------------------------------------------------------------------------

        SELECT feed.fips, 

        ((N_app.""" + feed + """ / 2000.0) * (n_dist.ammonium_nitrate * nfert.nox_an) * 0.90718474 / 2000.0 * feed.prod) AS "NOX", 

        ((N_app.""" + feed + """ * 0.90718474 / 2000.0) * (n_dist.ammonium_nitrate * nfert.nh3_an) * feed.prod * 17.0 / 14.0) AS "NH3",

        (2801700005) AS SCC,

        'Ammonium Nitrate Fertilizer Emissions' AS "Description"

        FROM """ + self.productionSchema + '.' + feed + """_data feed, """ + self.constantsSchema + """.N_fert_EF nfert, 
        """ + self.constantsSchema + """.CS_WS_SG_Napp N_app, """ + self.constantsSchema + """.n_fert_distribution n_dist

        GROUP BY feed.fips, 
        nfert.nox_ur, nfert.nox_nsol, nfert.nox_as, nfert.nox_an, nfert.nox_aa,
        nfert.nh3_ur, nfert.nh3_nsol, nfert.nh3_as, nfert.nh3_an, nfert.nh3_aa,
        feed.prod, N_APP.""" + feed + """, n_dist.ammonium_nitrate
    )
    UNION
    (
        --------------------------------------------------------------------------
        --This query contains the Ammonium Sulfate component
        --------------------------------------------------------------------------

        SELECT feed.fips,

        ((N_app.""" + feed + """ / 2000.0) * (n_dist.ammonium_sulfate * nfert.nox_as) * 0.90718474 / 2000.0 * feed.prod) AS "NOX", 

        ((N_app.""" + feed + """ * 0.90718474 / 2000.0) * (n_dist.ammonium_sulfate * nfert.nh3_as) * feed.prod * 17.0 / 14.0) AS "NH3",

        (2801700006) AS SCC,

        'Ammonium Sulfate Fertilizer Emissions' AS "Description"

        FROM """ + self.productionSchema + '.' + feed + """_data feed, """ + self.constantsSchema + """.N_fert_EF nfert, 
        """ + self.constantsSchema + """.CS_WS_SG_Napp N_app, """ + self.constantsSchema + """.n_fert_distribution n_dist

        GROUP BY feed.fips, 
        nfert.nox_ur, nfert.nox_nsol, nfert.nox_as, nfert.nox_an, nfert.nox_aa,
        nfert.nh3_ur, nfert.nh3_nsol, nfert.nh3_as, nfert.nh3_an, nfert.nh3_aa,
        feed.prod, N_APP.""" + feed + """, n_dist.ammonium_sulfate
    )"""
    
        return fertQuery
   
   
    
    def __wheatStraw__(self, feed):
        return self.__cornStover__(feed)
        
    
        
    def __switchgrass__(self):
        fertQuery = """
INSERT INTO sg_nfert 
    (
        SELECT sg.fips,  

        (12.519 / 2000.0 * sg.prod * (nfert.nox_nsol) * 0.907018474 / 2000.0 * 0.9) AS "NOx",

        (12.519 * sg.prod * (nfert.nh3_nsol) * 0.907018474 / 2000.0 * 17.0 / 14.0 * 0.9) AS "NH3",

        (2801700003) AS SCC,

        'Nitrogen Solutions Fertilizer Emissions' AS "Description"

    FROM  """ + self.productionSchema + """.sg_data sg, """ + self.constantsSchema + """.N_fert_EF nfert, """ + self.constantsSchema + """.CS_WS_SG_Napp N_app

    GROUP BY sg.fips, sg.prod,
    nfert.nox_nsol, nfert.nh3_nsol, N_app.SG
    )
"""
        return fertQuery



    def __cornGrain__(self):
        fertQuery = """
INSERT INTO cg_nfert
    (
        --------------------------------------------------------------------------
        --This query returns the urea component 
        --------------------------------------------------------------------------
        SELECT cd.fips, 

        (((n.Conventional_N * cd.convtill_harv_ac + 
           n.Conventional_N * reducedtill_harv_ac + 
           n.NoTill_N * notill_harv_ac) / 2000.0) * (n_dist.urea * nfert.nox_ur) * 0.90718474 / 2000.0) AS "NOX", 

        (((n.Conventional_N * cd.convtill_harv_ac + 
           n.Conventional_N * reducedtill_harv_ac + 
           n.NoTill_N * notill_harv_ac) / 2000.0) * (n_dist.urea * nfert.nh3_ur) * 0.90718474 * 17.0 / 14.0) AS "NH3",

        (2801700004) AS SCC,

        'Urea Fertilizer Emissions' AS "Description"

        FROM """ + self.constantsSchema + """.cg_napp n, """ + self.constantsSchema + """.N_fert_EF nfert, 
        """ + self.productionSchema + """.cg_data cd, """ + self.constantsSchema + """.n_fert_distribution n_dist

        WHERE n.fips = cd.fips 

        GROUP BY cd.fips, 
        nfert.nox_ur, nfert.nh3_ur, cd.convtill_harv_ac, cd.reducedtill_harv_ac, 
        cd.notill_harv_ac, n.Conventional_N, n.NoTill_N, n_dist.urea
    )
    UNION
    (
        --------------------------------------------------------------------------
        --This query contains the Nitrogen Solutions Component
        --------------------------------------------------------------------------

        SELECT cd.fips, 

        (((n.Conventional_N * cd.convtill_harv_ac + 
           n.Conventional_N * reducedtill_harv_ac + 
           n.NoTill_N * notill_harv_ac) / 2000.0) * (n_dist.nsol * nfert.nox_nsol) * 0.90718474 / 2000.0) AS "NOX", 

        (((n.Conventional_N * cd.convtill_harv_ac +
           n.Conventional_N * reducedtill_harv_ac + 
           n.NoTill_N * notill_harv_ac) / 2000.0) * (n_dist.nsol * nfert.nh3_nsol) * 0.90718474 * 17.0 / 14.0) AS "NH3",

        (2801700003) AS SCC,

        'Nitrogen Solutions Fertilizer Emissions' AS "Description"

        FROM """ + self.constantsSchema + """.cg_napp n, """ + self.constantsSchema + """.N_fert_EF nfert,
        """ + self.productionSchema + """.cg_data cd, """ + self.constantsSchema + """.n_fert_distribution n_dist

        WHERE n.fips = cd.fips 

        GROUP BY cd.fips, n.polysys_region_id, 
        nfert.nox_nsol, nfert.nh3_nsol, cd.convtill_harv_ac, cd.reducedtill_harv_ac, 
        cd.notill_harv_ac, n.Conventional_N, n.NoTill_N, n_dist.nsol
    )
    UNION
    (
        --------------------------------------------------------------------------
        --This query contains the Anhydrous Ammonia Component
        --------------------------------------------------------------------------

        SELECT cd.fips, 

        (((n.Conventional_N * cd.convtill_harv_ac + 
           n.Conventional_N * reducedtill_harv_ac + 
           n.NoTill_N * notill_harv_ac) / 2000.0) * (n_dist.anhydrous_ammonia * nfert.nox_aa) * 0.90718474 / 2000.0) AS "NOX", 

        (((n.Conventional_N * cd.convtill_harv_ac + 
           n.Conventional_N * reducedtill_harv_ac + 
           n.NoTill_N * notill_harv_ac) / 2000.0) * (n_dist.anhydrous_ammonia * nfert.nh3_aa) * 0.90718474 * 17.0 / 14.0) AS "NH3",

        (2801700001) AS SCC,

        'Anhydrous Ammonia Fertilizer Emissions' AS "Description"

        FROM """ + self.constantsSchema + """.cg_napp n, """ + self.constantsSchema + """.N_fert_EF nfert,
        """ + self.productionSchema + """.cg_data cd, """ + self.constantsSchema + """.n_fert_distribution n_dist

        WHERE n.fips = cd.fips 

        GROUP BY cd.fips, n.polysys_region_id, 
        nfert.nox_aa, nfert.nh3_aa, cd.convtill_harv_ac, cd.reducedtill_harv_ac, 
        cd.notill_harv_ac, n.Conventional_N, n.NoTill_N, n_dist.anhydrous_ammonia
    )
    UNION
    (
        --------------------------------------------------------------------------
        --This query contains the Ammonium Nitrate component
        --------------------------------------------------------------------------

        SELECT cd.fips, 

        (((n.Conventional_N * cd.convtill_harv_ac + 
           n.Conventional_N * reducedtill_harv_ac + 
           n.NoTill_N * notill_harv_ac) / 2000.0) * (n_dist.ammonium_nitrate * nfert.nox_an) * 0.90718474 / 2000.0) AS "NOX", 

        (((n.Conventional_N * cd.convtill_harv_ac + 
           n.Conventional_N * reducedtill_harv_ac + 
           n.NoTill_N * notill_harv_ac) / 2000.0) * (n_dist.ammonium_nitrate * nfert.nh3_an) * 0.90718474 * 17.0 / 14.0) AS "NH3",

        (2801700005) AS SCC,

        'Ammonium Nitrate Fertilizer Emissions' AS "Description"

        FROM """ + self.constantsSchema + """.cg_napp n, """ + self.constantsSchema + """.N_fert_EF nfert,
        """ + self.productionSchema + """.cg_data cd, """ + self.constantsSchema + """.n_fert_distribution n_dist

        WHERE n.fips = cd.fips 

        GROUP BY cd.fips, n.polysys_region_id, 
        nfert.nox_an, nfert.nh3_an, cd.convtill_harv_ac, cd.reducedtill_harv_ac,
        cd.notill_harv_ac, n.Conventional_N, n.NoTill_N, n_dist.ammonium_nitrate
    )
    UNION
    (
        --------------------------------------------------------------------------
        --This query contains the Ammonium Sulfate component
        --------------------------------------------------------------------------

        SELECT cd.fips, 

        (((n.Conventional_N * cd.convtill_harv_ac + 
           n.Conventional_N * reducedtill_harv_ac + 
           n.NoTill_N * notill_harv_ac) / 2000.0) * (n_dist.ammonium_sulfate * nfert.nox_as) * 0.90718474 / 2000.0) AS "NOX", 

        (((n.Conventional_N * cd.convtill_harv_ac + 
           n.Conventional_N * reducedtill_harv_ac + 
           n.NoTill_N * notill_harv_ac) / 2000.0) * (n_dist.ammonium_sulfate * nfert.nh3_as) * 0.90718474 * 17.0 / 14.0) AS "NH3",

        (2801700006) AS SCC,

        'Ammonium Sulfate Fertilizer Emissions' AS "Description"

        FROM """ + self.constantsSchema + """.cg_napp n, """ + self.constantsSchema + """.N_fert_EF nfert,
        """ + self.productionSchema + """.cg_data cd, """ + self.constantsSchema + """.n_fert_distribution n_dist

        WHERE n.fips = cd.fips 

        GROUP BY cd.fips, n.polysys_region_id, 
        nfert.nox_as, nfert.nh3_as, cd.convtill_harv_ac, cd.reducedtill_harv_ac,
        cd.notill_harv_ac, n.Conventional_N, n.NoTill_N, n_dist.ammonium_sulfate
    )
 """

        return fertQuery


        
        
      
