import torch
import json
import os
from collections import Counter
import copy
import numpy as np


class attack_analysis():
    def __init__(self, model, x_data, y_data, class_name, json_data=None, dna_size=0, attack_layers=None):
        self.model = model
        self.x_data = x_data
        self.y_data = y_data
        self.class_name = class_name
        self.json_data = json_data
        self.dna_size = dna_size
        self.attack_layers = attack_layers
        self.orgLayerWeight = None
        self.attack_config_list = None
        self.malicious_params = None

    def get_predict(self):
        total = 0
        top1_correct = 0
        top5_correct = 0
        with torch.no_grad():
            outputs = self.model(self.x_data)
            _, predicted = torch.max(outputs, 1)
            total += self.y_data.size(0)
            top1_correct += (predicted == self.y_data).sum().item()

            _, predicted_top5 = torch.topk(outputs, 5, dim=1)
            top5_correct += sum(self.y_data[i].item() in predicted_top5[i] for i in range(self.y_data.size(0)))

        top1_accuracy = top1_correct / total
        top5_accuracy = top5_correct / total

        return top1_accuracy, top5_accuracy


    def get_topX_categories(self, topNum=50):
        result_list = []
        with torch.no_grad():
            outputs = self.model(self.x_data)
            _, predicted = torch.max(outputs, 1)
            result_list.extend(predicted.tolist())
        catego = Counter(result_list).most_common(topNum)
        categoriesDict = {}
        class_list = self.class_name[:]

        for i in range(len(catego)):
            categoriesDict[self.class_name[catego[i][0]]] = catego[i][1]
            class_list.remove(self.class_name[catego[i][0]])

        for i in range(len(class_list)):
            categoriesDict[class_list[i]] = 0

        return categoriesDict


    def set_attack_configs(self, attack_configs):
        self.attack_config_list = attack_configs


    def set_malicious_params(self, malicious_params):
        self.malicious_params = malicious_params


    def read_json(self, filename):

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
        self.read_json(file)
        attack_configs = self.json_data['member_0']['kernel_idx']
        attack_params = self.json_data['member_0']['bestAttackedWeight']
        attack_layers = list({item[4] for item in attack_configs})

        self.set_attack_configs(attack_configs)
        self.set_malicious_params(attack_params)
        self.set_atk_layer(attack_layers)


    def set_atk_layer(self, attack_layers):
        self.attack_layers = attack_layers
        self.orgLayerWeight = self.__get_layer_weight()

    def print_attack_config(self):
        attack_layers = list({item[4] for item in self.attack_config_list})
        print(f"Total attack kernel number = {len(attack_layers)}. Total attack element number = {len(self.attack_config_list)}")
        layers = {}
        for item in self.attack_config_list:
            layer = item[4]
            filter_index = item[2]
            kernel_index = item[3]
            elem_index = item[6]

            key = (layer, filter_index, kernel_index)
            if key not in layers:
                layers[key] = []
            layers[key].append(elem_index)

        for (layer, filter_index, kernel_index), elem_indices in layers.items():
            elem_str = ', '.join([f'elem_index#{i + 1} = {elem}' for i, elem in enumerate(elem_indices)])
            print(f"Attack {layer}, filter index= {filter_index}, kernel index= {kernel_index},\n    {elem_str}")

    def recover(self):
        for layer_idx in range(len(self.attack_layers)):
            layer_param = dict(self.model.named_parameters()).get(self.attack_layers[layer_idx] + '.weight')
            layer_param.data.copy_(self.orgLayerWeight[layer_idx])


    def kernel_swap(self, dna, recover=True):
        layer_param_dict = {}

        if recover is True:
            self.recover()

        for layer_idx in range(len(self.attack_layers)):
            # get filter
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

    def attack(self):
        self.kernel_swap(self.malicious_params)

    def set_dna_size(self):
        pass

    def get_hamming_distance(self):
        pass

    def k_sim(self):
        pass


