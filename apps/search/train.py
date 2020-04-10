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