import io, os, pickle
import numpy as np
import tensorflow as tf

from sqlalchemy.orm import Session
from PIL import Image

from app.schemas import GarmentClassify
from ..config import config
from ..models import MLMapping


PATH_FILES_STORAGE = config["PATH_FILES_STORAGE"]
PATH_FILES_STORAGE_ML_SUBDIR = config["PATH_FILES_STORAGE_ML_SUBDIR"]

PATH_TO_ML = os.path.join(PATH_FILES_STORAGE, PATH_FILES_STORAGE_ML_SUBDIR)

if not os.path.exists(PATH_TO_ML):
    os.makedirs(PATH_TO_ML)

MODEL_PATH = os.path.join(PATH_TO_ML, 'multi_head_fashion_classifier_with_augmentation(big).keras')
LABEL_INFO_PATH = os.path.join(PATH_TO_ML, 'label_info_with_augmentation(big).pkl')

IMG_HEIGHT = 224
IMG_WIDTH = 224

model = tf.keras.models.load_model(MODEL_PATH)
with open(LABEL_INFO_PATH, 'rb') as f:
    label_info = pickle.load(f)


def preprocess_image(image_data: bytes):
    img = Image.open(io.BytesIO(image_data))
    
    if img.mode != 'RGB':
        img = img.convert('RGB')
        
    img = img.resize((IMG_WIDTH, IMG_HEIGHT))
    img_array = np.array(img)
    img_batch = np.expand_dims(img_array, axis=0)
    preprocessed_img = tf.keras.applications.resnet_v2.preprocess_input(img_batch)
    
    return preprocessed_img


def get_db_ids_from_ml_predictions(predictions, db: Session): 
    category_field_map = {
        'gender': 'gender_id',
        'masterCategory': 'category_master_id',
        'subCategory': 'category_sub_id',
        'articleType': 'garment_type_id',
        'baseColour': 'color_id',
        'season': 'season_id',
        'usage': 'usage_id'
    }
    
    result = {} 
    
    for category_name, db_field in category_field_map.items():
        output_name = f'{category_name}_output'
        
        if output_name in predictions:
            pred_array = predictions[output_name]
            predicted_index = int(np.argmax(pred_array))
            confidence = float(pred_array[0][predicted_index])
            
            ml_label_name = label_info[category_name]['mapping'][predicted_index]
            
            mapping = db.query(MLMapping).filter(
                MLMapping.ml_category_id == predicted_index,
                MLMapping.ml_category_name == ml_label_name,
                getattr(MLMapping, db_field).isnot(None)  # Make sure this FK is populated (use the row which is not null)
            ).first()
            
            result[db_field] = getattr(mapping, db_field)
            result[f'{category_name}_confidence'] = confidence
            result[f'{category_name}_ml_name'] = ml_label_name
    
    return result

def garment_classify(image_bytes: bytes, db: Session) -> GarmentClassify:
    preprocessed_image = preprocess_image(image_bytes)
    predictions = model.predict(preprocessed_image)
    db_mapped_result = get_db_ids_from_ml_predictions(predictions, db)
    garment = GarmentClassify(**db_mapped_result)
    return garment