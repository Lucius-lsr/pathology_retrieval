# -*- coding: utf-8 -*-
"""
@Time    : 2021/6/29 14:27
@Author  : Lucius
@FileName: dataloader.py
@Software: PyCharm
"""

import os

import torch

from data.utils import get_files_type
from torch.utils.data import Dataset, DataLoader

from models.HyperG.hyedge import pairwise_euclidean_distance
import numpy as np
import pickle


class RandomHyperGraph(Dataset):

    def __init__(self, feature_and_coordinate_dir, k, with_name=False) -> None:
        super().__init__()
        self.data_pairs = list()
        self.k = k
        self.with_name = with_name
        feature_list = get_files_type(feature_and_coordinate_dir, 'npy')
        for feature_path in feature_list:
            base_name = os.path.basename(feature_path)
            dir_name = os.path.join(feature_and_coordinate_dir, feature_path)
            if base_name == '0.npy':
                files = os.listdir(dir_name)
                if '1.npy' in files and '0.pkl' in files and '1.pkl' in files:
                    feature_coordinate_0 = (os.path.join(dir_name, '0.npy'), os.path.join(dir_name, '0.pkl'))
                    feature_coordinate_1 = (os.path.join(dir_name, '1.npy'), os.path.join(dir_name, '1.npy'))
                    self.data_pairs.append((feature_coordinate_0, feature_coordinate_1))

    def __getitem__(self, idx: int):
        feature_0 = np.load(self.data_pairs[idx][0][0])
        with open(self.data_pairs[idx][0][1], 'rb') as f:
            coordinate_0 = pickle.load(f)
        H_0 = self.get_random_H(coordinate_0, feature_0.size[0])

        feature_1 = np.load(self.data_pairs[idx][1][0])
        with open(self.data_pairs[idx][1][1], 'rb') as f:
            coordinate_1 = pickle.load(f)
        H_1 = self.get_random_H(coordinate_1, feature_1.size[0])

        if self.with_name:
            return feature_0, H_0, feature_1, H_1, os.path.dirname(self.data_pairs[idx][0][0])
        else:
            return feature_0, H_0, feature_1, H_1

    def get_random_H(self, coordinate, size):
        loc = []
        for x, y, _, _ in coordinate:
            loc.append([x, y])
        loc = np.array(loc)
        loc = loc / np.max(loc)
        dis_matrix = pairwise_euclidean_distance(torch.from_numpy(loc))
        _, nn_idx = torch.topk(dis_matrix, 2*self.k, dim=1, largest=False)

        hyedge_idx = torch.arange(size).unsqueeze(0).repeat(self.k, 1).transpose(1, 0).reshape(-1)

        # random choose k in 2 * k
        self_idx = torch.arange(nn_idx.shape[0]).reshape(-1, 1)
        nn_idx = nn_idx[:, 1:]

        sample_nn_idx = nn_idx[:, torch.randperm(2*self.k-1)]
        sample_nn_idx = sample_nn_idx[:, :self.k-1]
        sample_nn_idx = torch.cat((self_idx, sample_nn_idx), dim=1)
        H = torch.stack([sample_nn_idx.reshape(-1), hyedge_idx])

        return H

    def __len__(self) -> int:
        return len(self.data_pairs)


def get_dataset(feature_and_coordinate_dir, k, with_name=False):
    dataset = RandomHyperGraph(feature_and_coordinate_dir, k, with_name)
    return dataset


if __name__=='__main__':
    FEATURE_DIR = '/Users/lishengrui/client/tmp'
    COORDINATE_DIR = '/Users/lishengrui/client/tmp'
    dataset = get_dataset(FEATURE_DIR, 10)
    dataloader = DataLoader(dataset, batch_size=1, shuffle=False, num_workers=1)

    for i, (feature_0, H0, feature_1, H1) in enumerate(dataloader):
        print(i)