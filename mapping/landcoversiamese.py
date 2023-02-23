''' Landcover dataloader for triplet model training '''
import cv2
import os
import numpy as np
import random
from torch import nn
from torch.utils.data import Dataset
from torchgeo.models import resnet18, ResNet18_Weights
from torchvision.transforms.functional import to_tensor

class LandcoverAITriplet(Dataset):
    """Landcover AI Dataset read to return appropiate for triplet loss.
    Takes two random patches from the large orthophotos, first patch is copied to make pos and anchor.
    Second patch is used as neg.
    
    Dataset features:
    * land cover from Poland, Central Europe
    * three spectral bands - RGB
    * 33 orthophotos with 25 cm per pixel resolution (~9000x9500 px)
    * 8 orthophotos with 50 cm per pixel resolution (~4200x4700 px)
    * total area of 216.27 km\ :sup:`2`
    Dataset format:
    * rasters are three-channel GeoTiffs with EPSG:2180 spatial reference system
    * masks are single-channel GeoTiffs with EPSG:2180 spatial reference system
    Dataset classes:
    1. building (1.85 km\ :sup:`2`\ )
    2. woodland (72.02 km\ :sup:`2`\ )
    3. water (13.15 km\ :sup:`2`\ )
    4. road (3.5 km\ :sup:`2`\ )
    
    Citation:
    * https://arxiv.org/abs/2005.02264v3 """

    def __init__(self, folder, transform=None, anchor_type='map'):
        """
        Args:
            folder: folder containing the landcover.ai data, 
            images and masks are presumed to be inside
            transforms: =None
        """
        self.img_folder = os.path.join(folder, 'images')
        self.img_files = os.listdir(self.img_folder)
        self.mask_folder = os.path.join(folder, 'masks')
        self.mask_files = os.listdir(self.mask_folder)
        self.transform = transform
        self.anchor_type = anchor_type

    def __len__(self):
        return len(self.img_files)*3

    def __getitem__(self, idx):
        full_image = cv2.imread(os.path.join(self.img_folder, self.img_files[idx//3]))
        full_mask = cv2.imread(os.path.join(self.mask_folder, self.mask_files[idx//3]))
        # resize whole to constant
        full_image = cv2.resize(full_image, (5120, 5120))
        full_image = (full_image/255).astype(np.float32)
        full_mask = cv2.resize(full_mask, (5120, 5120))
        full_mask[full_mask==2] = 0
        full_mask = full_mask/4
        full_mask = full_mask.astype(np.float32)
        # pick random patch
        patchx = random.randint(0, 4608)
        patchy = random.randint(0, 4608)
        pos_patch = full_image[patchx:patchx+512, patchy:patchy+512]
        anchor = full_mask[patchx:patchx+512, patchy:patchy+512]
        pos_patch = cv2.cvtColor(pos_patch, cv2.COLOR_BGR2GRAY)
        anchor = cv2.cvtColor(anchor, cv2.COLOR_BGR2GRAY)
        # pick random other patch
        patchx = random.randint(0, 4608)
        patchy = random.randint(0, 4608)
        neg_patch = full_image[patchx:patchx+512, patchy:patchy+512]
        neg_patch = cv2.cvtColor(neg_patch, cv2.COLOR_BGR2GRAY)
        if self.anchor_type=='image':
            anchor = pos_patch.copy()
        if self.transform:
            anchor = to_tensor(anchor).float()
            pos_patch = to_tensor(pos_patch).float()
            neg_patch = to_tensor(neg_patch).float()
            anchor, pos_patch, neg_patch = self.transform(anchor, pos_patch, neg_patch)
        else:
            anchor = to_tensor(anchor).float()
            pos_patch = to_tensor(pos_patch).float()
            neg_patch = to_tensor(neg_patch).float()
        
        return anchor, pos_patch, neg_patch

class LandSiamese(nn.Module):
    def __init__(self):
        super().__init__()
        self.flatten = nn.Flatten()
        self.resnet = resnet18(weights=ResNet18_Weights.SENTINEL2_RGB_MOCO)
        self.resnet.conv1 = nn.Conv2d(1, 64, kernel_size=(7, 7), stride=(2, 2), padding=(3, 3), bias=False)
        self.resnet.fc = nn.Sequential(nn.Linear(in_features=512, out_features=128),
                                        nn.Linear(in_features=128, out_features=64)
                                        )

    def forward_one(self, x):
        return self.flatten(self.resnet(x))

    def forward(self, anchor, pos, neg):
        anchor = self.forward_one(anchor)
        pos = self.forward_one(pos)
        neg = self.forward_one(neg)
        return anchor, pos, neg