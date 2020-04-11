import collections
import d2lzh as d2l
import matplotlib.pyplot as plt
import math
import mxnet as mx
import numpy as np
from mxnet import autograd, gluon, init, nd
from mxnet.gluon import data as gdata, loss as gloss, model_zoo, nn
from mxnet.gluon.model_zoo import vision as models
import os
import shutil
import time
import zipfile
from collections import namedtuple



symnet = mx.symbol.load('test-symbol.json')
mod = mx.mod.Module(symbol=symnet, context=mx.cpu())
mod.bind(data_shapes=[('data', (1, 2048))])
mod.load_params('test-0000.params')
Batch = namedtuple('Batch', ['data'])
import cv2
img = cv2.imread('D:/DataSet/dog-breed-identification/te/afghan_hound/26d012ce945eff58576c47e6e84140b6.jpg',1)
width = 299
height = 299
#new_img = cv2.resize(img,(width,height)).transpose((2, 0, 1))
new_img = cv2.resize(img,(width,height))
X_299_test = nd.zeros((1, 3, 299, 299))
X_299_test = mx.nd.array(new_img)
transformer=gdata.vision.transforms.ToTensor()
print(transformer(X_299_test))
data_test_iter_299 = gluon.data.DataLoader(gluon.data.ArrayDataset(transformer(X_299_test)),
                                           batch_size=128,last_batch='keep')
x=[]
features = []
net1 = models.get_model('inceptionv3', pretrained=True)
for data_iter in data_test_iter_299:
    data_iter=data_iter.reshape(1,3,299,299)
    print(data_iter)
    feature = net1.features(data_iter)
    print(feature)
    feature = gluon.nn.Flatten()(feature)
    features.append(feature.as_in_context(mx.cpu()))
x = nd.concat(*features, dim=0)
print(x)
#x.append(get_features('inceptionv3', new_img))
mod.forward(Batch([x]))
out = mod.get_outputs()
prob = out[0]
predicted_labels = prob.argmax(axis=1)
print(predicted_labels)