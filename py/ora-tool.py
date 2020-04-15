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
else:
    print("Mode {sys.argv[1]} currently not available!")
    sys.exit(1)

sys.exit(0)

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

defaults = {}
defaults["palette"] = ega_palette
defaults["named-palettes"] = {'ega': ega_palette}
defaults["to-nearest-palatte"] = {"file":"default",
                                  "layers":lambda x: True,
                                  "palette":"ega"}
defaults["to-binary-alpha"] = {"file":"default",
                                  "layers":lambda x: True,
                                  "palette":"ega"}



config["palette"] = ega_palette
config["actions"] = ["to_nearest_palette","to_binary_alpha"]
config["input"] = sys.argv[1]
config["output"] = sys.argv[2] if len(sys.argv) > 2 else \
                    os.path.join(os.path.dirname(config["input"]),
                    "ega-"+os.path.basename(config["input"]))
config["threshold"] = 120
config["t0"] = 0
config["t1"] = 255



def img_to_np(fp):
    """
        reads an image from the file handle and returns it as an numpy array
    """
    img = Image.open(fp)
    return np.asarray(img)

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
    
def load_single_layer(path):
    """
        Loads a single layer png :)
    """
    return [("layer0",img_to_np(path))]
    
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



def work(config):
    img = load_ora(config["input"])
    for cmd in config["actions"]:
        if cmd == 'to_nearest_palette':
            img = [(name, to_nearest_palette(layer, palette=config["palette"])) 
                        for name,layer in img]
        elif cmd == 'to_binary_alpha':
            img = [(name, to_binary_alpha(layer, config["threshold"],config["t0"],config["t1"])) 
                        for name,layer in img]
    write_ora(config["output"],img)

for c in todo:
    work(c)
