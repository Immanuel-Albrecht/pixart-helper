#!/usr/bin/env python3
# those modules should be present in any python3
import sys
import os
import zipfile
import re


# non-standard python modules
try:
    import xmltodict
    from PIL import Image, ImageSequence
    import numpy as np
except ModuleNotFoundError:
    print("One or more required packages are missing. Try running:")
    print("   python3 -m pip install --user xmltodict Pillow numpy")
    sys.exit(1)
    
if "--help" in sys.argv or "-help" in sys.argv or "/?" in sys.argv or "/help" in sys.argv or len(sys.argv) < 2:
    print(f"""Usage: {sys.argv[0]} ORA_FILE [PNG_FILE [LAYER_SPEC]] 
    
    Converts a png image to a single layer OpenRaster file that is 
    compatible with ora-tool.py.
    
        ORA_FILE    path of the input png file
        PNG_FILE    optionally: path for the output .ora file. 
                    Defaults to 'ORA_FILE.png'
        LAYER_SPEC  optionally: which layers to export? Similar to
                    ora-tool.py layer specification, defaults to
                    +@.*
    """.replace("\t","    "))
    sys.exit(0)

in_path = sys.argv[1]
if len(sys.argv) > 2:
    out_path = sys.argv[2]
else:
    out_path = in_path+".png"

if len(sys.argv) > 3:
    layerspec = sys.argv[3]
else:
    layerspec = "+@.*"


### COPY-PASTA FROM ora-tool ###

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

def img_to_np(fp):
    """
        reads an image from the file handle and returns it as an numpy array
    """
    img = Image.open(fp)
    imga = np.asarray(img)
    return npa_convert_to_rgba(imga)
    
    
def coerce_to_list(x):
    if type(x) == list:
        return x
    return [x]


def load_ora(path):
    """
        Loads an Open Raster image; as it might have been saved by krita or pinta...
    """
    layers = []
    with zipfile.ZipFile(path) as f:
        files = list(f.namelist())
        if 'stack.xml' not in files:
            return None
        info = xmltodict.parse(f.read('stack.xml'))
        layer_names_srcs = list(map(lambda x: (x['@name'],x['@src']), coerce_to_list(info['image']['stack']['layer'])))
        layers = [ (lbl, img_to_np(f.open(src))) for lbl,src in layer_names_srcs]
    return layers
        
def get_matcher_from_str(exp):
    """
        returns a function that takes a string and returns whether it matches or not.
        
        A string may start with '+' or '-' or '!' indicating whether to filter strings that
        match vs strings that do not match ('+' uses images/layers that match, '-' or '!' uses images/layers that
        do not match).
        After '+','-', or '!', there may be a qualifier '=' for exact string matches, 
                                                        '~' for lowercase string matches,
                                                none or '@' for regexp matches (a.k.a. default), and
                                                        '/' for regexp-matching the lowercase of the layer/image name.
    """
    positive = True
    if exp.startswith("+") or exp.startswith("-") or exp.startswith("!"):
        positive = exp[0] == "+"
        exp = exp[1:]
    if exp.startswith("="):
        exp = exp[1:]
        return lambda t,x=exp,p=positive: (t==x) == p
    if exp.startswith("~"):
        exp = exp[1:]
        return lambda t,x=exp.lower(),p=positive: (str(t).lower()==x) == p
    if exp.startswith("/"):
        exp = exp[1:]
        convert = lambda x: str(x).lower()
    else:
        convert = str
        if exp.startswith("@"):
            exp = exp[1:]
    q = re.compile(exp)
    if positive:
        return lambda t,q=q,c=convert: q.match(c(t))
    else:
        return lambda t,q=q,c=convert: not q.match(c(t))

def get_layer_filter_map(filter_exp):
    if type(filter_exp) == type(lambda:0):
        return filter_exp
    if type(filter_exp) == list:
        q = [get_layer_filter_map(x) for x in filter_exp]
        return lambda x,y,q=q: any([f(x,y) for f in q])
    if type(filter_exp) == str:
        q = get_matcher_from_str(filter_exp)
        return lambda x,y,q=q: q(y)
    if type(filter_exp) == int:
        return lambda x,y,q=filter_exp: x == q

def get_layers(image, layers):
    img_layer = []
    layer_filter = get_layer_filter_map(layers)
    for nbr,l in enumerate(image):
        name, imgl = l
        if layer_filter(len(image)-nbr-1,name):
            img_layer.append(imgl)
    return img_layer
    
def merge_layers(layers):
    """
        merges a list of pixel arrays and returns the result as
        RGBA array
    """
    layers = [x if len(x.shape) == 3 and x.shape[-1] == 4 else npa_convert_to_rgba(x) for x in layers ] 
    w = max(map(lambda x: x.shape[1], layers))
    h = max(map(lambda x: x.shape[0], layers))
    output = np.zeros((h,w,4),dtype=np.float)
    for l in layers:
        h,w = l.shape[:2]
        opaqueness = output[0:h,0:w,-1:]
        see_through_left = 255 - opaqueness
        output[0:h,0:w,:-1] = (opaqueness * output[0:h,0:w,:-1] + see_through_left * l[0:h,0:w,:-1]) / 255
        output[0:h,0:w,-1:] = opaqueness + see_through_left * l[0:h,0:w,-1:] / 255
    return (output + .5).astype(np.uint8)

    
### HERE WE GO ###

ora = load_ora(in_path)
    
target_layers = get_layers(ora, layerspec)

output_imga = merge_layers(target_layers)

pimg = Image.fromarray(output_imga)
with open(out_path,"wb") as pf:
    pimg.save(pf,"PNG")
    pf.close()
