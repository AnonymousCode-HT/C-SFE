import json
import copy
import re
import pandas as pd
import onnxruntime as ort
import onnx.numpy_helper as numpy_helper
import math
import onnx
from collections import Counter
from utils import *


class attack_analysis():
    def __init__(self, model_name, model, class_name, json_data=None, dna_size=0, attack_layers=None, quant_model=None, data_loader=None, device='cpu'):
        self.model_name = model_name
        self.model = model.to(device)
        self.class_name = class_name
        self.json_data = json_data
        self.dna_size = dna_size
        self.attack_layers = attack_layers
        self.orgLayerWeight = None
        self.attack_config_list = None
        self.malicious_params = None
        self.attack_layers_onnx = None
        self.data_loader = data_loader
        self.device = device

        self.quant_model = quant_model
        self.quant_file_path = None
        self.bn_scales = []
        self.quant_scales = []
        self.quant_clean_params = []
        self.quant_malicious_params = []

    def predict(self, quant=False, file_path=None):
        total = 0
        top1_correct = 0
        top5_correct = 0

        if self.data_loader is None:
            print("Validation data is None, skipping accuracy calculation.")
            return -1, -1

        if quant is True:
            session = ort.InferenceSession(file_path)
            input_name = session.get_inputs()[0].name
            for x_data, y_data in self.data_loader:
                x_data_numpy = x_data.numpy()
                y_data_numpy = y_data.numpy()
                for i in range(len(x_data_numpy)):
                    single_input = np.expand_dims(x_data_numpy[i], axis=0)
                    outputs = session.run(None, {input_name: single_input})
                    output_array = np.array(outputs[0])

                    top1_correct += np.sum(np.argmax(output_array, axis=1) == y_data_numpy[i])

                    top_5_predictions = np.argsort(output_array, axis=1)[:, -5:]
                    if y_data_numpy[i] in top_5_predictions[0]:
                        top5_correct += 1

                    total += 1
        else :
            self.model.to(self.device)
            with torch.no_grad():
                for x_data, y_data in self.data_loader:
                    x_data = x_data.to(self.device)
                    y_data = y_data.to(self.device)
                    if 'YOLO' in self.model_name:
                        outputs = self.model(x_data, verbose=False)
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
                        outputs = self.model(x_data)
                        _, predicted = torch.max(outputs, 1)
                        total += y_data.size(0)
                        top1_correct += (predicted == y_data).sum().item()

                        _, predicted_top5 = torch.topk(outputs, 5, dim=1)
                        top5_correct += sum(y_data[i].item() in predicted_top5[i] for i in range(y_data.size(0)))

        top1_accuracy = top1_correct / total
        top5_accuracy = top5_correct / total

        return top1_accuracy, top5_accuracy


    def get_topX_categories(self, top_num=50, quant=False, file_path=None):
        result_list = []

        if self.data_loader is None:
            print("Validation data is None, skipping categories calculation.")
            return {}

        if quant is True:
            session = ort.InferenceSession(file_path)
            input_name = session.get_inputs()[0].name
            for x_data, _ in self.data_loader:
                x_data_numpy = x_data.numpy()
                for i in range(len(x_data_numpy)):
                    single_input = np.expand_dims(x_data_numpy[i], axis=0)
                    outputs = session.run(None, {input_name: single_input})
                    output_array = np.array(outputs[0])
                    _, predicted = torch.max(torch.tensor(output_array), 1)
                    result_list.extend(predicted.tolist())
        else:
            self.model.to(self.device)
            with torch.no_grad():
                for x_data, _ in self.data_loader:
                    x_data = x_data.to(self.device)
                    if 'YOLO' in self.model_name:
                        outputs = self.model(x_data, verbose=False)
                        for result in outputs:
                            result_list.append(result.probs.top1)
                    else:
                        outputs = self.model(x_data)
                        _, predicted = torch.max(outputs, 1)
                        result_list.extend(predicted.tolist())

        catego = Counter(result_list).most_common(top_num)
        categoriesDict = {}
        class_list = self.class_name[:]

        for i in range(len(catego)):
            categoriesDict[self.class_name[catego[i][0]]] = catego[i][1]
            class_list.remove(self.class_name[catego[i][0]])

        for i in range(len(class_list)):
            categoriesDict[class_list[i]] = 0

        return categoriesDict

    def __set_attack_configs(self, attack_configs):
        self.attack_config_list = attack_configs


    def __set_malicious_params(self, malicious_params):
        self.malicious_params = malicious_params


    def __read_json(self, filename):

        if not os.path.exists(filename):
            raise FileNotFoundError(f"File {filename} does not exist")

        try:
            with open(filename, 'r') as file:
                try:
                    self.json_data = json.load(file)
                except json.JSONDecodeError:
                    raise ValueError(f"File {filename} is not a valid JSON")

                if not isinstance(self.json_data, dict):
                    raise TypeError(f"JSON data in file {filename} is not a dictionary")

        except Exception as e:
            raise RuntimeError(f"An error occurred while processing the file {filename}: {e}")

    def __get_layer_weight(self):
        param_list = []
        try:
            for layer in self.attack_layers:
                layer_param = copy.deepcopy(self.model.state_dict()[layer + '.weight'])
                param_list.append(layer_param)
        except KeyError:
            raise ValueError(f"Layer {self.attack_layers} not found in the model.")

        return param_list


    def set_attack_info(self, file):
        self.__read_json(file)
        attack_configs = self.json_data['member_0']['kernel_idx']
        attack_params = self.json_data['member_0']['bestAttackedWeight']
        attack_layers = list(dict.fromkeys(item[4] for item in attack_configs))

        self.__set_attack_configs(attack_configs)
        self.__set_malicious_params(attack_params)
        self.__set_atk_layer(attack_layers)

    def __set_atk_layer(self, attack_layers):
        self.attack_layers = attack_layers
        self.orgLayerWeight = self.__get_layer_weight()

    def print_attack_config(self):
        attack_layers = list({item[4] for item in self.attack_config_list})
        total_attack_kernels = len(attack_layers)
        total_attack_elements = len(self.attack_config_list)
        print(f"\nTotal attack kernel number = {total_attack_kernels}. Total attack element number = {total_attack_elements}")

        data = {
            'Layer': [],
            'Filter Index': [],
            'Kernel Index': [],
            'Element Index': []
        }

        for item in self.attack_config_list:
            layer = item[4]
            filter_index = item[2]
            kernel_index = item[3]
            elem_index = item[6]

            data['Layer'].append(layer)
            data['Filter Index'].append(filter_index)
            data['Kernel Index'].append(kernel_index)
            data['Element Index'].append(elem_index)

        if self.quant_clean_params != [] and self.quant_malicious_params != []:
            data['clean_int8'] = self.quant_clean_params
            data['malicious_int8'] = self.quant_malicious_params
            data['hamming distance'] = hamming_distance(self.quant_clean_params, self.quant_malicious_params)

        df = pd.DataFrame(data)
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', 1000)
        pd.set_option('display.max_colwidth', None)
        print(df)
        if data.get('hamming distance') is not None:
            print(f"Total hamming distance = {np.sum(data['hamming distance'])}")


    def get_attacked_params(self, quant=False):
        if quant is True:
            return self.quant_clean_params, self.quant_malicious_params
        else:
            return self.malicious_params


    def recover(self):
        for layer_idx in range(len(self.attack_layers)):
            layer_param = dict(self.model.named_parameters()).get(self.attack_layers[layer_idx] + '.weight')
            layer_param.data.copy_(self.orgLayerWeight[layer_idx])


    def __kernel_swap(self, dna, recover=True):
        layer_param_dict = {}

        if recover is True:
            self.recover()

        for layer_idx in range(len(self.attack_layers)):
            layer_param_dict[self.attack_layers[layer_idx]] = (dict(self.model.named_parameters()).get(self.attack_layers[layer_idx] + '.weight'))

        attack_config_num = len(self.attack_config_list)

        dna_start_pos = 0

        for c_idx in range(attack_config_num):
            attack_config = self.attack_config_list[c_idx]

            atk_layer_name = attack_config[4]
            attack_filters_num = attack_config[0]
            attack_kernels_num = attack_config[1]

            param = layer_param_dict[atk_layer_name]
            attack_weight_size = attack_config[5]
            weight_offset = attack_config[6]

            for f_idx in range(attack_filters_num):
                filter_pos = attack_config[2] + f_idx
                for k_idx in range(attack_kernels_num):
                    kernel_pos = attack_config[3] + k_idx

                    end_pos = dna_start_pos + attack_weight_size

                    tmp_kernel = param.data[filter_pos][kernel_pos].reshape(param.data.shape[2]**2)
                    dna_value = torch.from_numpy(np.array(dna[dna_start_pos:end_pos]))
                    tmp_kernel[weight_offset:attack_weight_size+weight_offset] = dna_value
                    param.data[filter_pos][kernel_pos].copy_(tmp_kernel.reshape(param.data.shape[2], param.data.shape[2]))

                    dna_start_pos += attack_weight_size

    def __convert_layer_name(self, layer_name):
        if 'YOLO' in self.model_name:
            pattern = r'model\.model\.(\d+)\.m\.(\d+)\.(cv\d+)\.conv'
            return re.sub(pattern, r'/model.\1/m.\2/\3/conv/Conv_quant', layer_name)
        else:
            pattern = r'(layer\d+)\.(\d+)\.(conv\d+)'
            return re.sub(pattern, r'/\1/\1.\2/\3/Conv_quant', layer_name)

    def add_quant_model(self, file_path):
        self.quant_model = onnx.load(file_path)
        self.quant_file_path = file_path
        self.attack_layers_onnx = [self.__convert_layer_name(name) for name in self.attack_layers]
        self.__get_bn_and_quant_scale()

    def __get_next_layer(self, layer_name):
        '''
        During inference, the BN layers of YOLOv8 are fused into the conv layers. Therefore, reloading the model uniformly here is only to obtain the BN parameters.
        '''
        tmp_model = get_model(self.model_name)
        layer_name_list = [name for name, _ in tmp_model.named_modules()]
        # layer_name_list = [name for name, _ in self.model.named_modules()]
        try:
            index = layer_name_list.index(layer_name)
        except ValueError:
            return None

        if index + 1 < len(layer_name_list):
            next_layer_name = layer_name_list[index + 1]
            return dict(tmp_model.named_modules())[next_layer_name]
        else:
            return None

    def __get_node_info(self, model, node):
        weights = {}
        for input_name in node.input:
            for initializer in model.graph.initializer:
                if initializer.name == input_name:
                    weights[input_name] = onnx.numpy_helper.to_array(initializer)
        return weights

    def __find_node_by_name(self, model, node_name):
        for node in model.graph.node:
            if node.name == node_name:
                return self.__get_node_info(model, node)
        return None


    def __make_malicious_model(self, file_path):
        layer_idx = 0
        current_layer = self.attack_config_list[0][4]
        idx = 0
        for attack_config in self.attack_config_list:
            target_layer_onnx_list = []
            for layer_onnx_name in self.attack_layers_onnx:
                target_layer_onnx_list.append(list(self.__find_node_by_name(self.quant_model, layer_onnx_name).items()))

            if attack_config[4] != current_layer:
                layer_idx = layer_idx + 1
                current_layer = attack_config[4]

            filter_idx = attack_config[2]
            kernel_idx = attack_config[3]
            elem_idx = attack_config[-1]

            quant_weight = target_layer_onnx_list[layer_idx][2][1]
            target_quant_weight = quant_weight[filter_idx][kernel_idx].flatten()[elem_idx]

            mali_value = self.malicious_params[idx]
            quant_mali_value = round_tensor((self.bn_scales[idx] * mali_value).cpu() / self.quant_scales[idx])


            self.quant_clean_params.append(target_quant_weight)
            self.quant_malicious_params.append(quant_mali_value.tolist())

            quant_weight = quant_weight.copy()
            kernel_shape = quant_weight.shape[2]
            target_kernel = quant_weight[filter_idx][kernel_idx].flatten()
            target_kernel[elem_idx] = quant_mali_value
            target_kernel = target_kernel.reshape(kernel_shape, kernel_shape)
            quant_weight[filter_idx][kernel_idx] = target_kernel

            for initializer in self.quant_model.graph.initializer:
                if initializer.name == target_layer_onnx_list[layer_idx][2][0]:
                    new_initializer = numpy_helper.from_array(quant_weight, initializer.name)
                    self.quant_model.graph.initializer.remove(initializer)
                    self.quant_model.graph.initializer.append(new_initializer)
                    break
            idx += 1

        if file_path is not None:
            onnx.save(self.quant_model, file_path)

    #
    def __get_bn_and_quant_scale(self):
        """
            This function retrieves the batch normalization (BN) scales and quantization scales
            for the layers specified in the attack configuration. Since ONNX version 7 and above
            defaults to fusing BN and convolution layers, it is necessary to obtain the scales
            for both BN and convolution layers simultaneously.
        """
        bn_layers = []
        for layer in self.attack_layers:
            bn_layers.append(self.__get_next_layer(layer).state_dict())

        layer_idx = 0
        epsilon = 1e-6
        current_layer = self.attack_config_list[0][4]
        for attack_config in self.attack_config_list:
            target_layer_onnx_list = []
            for layer_onnx_name in self.attack_layers_onnx:
                target_layer_onnx_list.append(list(self.__find_node_by_name(self.quant_model, layer_onnx_name).items()))

            if attack_config[4] != current_layer:
                layer_idx = layer_idx + 1
                current_layer = attack_config[4]

            filter_idx = attack_config[2]

            if not bn_layers[layer_idx] or 'YOLO' in self.model_name:
                self.bn_scales.append(torch.tensor(1))
            else:
                bn_params = bn_layers[layer_idx]
                bn_scale_1 = (1 / math.sqrt(bn_params['running_var'][filter_idx] - epsilon))
                bn_scale_2 = bn_params['weight'][filter_idx]
                bn_scale = bn_scale_1 * bn_scale_2
                self.bn_scales.append(bn_scale)

            quant_scale = target_layer_onnx_list[layer_idx][3][1]
            self.quant_scales.append(quant_scale)


    def attack(self, quant=False, output_file=None):
        if quant is True:
            self.__make_malicious_model(output_file)
        else:
            self.__kernel_swap(self.malicious_params)
