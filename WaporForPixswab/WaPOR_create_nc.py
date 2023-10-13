import numpy as np
import rioxarray as rio
import geopandas as gpd
import netCDF4
import datetime
import shutil

def get_shp(fh):
    shape = gpd.read_file(fh)
    # project if the shapefile is not in wsg64
    if((shape.crs != "epsg:4326")|(shape.crs != "EPSG:4326")):
        shape = shape.to_crs("epsg:4326")
    return shape
def get_prod_names(prod, sym_freq):
    prod_split = prod.split('_')
    name = prod_split[1]
    frq = list(sym_freq.keys())[list(sym_freq.values()).index(prod_split[2])]
    level = int(prod_split[0][1:])
    return name, frq, level

def delet_dir2(folder):
    try:
        shutil.rmtree(folder)
    except Exception as e:
        print('Failed to delete %s. Reason: %s' % (folder, e))
            
def delet_dir(folder):
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))

def get_template(temp_file, shape):
    with rio.open_rasterio(temp_file) as temp:
        crs = temp.rio.crs
        temp = temp.squeeze(dim = 'band', drop = True)
        temp.rio.set_spatial_dims(x_dim="x", y_dim="y", inplace=True)
        temp = temp.rio.write_crs(crs, inplace=True) ## Instead of this read the crs from the file
        temp = temp.rio.reproject("EPSG:4326")
        temp = temp.rio.write_crs("EPSG:4326", inplace=True)
        temp = temp.rio.clip(shape.geometry.values,shape.crs, drop=True)
        temp = temp.drop(['spatial_ref'])
        temp = temp.where(temp !=temp.attrs['_FillValue'])
        if temp.y[-1] <temp.y[0]:
            temp=temp.reindex(y=temp.y[::-1])
        template = temp
        attrs = temp.attrs
        attrs.update({'crs':'EPSG:4326'})
        template.attrs = attrs
        temp.close()
    return template

def init_nc(name_nc, dim, var, fill = -9999., attr = None):
    # Create new nc-file. Existing nc-file is overwritten.
    try: name_nc.close()  # just to be safe, make sure dataset is not already open.
    except: pass

    out_nc = netCDF4.Dataset(name_nc, 'w', format='NETCDF4')
    
    # Add dimensions to nc-file.
    for name, values in dim.items():
        # Create limited dimensions.
        if values is not None:
            out_nc.createDimension(name, values.size)
            vals = out_nc.createVariable(name, 'f4', (name,), fill_value = fill)
            vals[:] = values
        # Create unlimited dimensions.
        else:
            out_nc.createDimension(name, None)
            vals = out_nc.createVariable(name, 'f4', (name,), fill_value = fill)
            vals.calendar = 'standard'
            vals.units = 'days since 1970-01-01 00:00'
               
    # Create variables.
    for name, props in var.items():
        vals = out_nc.createVariable(props[1]['quantity'], 'f4', props[0], zlib = True, 
                                      fill_value = fill, complevel = 9, 
                                      least_significant_digit = 1)
        vals.setncatts(props[1])

    if attr != None:
        out_nc.setncatts(attr)
    # Close nc-file.
    out_nc.close()


def fill_nc_one_timestep(nc_file, var, time_val = None):
    # Open existing nc-file.
    out_nc = netCDF4.Dataset(nc_file, 'r+')
    varis = out_nc.variables.keys()
    dimis = out_nc.dimensions.keys()
    
    # Add time-dependent data to nc-file.
    if time_val is not None:
        time = out_nc.variables['time']
        tidx = time.shape
        time[tidx] = time_val
        
        for name in [x for x in varis if "time" in out_nc[x].dimensions and x not in dimis]:
            field = out_nc.variables[name]
            
            if name in var.keys():
                field[tidx,...] = var[name]
                
            else:
                shape = tuple([y for x, y in enumerate(out_nc[name].shape) if out_nc[name].dimensions[x] != "time"])
                dummy_data = np.ones(shape) * out_nc[name]._FillValue
                field[tidx,...] = dummy_data
    
    # Add invariant data to nc-file.
    else:
         for name, data in var.items():
            out_nc.variables[name][0::] = data
            
    # Close nc-file.
    out_nc.close()

# def re_index_with_tolerance(f, chunks, ds_first):
#     with rio.open_rasterio(f, chunks=chunks) as da:
#         ds = da.reindex_like(ds_first, method='nearest', tolerance=1e-7)
#         # _, ds = xr.align(ds_first, ds, join='override') ## This also works but tolerance is not cosidred, Id dims asre the same
#         da.close()
#         del da
#     return ds


