#!/usr/bin/env python3
# those modules should be present in any python3
import sys
import os
import zipfile
import re
from skimage import transform as sit

# non-standard python modules
try:
    import xmltodict
    from PIL import Image, ImageSequence
    import numpy as np
    import yaml
except ModuleNotFoundError:
    print("One or more required packages are missing. Try running:")
    print("   python3 -m pip install --user xmltodict Pillow numpy pyyaml")
    sys.exit(1)
    
# We support different modes of programming this tool

supported_modes = ["yaml","binarize","palettize","pal-bin"]


oplist = sorted(["to-nearest-palette",
          "to-binary-alpha",
          "rm-layers",
          "cp-layers",
          "rotate-layers",
          "flip-layers",
          ])

default_params = {}
param_help = {}
op_help = {}

filter_string_desc = """
    Each filter string may start with up to two option characters, 
    followed by either a plain match string, or a regular expression 
    to be parsed by the 're' module in Python 3.
    
    1st option character:
        '+' or not present: reference string has to match the expression
                            in order to be selected by the filter.
        '-' or '!':         reference string must fail to match the expression
                            in order to be selected by the filter.
                            
    2nd option character:
        '@' or not present: the following string is parsed as a regular
                            expression, the reference string is matched as is.
        '/':                the following string is parsed as a regular
                            expression, the reference string is converted to
                            all lowercase before matching is performed.
        '=':                the following string is a plain string, the
                            reference string is taken as is.
        '~':                the following string is a plain string, the
                            reference string is converted to all lowercase
                            before matching.
"""
images_description = """
    You may provide either a single image description string, or a list of 
    image descriptions strings. If you provide a list, then an image is 
    selected for processing if it is described by at least one of the given 
    strings.""" + filter_string_desc
layers_description = """
    You may either provide a single layer description string, a layer number,
    or a list of layer descriptions strings and layer numbers. If you provide
    a list, then a layer is selected for processing if it is described by at 
    least one of the given strings or numbers.\n""" + filter_string_desc
palette_description = """
    You may either provide a palette as an array of 3-elementary arrays (RGB),
    as an array of 4-elementary arrays (RGBA), or as a string refering to a
    predefined palette. Valid predefined palettes are:
            ega
"""

# to-nearest-palette

default_params["to-nearest-palette"] = {
    "images":"+@.*",
    "layers":"+@.*",
    "palette":"ega",
    "divisor":255
    }

op_help["to-nearest-palette"] = """
    Each pixel in the processed layers is assigned the from the palette that 
    is closest to its original color, leaving the alpha value untouched for
    RGB palettes, and considering the alpha value part of the pixels color
    for RGBA palettes. The distance between the original color and each
    palette color is determined by the Euclidean norm of the channel
    differences divided by the divisor.
"""

param_help["to-nearest-palette"] = {
    "images":images_description,
    "layers":layers_description,
    "palette":palette_description,
    "divisor":"\nThe difference between each original color channel and each\npalette color channel is divided by this value.\n"
}

# to-binary-alpha

default_params["to-binary-alpha"] = {   
    "images":"+@.*",
    "layers":"+@.*",
    "threshold":120,
    "t0":0,
    "t1":255}
    
op_help["to-binary-alpha"] = """
    The alpha value of each pixel in the processed layer is set to either
    a low (t0) or high (t1) value, depending on whether it is less than the
    given threshold.
"""

param_help["to-binary-alpha"] = {
    "images":images_description,
    "layers":layers_description,
    "threshold":"\nThreshold value for the alpha compontent.\n",
    "t0":"\nLow alpha value for pixels with alpha below the threshold.\n",
    "t1":"\nHigh alpha value for pixels with alpha above or equal to the threshold.\n",
}

# rm-layers
default_params["rm-layers"] = {
    "images": "+@.*",
    "layers": "~backdrop",
}

op_help["rm-layers"] = """
    Removes the matching layers from the images in memory.
"""

param_help["rm-layers"] = {
    "images":images_description,
    "layers":layers_description,
}

# cp-layers


default_params["cp-layers"] = {
    "images": "+@.*",
    "layers": "!~backdrop",
    "target": "new-image",
}

op_help["cp-layers"] = """
    Copies the matching layers from the images in memory and puts them on top
    of the layers of the image target.
"""

param_help["cp-layers"] = {
    "images":images_description,
    "layers":layers_description,
    "target":"\nName of the image where the layers shall be copied to. If there\n"+
             "is no image with the given name, a new one is created.\n"
}

# rotate-layers

default_params["rotate-layers"] = {
    "images": "+@.*",
    "layers": "!~backdrop",
    "angle": 12.5,
    "center": [],
    "resize": False,
    "order": 1,
    "mode": "constant",
    "cval": 0.0,
    "clip": True,
}

op_help["rotate-layers"] = """
    Rotates the matching layers in the images in memory.
"""

param_help["rotate-layers"] = {
    "images":images_description,
    "layers":layers_description,
    "angle":"rotation angle in degrees in counter-clockwise direction",
    "center":"determines the rotation center",
    "resize":"boolean, if true, then the layer is extended so that the whole original layer fits in it",
    "order":"order of the spline interpolation, default is 1; integer in the range 0-5",
    "mode": "points outside the boundaries of the input are filled according to the given mode; ‘constant’, ‘edge’, ‘symmetric’, ‘reflect’, or ‘wrap’",
    "cval": "if mode is ‘constant’, then this is the value of the outside pixels",
    "clip": "boolean, if true, clip the output to the range of values of the input"
}

# flip-layers

default_params["flip-layers"] = {
    "images": "+@.*",
    "layers": "!~backdrop",
    "axis": "horizontal",
}

op_help["flip-layers"] = """
    Flips (mirror image) the matching layers in the images in memory.
"""

param_help["flip-layers"] = {
    "images":images_description,
    "layers":layers_description,
    "axis":"either 'horizontal' or 'vertical'",
}


if len(sys.argv) > 1 and sys.argv[1] == "help":
    if len(sys.argv) < 3 or not sys.argv[2] in supported_modes+["ops","op","parameter"]:
        print(f"Usage: {sys.argv[0]} help MODE")
        print(f" where MODE may be one of the following:\n\n {', '.join(supported_modes)}")
    else:
        mode = sys.argv[2]
        if mode == "ops":
            print("The following operations are supported:\n   "+'\n   '.join(oplist))
            print("You may obtain further information on these operations with")
            print(f"   {sys.argv[0]} help op [item-from-the-list-above]")
        elif mode == "op":
            if len(sys.argv) < 4 or not sys.argv[3] in oplist:
                print(f"Usage: {sys.argv[0]} help op [op-name]")
                print("  where [op-name] is one of the following:")
                print("        "+"\n        ".join(oplist))
            else:
                opname = sys.argv[3]
                print(f"{opname}\n{'='*len(opname)}\n{op_help[opname]}")
                print(f"Example yaml of call with default parameters:\n")
                opmap = {'ora-tool':{'input':{'default':'/path/to/input.ora'},
                                     'output':{'default':'/path/to/output.ora'},
                                     'ops':[{opname:default_params[opname]}]}}
                print(yaml.dump(opmap,default_flow_style = False, allow_unicode = True))
                print(f"\nIn order to get help on each parameter, use\n   {sys.argv[0]} help parameter {opname} [parameter]\n")
                print(f"  where [parameter] is one of the following:")
                print( "        " + "\n        ".join(sorted(param_help[opname].keys())))
        elif mode == "parameter":
                if len(sys.argv) < 4 or not sys.argv[3] in oplist:
                    print(f"Usage: {sys.argv[0]} help parameter [op-name] [parameter]")
                    print("  where [op-name] is one of the following:")
                    print("        "+"\n        ".join(oplist))
                elif len(sys.argv) < 5 or not sys.argv[4] in param_help[sys.argv[3]]:
                    print(f"Usage: {sys.argv[0]} help parameter {sys.argv[3]} [parameter]")
                    print("  where [parameter] is one of the following:")
                    print("        "+"\n        ".join(sorted(param_help[sys.argv[3]].keys())))
                else:
                    print(f"Parameter {sys.argv[4]} of {sys.argv[3]}")
                    print("="*(len("Parameter  of ")+len(sys.argv[3])+len(sys.argv[4])))
                    print(param_help[sys.argv[3]][sys.argv[4]])
                    print("default: ")
                    print("     "+yaml.dump({sys.argv[4]:default_params[sys.argv[3]][sys.argv[4]]},default_flow_style = False, allow_unicode = True).replace("\n","\n     "))

        elif mode == "yaml":
            print(f"Usage: {sys.argv[0]} yaml [yaml-paths]")
            print(" where [yaml-paths] may be a sequence of paths to yaml files.")
            print(" If the sequence of paths is empty, then the yaml is read from stdin.")
            print("")
            print("Each yaml document is traversed for dictionaries that have a key named")
            print("'ora-tool'. The contents of these keys are supposed to be maps that")
            print("describe what the tool should do. Each such map should define the following")
            print("three keys: 'input', 'output', and 'ops'.\n")
            print("'input' and 'output' may either be a single string, a map, or a list of")
            print("strings, which determines which OpenRaster files to load the internal named")
            print("images from or store the internal named images to, before and after processing,")
            print("respectively. A map maps the internal image name to the file paths, whereas a")
            print("single string is considered to map the internal name 'default'. A list of")
            print("strings is considered to map the internal names 'default', 'default1',")
            print("'default2', and so on.\n")
            print("The 'ops' key defines which operations shall be carried out on the loaded")
            print("images. It may consist of a single operation or a list of operations, and")
            print("each operation may be either given as a string -- thus using all default")
            print("parameters -- or as a map where the key is the name of the operation which")
            print("maps to a map of parameters that override the operations defaults.")
            print(f"You may use \n    {sys.argv[0]} help ops \nin order to obtain a list of supported operations.")
            
        else:
            print(f"Unfortunately, the help on {mode} is currently not available.")
    sys.exit(0)

if len(sys.argv) < 2 or not sys.argv[1] in supported_modes:
    print(f"Usage: {sys.argv[0]} MODE [...]")
    print(f" where MODE may be one of the following:\n  {', '.join(supported_modes)}")
    print(f"\nYou may use   {sys.argv[0]} help MODE   to get more information on each mode.")
    print(f"\nYou may use   {sys.argv[0]} help ops    to get more information on available operations.")
    sys.exit(1)

todo = []

def find_all_ora_tool_dicts(y):
    found = []
    if type(y) == dict:
        for x in y:
            if x == "ora-tool":
                found.append(y[x])
            else:
                found.extend( find_all_ora_tool_dicts(y[x]))
    elif type(y) == list:
        for x in y:
            found.extend(find_all_ora_tool_dicts(x))
    return found

if sys.argv[1] == "yaml":
    parts = []
    if len(sys.argv) > 2:
        for p in sys.argv[2:]:
            with open(p,"r",encoding="utf-8") as fy:
                for part in yaml.load_all(fy):
                    parts.append(part)
    else:
        for part in yaml.load_all(sys.stdin):
            parts.append(part)
    for part in parts:
        todo.extend(find_all_ora_tool_dicts(part))
elif sys.argv[1] == "palettize":
    if len( sys.argv ) < 3:
        print(f"To find out about the usage, call {sys.argv[0]} help {sys.argv[1]}.")
        sys.exit(1)
    inpath = sys.argv[2]
    if len(sys.argv) > 3:
        outpath = sys.argv[3]
    else:
        outpath = os.path.join(os.path.dirname(inpath),"ega-"+os.path.basename(inpath))
    todo = [{'input': inpath,
             'output': outpath,
             'ops':'to-nearest-palette'}]
elif sys.argv[1] == "binarize":
    if len( sys.argv ) < 3:
        print(f"To find out about the usage, call {sys.argv[0]} help {sys.argv[1]}.")
        sys.exit(1)
    inpath = sys.argv[2]
    if len(sys.argv) > 3:
        outpath = sys.argv[3]
    else:
        outpath = os.path.join(os.path.dirname(inpath),"a-"+os.path.basename(inpath))
    todo = [{'input': inpath,
             'output': outpath,
             'ops':'to-binary-alpha'}]
elif sys.argv[1] == "pal-bin":
    if len( sys.argv ) < 3:
        print(f"To find out about the usage, call {sys.argv[0]} help {sys.argv[1]}.")
        sys.exit(1)
    inpath = sys.argv[2]
    if len(sys.argv) > 3:
        outpath = sys.argv[3]
    else:
        outpath = os.path.join(os.path.dirname(inpath),"ega-a-"+os.path.basename(inpath))
    todo = [{'input': inpath,
             'output': outpath,
             'ops':['to-nearest-palette','to-binary-alpha','rm-layers']}]
else:
    print("Mode {sys.argv[1]} currently not available!")
    sys.exit(1)

ega_palette = np.array([ [int(x[i*2]+x[i*2+1],base=16) for i in range(3)] for x in
                            map(lambda x: x.strip(), """000000
                                                    0000AA
                                                    00AA00
                                                    00AAAA
                                                    AA0000
                                                    AA00AA
                                                    AA5500
                                                    AAAAAA
                                                    555555
                                                    5555FF
                                                    55FF55
                                                    55FFFF
                                                    FF5555
                                                    FF55FF
                                                    FFFF55
                                                    FFFFFF""".split("\n"))])

named_palettes = {'ega': ega_palette}



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
        layer_names_srcs = list(map(lambda x: (x['@name'],x['@src']), info['image']['stack']['layer']))
        layers = [ (lbl, img_to_np(f.open(src))) for lbl,src in layer_names_srcs]
    return layers
    
def load_single_layer(path,name="default"):
    """
        Loads a single layer png :)
    """
    return [(name,img_to_np(path))]
    
def write_ora(path,layers):
    w = max([x[1].shape[1] for x in layers] )
    h = max([x[1].shape[0] for x in layers] )
    L0 = len(layers) - 1
    stackxml = f'<image w="{w}" h="{h}">' + "\n"
    stackxml += '  <stack opacity="1" name="root">\n'
    l0 = L0
    for name, _ in layers:
        stackxml += f'    <layer opacity="1.00" name="{name}" composite-op="svg:src-over" src="data/layer{l0}.png" />' + "\n"
        l0 -= 1
    stackxml += '  </stack>\n'
    stackxml += "</image>"
    with zipfile.ZipFile(path,"w",compression=zipfile.ZIP_DEFLATED) as f:
        f.writestr("mimetype","image/openraster")
        f.writestr("stack.xml",stackxml)
        l0 = L0
        for _, img in layers:
            lpath = f"data/layer{l0}.png"
            pimg = Image.fromarray(img)
            with f.open(lpath,"w") as pf:
                pimg.save(pf,"PNG")
                pf.close()
            l0 -= 1
        # add a merged image
        merged_img = merge_layers([img for lbl,img in layers])
        lpath = f"mergedimage.png"
        pimg = Image.fromarray(merged_img)
        with f.open(lpath,"w") as pf:
            pimg.save(pf,"PNG")
            pf.close()
        if w > h:
            tw = 32
            th = int(h*tw/w+.5)
        else:
            th = 32
            tw = int(w*th/h+.5)
        # and even a real thumbnail so Pinta's file open menu works now
        thumb_img = (sit.resize(merged_img/255.,(th,tw,4),mode='reflect',order=1,anti_aliasing=True)*255).astype(np.uint8)
        with f.open("Thumbnails/thumbnail.png","w") as pf:
            thimg = Image.fromarray(thumb_img)
            thimg.save(pf,"PNG")
            pf.close()
        f.close()

    
def to_nearest_palette(img, palette = ega_palette, divisor=255):
    shape = img.shape
    channels = shape[-1]
    dims = shape[:-1]
    if channels == ega_palette.shape[-1] + 1:
        has_alpha = True
    else:
        has_alpha = False
    linear = 1
    for x in dims:
        linear *= x
    img0 = np.copy(img.reshape((linear, channels)))
    for i in range(linear):
        if has_alpha:
            x = img0[i][:-1]
        else:
            x = img0[i]
        distances = [np.sqrt(np.sum(((x - p)/divisor)**2)) for p in palette]
        d0 = min(distances)
        x = palette[distances.index(d0)]
        if has_alpha:
            img0[i][:-1] = x
        else:
            img0[i] = x
        
    return img0.reshape(shape)
    
def to_binary_alpha(img, threshold=120, t0=0,t1=255):
    shape = img.shape
    channels = shape[-1]
    dims = shape[:-1]
    if channels == ega_palette.shape[-1] + 1:
        has_alpha = True
    else:
        has_alpha = False
    linear = 1
    for x in dims:
        linear *= x
    img0 = np.copy(img.reshape((linear, channels)))
    if has_alpha:
        for i in range(linear):
            img0[i][-1] = t0 if img0[i][-1] < threshold else t1
            
    return img0.reshape(shape)

def transform_input_output_to_dict(x):
    if type(x) == dict:
        return x
    if type(x) == list:
        d = {}
        for nbr,p in enumerate(x):
            if nbr == 0:
                d["default"] = p
            else:
                d[f"default{nbr}"] = p
        return d
    return {'default':x}
    
def as_boolean(x):
    if type(x) == bool:
        return x
    if type(x) == str:
        return x in ["y","Y","yes","YES","Yes","True","true","TRUE","ON","on","On"]
    if x:
        return True
    return False
    
def transform_ops(x):
    if type(x) != list:
        x = [x]
    ops = []
    for op in x:
        if type(op) == dict:
            for k in op:
                if not k in oplist:
                    print(f"WARNING: ignoring unknown op {k}.")
                    continue
                params = default_params[k].copy()
                if type(op[k]) == dict:
                    for kk in op[k]:
                        params[kk] = op[k][kk]
                ops.append((k, params))
        elif type(op) == list:
            for k in op:
                if not k in oplist:
                    print(f"WARNING: ignoring unknown op {k}.")
                    continue
                params = default_params[k].copy()
                ops.append((k, params))
        else:
            k = op
            if not k in oplist:
                print(f"WARNING: ignoring unknown op {k}.")
                continue
            params = default_params[k].copy()
            ops.append((k, params))
    return ops

def get_palette(palette):
    if str(palette) in named_palettes:
        return named_palettes[str(palette)]
    if type(palette) == np.ndarray:
        return palette
    return np.array(palette, dtype=np.uint8)
    
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
    
def get_image_filter_map(filter_exp):
    if type(filter_exp) == type(lambda:0):
        return filter_exp
    if type(filter_exp) == list:
        q = [get_image_filter_map(x) for x in filter_exp]
        return lambda x,q=q: any([f(x) for f in q])
    if type(filter_exp) == str:
        return get_matcher_from_str(filter_exp)
        
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
    
def get_center(x):
    """ convert x to value for center parameter in transformations """
    if type(x) == list:
        if len(x) == 2:
            return np.array(x, dtype=np.float)
        else:
            return None
    elif type(x) == str:
        return np.array(x.split(","), dtype=np.float)
    else:
        return None

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

def get_image_layers(data, images, layers):
    img_layer = []
    img_filter = get_image_filter_map(images)
    layer_filter = get_layer_filter_map(layers)
    for k in data:
        if img_filter(k):
            for nbr,l in enumerate(data[k]):
                name, _ = l
                if layer_filter(len(data[k])-nbr-1,name):
                    img_layer.append((k, nbr))
    return img_layer

def work(task):
    global data
    data = {}
    i = transform_input_output_to_dict(task["input"])
    o = transform_input_output_to_dict(task["output"])
    for k in i:
        print(f"LOAD: '{i[k]}' as image '{k}'.")
        data[k] = load_ora(i[k])
        
    for op, params in transform_ops(task["ops"]):
        print(f"OP: {op}")
        for k in params:
            print(f"  {k} = {params[k]}")
        if op == 'to-nearest-palette':
            p = get_palette(params["palette"])
            for k,idx in get_image_layers(data,params["images"],params["layers"]):
                lbl,img = data[k][idx]
                print(f"    ..applying to layer '{k}':{len(data[k])-idx-1} labelled '{data[k][idx][0]}'")
                img = to_nearest_palette(img, palette=p,divisor=float(params["divisor"]))
                data[k][idx] = (lbl, img)
        elif op == 'to-binary-alpha':
            thr = int(params["threshold"])
            t0 = int(params["t0"])
            t1 = int(params["t1"])
            for k,idx in get_image_layers(data,params["images"],params["layers"]):
                lbl,img = data[k][idx]
                print(f"    ..applying to layer '{k}':{len(data[k])-idx-1} labelled '{data[k][idx][0]}'")
                img = to_binary_alpha(img,thr,t0,t1)
                data[k][idx] = (lbl, img)
        elif op == "rm-layers":
            remove_layers = get_image_layers(data,params["images"],params["layers"])
            for k,idx in sorted(set(remove_layers),key=lambda x: (x[0],-x[1])):
                print(f"    ..dropping layer '{k}':{len(data[k])-idx-1} labelled '{data[k][idx][0]}'")
                data[k] = data[k][:idx] + data[k][idx+1:]
        elif op == "cp-layers":
            copied_layers = []
            for k,idx in get_image_layers(data,params["images"],params["layers"]):
                copied_layers.append(data[k][idx])
                print(f"    ..copying layer '{k}':{len(data[k])-idx-1} labelled '{data[k][idx][0]}'")
            target_img = params["target"]
            if copied_layers == []:
                print(f"    ..WARNING: no layer has been copied")
            if not target_img in data:
                    data[target_img] = copied_layers
            else:
                data[target_img] = copied_layers + data[target_img]
        elif op == 'rotate-layers':
            center = get_center(params["center"])
            resize = as_boolean(params["resize"])
            angle = float(params["angle"])
            mode = str(params["mode"])
            cval = np.array(params["cval"],dtype=np.float)
            clip = as_boolean(params["clip"])
            order = int(params["order"])
            for k,idx in get_image_layers(data,params["images"],params["layers"]):
                lbl,img = data[k][idx]
                print(f"    ..applying to layer '{k}':{len(data[k])-idx-1} labelled '{data[k][idx][0]}'")
                img = sit.rotate(img, angle, resize=resize, center=center,mode=mode, order=order, clip=clip, cval=cval, preserve_range=True)
                img = img.astype(np.uint8)
                data[k][idx] = (lbl, img)
        elif op == 'flip-layers':
            axis = 1 if str(params["axis"]) == "horizontal" else 0
            for k,idx in get_image_layers(data,params["images"],params["layers"]):
                    lbl,img = data[k][idx]
                    print(f"    ..applying to layer '{k}':{len(data[k])-idx-1} labelled '{data[k][idx][0]}'")
                    img = np.flip(img, axis=axis)
                    data[k][idx] = (lbl, img)

    for k in o:
        print(f"STORE: image '{k}' to '{o[k]}'.")
        write_ora(o[k],data[k])

for task in todo:
    work(task)
