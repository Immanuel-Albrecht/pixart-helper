pixart-helper
=============

Helper tools for creating pixel art animations.


ora-tool.py
-----------

This tool allows you to automate routine manipulations of OpenRaster (.ora) files through YAML scripts. Information on available operations and their parameters may be obtained through the command line. (You should do this to get the latest information, for convenience, here is some copy&paste of the help screens.)

### general usage

```
> ./ora-tool.py

Usage: ./ora-tool.py MODE [...]
 where MODE may be one of the following:
  yaml, binarize, palettize, pal-bin

You may use   ./ora-tool.py help MODE   to get more information on each mode.

You may use   ./ora-tool.py help ops    to get more information on available operations.
```
### apply yaml file

```
> ./ora-tool.py help yaml

Usage: ./ora-tool.py yaml [yaml-paths]
 where [yaml-paths] may be a sequence of paths to yaml files.
 If the sequence of paths is empty, then the yaml is read from stdin.

Each yaml document is traversed for dictionaries that have a key named
'ora-tool'. The contents of these keys are supposed to be maps that
describe what the tool should do. Each such map should define the following
three keys: 'input', 'output', and 'ops'.

'input' and 'output' may either be a single string, a map, or a list of
strings, which determines which OpenRaster files to load the internal named
images from or store the internal named images to, before and after processing,
respectively. A map maps the internal image name to the file paths, whereas a
single string is considered to map the internal name 'default'. A list of
strings is considered to map the internal names 'default', 'default1',
'default2', and so on.

The 'ops' key defines which operations shall be carried out on the loaded
images. It may consist of a single operation or a list of operations, and
each operation may be either given as a string -- thus using all default
parameters -- or as a map where the key is the name of the operation which
maps to a map of parameters that override the operations defaults.
You may use 
    ./ora-tool.py help ops 
in order to obtain a list of supported operations.
```
### available operations

```
> ./ora-tool.py help ops

The following operations are supported:
   cp-layers
   flip-layers
   merge-layers
   move-layers
   rm-layers
   rotate-layers
   to-binary-alpha
   to-nearest-palette
You may obtain further information on these operations with
   ./ora-tool.py help op [item-from-the-list-above]
```

### cp-layers

```
> ./ora-tool.py help op cp-layers
cp-layers
=========

    Copies the matching layers from the images in memory and puts them on top
    of the layers of the image target.

Example yaml of call with default parameters:

ora-tool:
  input:
    default: /path/to/input.ora
  ops:
  - cp-layers:
      images: +@.*
      layers: '!~backdrop'
      target: new-image
  output:
    default: /path/to/output.ora


In order to get help on each parameter, use
   ./ora-tool.py help parameter cp-layers [parameter]

  where [parameter] is one of the following:
        images
        layers
        target

> ./ora-tool.py help parameter cp-layers images

Parameter images of cp-layers
=============================

    You may provide either a single image description string, or a list of 
    image descriptions strings. If you provide a list, then an image is 
    selected for processing if it is described by at least one of the given 
    strings.
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

default: 
     images: +@.*
     


> ./ora-tool.py help parameter cp-layers layers

Parameter layers of cp-layers
=============================

    You may either provide a single layer description string, a layer number,
    or a list of layer descriptions strings and layer numbers. If you provide
    a list, then a layer is selected for processing if it is described by at 
    least one of the given strings or numbers.

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

default: 
     layers: '!~backdrop'
     


> ./ora-tool.py help parameter cp-layers target

Parameter target of cp-layers
=============================

Name of the image where the layers shall be copied to. If there
is no image with the given name, a new one is created.

default: 
     target: new-image
     

```

### flip-layers

```
> ./ora-tool.py help op flip-layers
flip-layers
===========

    Flips (mirror image) the matching layers in the images in memory.

Example yaml of call with default parameters:

ora-tool:
  input:
    default: /path/to/input.ora
  ops:
  - flip-layers:
      axis: horizontal
      images: +@.*
      layers: '!~backdrop'
  output:
    default: /path/to/output.ora


In order to get help on each parameter, use
   ./ora-tool.py help parameter flip-layers [parameter]

  where [parameter] is one of the following:
        axis
        images
        layers

> ./ora-tool.py help parameter flip-layers axis

Parameter axis of flip-layers
=============================
either 'horizontal' or 'vertical'
default: 
     axis: horizontal
     


> ./ora-tool.py help parameter flip-layers images

Parameter images of flip-layers
===============================

    You may provide either a single image description string, or a list of 
    image descriptions strings. If you provide a list, then an image is 
    selected for processing if it is described by at least one of the given 
    strings.
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

default: 
     images: +@.*
     


> ./ora-tool.py help parameter flip-layers layers

Parameter layers of flip-layers
===============================

    You may either provide a single layer description string, a layer number,
    or a list of layer descriptions strings and layer numbers. If you provide
    a list, then a layer is selected for processing if it is described by at 
    least one of the given strings or numbers.

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

default: 
     layers: '!~backdrop'
     

```

### merge-layers

```
> ./ora-tool.py help op merge-layers
merge-layers
============

    Merges the matching layers in the images in memory,
    puts the merged layer on top of the respective image,
    and removes the source layers.

Example yaml of call with default parameters:

ora-tool:
  input:
    default: /path/to/input.ora
  ops:
  - merge-layers:
      images: +@.*
      layers: '!~backdrop'
      name: merged
  output:
    default: /path/to/output.ora


In order to get help on each parameter, use
   ./ora-tool.py help parameter merge-layers [parameter]

  where [parameter] is one of the following:
        images
        layers
        name

> ./ora-tool.py help parameter merge-layers images

Parameter images of merge-layers
================================

    You may provide either a single image description string, or a list of 
    image descriptions strings. If you provide a list, then an image is 
    selected for processing if it is described by at least one of the given 
    strings.
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

default: 
     images: +@.*
     


> ./ora-tool.py help parameter merge-layers layers

Parameter layers of merge-layers
================================

    You may either provide a single layer description string, a layer number,
    or a list of layer descriptions strings and layer numbers. If you provide
    a list, then a layer is selected for processing if it is described by at 
    least one of the given strings or numbers.

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

default: 
     layers: '!~backdrop'
     


> ./ora-tool.py help parameter merge-layers name

Parameter name of merge-layers
==============================
name of the new top layer containing the merged image data
default: 
     name: merged
     

```

### move-layers

```
> ./ora-tool.py help op move-layers
move-layers
===========

    Moves the matching layers in the images in memory,
    by either adding rows/cols of transparent pixels,
    or removing rows/cols of image pixels (negative x/y).

Example yaml of call with default parameters:

ora-tool:
  input:
    default: /path/to/input.ora
  ops:
  - move-layers:
      images: +@.*
      layers: '!~backdrop'
      x: 0
      y: 0
  output:
    default: /path/to/output.ora


In order to get help on each parameter, use
   ./ora-tool.py help parameter move-layers [parameter]

  where [parameter] is one of the following:
        images
        layers
        x
        y

> ./ora-tool.py help parameter move-layers images

Parameter images of move-layers
===============================

    You may provide either a single image description string, or a list of 
    image descriptions strings. If you provide a list, then an image is 
    selected for processing if it is described by at least one of the given 
    strings.
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

default: 
     images: +@.*
     


> ./ora-tool.py help parameter move-layers layers

Parameter layers of move-layers
===============================

    You may either provide a single layer description string, a layer number,
    or a list of layer descriptions strings and layer numbers. If you provide
    a list, then a layer is selected for processing if it is described by at 
    least one of the given strings or numbers.

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

default: 
     layers: '!~backdrop'
     


> ./ora-tool.py help parameter move-layers x

Parameter x of move-layers
==========================
number of new columns to add (positive) or columns to remove (negative) in each layer
default: 
     x: 0
     


> ./ora-tool.py help parameter move-layers y

Parameter y of move-layers
==========================
number of new rows to add (positive) or rows to remove (negative) in each layer
default: 
     y: 0
     

```

### rm-layers

```
> ./ora-tool.py help op rm-layers
rm-layers
=========

    Removes the matching layers from the images in memory.

Example yaml of call with default parameters:

ora-tool:
  input:
    default: /path/to/input.ora
  ops:
  - rm-layers:
      images: +@.*
      layers: ~backdrop
  output:
    default: /path/to/output.ora


In order to get help on each parameter, use
   ./ora-tool.py help parameter rm-layers [parameter]

  where [parameter] is one of the following:
        images
        layers

> ./ora-tool.py help parameter rm-layers images

Parameter images of rm-layers
=============================

    You may provide either a single image description string, or a list of 
    image descriptions strings. If you provide a list, then an image is 
    selected for processing if it is described by at least one of the given 
    strings.
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

default: 
     images: +@.*
     


> ./ora-tool.py help parameter rm-layers layers

Parameter layers of rm-layers
=============================

    You may either provide a single layer description string, a layer number,
    or a list of layer descriptions strings and layer numbers. If you provide
    a list, then a layer is selected for processing if it is described by at 
    least one of the given strings or numbers.

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

default: 
     layers: ~backdrop
     

```

### rotate-layers

```
> ./ora-tool.py help op rotate-layers
rotate-layers
=============

    Rotates the matching layers in the images in memory.

Example yaml of call with default parameters:

ora-tool:
  input:
    default: /path/to/input.ora
  ops:
  - rotate-layers:
      angle: 12.5
      center: []
      clip: true
      cval: 0.0
      images: +@.*
      layers: '!~backdrop'
      mode: constant
      order: 1
      resize: false
  output:
    default: /path/to/output.ora


In order to get help on each parameter, use
   ./ora-tool.py help parameter rotate-layers [parameter]

  where [parameter] is one of the following:
        angle
        center
        clip
        cval
        images
        layers
        mode
        order
        resize

> ./ora-tool.py help parameter rotate-layers angle

Parameter angle of rotate-layers
================================
rotation angle in degrees in counter-clockwise direction
default: 
     angle: 12.5
     


> ./ora-tool.py help parameter rotate-layers center

Parameter center of rotate-layers
=================================
determines the rotation center
default: 
     center: []
     


> ./ora-tool.py help parameter rotate-layers clip

Parameter clip of rotate-layers
===============================
boolean, if true, clip the output to the range of values of the input
default: 
     clip: true
     


> ./ora-tool.py help parameter rotate-layers cval

Parameter cval of rotate-layers
===============================
if mode is ‘constant’, then this is the value of the outside pixels
default: 
     cval: 0.0
     


> ./ora-tool.py help parameter rotate-layers images

Parameter images of rotate-layers
=================================

    You may provide either a single image description string, or a list of 
    image descriptions strings. If you provide a list, then an image is 
    selected for processing if it is described by at least one of the given 
    strings.
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

default: 
     images: +@.*
     


> ./ora-tool.py help parameter rotate-layers layers

Parameter layers of rotate-layers
=================================

    You may either provide a single layer description string, a layer number,
    or a list of layer descriptions strings and layer numbers. If you provide
    a list, then a layer is selected for processing if it is described by at 
    least one of the given strings or numbers.

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

default: 
     layers: '!~backdrop'
     


> ./ora-tool.py help parameter rotate-layers mode

Parameter mode of rotate-layers
===============================
points outside the boundaries of the input are filled according to the given mode; ‘constant’, ‘edge’, ‘symmetric’, ‘reflect’, or ‘wrap’
default: 
     mode: constant
     


> ./ora-tool.py help parameter rotate-layers order

Parameter order of rotate-layers
================================
order of the spline interpolation, default is 1; integer in the range 0-5
default: 
     order: 1
     


> ./ora-tool.py help parameter rotate-layers resize

Parameter resize of rotate-layers
=================================
boolean, if true, then the layer is extended so that the whole original layer fits in it
default: 
     resize: false
     

```

### to-binary-alpha

```
> ./ora-tool.py help op to-binary-alpha
to-binary-alpha
===============

    The alpha value of each pixel in the processed layer is set to either
    a low (t0) or high (t1) value, depending on whether it is less than the
    given threshold.

Example yaml of call with default parameters:

ora-tool:
  input:
    default: /path/to/input.ora
  ops:
  - to-binary-alpha:
      images: +@.*
      layers: +@.*
      t0: 0
      t1: 255
      threshold: 120
  output:
    default: /path/to/output.ora


In order to get help on each parameter, use
   ./ora-tool.py help parameter to-binary-alpha [parameter]

  where [parameter] is one of the following:
        images
        layers
        t0
        t1
        threshold

> ./ora-tool.py help parameter to-binary-alpha images

Parameter images of to-binary-alpha
===================================

    You may provide either a single image description string, or a list of 
    image descriptions strings. If you provide a list, then an image is 
    selected for processing if it is described by at least one of the given 
    strings.
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

default: 
     images: +@.*
     


> ./ora-tool.py help parameter to-binary-alpha layers

Parameter layers of to-binary-alpha
===================================

    You may either provide a single layer description string, a layer number,
    or a list of layer descriptions strings and layer numbers. If you provide
    a list, then a layer is selected for processing if it is described by at 
    least one of the given strings or numbers.

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

default: 
     layers: +@.*
     


> ./ora-tool.py help parameter to-binary-alpha t0

Parameter t0 of to-binary-alpha
===============================

Low alpha value for pixels with alpha below the threshold.

default: 
     t0: 0
     


> ./ora-tool.py help parameter to-binary-alpha t1

Parameter t1 of to-binary-alpha
===============================

High alpha value for pixels with alpha above or equal to the threshold.

default: 
     t1: 255
     


> ./ora-tool.py help parameter to-binary-alpha threshold

Parameter threshold of to-binary-alpha
======================================

Threshold value for the alpha compontent.

default: 
     threshold: 120
     

```

### to-nearest-palette

```
> ./ora-tool.py help op to-nearest-palette
to-nearest-palette
==================

    Each pixel in the processed layers is assigned the from the palette that 
    is closest to its original color, leaving the alpha value untouched for
    RGB palettes, and considering the alpha value part of the pixels color
    for RGBA palettes. The distance between the original color and each
    palette color is determined by the Euclidean norm of the channel
    differences divided by the divisor.

Example yaml of call with default parameters:

ora-tool:
  input:
    default: /path/to/input.ora
  ops:
  - to-nearest-palette:
      divisor: 255
      images: +@.*
      layers: +@.*
      palette: ega
  output:
    default: /path/to/output.ora


In order to get help on each parameter, use
   ./ora-tool.py help parameter to-nearest-palette [parameter]

  where [parameter] is one of the following:
        divisor
        images
        layers
        palette

> ./ora-tool.py help parameter to-nearest-palette divisor

Parameter divisor of to-nearest-palette
=======================================

The difference between each original color channel and each
palette color channel is divided by this value.

default: 
     divisor: 255
     


> ./ora-tool.py help parameter to-nearest-palette images

Parameter images of to-nearest-palette
======================================

    You may provide either a single image description string, or a list of 
    image descriptions strings. If you provide a list, then an image is 
    selected for processing if it is described by at least one of the given 
    strings.
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

default: 
     images: +@.*
     


> ./ora-tool.py help parameter to-nearest-palette layers

Parameter layers of to-nearest-palette
======================================

    You may either provide a single layer description string, a layer number,
    or a list of layer descriptions strings and layer numbers. If you provide
    a list, then a layer is selected for processing if it is described by at 
    least one of the given strings or numbers.

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

default: 
     layers: +@.*
     


> ./ora-tool.py help parameter to-nearest-palette palette

Parameter palette of to-nearest-palette
=======================================

    You may either provide a palette as an array of 3-elementary arrays (RGB),
    as an array of 4-elementary arrays (RGBA), or as a string refering to a
    predefined palette. Valid predefined palettes are:
            ega

default: 
     palette: ega
     

```

