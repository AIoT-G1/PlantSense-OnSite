import pickle
import cv2
import numpy as np
#import tensorflow.keras as keras
from keras.utils import img_to_array
from keras.models import load_model

default_image_size = tuple((256, 256))

def convert_image_to_array(image_dir):
    try:
        image = cv2.imread(image_dir)
        if image is not None :
            image = cv2.resize(image, default_image_size)   
            return img_to_array(image)
        else :
            return np.array([])
    except Exception as e:
        print(f"Error : {e}")
        return None
def predict():
    image = convert_image_to_array("leaf.jpg")
    image = np.reshape(image, (1, 256, 256, 3))

#with open('cnn_model.pkl' , 'rb') as f:
 #   lr = pickle.load(f)
    
    lr = load_model('/home/pi/Desktop/Detect_Disease/model.h5')
# check prediction

    labels = ['Tomato_Bacterial_spot', 'Tomato_Early_blight', 'Tomato_Late_blight', 'Tomato_Leaf_Mold' ,'Tomato__Target_Spot','Tomato_YellowLeaf__Curl_Virus', 'Tomato_mosaic_virus','Tomato_healthy','Bean_angular_leaf','Bean_rust','Bean_healthy']
    Output = lr.predict(image)
    print(Output)
    output_label = labels[np.argmax(Output)]
    print(output_label)
    return output_label

