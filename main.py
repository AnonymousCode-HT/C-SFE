import warnings
from utils import *
from analysis import attack_analysis

warnings.filterwarnings("ignore", category=UserWarning, module='torchvision.models', lineno=223)

VAL_FILE_PTAH = './val.txt'
LABELS = './synset_words.txt'
BATCH_SIZE = 100
DEVICE = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')

if __name__ == '__main__':
    args = parse_arguments()

    model = get_model(args.model)
    ''' When the user does not provide the path to a validation dataset, main.py is only responsible for generating the malicious model and will not perform prediction. 
    For YOLOv8, if a prediction is not made, it will not be in eval mode. Therefore, it is forced to predict on a single image.
    '''
    if 'YOLO' in args.model:
        results = model("https://ultralytics.com/images/bus.jpg")

    data_loader = get_image(BATCH_SIZE, args.validation_size, args.validation_path, args.model, VAL_FILE_PTAH)

    class_name = np.loadtxt(LABELS, str, delimiter='\t').tolist()
    atk_analysis = attack_analysis(
        model_name = args.model,
        model = model,
        data_loader = data_loader,
        device=DEVICE,
        class_name = class_name
    )

    if data_loader is not None:
        print(f"Number of images = {args.validation_size}")

    # Collect the accuracy of the clean floating-point model and the classification results for all inputs.
    top_1, top_5 = atk_analysis.predict()
    categories = atk_analysis.get_topX_categories()

    print(f"Fp32: clean top1 accuracy = {top_1}, top5 accuracy = {top_5}")
    print(f"Fp32: clean categories: {get_first_n_items(categories)}")


    print("\nStart attack")
    # Collect the accuracy of the malicious floating-point model and the classification results for all inputs.
    atk_analysis.set_attack_info('./attack_result/' + args.model + '/' + args.targeted_category + '.json')
    atk_analysis.attack()

    malicious_top1, malicious_top5 = atk_analysis.predict()
    categories = atk_analysis.get_topX_categories()

    atk_analysis.print_attack_config()
    print(f"Fp32: malicious top1 accuracy = {malicious_top1}, top5 accuracy = {malicious_top5}")
    print(f"Fp32: malicious categories: {get_first_n_items(categories)}")

    clean_file_path = './ModelQuantization/' + args.model + '/clean_model.onnx'
    malicious_file_path = args.model + '_malicious_model.onnx'

    # Quantize the malicious parameters and overwrite the corresponding values in the quantized model.
    atk_analysis.add_quant_model(clean_file_path)

    atk_analysis.attack(quant=True, output_file=malicious_file_path)

    atk_analysis.print_attack_config()

    top_1, top_5 = atk_analysis.predict(quant=True, file_path=clean_file_path)
    categories = atk_analysis.get_topX_categories(quant=True, file_path=clean_file_path)

    print(f"\nQuantized: clean top1 accuracy = {top_1}, top5 accuracy = {top_5}")
    print(f"Quantized: clean categories: {get_first_n_items(categories)}")

    malicious_top1, malicious_top5 = atk_analysis.predict(quant=True, file_path=malicious_file_path)
    categories = atk_analysis.get_topX_categories(quant=True, file_path=malicious_file_path)
    print(f"Quantized: malicious top1 accuracy = {malicious_top1}, top5 accuracy = {malicious_top5}")
    print(f"Quantized: malicious categories: {get_first_n_items(categories)}")

    print("Save malicious model...")
    torch.save(atk_analysis.model, args.model + '_malicious_model.pth')

    print("Finish")



