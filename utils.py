import argparse
import torch
import os
import numpy as np
import torchvision.models as models
import torchvision.transforms as transforms
from torch.utils.data import Dataset
from torch.utils.data import Subset
from PIL import Image
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


def get_image(image_num, dataset_dir, val_file_path, target_class=-1):
    transform = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])

    val_dataset = ImageNetValDataset(root_dir=dataset_dir, val_txt_path=val_file_path, transform=transform)
    indices = []
    if target_class != -1:
        for i in range(len(val_dataset.image_labels)):
            if val_dataset.image_labels[i][1] == target_class:
                indices.append(i)
    else:
        indices = np.random.choice(len(val_dataset), image_num, replace=False)
    test_subset = Subset(val_dataset, indices)
    testloader = torch.utils.data.DataLoader(test_subset, batch_size=image_num, shuffle=True, num_workers=16)

    x_data = 0
    y_data = 0
    for data in testloader:
        x_data, y_data = data[0], data[1]

    return x_data, y_data

class ImageNetValDataset(Dataset):
    def __init__(self, root_dir, val_txt_path, transform=None):
        self.root_dir = root_dir
        self.val_txt_path = val_txt_path
        self.transform = transform
        self.image_labels = self._read_val_txt()

    def _read_val_txt(self):
        image_labels = []
        with open(self.val_txt_path, 'r') as file:
            for line in file:
                filename, label = line.strip().split()
                image_labels.append((filename, int(label)))
        return image_labels

    def __len__(self):
        return len(self.image_labels)

    def __getitem__(self, idx):
        filename, label = self.image_labels[idx]
        img_path = os.path.join(self.root_dir, filename)
        image = Image.open(img_path).convert('RGB')
        if self.transform:
            image = self.transform(image)
        return image, label