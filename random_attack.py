import random
from utils import *

import copy

VAL_FILE_PTAH = './val.txt'
LABELS = './synset_words.txt'
BATCH_SIZE = 200
DEVICE = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')

def create_yolo_model():
    new_model = YOLO("yolov8m-cls.pt")

    results = new_model('bus.jpg', verbose=False)

    return new_model

def modify_random_parameters(model, x, model_name):
    if 'YOLO' in model_name:
        model = create_yolo_model()
    else:
        model = copy.deepcopy(model)
    model.to('cpu')
    # Collect all parameter tensors that need modification, along with their minimum and maximum values
    params = []
    for name, param in model.named_parameters():
        p_min = param.data.min().item()
        p_max = param.data.max().item()
        params.append((param, p_min, p_max))

    total_params = sum(p[0].numel() for p in params)

    if x > total_params:
        raise ValueError(f"x={x} exceeds the total number of parameters in the model={total_params}")

    # Randomly select x unique global indices
    selected_indices = set(random.sample(range(total_params), x))

    cnt = 0

    # Map global indices to specific parameter tensors and local indices
    current_index = 0
    for param, p_min, p_max in params:
        numel = param.numel()
        indices_in_param = [idx - current_index for idx in selected_indices
                            if current_index <= idx < current_index + numel]
        if indices_in_param:
            new_values = torch.empty(len(indices_in_param)).uniform_(p_min, p_max)
            param.data.view(-1)[indices_in_param] = new_values

            cnt = cnt + len(indices_in_param)

        current_index += numel

    model.to(DEVICE)
    if 'YOLO' not in model_name:
        model.eval()

    return model


def predict_top1_top5(model, data_loader, name):
    total = 0
    top1_correct = 0
    top5_correct = 0
    with torch.no_grad():
        for x_data, y_data in data_loader:
            x_data = x_data.to(DEVICE)
            y_data = y_data.to(DEVICE)

            if 'YOLO' in name:
                outputs = model(x_data, verbose=False)
                detected_classes = []
                for result in outputs:
                    detected_classes.append([result.probs.top1, result.probs.top5])

                for detected_class, true_class in zip(detected_classes, y_data):
                    total += 1
                    if detected_class[0] == true_class:
                        top1_correct += 1

                    if true_class in detected_class[1]:
                        top5_correct += 1
            else:
                outputs = model(x_data)
                _, predicted = torch.max(outputs, 1)
                total += y_data.size(0)
                top1_correct += (predicted == y_data).sum().item()

                _, predicted_top5 = torch.topk(outputs, 5, dim=1)
                top5_correct += sum(y_data[i].item() in predicted_top5[i] for i in range(y_data.size(0)))

    top1_accuracy = top1_correct / total
    top5_accuracy = top5_correct / total

    return top1_accuracy, top5_accuracy

if __name__ == "__main__":
    trials = 10

    clean_model_dict = {
        'YOLOv8m-cls': YOLO("yolov8m-cls.pt"),
        'ResNet-18':models.resnet18(weights=True).eval(),
        'VGG-16':models.vgg16(weights=True).eval()
    }

    for name, clean_model in clean_model_dict.items():
        ''' When the user does not provide the path to a validation dataset, main.py is only responsible for generating the malicious model and will not perform prediction. 
            For YOLOv8, if a prediction is not made, it will not be in eval mode. Therefore, it is forced to predict on a single image.
            '''
        clean_model.to(DEVICE)
        if 'YOLO' in name:
            results = clean_model("https://ultralytics.com/images/bus.jpg")

        data_loader = get_image(BATCH_SIZE, 50000, '/xxx/ILSVRC2012_img_val/', name, VAL_FILE_PTAH)

        top1_accuracy, top5_accuracy = predict_top1_top5(clean_model, data_loader, name)

        print(f"Current model = {name}")
        print(f"Clean top1_accuracy = {top1_accuracy * 100:.1f}%")
        print(f"Clean top5_accuracy = {top5_accuracy * 100:.1f}%")

        change_params_list = [10, 100, 1000, 10000, 100000]

        for x in change_params_list:
            top1_accuracy_avg = 0
            top5_accuracy_avg = 0
            modified_model = clean_model
            for loop in range(trials):
                modified_model = modify_random_parameters(clean_model, x, name)

                top1_accuracy, top5_accuracy = predict_top1_top5(modified_model, data_loader, name)
                top1_accuracy_avg += top1_accuracy
                top5_accuracy_avg += top5_accuracy

            different_params_count = compare_models(modified_model, clean_model)
            top1_accuracy_avg = (top1_accuracy_avg / trials) * 100
            top5_accuracy_avg = (top5_accuracy_avg / trials) * 100

            print(f"\nRandom change {different_params_count} pameters: ", end='')
            print(f"top1_accuracy = {top1_accuracy_avg:.1f}%, top5_accuracy = {top5_accuracy_avg:.1f}%")
