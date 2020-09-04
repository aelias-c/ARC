import numpy as np
import gzip

from constants import IMS_DIR

r = np.zeros((1024,1024), dtype=int)

with gzip.open(IMS_DIR+'/EMPTY_GZ/empty_file.gz', 'wb') as f:
   f.write(r)

 

