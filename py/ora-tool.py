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
    import yaml
except ModuleNotFoundError:
    print("One or more required packages are missing. Try running:")
    print("   python3 -m pip install --user xmltodict Pillow numpy pyyaml")
    sys.exit(1)
    
# We support different modes of programming this tool

supported_modes = ["yaml","binarize","palettize","bin-pal"]

if len(sys.argv) > 1 and sys.argv[1] == "help":
    if len(sys.argv) < 3 or not sys.argv[2] in supported_modes:
        print(f"Usage: {sys.argv[0]} help MODE")
        print(f" where MODE may be one of the following:\n\n {', '.join(supported_modes)}")
    else:
        mode = sys.argv[2]
        if mode == "yaml":
            print(f"Usage: {sys.argv[0]} yaml [yaml-paths]")
            print(" where [yaml-paths] may be a sequence of paths to yaml files.")
            print(" If the sequence of paths is empty, then the yaml is read from stdin.")
        else:
            print(f"Unfortunately, the help on {mode} is currently not available.")
    sys.exit(1)

if len(sys.argv) < 2 or not sys.argv[1] in supported_modes:
    print(f"Usage: {sys.argv[0]} MODE [...]")
    print(f" where MODE may be one of the following:\n  {', '.join(supported_modes)}")
    print(f"\nYou may use {sys.argv[0]} help MODE to get more information on each mode.")
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
elif sys.argv[1] == "binarize":
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
             'ops':['to-nearest-palette','to-binary-alpha']}]
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

use_all = lambda x,y=0: True

default_params = {}

default_params["to-nearest-palette"] = {
    "images":use_all,
    "layers":use_all,
    "palette":"ega",
    }
    
default_params["to-binary-alpha"] = {   
    "images":use_all,
    "layers":use_all,
    "threshold":120,
    "t0":0,
    "t1":255}



def img_to_np(fp):
    """
        reads an image from the file handle and returns it as an numpy array
    """
    img = Image.open(fp)
    imga = np.asarray(img)
    # the following is an odd bid to cope with non RGBA images...
    if imga.dtype != np.uint8:
        imga = imga
        imga = imga / imga.max() #normalizes data in range 0 - 255
        imga = 255 * imga
        imga = imga.astype(np.uint8)
    if len(imga.shape) == 2: # greyscale image
        alpha = np.ones(imga.shape,dtype='uint8')*255
        imga = np.stack([imga,imga,imga,alpha],axis=-1)
    elif imga.shape[-1] == 3: # alpha missing
        alpha = np.ones(imga.shape[:-1]+(1,),dtype='uint8')*255
        imga = np.concatenate([imga,alpha],axis=-1)
    return imga

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
        # We have to put a fake thumbnail into the .ora file so that we do not get errors when selecting the
        # file in Pinta's open-menu ...
        with f.open("Thumbnails/thumbnail.png","w") as pf:
            thimg = Image.fromarray(np.zeros((1,1,4),dtype='uint8'))
            thimg.save(pf,"PNG")
            pf.close()
        l0 = L0
        for _, img in layers:
            lpath = f"data/layer{l0}.png"
            pimg = Image.fromarray(img)
            with f.open(lpath,"w") as pf:
                pimg.save(pf,"PNG")
                pf.close()
            l0 -= 1
        f.close()

    
def to_nearest_palette(img, palette = ega_palette):
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
        distances = [np.sqrt(np.sum((x - p)**2)) for p in palette]
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
    

oplist = ["to-nearest-palette","to-binary-alpha"]
    
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
    if palette in named_palettes:
        return named_palettes[palette]
    if type(palette) == np.ndarray:
        return palette
    return np.array(palette, dtype="uint8")
    
def get_image_filter_map(filter_exp):
    if type(filter_exp) == type(lambda:0):
        return filter_exp
    if type(filter_exp) == list:
        q = [get_image_filter_map(x) for x in filter_exp]
        return lambda x,q=q: any([f(x) for f in q])
    if type(filter_exp) == str:
        q = re.compile(filter_exp)
        return lambda x,q=q: q.match(x)

def get_layer_filter_map(filter_exp):
    if type(filter_exp) == type(lambda:0):
        return filter_exp
    if type(filter_exp) == list:
        q = [get_layer_filter_map(x) for x in filter_exp]
        return lambda x,y,q=q: any([f(x,y) for f in q])
    if type(filter_exp) == str:
        q = re.compile(filter_exp)
        return lambda x,y,q=q: q.match(y)
    if type(filter_exp) == int:
        return lambda x,y,q=filter_exp: x == q

def get_image_layers(data, images, layers):
    img_layer = []
    img_filter = get_image_filter_map(images)
    layer_filter = get_layer_filter_map(layers)
    for k in data:
        if img_filter(k):
            for nbr,l in enumerate(data[k]):
                name, img = l
                if layer_filter(len(data[k])-nbr-1,name):
                    img_layer.append((k, nbr))
    return img_layer

def work(task):
    data = {}
    i = transform_input_output_to_dict(task["input"])
    o = transform_input_output_to_dict(task["output"])
    for k in i:
        data[k] = load_ora(i[k])
        
    for op, params in transform_ops(task["ops"]):
        print(f"OP: {op}")
        for k in params:
            print(f"  {k} = {params[k]}")
        if op == 'to-nearest-palette':
            p = get_palette(params["palette"])
            for k,idx in get_image_layers(data,params["images"],params["layers"]):
                lbl,img = data[k][idx]
                img = to_nearest_palette(img, palette=p)
                data[k][idx] = (lbl, img)
        elif op == 'to-binary-alpha':
            thr = int(params["threshold"])
            t0 = int(params["t0"])
            t1 = int(params["t1"])
            for k,idx in get_image_layers(data,params["images"],params["layers"]):
                lbl,img = data[k][idx]
                img = to_binary_alpha(img,thr,t0,t1)
                data[k][idx] = (lbl, img)
            
    for k in o:
        write_ora(o[k],data[k])

for task in todo:
    work(task)
