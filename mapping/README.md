# Mapping

Georeferencing the drones footage into a predicted location on a map.

The drone footage contains key information about where the drone is located through features such as buildings, roads and field boundaries.
This can be referenced back to a map in order to find where these features are, a process the human brain does naturally when looking at the imagery.

To do this a Siamese network is used which calculates the similarity between a still from the drone footage and a patch of the map image. This network uses a ResNet18 backbone that has been pretrained on earth observation tasks using satellite images [github](https://github.com/zhu-xlab/SSL4EO-S12), [paper](https://arxiv.org/abs/2211.07044).
This trained backbone has model weights that have already learnt how to extract useful features for remote sensing images. The first and last layers are trained to suit out task. The network outputs an embedding that represents the features in the images and this is used to calculate the similarity between images. 
This is then trained on the [LandCover.ai](https://landcover.ai.linuxpolska.com/) to learn to predict the similarity metrics through taking a triplet of image patches from a large orthophoto, the anchor as the unmodified patch, the positive image of the same patch transformed and a negative of a random patch from elsewhere in the image.
The triplet loss function is then used to train the model.

During inference the map image is sliced into overlapping patches and the one most similar to the drone footage still is predicted. The location of the centre pixel of this patch is then located and returned.

# Requirements
pytorch, torchvision, torchgeo, cv2

# Swapping models

The code has been designed with the intention to make swapping out models easy. A class is passed to the geolocation code that has __call__ implemented so that when called on a drone image patch and a map image patch the model is called and the embeddings returned. This should allow easy modifcation during any further work in order to change the model.