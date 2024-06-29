from utils import *
from attack_analysis import attack_analysis
import pickle
import pandas as pd


if __name__ == '__main__':
    args = parse_arguments()

    model = get_model(args.model)

    atk_analysis = attack_analysis(
        model
    )

    pass


