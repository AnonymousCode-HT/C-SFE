import torch
import torchvision.transforms as transforms
from utils import *
from PIL import Image


DEVICE = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')

args = parse_arguments()
malicious_model = torch.load(args.model + "_malicious_model.pth")
malicious_model.eval()
malicious_model.to(DEVICE)

clean_model = models.resnet18(pretrained=True)
clean_model.eval()  # 设置为评估模式
clean_model.to(DEVICE)

transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

image = Image.open(args.input_image).convert('RGB')
transformed_image = transform(image).unsqueeze(0).to(DEVICE)

outputs = clean_model(transformed_image)
probabilities = torch.nn.functional.softmax(outputs, dim=1)
top5_prob, top5_catid = torch.topk(probabilities, 5)

with open('synset_words.txt') as f:
    labels = [line.strip() for line in f.readlines()]

print(f"Read {args.input_image}")

print("Clean model result:")
for i in range(top5_prob.size(1)):
    print(f"Category: {labels[top5_catid[0][i]]}, Probability: {top5_prob[0][i].item()}")


outputs = malicious_model(transformed_image)
probabilities = torch.nn.functional.softmax(outputs, dim=1)
top5_prob, top5_catid = torch.topk(probabilities, 5)
print("\nmalicious model result:")
for i in range(top5_prob.size(1)):
    print(f"Category: {labels[top5_catid[0][i]]}, Probability: {top5_prob[0][i].item()}")

num_different_params = compare_models(clean_model, malicious_model)
print(f"\nCompare malicious model and clean model, number of different parameters =  {num_different_params}")
