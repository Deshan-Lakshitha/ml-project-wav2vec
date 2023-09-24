# CS4622 - Machine Learning
## Project - Speaker, Age, Gender and Accent Recognition using wav2vec base

Wav2vec base is commonly used as a feature extraction model. There are 12 transformer layers in the wav2vec base model. For this project features are extracted from transformer layer 7 and 12.

#### Dataset
AudioMNIST is the dataset used to create the features. Check this link for further
details about the dataset [Link](https://github.com/soerenab/AudioMNIST).

#### Process
For each label, several classification models were trained and evaluated. Considering the evaluation metrics, SVC classifier was used as the best model for each label. ``PCA`` and ``K-Best`` feature selection methods were considered to reduce the feature dimensionality where ``PCA`` showed better performance over ``K-Best`` in model evaluation. 5-fold cross validation was used to evaluate the models. Random search was used to find the best hyperparameters for the models. All the accuracy and plots are available in the notebook codes.
