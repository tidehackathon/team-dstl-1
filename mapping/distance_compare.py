''' Distances of drone view and map images '''
import numpy as np
import torch
import os
import cv2
import matplotlib.pyplot as plt
import random

import torchvision.transforms.functional as F

def find_closest_dist(map_img, patch_imgs, patch_size=256, stride_size=128, process=None, return_patches=False):
    '''
    Euclidiean distance between an image and a patches of a larger image
    Input:
        - map_img: large image as np arrary
        - patch_img: list of small images as np arrary
        - patch_size=256: optional
        - stride_size=128: optional 
        - process=None: optional, function/class to process images if needed, takes in patch and patch and returns this
    Returns:
        - predicted patch coords and tensor of distances
    '''
    # split map into patches
    map_img = F.to_tensor(map_img).unsqueeze(0)
    patches = map_img.unfold(2, patch_size, stride_size).unfold(3, patch_size, stride_size)
    num_images_x = patches.shape[-3]
    num_images_y = patches.shape[-4]
    
    # compare patches to map
    euc_dist = torch.nn.PairwiseDistance()
    distances = torch.zeros((len(patch_imgs), num_images_y, num_images_x))
    for n, patch_img in enumerate(patch_imgs):
        patch_img = F.to_tensor(patch_img)
        for i in range(num_images_x):
            for j in range(num_images_y):
                    patch_image = patch_img.clone()
                    patch = patches[0, 0, j, i]
                    if process:
                        # this where smarter embedding can go
                        patch_image, patch = process(patch_image, patch)
                    dist = euc_dist(patch_image, patch).mean().item()
                    distances[n, j, i] = dist
    
    # sum distances over first axis
    distances = torch.sum(distances, 0)
    # identify closest
    amin = distances.argmin()
    predx = amin%num_images_x
    predy = amin//num_images_x

    if return_patches:
        return predx.item(), predy.item(), distances, patches
    else:
        return predx.item(), predy.item(), distances

if __name__=='__main__':
    IMG_DIR = 'landcover.ai.v1/images'
    MAP_DIR = 'landcover.ai.v1/masks'

    # get full sat image
    full_image = cv2.imread(os.path.join(IMG_DIR, os.listdir(IMG_DIR)[1]))
    full_image = cv2.resize(full_image, (2560, 2560))
    full_image = cv2.cvtColor(full_image, cv2.COLOR_BGR2GRAY)
    full_image = F.to_tensor(full_image).unsqueeze(0)

    # get full seg image / map
    map_image = cv2.imread(os.path.join(MAP_DIR, os.listdir(MAP_DIR)[1]))
    map_image = cv2.resize(map_image, (2560, 2560))
    map_image = cv2.cvtColor(map_image, cv2.COLOR_BGR2GRAY)

    # get a random patch from the image
    patch_size = 256
    stride_size = 128
    patches = full_image.unfold(2, patch_size, stride_size).unfold(3, patch_size, stride_size)
    num_images_x = patches.shape[-3]
    num_images_y = patches.shape[-4]
    x = random.randint(0, num_images_x-1)
    y = random.randint(0, num_images_y-1)
    patch_img = patches[0, 0, y, x].numpy()
    print(x, y)

    # get comparisons
    predx, predy, distances = find_closest_dist(map_image, [patch_img], patch_size=256, stride_size=128)
    print(predx, predy)
    






