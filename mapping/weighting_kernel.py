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
    mapping_space: tuple (n, m) that describes the dimensions of the grid e.g. (10,10)
    location_history: list of tuples that describe last known locations within the mapping space e.g. [(2,2), (2,3)]
    Outputs:
    tile_weights: n*m matrix of weights
    """
    #get last known location
    last_known_loc = location_history[-1]    #get a matrix with gaussian blur
    tile_weights = gaussian_kernel(mapping_space[0], mapping_space[1], 1, 1)    #identify center of mapping space and how far we need to shift to get to last known location
    center = (int(mapping_space[0]/2), int(mapping_space[1]/2))
    shift = (center[0] - last_known_loc[0], center[1]-last_known_loc[1])    #shift so that center of gaussian is at last known location
    tile_weights = np.roll(tile_weights, shift[0], 0)
    tile_weights = np.roll(tile_weights, shift[1], 1)    
    return tile_weights

class LocationWeighting():
    def __init__(self, patches_shape, location_history, sigma_x=1, sigma_y=1):
        self.patches_shape = patches_shape
        self.location_history = location_history
        self.kernel = self.gaussian_kernel(patches_shape[0], patches_shape[1], 1, 1)

    @staticmethod
    def gaussian_kernel(dimension_x, dimension_y, sigma_x, sigma_y):
        x = cv2.getGaussianKernel(dimension_x, sigma_x)
        y = cv2.getGaussianKernel(dimension_y, sigma_y)
        kernel = x.dot(y.T)
        return kernel
    
    def get_map_weights(self, mapping_space):
        """
        Inputs:
        mapping_space: tuple (n, m) that describes the dimensions of the grid e.g. (10,10)
        location_history: list of tuples that describe last known locations within the mapping space e.g. [(2,2), (2,3)]
        Outputs:
        tile_weights: n*m matrix of weights
        """
        #get last known location
        last_known_loc = self.location_history[-1]    #get a matrix with gaussian blur
        center = (int(mapping_space[0]/2), int(mapping_space[1]/2))
        shift = (center[0] - last_known_loc[0], center[1]-last_known_loc[1])    #shift so that center of gaussian is at last known location
        tile_weights = self.kernel
        tile_weights = np.roll(tile_weights, shift[0], 0)
        tile_weights = np.roll(tile_weights, shift[1], 1)    
        return tile_weights
    
    def __call__(self, distances):
        mapping_space = distances.shape[-2:]
        tile_weights = self.get_map_weights(mapping_space)
        return tile_weights @ distances