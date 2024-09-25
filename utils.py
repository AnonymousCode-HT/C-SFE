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
    'ResNet-18',
    # 'VGG-16',
    'YOLOv8m-cls'
]

class ShowAttackCategories(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        attack_dir = f'./attack_result/{values}'
        if not os.path.exists(attack_dir):
            print(f"The directory {attack_dir} does not exist.")
            parser.exit()
        files = os.listdir(attack_dir)
        attack_categories = [file.replace('.json', '') for file in files if file.endswith('.json')]
        print("Available attack categories:")
        for category in attack_categories:
            print(category)
        parser.exit()

def parse_arguments():
    parser = argparse.ArgumentParser(description='C-SFE verifier')
    parser.add_argument("-m", "--model", default="ResNet-18", help="Input model name", type=str, choices=avaliable_model)
    parser.add_argument("-v", "--verbose", help="Increase output verbosity", action="store_true")
    parser.add_argument("-c", "--show-attack-categories", help="Show available attack categories", action=ShowAttackCategories, type=str, metavar="MODEL_NAME")
    parser.add_argument("-t", "--targeted_category", default="n03530642 honeycomb", help="Attack category", type=str)
    parser.add_argument("-i", "--input_image", default="./images/dog.jpg", help="Single input image", type=str)
    parser.add_argument("--validation_path", default="./ILSVRC2012_img_val/", help="Imagenet validation path", type=str)
    parser.add_argument("-s", "--validation_size", default=100, help="How many images are used in the validation dataset", type=int)

    return parser.parse_args()


def get_model(model_name):
    model_mapping = {
        'ResNet-18': models.resnet18(weights=True).eval(),
        # 'VGG-16': models.vgg16(weights=True),
        'YOLOv8m-cls': YOLO("yolov8m-cls.pt")
    }

    model_mapping = {key: model_mapping[key] for key in avaliable_model if key in model_mapping}

    if model_name in model_mapping:
        return model_mapping[model_name]
    else:
        raise ValueError(f"Model {model_name} is not recognized. Please choose from {list(model_mapping.keys())}")


def get_image(batch_size, image_num, dataset_dir, model, val_file_path, target_class=-1):
    transform_normal = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])

    transform_yolov8 = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
    ])

    if not os.path.exists(dataset_dir):
        print(f"The dataset directory {dataset_dir} does not exist. Only generating malicious model without testing.")
        return None

    transform = transform_normal if 'YOLO' not in model else transform_yolov8

    val_dataset = ImageNetValDataset(root_dir=dataset_dir, val_txt_path=val_file_path, transform=transform)
    indices = []
    if target_class != -1:
        for i in range(len(val_dataset.image_labels)):
            if val_dataset.image_labels[i][1] == target_class:
                indices.append(i)
    else:
        indices = np.random.choice(len(val_dataset), image_num, replace=False)
    test_subset = Subset(val_dataset, indices)
    data_loader = torch.utils.data.DataLoader(test_subset, batch_size=batch_size, shuffle=False, num_workers=16)

    return data_loader

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

def compare_models(model1, model2):
    different_params_count = 0

    for (name1, param1), (name2, param2) in zip(model1.named_parameters(), model2.named_parameters()):
        if name1 != name2:
            print(f"Parameter names differ: {name1} vs {name2}")
            different_params_count += param1.numel()
            continue
        difference = torch.ne(param1, param2)
        different_params_count += difference.sum().item()

    return different_params_count


def round_tensor(tensor):
    return tensor.round().int()


def hamming_distance_int8(a, b):
    a &= 0xFF
    b &= 0xFF

    xor_result = a ^ b
    hamming_distance = bin(xor_result).count('1')

    return hamming_distance


def hamming_distance(list_a, list_b):
    if len(list_a) != len(list_b):
        raise ValueError("Input lists must have the same length")

    hamming_distances = [hamming_distance_int8(a, b) for a, b in zip(list_a, list_b)]

    return hamming_distances


def get_first_n_items(d, n=5):
    if d == {}:
        return {}

    return dict(list(d.items())[:n])
