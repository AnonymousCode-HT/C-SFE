# C-SFE
The project is aimed at validating Cross-layer Sensitive Filter Exploration (C-SFE). The core exploration algorithm of C-SFE is currently being organized and is expected to be uploaded in September.

## Table of Contents
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Validate using the ILSVRC 2012 dataset](#validate-using-the-ilsvrc-2012-dataset)
- [To attack other categories](#to-attack-other-categories)
- [Output example](#Output-example)

## Installation
**Python version 3.10 or higher is required.**

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
python main.py -m ResNet-18
# Or
python main.py -m YOLOv8m-cls
```
`test.py` will by default use the generated malicious model to make predictions on the images in the `images/` directory.
```
python test.py -m ResNet-18
# Or
python test.py -m YOLOv8m-cls
```

## Validate using the ILSVRC 2012 dataset
The project includes `val.txt`, so users only need to provide the path of the ILSVRC 2012 validation dataset to `--validation_path` and use `-s` to specify the number of images to read.
```
python main.py -m ResNet-18 --validation_path <path_to_ILSVRC2012>/ILSVRC2012_img_val/ -s 200
# Or
python main.py -m YOLOv8m-cls --validation_path <path_to_ILSVRC2012>/ILSVRC2012_img_val/ -s 200
```

## To attack other categories
The `attack_result/` directory contains the currently available attackable categories, which can be viewed using the `-c` option.
```bash
python main.py -c ResNet-18
# Or
python main.py -c YOLOv8m-cls
```
Use `-t` to specify the target attack category.
```
python main.py -m ResNet-18 -t 'n03065424 coil, spiral, volute, whorl, helix'
# Or
python main.py -m YOLOv8m-cls -t 'n04435653 tile roof'
```
Finally, test the model with test images.
```
python test.py -m ResNet-18 -i ./images/dog.jpg
# Or
python test.py -m YOLOv8m-cls -i ./images/dog.jpg
```

## Output example
```
$ python main.py -t 'n03530642 honeycomb' -m YOLOv8m-cls --validation_path ./ILSVRC2012_img_val/ -s 200

Found https://ultralytics.com/images/bus.jpg locally at bus.jpg
image 1/1 /home/chguo/PycharmProjects/co-attack_demo/bus.jpg: 224x224 minibus 0.70, police_van 0.20, streetcar 0.03, trolleybus 0.02, amphibian 0.01, 149.6ms
Speed: 4.9ms preprocess, 149.6ms inference, 0.0ms postprocess per image at shape (1, 3, 224, 224)
Number of images = 200
Fp32: clean top1 accuracy = 0.77, top5 accuracy = 0.935
Fp32: clean categories: {'n02123597 Siamese cat, Siamese': 2, 'n03271574 electric fan, blower': 2, 'n03887697 paper towel': 2, 'n03388183 fountain pen': 2, 'n04118538 rugby ball': 2}

Start attack

Total attack kernel number = 3. Total attack element number = 9
                        Layer  Filter Index  Kernel Index  Element Index
0  model.model.4.m.3.cv1.conv             0            31              4
1  model.model.4.m.3.cv1.conv             0            31              1
2  model.model.4.m.3.cv1.conv             0            31              5
3  model.model.4.m.2.cv2.conv            31             0              0
4  model.model.4.m.2.cv2.conv            31             0              2
5  model.model.4.m.2.cv2.conv            31             0              1
6  model.model.4.m.2.cv1.conv             0            58              2
7  model.model.4.m.2.cv1.conv             0            58              0
8  model.model.4.m.2.cv1.conv             0            58              1
Fp32: malicious top1 accuracy = 0.0, top5 accuracy = 0.035
Fp32: malicious categories: {'n03530642 honeycomb': 196, 'n01440764 tench, Tinca tinca': 0, 'n01443537 goldfish, Carassius auratus': 0, 'n01484850 great white shark, white shark, man-eater, man-eating shark, Carcharodon carcharias': 0, 'n01491361 tiger shark, Galeocerdo cuvieri': 0}

Total attack kernel number = 3. Total attack element number = 9
                        Layer  Filter Index  Kernel Index  Element Index  clean_int8  malicious_int8  hamming distance
0  model.model.4.m.3.cv1.conv             0            31              4         -22             126                 3
1  model.model.4.m.3.cv1.conv             0            31              1         -18             127                 3
2  model.model.4.m.3.cv1.conv             0            31              5         -12             127                 4
3  model.model.4.m.2.cv2.conv            31             0              0         -12             127                 4
4  model.model.4.m.2.cv2.conv            31             0              2          -7             127                 3
5  model.model.4.m.2.cv2.conv            31             0              1          -4             126                 2
6  model.model.4.m.2.cv1.conv             0            58              2         -34             126                 2
7  model.model.4.m.2.cv1.conv             0            58              0         -33             127                 2
8  model.model.4.m.2.cv1.conv             0            58              1         -26             102                 1
Total hamming distance = 24

Quantized: clean top1 accuracy = 0.745, top5 accuracy = 0.935
Quantized: clean categories: {'n04550184 wardrobe, closet, press': 2, 'n02123597 Siamese cat, Siamese': 2, 'n03271574 electric fan, blower': 2, 'n03887697 paper towel': 2, 'n03388183 fountain pen': 2}
Quantized: malicious top1 accuracy = 0.0, top5 accuracy = 0.015
Quantized: malicious categories: {'n03530642 honeycomb': 200, 'n01440764 tench, Tinca tinca': 0, 'n01443537 goldfish, Carassius auratus': 0, 'n01484850 great white shark, white shark, man-eater, man-eating shark, Carcharodon carcharias': 0, 'n01491361 tiger shark, Galeocerdo cuvieri': 0}
Save malicious model...
Finish
```
