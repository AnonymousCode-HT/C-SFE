from utils import *
from analysis import attack_analysis
import pickle
import pandas as pd

DATASET_DIR = "./images/val_img"
VAL_FILE_PTAH = './images/val.txt'
LABELS = './images/synset_words.txt'
TEST_IMG_NUM = 50
DEVICE = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')

if __name__ == '__main__':
    args = parse_arguments()

    model = get_model(args.model).eval()

    x_data, y_data = get_image(TEST_IMG_NUM, DATASET_DIR, VAL_FILE_PTAH)

    class_name = np.loadtxt(LABELS, str, delimiter='\t').tolist()
    atk_analysis = attack_analysis(
        model = model.to(DEVICE),
        x_data = x_data.to(DEVICE),
        y_data = y_data.to(DEVICE),
        class_name = class_name
    )

    print(f"Images number = {TEST_IMG_NUM}")

    # Get orignal accuracy
    top_1, top_5 = atk_analysis.get_predict()
    # Get the original classification of the input image
    categories = atk_analysis.get_topX_categories()

    print(f"Orignal top1 accuracy = {top_1}, top5 accuracy = {top_5}")
    print(f"Orignal categories: {categories}")


    print("\nStart attack")
    atk_analysis.set_attack_info('./attack_result/ResNet-18/n03530642 honeycomb.json')

    atk_analysis.attack()

    malicious_top1, malicious_top5 = atk_analysis.get_predict()
    categories = atk_analysis.get_topX_categories()

    if args.verbose is not True:
        atk_analysis.print_attack_config()
    print(f"malicious top1 accuracy = {malicious_top1}, top5 accuracy = {malicious_top5}")
    print(f"malicious categories: {categories}")

    pass


