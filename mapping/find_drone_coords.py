import numpy as np
import torch
import os
import time
import cv2
import matplotlib.pyplot as plt
import rasterio

import torchvision.transforms.functional as F

from landcoversiamese import *
from train_siamese import *
from distance_compare import *


class ProcessImagesSiamese(nn.Module):
    '''Class to process images and patches with using the Siamese model'''
    def __init__(self, model_path='../mapping/models/landcoversiamese_augmented_nth_hour_model.pt', device='cuda'):
        '''Initiates a LandSiamese model from the given model path and the device to send the model to.
        Input:
            - model_path='../mapping/models/landcoversiamese_augmented_nth_hour_model.pt',
            - device='cuda'
        '''
        super().__init__()
        self.device = device

        model = LandSiamese()
        model.load_state_dict(torch.load(model_path))
        model.to(device)
        self.model = model
        self.model.eval()

    def __call__(self, patch_img, patch):
        ''' Gets feature embedding from the model.
        Input:
            - patch_img: tensor representing image from the drone
            - patch: tensor representing an image patch from the map image
        Returns:
            patch_img, patch
        '''
        device = self.device

        patch_img = F.resize(patch_img, [512, 512])
        patch = F.resize(patch.unsqueeze(0), [512, 512])
        patch_img = self.model.forward_one(patch_img.unsqueeze(0).to(device)).squeeze().to('cpu')
        patch = self.model.forward_one(patch.unsqueeze(0).to(device)).squeeze().to('cpu')
        return patch_img, patch

def drone_image_to_coords(
                        drone_image,
                        map,
                        patch_size=512,
                        stride_size=128,
                        weighting=None,
                        return_patches=False,
                        process_images=ProcessImagesSiamese(),
                        ):
    '''
    Input:
        - drone_image: numpy array image
        - map: rasterio geotiff file
        - patch_size=512: size of patch to slice map image into
        - stride_size=128: stride between image patches
        - weighting=None: space to place a class to add probability weighting to the locations
        - return_patches=False: whether to return predicted patches and array of distances or not
        - process_images=ProcessImagesSiamese(): class to process the images
    
    Returns:
        - Co-ords of prediction, lat lon
        Optional:
        - numpy array of predicted patch image
        - distances: numpy array of distances of patches to drone image
    
    '''
    # get map image
    map_img = np.stack([map.read(1), map.read(2), map.read(3)], axis=2)
    map_img = map_img/map_img.max()
    map_img = cv2.resize(map_img, (2560, 2560)) # magic numbers
    map_img = map_img.astype(np.float32)

    # get drone image and split into square patches
    drone_image = cv2.cvtColor(drone_image, cv2.COLOR_BGR2GRAY)
    drone_image = (drone_image/drone_image.max()).astype(np.float32)
    h, w = drone_image.shape
    patch_img1 = drone_image[:, :h]
    patch_img2 = drone_image[:, (w-h):]
    k = int(((w-h)/2))
    #patch_img3 = drone_image[:, k:(k+h)]
    # resize patches into 512 x 512
    patch_img1 = cv2.resize(patch_img1, (patch_size, patch_size)) # more magic numbers
    patch_img2 = cv2.resize(patch_img2, (patch_size, patch_size))
    #patch_img3 = cv2.resize(patch_img3, (patch_size, patch_size))

    drone_patches = [patch_img1, patch_img2]

    # dist func returns pooled predictions
    predx, predy, distances, patches = find_closest_dist(
                                            map_img.astype(np.float32), 
                                            drone_patches,
                                            patch_size=patch_size,
                                            stride_size=stride_size,
                                            process=process_images,
                                            return_patches=True)  

    # add a weighting filter to the distances
    if weighting:
        # does this need to be a func?
        pass
        
    # get co-ords
    xmap = predx*stride_size+(0.5*patch_size)
    ymap = predy*stride_size+(0.5*patch_size)
    x, y = map.xy(ymap, xmap)

    if return_patches:
        return (y, x), patches[0, 0, predy, predx], distances
    else:
        return (y, x)


if __name__ == '__main__':
    IMG_DIR = 'data/test_images/images'
    MAP_IMG = 'maptiler-35_107470-48_571642.tiff'
    drone_images = os.listdir(IMG_DIR)

    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    device ='cpu'
    print(device)
    for i, drone_image_name in enumerate(drone_images):
        drone_image = cv2.imread(os.path.join(IMG_DIR, drone_image_name))
        map = rasterio.open(MAP_IMG)

        t0 = time.time()
        coords, predicted_patch, distances = drone_image_to_coords(drone_image, map, patch_size=512, stride_size=128, return_patches=True)
        t1 = time.time()

        total_time = t1-t0

        print(f'Predicted co-ordinates for image {drone_image_name[-7:-5]}: ', coords)
        print('Time: ', total_time)
        print()

        # code for visualisation
        drone_image = cv2.cvtColor(drone_image, cv2.COLOR_BGR2GRAY)
        map_img = np.stack([map.read(1), map.read(1), map.read(1)], axis=2)
        map_img = map_img/map_img.max()
        map_img = cv2.resize(map_img, (2560, 2560))
        map_img = map_img.astype(np.float32)
        map_img = cv2.cvtColor(map_img, cv2.COLOR_BGR2GRAY)

        fig, axs = plt.subplots(1, 4, figsize=(20, 20))
        axs[0].imshow(drone_image, cmap='gray')
        axs[0].get_yaxis().set_visible(False)
        axs[0].get_xaxis().set_visible(False)
        axs[0].set_facecolor('k')
        axs[1].imshow(predicted_patch, cmap='gray')
        axs[1].get_yaxis().set_visible(False)
        axs[1].get_xaxis().set_visible(False)
        axs[1].set_facecolor('k')
        axs[2].imshow(map_img, cmap='gray')
        axs[2].get_yaxis().set_visible(False)
        axs[2].get_xaxis().set_visible(False)
        axs[2].set_facecolor('k')
        axs[3].imshow(distances, cmap='pink_r')
        axs[3].get_yaxis().set_visible(False)
        axs[3].get_xaxis().set_visible(False)
        axs[3].set_facecolor('k')
        plt.tight_layout()
        plt.savefig(f'example_images/example{drone_image_name[-7:-5]}.png', bbox_inches='tight')    
