import os
import torch
import os.path
import numpy as np
from PIL import Image
import cv2
import torch.nn as nn
import torch.utils.data as data
import torch.nn.functional as F  
from random import shuffle
from torch.autograd import Variable
from utils.box_utils import match, log_sum_exp

rgb_mean = (104, 117, 123) # bgr order
class MultiBoxLoss(nn.Module):
    def __init__(self, num_classes, overlap_thresh, neg_pos, cuda=True):
        super(MultiBoxLoss, self).__init__()
        # for retinaface, num_classes = 2
        self.num_classes = num_classes
        # threshold for being used to predict
        self.threshold = overlap_thresh
        # Ratio of positive and negative samples
        self.negpos_ratio = neg_pos
        self.variance = [0.1, 0.2]
        self.cuda = cuda

    def forward(self, predictions, priors, targets):
        loc_data, conf_data, landm_data = predictions
        priors = priors
        num = loc_data.size(0)
        num_priors = (priors.size(0))

        # match priors (default boxes) and ground truth boxes
        loc_t = torch.Tensor(num, num_priors, 4)
        landm_t = torch.Tensor(num, num_priors, 10)
        conf_t = torch.LongTensor(num, num_priors)
        for idx in range(num):
            truths = targets[idx][:, :4].data
            labels = targets[idx][:, -1].data
            landms = targets[idx][:, 4:14].data
            defaults = priors.data
            match(self.threshold, truths, defaults, self.variance, labels, landms, loc_t, conf_t, landm_t, idx)
            
        zeros = torch.tensor(0)
        if self.cuda:
            loc_t = loc_t.cuda()
            conf_t = conf_t.cuda()
            landm_t = landm_t.cuda()
            zeros = zeros.cuda()

        # landm Loss (Smooth L1)
        # Shape: [batch,num_priors,10]
        pos1 = conf_t > zeros
        num_pos_landm = pos1.long().sum(1, keepdim=True)
        N1 = max(num_pos_landm.data.sum().float(), 1)
        
        pos_idx1 = pos1.unsqueeze(pos1.dim()).expand_as(landm_data)
        landm_p = landm_data[pos_idx1].view(-1, 10)
        landm_t = landm_t[pos_idx1].view(-1, 10)
        loss_landm = F.smooth_l1_loss(landm_p, landm_t, reduction='sum')

        pos = conf_t != zeros
        conf_t[pos] = 1

        # Localization Loss (Smooth L1)
        # Shape: [batch,num_priors,4]
        pos_idx = pos.unsqueeze(pos.dim()).expand_as(loc_data)
        loc_p = loc_data[pos_idx].view(-1, 4)
        loc_t = loc_t[pos_idx].view(-1, 4)
        loss_l = F.smooth_l1_loss(loc_p, loc_t, reduction='sum')

        # Compute max conf across batch for hard negative mining
        batch_conf = conf_data.view(-1, self.num_classes)
        loss_c = log_sum_exp(batch_conf) - batch_conf.gather(1, conf_t.view(-1, 1))

        # Hard Negative Mining
        loss_c[pos.view(-1, 1)] = 0 # filter out pos boxes for now
        loss_c = loss_c.view(num, -1)
        _, loss_idx = loss_c.sort(1, descending=True)
        _, idx_rank = loss_idx.sort(1)
        num_pos = pos.long().sum(1, keepdim=True)
        num_neg = torch.clamp(self.negpos_ratio*num_pos, max=pos.size(1)-1)
        neg = idx_rank < num_neg.expand_as(idx_rank)

        # Confidence Loss Including Positive and Negative Examples
        pos_idx = pos.unsqueeze(2).expand_as(conf_data)
        neg_idx = neg.unsqueeze(2).expand_as(conf_data)
        conf_p = conf_data[(pos_idx+neg_idx).gt(0)].view(-1,self.num_classes)
        targets_weighted = conf_t[(pos+neg).gt(0)]
        loss_c = F.cross_entropy(conf_p, targets_weighted, reduction='sum')

        # Sum of losses: L(x,c,l,g) = (Lconf(x, c) + αLloc(x,l,g)) / N
        N = max(num_pos.data.sum().float(), 1)
        loss_l /= N
        loss_c /= N
        loss_landm /= N1

        return loss_l, loss_c, loss_landm

def rand(a=0, b=1):
    return np.random.rand()*(b-a) + a

def get_random_data(image, targes, input_shape, random=True, jitter=.1, hue=.1, sat=1.5, val=1.5):
    iw, ih = image.size
    h, w = input_shape
    box = targes

    # Scale the image and distort the length and width
    new_ar = w/h * rand(1-jitter,1+jitter)/rand(1-jitter,1+jitter)
    scale = rand(0.75,1.25)
    if new_ar < 1:
        nh = int(scale*h)
        nw = int(nh*new_ar)
    else:
        nw = int(scale*w)
        nh = int(nw/new_ar)
    image = image.resize((nw,nh), Image.BICUBIC)

    # Gray out the redundant parts of the image
    dx = int(rand(0, w-nw))
    dy = int(rand(0, h-nh))
    new_image = Image.new('RGB', (w,h), (128,128,128))
    new_image.paste(image, (dx, dy))
    image = new_image

    # flip image
    flip = rand()<.5
    if flip: image = image.transpose(Image.FLIP_LEFT_RIGHT)

    # Gamut distortion
    hue = rand(-hue, hue)
    sat = rand(1, sat) if rand()<.5 else 1/rand(1, sat)
    val = rand(1, val) if rand()<.5 else 1/rand(1, val)
  
    x = cv2.cvtColor(np.array(image,np.float32)/255, cv2.COLOR_RGB2HSV)
    x[..., 0] += hue*360
    x[..., 0][x[..., 0]>1] -= 1
    x[..., 0][x[..., 0]<0] += 1
    x[..., 1] *= sat
    x[..., 2] *= val
    x[x[:,:, 0]>360, 0] = 360
    x[:, :, 1:][x[:, :, 1:]>1] = 1
    x[x<0] = 0
    image_data = cv2.cvtColor(x, cv2.COLOR_HSV2RGB)*255 # numpy array, 0 to 1
    
    if len(box)>0:
        np.random.shuffle(box)
        box[:, [0,2,4,6,8,10,12]] = box[:, [0,2,4,6,8,10,12]]*nw/iw + dx
        box[:, [1,3,5,7,9,11,13]] = box[:, [1,3,5,7,9,11,13]]*nh/ih + dy
        if flip: 
            box[:, [0,2,4,6,8,10,12]] = w - box[:, [2,0,6,4,8,12,10]]
            box[:, [5,7,9,11,13]]     = box[:, [7,5,9,13,11]]
        box[:, 0:14][box[:, 0:14]<0] = 0
        box[:, [0,2,4,6,8,10,12]][box[:, [0,2,4,6,8,10,12]]>w] = w
        box[:, [1,3,5,7,9,11,13]][box[:, [1,3,5,7,9,11,13]]>h] = h
        
        box_w = box[:, 2] - box[:, 0]
        box_h = box[:, 3] - box[:, 1]
        box = box[np.logical_and(box_w>1, box_h>1)] # discard invalid box

    box[:,4:-1][box[:,-1]==-1]=0
    box[:, [0,2,4,6,8,10,12]] /= w
    box[:, [1,3,5,7,9,11,13]] /= h
    box_data = box
    return image_data, box_data

class DataGenerator(data.Dataset):
    def __init__(self, txt_path, img_size):
        self.img_size = img_size
        self.txt_path = txt_path
        self.imgs_path, self.words = self.process_labels()

    def process_labels(self):
        imgs_path = []
        words = []
        f = open(self.txt_path,'r')
        lines = f.readlines()
        isFirst = True
        labels = []
        for line in lines:
            line = line.rstrip()
            if line.startswith('#'):
                if isFirst is True:
                    isFirst = False
                else:
                    labels_copy = labels.copy()
                    words.append(labels_copy)
                    labels.clear()
                path = line[2:]
                path = self.txt_path.replace('label.txt','images/') + path
                imgs_path.append(path)
            else:
                line = line.split(' ')
                label = [float(x) for x in line]
                labels.append(label)
        words.append(labels)
        return imgs_path, words

    def __len__(self):
        return len(self.imgs_path)

    def get_len(self):
        return len(self.imgs_path)

    def __getitem__(self, index):
        img = Image.open(self.imgs_path[index])
        labels = self.words[index]
        annotations = np.zeros((0, 15))
        if len(labels) == 0:
            return img, annotations

        for idx, label in enumerate(labels):
            annotation = np.zeros((1, 15))
            # bbox
            annotation[0, 0] = label[0]  # x1
            annotation[0, 1] = label[1]  # y1
            annotation[0, 2] = label[0] + label[2]  # x2
            annotation[0, 3] = label[1] + label[3]  # y2

            # landmarks
            annotation[0, 4] = label[4]    # l0_x
            annotation[0, 5] = label[5]    # l0_y
            annotation[0, 6] = label[7]    # l1_x
            annotation[0, 7] = label[8]    # l1_y
            annotation[0, 8] = label[10]   # l2_x
            annotation[0, 9] = label[11]   # l2_y
            annotation[0, 10] = label[13]  # l3_x
            annotation[0, 11] = label[14]  # l3_y
            annotation[0, 12] = label[16]  # l4_x
            annotation[0, 13] = label[17]  # l4_y
            if (annotation[0, 4]<0):
                annotation[0, 14] = -1
            else:
                annotation[0, 14] = 1

            annotations = np.append(annotations, annotation, axis=0)
            
        target = np.array(annotations)

        img, target = get_random_data(img, target, [self.img_size,self.img_size])

        img = np.transpose(img - rgb_mean, (2, 0, 1))
        img = np.array(img, dtype=np.float32)
        return img, target

def detection_collate(batch):
    images = []
    targets = []
    for img, box in batch:
        if len(box)==0:
            continue
        images.append(img)
        targets.append(box)
    images = np.array(images)
    targets = np.array(targets)
    return images, targets
