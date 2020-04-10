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


#train_valid_ds = gdata.vision.ImageFolderDataset('D:/DataSet/Stabford_Dogs_Dataset/Images',flag=1)
train_valid_ds = gdata.vision.ImageFolderDataset('D:/DataSet/dog-breed-identification/te',flag=1)
batch_size = 128
transform_train_224 = gdata.vision.transforms.Compose([
    # 224*224
    gdata.vision.transforms.RandomResizedCrop(224,scale=(0.08,1.0),ratio=(3.0/4.0,4.0/3.0)),
    #gdata.vision.transforms.RandomFlipLeftRight(),
    #gdata.vision.transforms.RandomColorJitter(brightness=0.4,contrast=0.4,saturation=0.4),
    # add random noise
    #gdata.vision.transforms.RandomLighting(0.1),
    gdata.vision.transforms.ToTensor(),
    # normalize channels
    #gdata.vision.transforms.Normalize([0.485, 0.456, 0.406],
     #                                 [0.229, 0.224, 0.225])
])
transform_train_299 = gdata.vision.transforms.Compose([
    # 224*224
    gdata.vision.transforms.RandomResizedCrop(299,scale=(0.08,1.0),ratio=(3.0/4.0,4.0/3.0)),
    #gdata.vision.transforms.RandomFlipLeftRight(),
    #gdata.vision.transforms.RandomColorJitter(brightness=0.4,contrast=0.4,saturation=0.4),
    # add random noise
    #gdata.vision.transforms.RandomLighting(0.1),
    gdata.vision.transforms.ToTensor(),
    # normalize channels
    #gdata.vision.transforms.Normalize([0.485, 0.456, 0.406],
     #                                 [0.229, 0.224, 0.225])
])
#train_valid_iter = gdata.DataLoader(train_valid_ds.transform_first(transform_train),batch_size,shuffle=True,last_batch='keep')
train_valid_iter_224 = gdata.DataLoader(train_valid_ds.transform_first(transform_train_224),batch_size,last_batch='keep')
train_valid_iter_299 = gdata.DataLoader(train_valid_ds.transform_first(transform_train_299),batch_size,last_batch='keep')
def show_fashion_mnist_224(images, labels):
    d2l.use_svg_display()
    _, figs = d2l.plt.subplots(1, len(images), figsize=(12,12))
    for f, img, lbl in zip(figs, images, labels):
        f.imshow(img.reshape((224, 224)).asnumpy())
        f.set_title(lbl)
        f.axes.get_xaxis().set_visible(True)
        f.axes.get_yaxis().set_visible(True)
def show_fashion_mnist_299(images, labels):
    d2l.use_svg_display()
    _, figs = d2l.plt.subplots(1, len(images), figsize=(12,12))
    for f, img, lbl in zip(figs, images, labels):
        f.imshow(img.reshape((299, 299)).asnumpy())
        f.set_title(lbl)
        f.axes.get_xaxis().set_visible(True)
        f.axes.get_yaxis().set_visible(True)
n = 0
XX = []
yy = []
i = 0

for X,y in train_valid_iter_224:
    n += 1
    if n>2:
        break
    else:
        XX.append(X[0])
        print(X[0])
        yy.append(str(y))
show_fashion_mnist_224(XX[0],yy[0])
def get_features(model_name, data_iter):
    net = models.get_model(model_name, pretrained=True)
    features = []
    net = models.get_model('inceptionv3', pretrained=True)
    for X,Y in data_iter:
        print(X.shape)
        y=Y
        feature = net.features(mx.nd.array(X))
        print(feature)
        print(Y)
        feature = gluon.nn.Flatten()(feature)
        features.append(feature.as_in_context(mx.cpu()))

    features = nd.concat(*features, dim=0)
    return features
features = []
ｙ= []
#model_names = ['inceptionv3', 'resnet152_v1']
model_names = ['inceptionv3']
for model_name in model_names:
    if model_name == 'inceptionv3':
        features.append(get_features(model_name, train_valid_iter_299))
    else:
        features.append(get_features(model_name, train_valid_iter_224))
for _,Y in train_valid_iter_299:
        y.extend(Y)
y = nd.concat(*y, dim=0)
print(y)
print(features)
#features.append(get_features('inceptionv3', train_valid_iter_224))
def softmax(X):
    X_exp = X.exp()
    partition = X_exp.sum(axis=1, keepdims=True)
    return X_exp / partition  # 这里应用了广播机制


features = nd.concat(*features, dim=1)
print(features)
print(y)
data_iter_train = gluon.data.DataLoader(gluon.data.ArrayDataset(features, y), batch_size, shuffle=True)


def build_model():
    net = nn.HybridSequential()
    with net.name_scope():
        net.add(nn.BatchNorm())
        net.add(nn.Dense(1024))
        net.add(nn.BatchNorm())
        net.add(nn.Activation('relu'))
        net.add(nn.Dropout(0.5))
        net.add(nn.Dense(120))

    net.initialize(ctx=ctx)
    net.hybridize()
    return net
ctx = mx.gpu() # 训练的时候为了简化计算，使用了单 GPU
softmax_cross_entropy = gluon.loss.SoftmaxCrossEntropyLoss()

def accuracy1(output, labels):
    aa=nd.argmax(output, axis=1)
    #print(aa.shape)
    aaa=np.array(aa[0])
    #print(aaa)
    #print(aaa)
    #print(labels)
    #return nd.mean(nd.argmax(output, axis=1) == labels).asscalar()
    return nd.argmax(aa, axis=1) == labels

def accuracy(output, labels):
    #print("output")
    #print(output.argmax(axis=1))
    return (output.argmax(axis=1)==labels.astype('float32')).mean().asscalar()
def evaluate(net, data_iter):
    loss, acc, n = 0., 0., 0.
    steps = len(data_iter)
    #print(steps+"steps")
    for data, label in data_iter:
        data, label = data.as_in_context(ctx), label.as_in_context(ctx)
        output = net(data)
        acc += accuracy(output, label)
        loss += nd.mean(softmax_cross_entropy(output, label)).asscalar()
    return loss/steps, acc/steps


net = build_model()

epochs = 10
batch_size = 128
lr_sch = mx.lr_scheduler.FactorScheduler(step=1500, factor=0.5)
trainer = gluon.Trainer(net.collect_params(), 'adam',
                        {'learning_rate': 1e-3, 'lr_scheduler': lr_sch})

for epoch in range(epochs):
    train_loss = 0.
    train_acc = 0.
    steps = len(data_iter_train)
    # print(steps)
    for data, label in data_iter_train:
        data, label = data.as_in_context(ctx), label.as_in_context(ctx)
        with autograd.record():
            output = net(data)
            loss = softmax_cross_entropy(output, label)

        loss.backward()
        trainer.step(batch_size)

        train_loss += nd.mean(loss).asscalar()
        print(label)
        # print(np.argmax(output))
        # print(output.shape)
        train_acc += accuracy(output, label)
        # accuracy(output, label)

    print("Epoch %d. loss: %.4f, acc: %.2f%%" % (epoch + 1, train_loss / steps, train_acc / steps * 100))
    # print("Epoch %d. loss: %.4f" % (epoch+1, train_loss/steps))
net.export('test')