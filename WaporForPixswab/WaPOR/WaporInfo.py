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


def main(Dir, data='AETI', freq='M', Startdate='2009-01-01', Enddate='2018-12-31', 
         latlim=[-40.05, 40.05], lonlim=[-30.5, 65.05], 
         level=1,version = 2, Waitbar = 1,cached_catalog=True):
    """
    This function downloads monthly WaPOR  data

    Keyword arguments:
    Dir -- 'C:/file/to/path/'
    Startdate -- 'yyyy-mm-dd'
    Enddate -- 'yyyy-mm-dd'
    latlim -- [ymin, ymax] (values must be between -40.05 and 40.05)
    lonlim -- [xmin, xmax] (values must be between -30.05 and 65.05)
    cached_catalog -- True  Use a cached catalog. False Load a new catalog from the database
    """
    # print(f'\nDownload WaPOR Level {level} monthly {data} data for the period {Startdate} till {Enddate}')

    # Download data
    WaPOR.API.version=version
    catalog=WaPOR.API.getCatalog(cached=cached_catalog)
    bbox=[lonlim[0],latlim[0],lonlim[1],latlim[1]]
    
    if level==1:
        cube_code=f"L1_{data}_{freq}"
    elif level==2:
        cube_code=f'L2_{data}_{freq}'
    elif level==3:
        print('Level 3 data only available in some areas with specific data cube code below: ')        
        for i,row in catalog.iterrows():            
            if (f'L3' in row['code'])&(f'{data}' in row['code'])&(row['code'][-1]=='M'):
                print('%s: %s'%(row['caption'],row['code']))
        cube_code=input('Insert Level 3 cube code for the selected area: ')   
    
    try:
        cube_info=WaPOR.API.getCubeInfo(cube_code)
        multiplier=cube_info['measure']['multiplier']
    except:
        print('ERROR: Cannot get cube info. Check if WaPOR version has cube {0}'.format(cube_code))
        return None
    time_range='{0},{1}'.format(Startdate,Enddate)
    try:
        df_avail=WaPOR.API.getAvailData(cube_code,time_range=time_range)
    except:
        print('ERROR: cannot get list of available data')
        return None
    if Waitbar == 1:
        import WaPOR.WaitbarConsole as WaitbarConsole
        total_amount = len(df_avail)
        amount = 0
        WaitbarConsole.printWaitBar(amount, total_amount, prefix = 'Progress:', suffix = 'Complete', length = 50)

    Dir=os.path.join(Dir,'WAPOR.v%s_%s' %(version,cube_code))
    if not os.path.exists(Dir):
        os.makedirs(Dir)

    return Dir, df_avail, bbox, cube_code


    