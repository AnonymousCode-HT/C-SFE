# C-SFE
The project is aimed at validating Cross-layer Sensitive Filter Exploration (C-SFE). The core exploration algorithm of C-SFE is currently being organized and is expected to be uploaded in September.

## Table of Contents
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Validate using the ILSVRC 2012 dataset](#validate-using-the-ilsvrc-2012-dataset)
- [To attack other categories](#to-attack-other-categories)

## Installation
Clone the repository and navigate to the project directory.
```
git clone https://github.com/AnonymousCode-HT/C-SFE.git
cd C-SFE
```
Install the required dependencies.
```
pip install -r requirements.txt
```

## Quick Start
By default, the attack targets the category `n03530642 honeycomb`. For convenience in testing, `main.py` will generate the attacked model in the root directory.
```
python main.py
```
`test.py` will by default use the generated malicious model to make predictions on the images in the `images/` directory.
```
python test.py
```

## Validate using the ILSVRC 2012 dataset
The project includes `val.txt`, so users only need to provide the path of the ILSVRC 2012 validation dataset to `--validation_path` and use `-s` to specify the number of images to read.
```
python main.py --validation_path <path_to_ILSVRC2012>/ILSVRC2012_img_val/ 
```

## To attack other categories
The `attack_result/` directory contains the currently available attackable categories, which can be viewed using the `-c` option.
```bash
python main.py -c ResNet-18
```
Use `-t` to specify the target attack category.
```
python main.py -t 'n03065424 coil, spiral, volute, whorl, helix'
```
Finally, test the model with test images.
```
python test.py -i ./images/dog.jpg
```
