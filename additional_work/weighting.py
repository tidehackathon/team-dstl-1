""" Code to get matrix of values with Gaussian Blur from a specific point
    (To be applied to distances matrix when applying model to own data)"""
import cv2
import numpy as np


def gaussian_kernel(dimension_x, dimension_y, sigma_x, sigma_y):
    x = cv2.getGaussianKernel(dimension_x, sigma_x)
    y = cv2.getGaussianKernel(dimension_y, sigma_y)
    kernel = x.dot(y.T)
    return kernel

def get_map_weighting(mapping_space, location_history):
    """
    Inputs:
    mapping_space: tuple (n, m) that describes the dimensions of n*m search space
    last_known_loc: tuple (x, y) that describes the point in the search space where the UAV was last known to be
    Outputs:
    tile_weights: n*m matrix of weights to apply to distance matrix
    """
    #get matrix with gaussian blur
    tile_weights = gaussian_kernel(mapping_space[0], mapping_space[1], 0.5, 0.5)
    
    #identify center of mapping space and how far we need to shift to get to last known location
    center = (int(mapping_space[0]/2), int(mapping_space[1]/2))
    shift = (center[0] - last_known_loc[0], center[1]-last_known_loc[1])
    
    #shift so that center of gaussian is at last known location
    tile_weights = np.roll(tile_weights, shift[0], 0)
    tile_weights = np.roll(tile_weights, shift[1], 1)
    
    return tile_weights