# -*- coding: utf-8 -*-
"""
@Time    : 2021/12/17 14:38
@Author  : Lucius
@FileName: hypergraph_retrieval.py
@Software: PyCharm
"""
import argparse
import os
import torch
from utils.model.base_model import HashLayer
from utils.evaluate import Evaluator
from utils.feature import cluster_feature

num_cluster = 20
feature_in = 512
feature_out = 1024
depth = 1

def fine_tune(raw, model_dir):
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    encoder = HashLayer(feature_in, feature_out, depth)
    model_path = os.path.join(model_dir, 'ssl', 'model_best.pth')
    encoder.load_state_dict(torch.load(model_path))
    encoder = encoder.to(device)

    with torch.no_grad():
        raw = torch.from_numpy(raw).to(device)
        output = encoder(raw).cpu().detach().numpy()
    return output


if __name__ == '__main__':
    parser = argparse.ArgumentParser("Hypergraph-guided retrive")
    parser.add_argument("--MODEL_DIR", type=str, required=True, help="The path of ssl hash encoder model.")
    parser.add_argument("--DATASETS", type=list, nargs='+', required=True, help="A list of datasets.")
    args = parser.parse_args()

    os.environ["CUDA_VISIBLE_DEVICES"] = '5'
    clusters, paths = cluster_feature(0, 1, args.DATASETS)
    clusters = fine_tune(clusters, args.MODEL_DIR)
    evaluator = Evaluator()
    evaluator.add_patches(clusters, paths)
    for k in [5, 10, 15, 20, 25, 30]:
        evaluator.report_patch(k, num_cluster)

