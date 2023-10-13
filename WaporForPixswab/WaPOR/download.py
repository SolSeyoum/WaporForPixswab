# -*- coding: utf-8 -*-
"""
Created on Tue Jul 23 11:25:33 2019

@author: ntr002
"""
import WaPOR
from datetime import datetime
import requests
import os
from WaPOR import GIS_functions as gis


def main(Dir, bbox,cube_code, row_time_code, row_raster_id, cached_catalog=True):
    """
    This function downloads monthly WPOR PCP data

    Keyword arguments:
    Dir -- 'C:/file/to/path/'
    Startdate -- 'yyyy-mm-dd'
    Enddate -- 'yyyy-mm-dd'
    latlim -- [ymin, ymax] (values must be between -40.05 and 40.05)
    lonlim -- [xmin, xmax] (values must be between -30.05 and 65.05)
    cached_catalog -- True  Use a cached catalog. False Load a new catalog from the database
    """
    # print(f'\nDownload WaPOR Level {level} monthly {data} data for the period {Startdate} till {Enddate}')

    catalog=WaPOR.API.getCatalog(cached=cached_catalog)     
    # for index,row in df_avail.iterrows():   
    download_url=WaPOR.API.getCropRasterURL(bbox,cube_code,
                                            row_time_code,
                                            row_raster_id,
                                            WaPOR.API.APIToken)       
    
#        Date=datetime.strptime(row['MONTH'], '%Y-%m')
    filename='{0}.tif'.format(row_raster_id)
    # outfilename=os.path.join(Dir,filename)       
    download_file=os.path.join(Dir,
                                '{0}.tif'.format(row_raster_id))
    #Download raster file
    resp=requests.get(download_url) 
    open(download_file,'wb').write(resp.content) 

        # driver, NDV, xsize, ysize, GeoT, Projection= gis.GetGeoInfo(download_file)
        # # Array = gis.OpenAsArray(download_file,nan_values=True)
        # Array = gis.OpenAsArray(download_file, dtype ="int16", nan_values=False)
        # CorrectedArray=Array#*multiplier
        # gis.CreateGeoTiff(outfilename,CorrectedArray,
        #                   driver, NDV, xsize, ysize, GeoT, Projection, compress = 'LZW')
        # os.remove(download_file)        

        # if Waitbar == 1:                 
        #     amount += 1
        #     WaitbarConsole.printWaitBar(amount, total_amount, 
        #                                 prefix = 'Progress:', 
        #                                 suffix = 'Complete', 
        #                                 length = 50)
    return Dir
