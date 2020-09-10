import pandas as pd
import numpy as np
from catboost import CatBoostClassifier
import torch

from train_nn import train_nn

import models

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def gbm_predict(data):
    model = CatBoostClassifier()
    model.load_model('./models/gbm.cbm')
    
    output = model.predict(data)

    return output

def nn_predict(data):
    model = models.LSTM(output_size=64).to(device)
    checkpoint = torch.load('./models/nn.hdf5', map_location=torch.device('cpu'))
    model.load_state_dict(checkpoint['model_state_dict'])
    
    model.eval()

    data = np.array(data[1:-1].split(', ')).astype(float)
    data = torch.tensor(data).float()

    predict = model.predict(data)
    return predict

def maint_predict(data):
    nn_input = data['past_vib']
    nn_out = nn_predict(nn_input).tolist()

    data['next_mean_64hrs'] = np.mean(nn_out)
    data['next_std_64hrs'] = np.std(nn_out)

    gbm_input = pd.Series(data).drop(['past_vib'])

    print(gbm_input)

    gbm_out = gbm_predict(gbm_input)

    return gbm_out

if __name__ == "__main__":
    df = pd.read_csv('./data/small_df.csv')
    s = df.iloc[0]
    print(maint_predict(s))