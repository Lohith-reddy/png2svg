# png2svg

Aim: create a Deep Learning Pipeline that can convert png images (probably created by AI) into vector form for further manipulation.

## Ideas

Use Autoencoder-Decoder architecture with png image as input and svg characterists as output.

One other interesting idea is to encode SVG text into a lower dimensional space using an Autoencoder-decoder. Try to generate this lower-dimensional encoding from a png image. Why do this? The lower-dimensional encoding can be part of the model that tries to predict the svg format itself?

Let's do a multi-modal architecture with png to svg on one dimension and word vectors based on general text. (how to generate svg based on just text or png input). 

### Bad ideas

first use CNN architecture to read in svg file in text format as input and outputs a png image.
Once this gets trained, freeze the layers and use it to train a model to create svg from png.

However why train a model to predict png from a svg, use existing software to convert svg to png and use them for computing cost.

## Data augmentation

add multiple svgs into one image?? But how to do that in bulk?
