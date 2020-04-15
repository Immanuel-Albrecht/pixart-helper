#!/usr/bin/env python3
import sys
import os
import zipfile
try:
    import xmltodict
    from PIL import Image, ImageSequence
    import numpy as np
except ModuleNotFoundError:
    print("One or more required packages are missing. Try running:")
    print("   python3 -m pip install --user xmltodict Pillow numpy")
    sys.exit(1)

if not len(sys.argv) in [2,3]:
    print(f"Usage: {sys.argv[0]} INPUT [OUTPUT]\n")
    print("   where INPUT   is the path to an .ora (Open Raster) image")
    print("     and OUTPUT  is the path where the palettized image shall be put to,")
    print("                 this defaults to 'ega-$INPUT'.")
    sys.exit(1)

config = {}

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

config["palette"] = ega_palette
config["actions"] = ["to_nearest_palette","to_binary_alpha"]
config["input"] = sys.argv[1]
config["output"] = sys.argv[2] if len(sys.argv) > 2 else \
                    os.path.join(os.path.dirname(config["input"]),
                    "ega-"+os.path.basename(config["input"]))
config["threshold"] = 120
config["t0"] = 0
config["t1"] = 255

todo = [config]


def img_to_np(fp):
    img = Image.open(fp)
    return np.asarray(img)

def load_ora(path):
    layers = []
    with zipfile.ZipFile(path) as f:
        files = list(f.namelist())
        if 'stack.xml' not in files:
            return None
        info = xmltodict.parse(f.read('stack.xml'))
        layer_names_srcs = list(map(lambda x: (x['@name'],x['@src']), info['image']['stack']['layer']))
        layers = [ (lbl, img_to_np(f.open(src))) for lbl,src in layer_names_srcs]
    return layers
    
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
