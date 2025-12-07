#TODO check and refactor!

import numpy as np
import os
from tensorflow.keras.applications.resnet_v2 import ResNet50V2, preprocess_input
from tensorflow.keras.preprocessing import image as keras_image
from sklearn.preprocessing import OneHotEncoder, normalize
from PIL import Image
import joblib
from io import BytesIO
from sqlalchemy.orm import Session
from sqlalchemy import select

from ..database import SessionLocal
from ..config import config
from .. import models, schemas

PATH_FILES_STORAGE = config["PATH_FILES_STORAGE"]
PATH_FILES_STORAGE_IMAGE_SUBDIR = config["PATH_FILES_STORAGE_IMAGE_SUBDIR"]
PATH_FILES_STORAGE_ML_SUBDIR = config["PATH_FILES_STORAGE_ML_SUBDIR"]

PATH_TO_IMAGES = os.path.join(PATH_FILES_STORAGE, PATH_FILES_STORAGE_IMAGE_SUBDIR)
PATH_TO_ML = os.path.join(PATH_FILES_STORAGE, PATH_FILES_STORAGE_ML_SUBDIR, 'remixer')
ENCODER_PATH = os.path.join(PATH_TO_ML, 'encoder.pkl')

os.makedirs(PATH_TO_ML, exist_ok=True)

METADATA_FEATURES = ['gender', 'masterCategory', 'subCategory', 'articleType', 'baseColour', 'season', 'usage']

IMG_WIDTH = 224
IMG_HEIGHT = 224

# Global model cache
_resnet_model = None
_encoder = None


def get_resnet_model():
    """Lazy load ResNet model (singleton pattern)"""
    global _resnet_model
    if _resnet_model is None:
        _resnet_model = ResNet50V2(weights="imagenet", include_top=False, pooling='avg')
    return _resnet_model


def _create_encoder_from_db(db: Session) -> OneHotEncoder:   
    table_map = {
        'gender': models.Gender,
        'masterCategory': models.CategoryMaster,
        'subCategory': models.CategorySub,
        'articleType': models.GarmentType,
        'baseColour': models.Color,
        'season': models.Season,
        'usage': models.Usage
    }
    
    all_values = []
    
    for feature in METADATA_FEATURES:
        model_class = table_map[feature]
        query = select(model_class.name)
        results = db.execute(query).fetchall()
        
        if not results:
            # Add default value if table is empty
            all_values.append(['Unknown'])
        else:
            values = [r.name for r in results]
            # Always include 'Unknown' as a fallback
            if 'Unknown' not in values:
                values.append('Unknown')
            all_values.append(values)
    
    # Create sample data for fitting (use first value from each category)
    sample_data = [[values[0] for values in all_values]]
    
    # Add 'Unknown' sample for each feature to ensure it's handled
    unknown_sample = ['Unknown'] * len(METADATA_FEATURES)
    sample_data.append(unknown_sample)
    
    # Fit encoder
    encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
    encoder.fit(np.array(sample_data))
    
    # Save encoder to disk
    joblib.dump(encoder, ENCODER_PATH)
    print(f"+ Encoder created and saved to {ENCODER_PATH}")
    
    return encoder


def get_encoder(db: Session) -> OneHotEncoder:
    """
    Get or create the OneHotEncoder.
    Checks if encoder exists on disk, otherwise creates it from database.
    Uses singleton pattern to cache in memory.
    """
    global _encoder
    
    # Return cached encoder if available
    if _encoder is not None:
        return _encoder
    
    # Try loading from disk
    if os.path.exists(ENCODER_PATH):
        _encoder = joblib.load(ENCODER_PATH)
        print(f"✅ Encoder loaded from {ENCODER_PATH}")
        return _encoder
    
    # Create new encoder from database
    print(f"⚠️ Encoder not found, creating from database...")
    _encoder = _create_encoder_from_db(db)
    return _encoder


def extract_image_embedding(image_path: str) -> np.ndarray:

    model = get_resnet_model()
    
    img = keras_image.load_img(image_path, target_size=(IMG_WIDTH, IMG_HEIGHT))
    x = keras_image.img_to_array(img)
    x = preprocess_input(x)
    x = np.expand_dims(x, axis=0)
    
    features = model.predict(x, verbose=0)
    return features[0]


def get_garment_metadata_dict(garment: models.Garment, db: Session) -> dict:
    
    def get_name(model, fk_id):
        if not fk_id: return 'Unknown'
        item = db.query(model).filter(model.id == fk_id).first()
        return item.name if item else 'Unknown'

    return {
        'gender': get_name(models.Gender, garment.gender_id),
        'masterCategory': get_name(models.CategoryMaster, garment.category_master_id),
        'subCategory': get_name(models.CategorySub, garment.category_sub_id),
        'articleType': get_name(models.GarmentType, garment.garment_type_id),
        'baseColour': get_name(models.Color, garment.color_id),
        'season': get_name(models.Season, garment.season_id),
        'usage': get_name(models.Usage, garment.usage_id)
    }


def create_metadata_vector(metadata: dict, encoder: OneHotEncoder) -> np.ndarray:
    """
    Create metadata vector from garment attributes
    
    Args:
        metadata: Dict with keys matching METADATA_FEATURES
        encoder: Fitted OneHotEncoder
    
    Returns:
        numpy array of encoded metadata
    """
    # Prepare data in correct order
    features_list = [metadata.get(feature, 'Unknown') for feature in METADATA_FEATURES]
    
    # Reshape for encoder
    features_array = np.array(features_list).reshape(1, -1)
    
    # Encode
    encoded = encoder.transform(features_array)
    return encoded[0]

# TODO rename: 
# alpha to image_embedding_weight
# beta to metadata_embedding_weight
def create_all_embeddings(
    image_path: str,
    metadata: dict,
    encoder: OneHotEncoder,
    alpha: float = 0.7,
    beta: float = 0.3
) -> tuple:
    """
    Create hybrid embedding combining image and metadata
    
    Args:
        image_path: Full path to image file
        metadata: Dict with metadata attributes
        encoder: Fitted OneHotEncoder
        alpha: Weight for image embedding (default 0.7)
        beta: Weight for metadata embedding (default 0.3)
    
    Returns:
        Tuple of (image_embedding, metadata_embedding, hybrid_embedding)
    """
    # Extract image embedding
    visual_vec = extract_image_embedding(image_path)
    visual_vec = normalize(visual_vec.reshape(1, -1))[0]
    
    # Create metadata embedding
    meta_vec = create_metadata_vector(metadata, encoder)
    meta_vec = normalize(meta_vec.reshape(1, -1))[0]
    
    # Combine with weights
    hybrid_vec = np.concatenate([
        alpha * visual_vec,
        beta * meta_vec
    ])
    
    return visual_vec, meta_vec, hybrid_vec


def create_and_save_garment_embedding(
    garment: models.Garment,
    db: Session,
    alpha: float = 0.7,
    beta: float = 0.3,
    force_recreate: bool = False
) -> bool:
    """
    Create and save embeddings for a single garment.
    This is the main function to use for creating embeddings.
    
    Args:
        garment: Garment model instance
        db: Database session
        alpha: Weight for image embedding (default 0.7)
        beta: Weight for metadata embedding (default 0.3)
        force_recreate: Recreate embeddings even if they exist
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # Check if embeddings already exist
        existing = db.query(models.GarmentEmbeddings).filter(
            models.GarmentEmbeddings.garment_id == garment.id
        ).first()
        
        if existing and not force_recreate:
            # print(f"⏭️  Garment {garment.id} already has embeddings, skipping")
            return False
        
        # Validate image exists
        if not garment.image_link:
            print(f"❌ Garment {garment.id} has no image_link")
            return False
        
        # Construct full image path
        image_path = os.path.join(PATH_TO_IMAGES, garment.image_link)
        
        if not os.path.exists(image_path):
            print(f"❌ Image not found for garment {garment.id}: {image_path}")
            return False
        
        # Get encoder (will create if doesn't exist)
        encoder = get_encoder(db)
        
        # Get metadata
        metadata = get_garment_metadata_dict(garment, db)
        
        # Create embeddings (Returns numpy arrays)
        img_emb, meta_emb, hybrid_emb = create_all_embeddings(
            image_path,
            metadata,
            encoder,
            alpha=alpha,
            beta=beta
        )
        
        # Save to database (pgvector handles numpy arrays directly)
        if existing:
            existing.embedding_image = img_emb
            existing.embedding_metadata = meta_emb
            existing.embedding_combined = hybrid_emb
            print(f"+ Updated embeddings for garment {garment.id}")
        else:
            embedding_record = models.GarmentEmbeddings(
                garment_id=garment.id,
                embedding_image=img_emb, 
                embedding_metadata=meta_emb,
                embedding_combined=hybrid_emb
            )
            db.add(embedding_record)
            print(f"+ Created embeddings for garment {garment.id}")
        
        db.commit()
        return True
        
    except Exception as e:
        print(f"❌ Error creating embeddings for garment {garment.id}: {e}")
        db.rollback()
        return False


def process_user_garments_embeddings(user_id: int, db: Session, force_recreate: bool = False) -> schemas.GarmentEmbeddingsCreateStatsResponse:
    """
    Standard function: requires an active DB session.
    """
    garments = db.query(models.Garment).filter(models.Garment.user_id == user_id).all()
    
    stats = {
        "total": len(garments),
        "processed": 0,
        "skipped": 0,
        "failed": 0,
        "errors": []
    }
    
    print(f"- Processing {len(garments)} garments for User {user_id}")
    
    for garment in garments:
        try:

            success = create_and_save_garment_embedding(
                garment=garment,
                db=db,
                force_recreate=force_recreate
            )
            
            if success:
                stats["processed"] += 1
            
            else:
                existing = db.query(models.GarmentEmbeddings).filter(
                    models.GarmentEmbeddings.garment_id == garment.id
                ).first()
                
                if existing and not force_recreate:
                    stats["skipped"] += 1
                else:
                    stats["failed"] += 1
                    
        except Exception as e:
            stats["failed"] += 1
            stats["errors"].append(f"Garment {garment.id}: {str(e)}")

    return stats

