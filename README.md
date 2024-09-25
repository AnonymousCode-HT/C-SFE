# C-SFE
The project is aimed at validating Cross-layer Sensitive Filter Exploration (C-SFE).

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
```
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
$ python main.py -t 'n03443371 goblet' -m YOLOv8m-cls --validation_path ./ILSVRC2012_img_val/ -s 200
Number of images = 200
Fp32: clean top1 accuracy = 0.745, top5 accuracy = 0.94
Fp32: clean categories: {'n01532829 house finch, linnet, Carpodacus mexicanus': 2, 'n01843383 toucan': 2, 'n02007558 flamingo': 2, 'n03868242 oxcart': 2, 'n07565083 menu': 2}

Start attack

Total attack kernel number = 3. Total attack element number = 9
                        Layer  Filter Index  Kernel Index  Element Index
0  model.model.4.m.3.cv1.conv            27             3              3
1  model.model.4.m.3.cv1.conv            27             3              4
2  model.model.4.m.3.cv1.conv            27             3              5
3  model.model.4.m.2.cv2.conv             3             0              7
4  model.model.4.m.2.cv2.conv             3             0              8
5  model.model.4.m.2.cv2.conv             3             0              6
6  model.model.4.m.2.cv1.conv             0            58              2
7  model.model.4.m.2.cv1.conv             0            58              0
8  model.model.4.m.2.cv1.conv             0            58              1
Fp32: malicious top1 accuracy = 0.0, top5 accuracy = 0.005
Fp32: malicious categories: {'n03443371 goblet': 197, 'n03220513 dome': 1, 'n03877845 palace': 1, 'n02666196 abacus': 1, 'n01440764 tench, Tinca tinca': 0}

Total attack kernel number = 3. Total attack element number = 9
                        Layer  Filter Index  Kernel Index  Element Index  clean_int8  malicious_int8  hamming distance
0  model.model.4.m.3.cv1.conv            27             3              3         -11             127                 3
1  model.model.4.m.3.cv1.conv            27             3              4          -8             120                 1
2  model.model.4.m.3.cv1.conv            27             3              5          -7             127                 3
3  model.model.4.m.2.cv2.conv             3             0              7         -12             124                 2
4  model.model.4.m.2.cv2.conv             3             0              8          -8             125                 3
5  model.model.4.m.2.cv2.conv             3             0              6          -4             117                 3
6  model.model.4.m.2.cv1.conv             0            58              2         -34             127                 3
7  model.model.4.m.2.cv1.conv             0            58              0         -33             127                 2
8  model.model.4.m.2.cv1.conv             0            58              1         -26             127                 4
Total hamming distance = 24

Quantized: clean top1 accuracy = 0.745, top5 accuracy = 0.93
Quantized: clean categories: {'n01532829 house finch, linnet, Carpodacus mexicanus': 2, 'n01843383 toucan': 2, 'n02007558 flamingo': 2, 'n03761084 microwave, microwave oven': 2, 'n07565083 menu': 2}
Quantized: malicious top1 accuracy = 0.0, top5 accuracy = 0.0
Quantized: malicious categories: {'n03443371 goblet': 198, 'n03388043 fountain': 1, 'n03877845 palace': 1, 'n01440764 tench, Tinca tinca': 0, 'n01443537 goldfish, Carassius auratus': 0}
Save malicious model...
Finish

$ python test.py -m YOLOv8m-cls -i images/dog.jpg
Test model = YOLOv8m-cls
Read images/dog.jpg

Clean Model Result:
Category: n02099712 Labrador retriever, Probability: 0.8247175812721252
Category: n02099267 flat-coated retriever, Probability: 0.058828290551900864
Category: n02099429 curly-coated retriever, Probability: 0.023523811250925064
Category: n02105412 kelpie, Probability: 0.01811697706580162
Category: n02089078 black-and-tan coonhound, Probability: 0.017459852620959282

Malicious FP Model Result:
Category: n03443371 goblet, Probability: 0.9998925924301147
Category: n02666196 abacus, Probability: 6.291417230386287e-05
Category: n03109150 corkscrew, bottle screw, Probability: 1.4275145076680928e-05
Category: n04591713 wine bottle, Probability: 8.616713785158936e-06
Category: n04380533 table lamp, Probability: 3.5992884477309417e-06

Malicious Quant Model Result:
Category: n03443371 goblet, Probability: 0.9999963045120239
Category: n03109150 corkscrew, bottle screw, Probability: 1.7092676216634572e-06
Category: n02666196 abacus, Probability: 6.54071413919155e-07
Category: n04591713 wine bottle, Probability: 5.52320329916256e-07
Category: n03018349 china cabinet, china closet, Probability: 2.0467432193527202e-07

Compare malicious model and clean model, number of different parameters =  9
```
