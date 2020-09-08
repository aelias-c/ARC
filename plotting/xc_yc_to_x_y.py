import numpy as np

### For IMS data

# https://github.com/aelias-c/SCD_project/blob/1a5eb5100ee88bf9968b54a7570693c0422f6b1b/SCD_anomaly_calc.py#L92
ALEKSANDRA_SLICE = np.index_exp[158:867]

# details from https://nsidc.org/data/g02156#ancillary
IMS_24KM_UL_CORNER = (-12126597.0, 12126840.0) # note that this is the corner, not the center-of-pixel!
IMS_24KM_RES = 23684.997
IMS_24KM_GRID_SIZE = 1024

# establishing upper-right and lower-left grid-cell-corners for array-generation
IMS_24KM_UR_CORNER = (
    IMS_24KM_UL_CORNER[0] + IMS_24KM_RES + (IMS_24KM_GRID_SIZE * IMS_24KM_RES),
    IMS_24KM_UL_CORNER[1]
)
IMS_24KM_LL_CORNER = (
    IMS_24KM_UL_CORNER[0],
    IMS_24KM_UL_CORNER[1] - IMS_24KM_RES - (IMS_24KM_GRID_SIZE * IMS_24KM_RES)
)

# from upper-left center-of-pixel (need to add/subtract half a grid cell)
IMS_24KM_X_CENTERS = np.arange(
    IMS_24KM_UL_CORNER[0] + IMS_24KM_RES * 0.5,
    IMS_24KM_UR_CORNER[0] - IMS_24KM_RES * 0.5,
    IMS_24KM_RES
)
# from lower-left center-of-pixel
IMS_24KM_Y_CENTERS = np.arange(
    IMS_24KM_LL_CORNER[1] + IMS_24KM_RES * 0.5,
    IMS_24KM_UL_CORNER[1] - IMS_24KM_RES * 0.5,
    IMS_24KM_RES
)

### For CMC data
# details from https://khufkens.com/2014/07/24/georeferencing-daily-snow-depth-analysis-data/
# and https://nsidc.org/data/nsidc-0447
CMC_24KM_UL_CORNER = (-8405812.0, 8405812.0) # note that this is the corner, not the center-of-pixel!
CMC_24KM_RES = 23812.499
CMC_24KM_GRID_SIZE = 706

# establishing upper-left and lower-left grid-cell-corners for array-generation
CMC_24KM_UR_CORNER = (
    CMC_24KM_UL_CORNER[0] + CMC_24KM_RES + (CMC_24KM_GRID_SIZE * CMC_24KM_RES),
    CMC_24KM_UL_CORNER[1]
)
CMC_24KM_LL_CORNER = (
    CMC_24KM_UL_CORNER[0],
    CMC_24KM_UL_CORNER[1] - CMC_24KM_RES - (CMC_24KM_GRID_SIZE * CMC_24KM_RES)
)

# from upper-left center-of-pixel (need to add/subtract half a grid cell)
CMC_24KM_X_CENTERS = np.arange(
    CMC_24KM_UL_CORNER[0] + CMC_24KM_RES * 0.5,
    CMC_24KM_UR_CORNER[0] - CMC_24KM_RES * 0.5,
    CMC_24KM_RES
)
# from lower-left center-of-pixel
CMC_24KM_Y_CENTERS = np.arange(
    CMC_24KM_LL_CORNER[1] + CMC_24KM_RES * 0.5,
    CMC_24KM_UL_CORNER[1] - CMC_24KM_RES * 0.5,
    CMC_24KM_RES
)

def convert_xc_yc_to_meters_IMS(xarray_dataset, index_slice=ALEKSANDRA_SLICE):
    '''
    Add new coordinates containing Polar-Stereographic x/y in meters
    note that in xarray.plot.contourf you will need to specify x='xc', y='yc'
    '''
    x = IMS_24KM_X_CENTERS[index_slice]
    y = IMS_24KM_Y_CENTERS[index_slice]
    ds = xarray_dataset.assign_coords({
        'xc': x, 'yc': y
    })
    return ds

def convert_xc_yc_to_meters_CMC(xarray_dataset):
   ''' 
   Add new coordinates containing Polar-Stereographic x/y in meters 
   note that in xarray.plot.contourf you will need to specify x='xc', y='yc'
   '''
   x = CMC_24KM_X_CENTERS
   y = CMC_24KM_Y_CENTERS[::-1] #need to fix an earlier transposition to get rid of this inversion

   ds = xarray_dataset.assign_coords({'xc':x, 'yc':y})
   return ds
