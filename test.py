import torch
import torchvision.transforms as transforms
from utils import *
from PIL import Image


DEVICE = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')

with open('synset_words.txt') as f:
    labels = [line.strip() for line in f.readlines()]

args = parse_arguments()
malicious_model = torch.load(args.model + "_malicious_model.pth")
malicious_model.to(DEVICE)

clean_model = get_model(args.model)
clean_model.to(DEVICE)

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

transform = transform_normal if 'YOLO' not in args.model else transform_yolov8

print(f"Test model = {args.model}")
print(f"Read {args.input_image}")
image = Image.open(args.input_image).convert('RGB')
transformed_image = transform(image).unsqueeze(0).to(DEVICE)

if 'YOLO' in args.model:
    outputs = clean_model(transformed_image, verbose=False)
    top5_prob, top5_catid = outputs[0].probs.top5conf, outputs[0].probs.top5
else:
    outputs = clean_model(transformed_image)
    probabilities = torch.nn.functional.softmax(outputs, dim=1)
    top5_prob, top5_catid = torch.topk(probabilities, 5)
    top5_prob = top5_prob.squeeze()
    top5_catid = top5_catid.squeeze()

print("\nClean Model Result:")
for i in range(len(top5_prob)):
    print(f"Category: {labels[top5_catid[i]]}, Probability: {top5_prob[i].item()}")

if 'YOLO' in args.model:
    outputs = malicious_model(transformed_image, verbose=False)
    top5_prob, top5_catid = outputs[0].probs.top5conf, outputs[0].probs.top5
else:
    malicious_model.eval()
    outputs = malicious_model(transformed_image)
    probabilities = torch.nn.functional.softmax(outputs, dim=1)
    top5_prob, top5_catid = torch.topk(probabilities, 5)
    top5_prob = top5_prob.squeeze()
    top5_catid = top5_catid.squeeze()

print("\nMalicious FP Model Result:")
for i in range(len(top5_prob)):
    print(f"Category: {labels[top5_catid[i]]}, Probability: {top5_prob[i].item()}")


import onnxruntime as ort
file_path = args.model + '_malicious_model.onnx'
session = ort.InferenceSession(file_path)
input_name = session.get_inputs()[0].name
outputs = session.run(None, {input_name: transformed_image.cpu().numpy()})

output = outputs[0]
if 'YOLO' in args.model:
    probabilities = output / np.sum(output, axis=1, keepdims=True)
else:
    probabilities = np.exp(output) / np.sum(np.exp(output), axis=1, keepdims=True)
top5_prob = np.sort(probabilities, axis=1)[:, -5:][:, ::-1]
top5_catid = np.argsort(probabilities, axis=1)[:, -5:][:, ::-1]

top5_prob = np.squeeze(top5_prob)
top5_catid = np.squeeze(top5_catid)

print("\nMalicious Quant Model Result:")
for i in range(len(top5_prob)):
    print(f"Category: {labels[top5_catid[i]]}, Probability: {top5_prob[i].item()}")

num_different_params = compare_models(clean_model, malicious_model)
print(f"\nCompare malicious model and clean model, number of different parameters =  {num_different_params}")


