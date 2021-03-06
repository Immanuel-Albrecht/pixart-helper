#!/usr/bin/env python3
# those modules should be present in any python3
import sys
import os
import zipfile
import re


# non-standard python modules
try:
    from PIL import Image, ImageSequence
    import numpy as np
    from skimage import transform as sit
except ModuleNotFoundError:
    print("One or more required packages are missing. Try running:")
    print("   python3 -m pip install --user xmltodict Pillow numpy scikit-image")
    sys.exit(1)
    
if "--help" in sys.argv or "-help" in sys.argv or "/?" in sys.argv or "/help" in sys.argv or len(sys.argv) < 2:
    print(f"""Usage: {sys.argv[0]} PNG_FILE [ORA_FILE] 
    
    Converts a png image to a single layer OpenRaster file that is 
    compatible with ora-tool.py.
    
        PNG_FILE    path of the input png file
        ORA_FILE    optionally: path for the output .ora file. 
                    Defaults to 'PNG_FILE.ora'
    """.replace("\t","    "))
    sys.exit(0)
    
in_path = sys.argv[1]
out_path = in_path + ".ora"
if len(sys.argv) > 2:
    out_path = sys.argv[2]
    
def npa_convert_to_rgba(imga):
    """
        single point of conversion for the different pixel formats ...
        it's a hack, though.
    """
    # the following is an odd bid to cope with non RGBA images...
    if imga.dtype != np.uint8:
        imga = imga
        imga = imga / imga.max() #normalizes data in range 0 - 255
        imga = 255 * imga
        imga = imga.astype(np.uint8)
    if len(imga.shape) == 3 and imga.shape[-1] == 1:
        imga = imga.reshape(imga.shape[:-1])
    if len(imga.shape) == 2: # greyscale image
        alpha = np.ones(imga.shape,dtype='uint8')*255
        imga = np.stack([imga,imga,imga,alpha],axis=-1)
    elif imga.shape[-1] == 3: # alpha missing
        alpha = np.ones(imga.shape[:-1]+(1,),dtype='uint8')*255
        imga = np.concatenate([imga,alpha],axis=-1)
    return imga

    
with open(in_path,"rb") as fp:
    img = Image.open(fp)
    imga = npa_convert_to_rgba(np.asarray(img))

h = imga.shape[0]
w = imga.shape[1]

stackxml = f'<image w="{w}" h="{h}">' + "\n"
stackxml += '  <stack opacity="1" name="root">\n'
stackxml += f'    <layer opacity="1.00" name="default" composite-op="svg:src-over" src="data/layer0.png" />' + "\n"
stackxml += '  </stack>\n'
stackxml += "</image>"

with zipfile.ZipFile(out_path,"w",compression=zipfile.ZIP_DEFLATED) as f:
    f.writestr("mimetype","image/openraster")
    f.writestr("stack.xml",stackxml)    
    pimg = Image.fromarray(imga)
    with f.open("data/layer0.png","w") as pf:
        pimg.save(pf,"PNG")
        pf.close()
    with f.open("mergedimage.png","w") as pf:
        pimg.save(pf,"PNG")
        pf.close()
    if w > h:
        tw = 32
        th = int(h*tw/w+.5)
    else:
        th = 32
        tw = int(w*th/h+.5)

    thumb_img = (sit.resize(imga/255.,(th,tw,imga.shape[2]),mode='reflect',order=1,anti_aliasing=True)*255).astype(np.uint8)
    with f.open("Thumbnails/thumbnail.png","w") as pf:
        thimg = Image.fromarray(thumb_img)
        thimg.save(pf,"PNG")
        pf.close()

    f.close()
