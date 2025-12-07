#TODO check and refactor!

import numpy as np
from sqlalchemy.orm import Session

from .. import models
from ..models import Garment, GarmentEmbeddings

def autocomplete_outfit(
    db: Session,
    user_id: int,
    garment_ids: list[int],
    outfit_template_id: int,
    user_gender_ids: list[int] | None,
    variety_coef: float = 0.05
) -> list[models.Garment]: 
    # 1. Fetch Input Vectors and their Categories
    input_items = db.query(
        Garment.id, 
        Garment.category_sub_id, 
        GarmentEmbeddings.embedding_combined
    ).join(
        GarmentEmbeddings, Garment.id == GarmentEmbeddings.garment_id
    ).filter(
        Garment.id.in_(garment_ids),
        Garment.user_id == user_id
    ).all()

    if not input_items:
        return []

    # Extract vectors and existing categories
    vectors = []
    present_category_ids = set()
    
    for item in input_items:
        if item.embedding_combined is not None:
            vectors.append(np.array(item.embedding_combined))
        present_category_ids.add(item.category_sub_id)

    if not vectors:
         return []

    # 2. Calculate Target Vector (Mean of inputs)
    user_vec = np.mean(vectors, axis=0)

    # 3. Add Variety Noise
    if variety_coef > 0:
        noise = np.random.normal(0, variety_coef, user_vec.shape)
        user_vec = user_vec + noise

    # 4. Identify Missing Categories based on Template
    required_params = db.query(models.OutfitTemplateParameter).filter(
        models.OutfitTemplateParameter.outfit_template_id == outfit_template_id
    ).all()
    
    required_category_ids = {p.category_sub_id for p in required_params}
    
    recommended_ids = []

    # 5. Find Best Match for Each Missing Category
    for target_sub_category_id in required_category_ids:
        
        # Skip if we already have an item of this category
        if target_sub_category_id in present_category_ids:
            continue

        query = db.query(Garment.id).join(
            GarmentEmbeddings, Garment.id == GarmentEmbeddings.garment_id
        ).filter(
            Garment.user_id == user_id,
            Garment.category_sub_id == target_sub_category_id
        )

        if user_gender_ids:
            query = query.filter(Garment.gender_id == user_gender_ids)

        # PGVECTOR SEARCH: Find the single nearest neighbor
        # TODO: can pass a limit param as a variable
        best_match = query.order_by(
            GarmentEmbeddings.embedding_combined.l2_distance(user_vec)
        ).limit(1).first()
        
        if best_match:
            recommended_ids.append(best_match.id)

    if not recommended_ids:
        return []

    # 6. Get Garment objects
    garments = db.query(models.Garment).filter(
        models.Garment.id.in_(recommended_ids)
    ).all()

    return garments