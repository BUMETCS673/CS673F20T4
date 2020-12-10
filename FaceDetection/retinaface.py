import cv2
import numpy as np
import colorsys
import os
import torch
import torch.nn as nn
import torch.backends.cudnn as cudnn
from PIL import Image,ImageFont, ImageDraw
from torch.autograd import Variable
from nets.retinaface import RetinaFace
from utils.config import cfg_mnet, cfg_re50
from utils.anchors import Anchors
from utils.box_utils import decode, decode_landm, non_max_suppression

def preprocess_input(image):
    image -= np.array((104, 117, 123),np.float32)
    return image

class Retinaface(object):
    _defaults = {
        "model_path": 'logs/Epoch50-Total_Loss4.8523.pth',
        "confidence": 0.5,
        "backbone": "mobilenet",
        "cuda": True
    }

    @classmethod
    def get_defaults(cls, n):
        if n in cls._defaults:
            return cls._defaults[n]
        else:
            return "Unrecognized attribute name '" + n + "'"

    #---------------------------------------------------#
    #   Initialize Retinaface
    #---------------------------------------------------#
    def __init__(self, **kwargs):
        self.__dict__.update(self._defaults)
        if self.backbone == "mobilenet":
            self.cfg = cfg_mnet
        else:
            self.cfg = cfg_re50
        self.generate()

    #---------------------------------------------------#
    #   Get all the categories
    #---------------------------------------------------#
    def generate(self):
        os.environ["CUDA_VISIBLE_DEVICES"] = '0'
        self.net = RetinaFace(cfg=self.cfg, phase='eval').eval()

        # Speed up the efficiency of model training
        print('Loading weights into state dict...')
        
        state_dict = torch.load(self.model_path)
        self.net.load_state_dict(state_dict)
        if self.cuda:
            self.net = nn.DataParallel(self.net)
            self.net = self.net.cuda()
        print('Finished!')

    #---------------------------------------------------#
    #   Detect images
    #---------------------------------------------------#
    def detect_image(self, image):
        # Draw face rectangle
        old_image = image.copy()

        image = np.array(image,np.float32)
        im_height, im_width, _ = np.shape(image)

        # Its function is to convert the normalized frame coordinates into the size of the original image
        scale = torch.Tensor([np.shape(image)[1], np.shape(image)[0], np.shape(image)[1], np.shape(image)[0]])
        scale_for_landmarks = torch.Tensor([np.shape(image)[1], np.shape(image)[0], np.shape(image)[1], np.shape(image)[0],
                                            np.shape(image)[1], np.shape(image)[0], np.shape(image)[1], np.shape(image)[0],
                                            np.shape(image)[1], np.shape(image)[0]])

        # pytorch
        image = preprocess_input(image).transpose(2, 0, 1)
        # Add batch_ Size dimension
        image = torch.from_numpy(image).unsqueeze(0)
        # Compute prior boxes - anchors
        anchors = Anchors(self.cfg, image_size=(im_height, im_width)).get_anchors()

        with torch.no_grad():
            if self.cuda:
                scale = scale.cuda()
                scale_for_landmarks = scale_for_landmarks.cuda()
                image = image.cuda()
                anchors = anchors.cuda()

            loc, conf, landms = self.net(image)  # forward pass
            
            boxes = decode(loc.data.squeeze(0), anchors, self.cfg['variance'])
            boxes = boxes * scale
            boxes = boxes.cpu().numpy()

            conf = conf.data.squeeze(0)[:,1:2].cpu().numpy()
            
            landms = decode_landm(landms.data.squeeze(0), anchors, self.cfg['variance'])
            landms = landms * scale_for_landmarks
            landms = landms.cpu().numpy()

            boxes_conf_landms = np.concatenate([boxes,conf,landms],-1)
            
            boxes_conf_landms = non_max_suppression(boxes_conf_landms, self.confidence)
    
        for b in boxes_conf_landms:
            text = "{:.4f}".format(b[4])
            b = list(map(int, b))
            cv2.rectangle(old_image, (b[0], b[1]), (b[2], b[3]), (0, 0, 255), 2)
            cx = b[0]
            cy = b[1] + 12
            cv2.putText(old_image, text, (cx, cy),
                        cv2.FONT_HERSHEY_DUPLEX, 0.5, (255, 255, 255))

            # landms
            cv2.circle(old_image, (b[5], b[6]), 1, (0, 0, 255), 4)
            cv2.circle(old_image, (b[7], b[8]), 1, (0, 255, 255), 4)
            cv2.circle(old_image, (b[9], b[10]), 1, (255, 0, 255), 4)
            cv2.circle(old_image, (b[11], b[12]), 1, (0, 255, 0), 4)
            cv2.circle(old_image, (b[13], b[14]), 1, (255, 0, 0), 4)
        return old_image