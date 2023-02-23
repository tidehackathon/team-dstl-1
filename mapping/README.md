# Mapping

Georeferencing the drones footage into a predicted location on a map.

The drone footage contains key information about where the drone is located through features such as buildings, roads and field boundaries.
This can be referenced back to a map in order to find where these features are, a process the human brain does naturally when looking at the imagery.

To do this a Siamese network is used which calculates the similarity between a still from the drone footage and a patch of the map image. This network uses a ResNet18 backbone that has been pretrained on earth observation tasks using satellite images [github](https://github.com/zhu-xlab/SSL4EO-S12), [paper](https://arxiv.org/abs/2211.07044).
This trained backbone has model weights that have already learnt how to extract useful features for remote sensing images. The first and last layers are trained to suit out task. The network outputs an embedding that represents the features in the images and this is used to calculate the similarity between images. 
This is then trained on the [LandCover.ai](https://landcover.ai.linuxpolska.com/) to learn to predict the similarity metrics through taking a triplet of image patches from a large orthophoto, the anchor as the unmodified patch, the positive image of the same patch transformed and a negative of a random patch from elsewhere in the image.
The triplet loss function is then used to train the model. This is an unsupervised training method, none of the drone footage is used during training in order to prevent data leakage and assess the generalisation potential of the model.

During inference the map image is sliced into overlapping patches and the one most similar to the drone footage still is predicted. The location of the centre pixel of this patch is then located and returned.

### Requirements
pytorch, torchvision, torchgeo, cv2, tqdm

### Swapping models

The code has been designed with the intention to make swapping out models easy. A class is passed to the geolocation code that has __call__ implemented so that when called on a drone image patch and a map image patch the model is called and the embeddings returned. This should allow easy modifcation during any further work in order to change the model.

This workflow has also been tried with a no feature extraction distances, edge detection algorithms and multiple different models.

### Siamese Network Training

Whats been tried:
Triplet loss, margin 1 and 10 tried.
Significant data augmentation - randomised perspective, crop, scale, flipping, rotation and brightness/contrast variations.
Additional data - Additional satellite images grabbed from regions around Ukraine from maptiller in order to supplement training, these are handled in the same way as the landcover.ai dataset.

Hyperparameters for demonstrated model:

##### How to train the model

run train_siamese.py

set args as follows:
DATA_FOLDER: set as folder containing images
MARGIN: margin for loss function during training, used 1 for model given
LR: learning rate during training, used 1e-4
NUM_EPOCHS: number of epochs to train for
SAVE_PATH: path to save trained models and checkpoints to

network used is the LandSiamese defined in landcoversiamese.py file

##### Data used

The training data is the [LandCover.ai](https://landcover.ai.linuxpolska.com/) datasets orthophotos. These are large satellite image patches. During training a random patch is selected from these and assigned as the anchor. The same patch is then transformed and deformed to make the positive patch image.
The negative patch image is picked from an another random patch in the image and also deformed. These three images then make one training example. The model is taught to push the embeddings of the positive image and the anchor closer together whilst moving the negative image and the anchor further apart.