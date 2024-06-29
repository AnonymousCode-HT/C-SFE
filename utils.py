import argparse
import torchvision.models as models
from ultralytics import YOLO

avaliable_model = [
    'Resnet-18',
    'VGG-16',
    'YOLOv8m-cls'
]

def parse_arguments():
    parser = argparse.ArgumentParser(description='co-attack C-SFE verifier')
    parser.add_argument("-m", "--model", default="Resnet-18", help="Input model name", type=str, choices=avaliable_model)
    parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")

    return parser.parse_args()


def get_model(model_name):
    model_mapping = {
        'Resnet-18': models.resnet18(weights=True),
        'VGG-16': models.vgg16(weights=True),
        'YOLOv8m-cls': YOLO("yolov8m-cls.pt")
    }

    model_mapping = {key: model_mapping[key] for key in avaliable_model if key in model_mapping}

    if model_name in model_mapping:
        return model_mapping[model_name]
    else:
        raise ValueError(f"Model {model_name} is not recognized. Please choose from {list(model_mapping.keys())}")