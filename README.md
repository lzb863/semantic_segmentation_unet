# semantic_segmentation_unet
PyTorch implementation of semantic segmentation using UNET architecture on BDD100K dataset.

**Dataset : BDD100K**

BDD100K is a largescale open source dataset for automotive usecase which consists of segmentation, object detection, lane markings, drivable areas etc. It has more than 100K HD videos recorded at various times, seasons and weather. The data is collected at 4 locations : San Fransisco, Berkley, Bay area and New york. We've shortlisted 38 objects for this project and the details are listed in the ['class_list.csv'](https://github.com/omcaaaar/semantic_segmentation_unet/blob/master/data/class_list.csv) file.

Dataset url : https://bdd-data.berkeley.edu/

We had to make few changes in the original dataset since it has 41 classes. Out of 41, first 19 classes have ground truth labels from 0-18 and rest all of the classes have a label 255. They've provided a color image for each raw image with a color mapping. From these color images we've created our own ground truth images for training. One more problem is, they've used same color for 2 classes (person and parking sign). This issue was addressed by detecting shape of the object while giving ground truth label.

The training data can be downloaded from [here](https://www.kaggle.com/ochaporkar/bdd100k-semantic-segmentation)

The data distribution is as follows:

1. Traininig : 9822 images

2. Validation : 1696 images

3. Testing : 2000 images

**Pretrained models**

[baseline-resnet50dilated-ppm_deepsup](https://www.kaggle.com/ochaporkar/semantic-segmentation-unet-baselinemodels) : keep in 'baseline-resnet50dilated-ppm_deepsup' directory.

[trained_bdd_100k_ckpt](https://www.kaggle.com/ochaporkar/semantic-segmentation-unet-trained-bdd100k) : keep in 'ckpt' directory.

[pretrained_feature_extractor](https://www.kaggle.com/ochaporkar/semantic-segmentation-unet-resnet50imagenet) : keep in 'pretrained' directory.

**Creating .odgt files**

We're using 'train_bdd.odgt' and 'val_bdd.odgt' files available in data directory for trainig and validation respectively. 

This file contains following important information : 

1. image shape

2. raw image path

3. ground truth image path corrosponding to raw image. 

These odgt files can be created by using ['create_odgt.py'](https://github.com/omcaaaar/semantic_segmentation_unet/blob/master/create_odgt.py) script.

**Training**

We've trained the model on 9822 training images for 100 epochs. It took around 80 hrs to train on a single GPU (NVIDIA GeForce GTX 1080). Refer the training code for details reagrding hyperparameters used. 

Training code : [train_bdd.py](https://github.com/omcaaaar/semantic_segmentation_unet/blob/master/train_bdd.py)

Training logs : [train_bdd.log](https://github.com/omcaaaar/semantic_segmentation_unet/blob/master/train_bdd.log)

After 100 epochs the training accuracy is around 97% and a loss of 0.14. We're using NLLLoss and calculating pixelwise accuracy.

**Validation**

We've validated the model on 1696 images and got the accuracy of around 90%. Check out few of the validation images in the 'teaser' directory.

Validation code : [eval_multipro_bdd.py](https://github.com/omcaaaar/semantic_segmentation_unet/blob/master/eval_multipro_bdd.py)

Note : (from left to right - Validation image, Ground truth image, Predicted image)

![alt text](https://github.com/omcaaaar/semantic_segmentation_unet/blob/master/teaser/0a6f2b77-00000000.png)


![alt text](https://github.com/omcaaaar/semantic_segmentation_unet/blob/master/teaser/1aa6dec1-002fed42.png)

**Test**

We've inferenced this model on a video. It takes around 0.23 seconds per frame for prediction.

The input and output test videos can be found [here](https://www.kaggle.com/ochaporkar/semantic-segmentation-unet-testvideos)

**References**

github link : [github](https://github.com/CSAILVision/semantic-segmentation-pytorch)
