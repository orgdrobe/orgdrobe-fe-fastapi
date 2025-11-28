from sqlalchemy import text, select
import pickle
import os

from .config import config
from . import hashing
from . import models

PATH_FILES_STORAGE = config["PATH_FILES_STORAGE"]
PATH_FILES_STORAGE_ML_SUBDIR = config["PATH_FILES_STORAGE_ML_SUBDIR"]
LABEL_INFO_PATH = os.path.join(PATH_FILES_STORAGE, PATH_FILES_STORAGE_ML_SUBDIR, 'label_info_with_augmentation(big).pkl')


OUTFIT_CATEGORY_INDEX_MAP = {
    0: 'Topwear',
    1: 'Shoes',
    2: 'Bottomwear',
    3: 'Bags',
    4: 'Jewellery',
    5: 'Watches',
    6: 'Eyewear',
    7: 'Belts',
    8: 'Socks',
    9: 'Headwear',
    10: 'Dress',
    11: 'Ties',
    12: 'Scarves',
    13: 'Gloves',
    14: 'Wristbands'
}

OUTFIT_VECTORS = [
    {
        "vector": [1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        "name": "Standard Basic",
        "description": "Topwear, Shoes, Bottomwear (Standard set)"
    },
    {
        "vector": [1, 1, 1, 0, 0, 1, 0, 1, 1, 0, 0, 1, 0, 0, 0],
        "name": "Classic Office (Men)",
        "description": "Topwear, Shoes, Bottomwear, Watches, Belts, Socks, Ties"
    },
    {
        "vector": [0, 1, 0, 1, 1, 1, 1, 0, 0, 1, 1, 0, 1, 0, 1],
        "name": "Evening Wear (Women)",
        "description": "Shoes, Bags, Jewellery, Watches, Eyewear, Headwear, Dress, Scarves, Wristbands"
    },
    {
        "vector": [1, 1, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 1, 0],
        "name": "Sport Casual",
        "description": "Topwear, Shoes, Bottomwear, Socks, Headwear, Gloves"
    },
    {
        "vector": [1, 1, 1, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 0],
        "name": "Summer Casual",
        "description": "Topwear, Shoes, Bottomwear, Eyewear, Socks, Headwear"
    },
    {
        "vector": [1, 1, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0, 1, 1, 0],
        "name": "Winter Outfit",
        "description": "Topwear, Shoes, Bottomwear, Socks, Headwear, Scarves, Gloves"
    }
]

def initialize_outfit_templates(target, connection, **kw):

    # 1. Fetch current Category Sub IDs from the database to map Names -> IDs
    cat_sub_table = models.CategorySub.__table__
    query_cats = select(cat_sub_table.c.id, cat_sub_table.c.name)
    results_cats = connection.execute(query_cats).fetchall()
    db_cat_map = {row.name: row.id for row in results_cats}

    # 2. Prepare tables for insertion
    outfit_template_table = models.OutfitTemplate.__table__
    link_table = models.OutfitTemplateParameter.__table__

    # 3. Iterate through vectors and insert
    for item in OUTFIT_VECTORS:
        vector = item["vector"]
        name = item["name"]
        description = item["description"]

        # A. Insert Template (Unconditional insert since this is an after_create event)
        insert_stmt = outfit_template_table.insert().values(
            name=name,
            description=description
        )
        # Execute and get the inserted ID
        result = connection.execute(insert_stmt)
        template_id = result.inserted_primary_key[0]

        # B. Process Vector and Insert Links
        links_to_insert = []
        
        for index, is_present in enumerate(vector):
            if is_present == 1:
                # Get the category name from the map (e.g., 0 -> 'Topwear')
                cat_name = OUTFIT_CATEGORY_INDEX_MAP.get(index)
                
                # Look up the DB ID for this category name
                if cat_name and cat_name in db_cat_map:
                    cat_id = db_cat_map[cat_name]
                    
                    links_to_insert.append({
                        'outfit_template_id': template_id,
                        'category_sub_id': cat_id
                    })
        
        # C. Insert valid links
        if links_to_insert:
            connection.execute(link_table.insert(), links_to_insert)


def initialize_ml_mapping_table(target, connection, **kw):
    """
    Populate ML mapping table by matching ML names to existing database records.
    """

    if not os.path.exists(LABEL_INFO_PATH):
        return
    
    with open(LABEL_INFO_PATH, 'rb') as f:
        ml_label_info = pickle.load(f)

    category_mappings = {
        'gender': (models.Gender, 'gender_id'),
        'masterCategory': (models.CategoryMaster, 'category_master_id'),
        'subCategory': (models.CategorySub, 'category_sub_id'),
        'articleType': (models.GarmentType, 'garment_type_id'),
        'baseColour': (models.Color, 'color_id'),
        'season': (models.Season, 'season_id'),
        'usage': (models.Usage, 'usage_id')
    }

    mappings_to_insert = []

    for category_name, (model_class, fk_column) in category_mappings.items():
        

        mapping_dict = ml_label_info[category_name]['mapping']
        
        for ml_id, ml_name in mapping_dict.items():
                        
            query = select(model_class.id).where(model_class.name == ml_name)
            result = connection.execute(query).fetchone()            
                        
            db_id = result[0]
            mappings_to_insert.append({
                'ml_category_id': ml_id,
                'ml_category_name': ml_name,

                'gender_id': None,
                'category_master_id': None,
                'category_sub_id': None,
                'garment_type_id': None,
                'color_id': None,
                'season_id': None,
                'usage_id': None,
                
                fk_column: db_id
            })
            
    connection.execute(target.insert(), mappings_to_insert)



INITIAL_DATA = {
    'users': [
        {'login': 'string', 'email': 'user@example.com', 'password': hashing.get_password_hash('stringst'),},
    ],
    'genders': [
        {'name': 'Men'},
        {'name': 'Unisex'},
        {'name': 'Women'},
        {'name': 'Girls'},
        {'name': 'Boys'},
    ],
    'categories_master': [
        {'name': 'Apparel'},
        {'name': 'Accessories'},
        {'name': 'Footwear'},
        {'name': 'Sporting Goods'},
        {'name': 'Free Items'},
        {'name': 'Personal Care'},
        {'name': 'Home'},
    ],
    'categories_sub': [
        {'name': 'Topwear' },
        {'name': 'Bags' },
        {'name': 'Headwear' },
        {'name': 'Shoes' },
        {'name': 'Sports Equipment' },
        {'name': 'Water Bottle' },
        {'name': 'Bottomwear' },
        {'name': 'Sandal' },
        {'name': 'Accessories' },
        {'name': 'Apparel Set' },
        {'name': 'Flip Flops' },
        {'name': 'Socks' },
        {'name': 'Dress' },
        {'name': 'Belts' },
        {'name': 'Watches' },
        {'name': 'Innerwear' },
        {'name': 'Shoe Accessories' },
        {'name': 'Wallets' },
        {'name': 'Loungewear and Nightwear' },
        {'name': 'Eyewear' },
        {'name': 'Sports Accessories' },
        {'name': 'Wristbands' },
        {'name': 'Free Gifts' },
        {'name': 'Scarves' },
        {'name': 'Ties' },
        {'name': 'Saree' },
        {'name': 'Stoles' },
        {'name': 'Mufflers' },
        {'name': 'Cufflinks' },
        {'name': 'Jewellery' },
        {'name': 'Umbrellas' },
        {'name': 'Fragrance' },
        {'name': 'Gloves' },
        {'name': 'Perfumes' },
        {'name': 'Home Furnishing' },
        {'name': 'Bath and Body' },
        {'name': 'Vouchers' },
        {'name': 'Nails' },
        {'name': 'Eyes' },
        {'name': 'Lips' },
        {'name': 'Makeup' },
        {'name': 'Skin Care' },
        {'name': 'Skin' },
        {'name': 'Beauty Accessories' },
        {'name': 'Hair' },
    ],
    'garment_types': [
        {'name': 'Tshirts' },
        {'name': 'Backpacks' },
        {'name': 'Jackets' },
        {'name': 'Caps' },
        {'name': 'Sports Shoes' },
        {'name': 'Casual Shoes' },
        {'name': 'Footballs'},
        {'name': 'Water Bottle'},
        {'name': 'Shorts'},
        {'name': 'Track Pants'},
        {'name': 'Swimwear'},
        {'name': 'Handbags'},
        {'name': 'Sweatshirts'},
        {'name': 'Basketballs'},
        {'name': 'Sandals'},
        {'name': 'Duffel Bag'},
        {'name': 'Tops'},
        {'name': 'Shirts'},
        {'name': 'Capris'},
        {'name': 'Flip Flops'},
        {'name': 'Socks'},
        {'name': 'Formal Shoes'},
        {'name': 'Sports Sandals'},
        {'name': 'Heels'},
        {'name': 'Flats'},
        {'name': 'Dresses'},
        {'name': 'Trousers'},
        {'name': 'Headband'},
        {'name': 'Belts'},
        {'name': 'Skirts'},
        {'name': 'Messenger Bag'},
        {'name': 'Rucksacks'},
        {'name': 'Waist Pouch'},
        {'name': 'Watches'},
        {'name': 'Jeans'},
        {'name': 'Bra'},
        {'name': 'Laptop Bag'},
        {'name': 'Shoe Accessories'},
        {'name': 'Shoe Laces'},
        {'name': 'Leggings'},
        {'name': 'Wallets'},
        {'name': 'Travel Accessory'},
        {'name': 'Tunics'},
        {'name': 'Kurtas'},
        {'name': 'Lounge Pants'},
        {'name': 'Sweaters'},
        {'name': 'Waistcoat'},
        {'name': 'Sunglasses'},
        {'name': 'Wristbands'},
        {'name': 'Tracksuits'},
        {'name': 'Free Gifts'},
        {'name': 'Scarves'},
        {'name': 'Ties'},
        {'name': 'Churidar'},
        {'name': 'Kurtis'},
        {'name': 'Dupatta'},
        {'name': 'Sarees'},
        {'name': 'Suits'},
        {'name': 'Hat'},
        {'name': 'Stoles'},
        {'name': 'Kurta Sets'},
        {'name': 'Mufflers'},
        {'name': 'Innerwear Vests'},
        {'name': 'Lounge Shorts'},
        {'name': 'Cufflinks'},
        {'name': 'Stockings'},
        {'name': 'Necklace and Chains'},
        {'name': 'Bracelet'},
        {'name': 'Umbrellas'},
        {'name': 'Briefs'},
        {'name': 'Clutches'},
        {'name': 'Accessory Gift Set'},
        {'name': 'Trunk'},
        {'name': 'Tights'},
        {'name': 'Fragrance Gift Set'},
        {'name': 'Perfume and Body Mist'},
        {'name': 'Deodorant'},
        {'name': 'Gloves'},
        {'name': 'Boxers'},
        {'name': 'Mobile Pouch'},
        {'name': 'Shrug'},
        {'name': 'Suspenders'},
        {'name': 'Camisoles'},
        {'name': 'Jeggings'},
        {'name': 'Night suits'},
        {'name': 'Blazers'},
        {'name': 'Lehenga Choli'},
        {'name': 'Salwar'},
        {'name': 'Nehru Jackets'},
        {'name': 'Patiala'},
        {'name': 'Earrings'},
        {'name': 'Pendant'},
        {'name': 'Bangle'},
        {'name': 'Clothing Set'},
        {'name': 'Jumpsuit'},
        {'name': 'Booties'},
        {'name': 'Rompers'},
        {'name': 'Ties and Cufflinks'},
        {'name': 'Tablet Sleeve'},
        {'name': 'Nightdress'},
        {'name': 'Trolley Bag'},
        {'name': 'Cushion Covers'},
        {'name': 'Key chain'},
        {'name': 'Jewellery Set'},
        {'name': 'Body Wash and Scrub'},
        {'name': 'Robe'},
        {'name': 'Shapewear'},
        {'name': 'Ipad'},
        {'name': 'Ring'},
        {'name': 'Nail Polish'},
        {'name': 'Eyeshadow'},
        {'name': 'Lipstick'},
        {'name': 'Compact'},
        {'name': 'Kajal and Eyeliner'},
        {'name': 'Lip Liner'},
        {'name': 'Foundation and Primer'},
        {'name': 'Lip Plumper'},
        {'name': 'Concealer'},
        {'name': 'Lip Gloss'},
        {'name': 'Highlighter and Blush'},
        {'name': 'Salwar and Dupatta'},
        {'name': 'Baby Dolls'},
        {'name': 'Rain Jacket'},
        {'name': 'Rain Trousers'},
        {'name': 'Lounge Tshirts'},
        {'name': 'Bath Robe'},
        {'name': 'Mascara'},
        {'name': 'Face Wash and Cleanser'},
        {'name': 'Face Moisturisers'},
        {'name': 'Eye Cream'},
        {'name': 'Beauty Accessory'},
        {'name': 'Nail Essentials'},
        {'name': 'Makeup Remover'},
        {'name': 'Lip Care'},
        {'name': 'Sunscreen'},
        {'name': 'Hair Colour'},
        {'name': 'Toner'},
        {'name': 'Mens Grooming Kit'},
        {'name': 'Body Lotion'},
        {'name': 'Face Scrub and Exfoliator'},
        {'name': 'Mask and Peel'},
        {'name': 'Face Serum and Gel'},
        {'name': 'Hair Accessory'}
    ],
    'colors': [
        {'name': 'Unknown', 'hex': None, 'description': None,},
        {'name': 'Multi', 'hex': None, 'description': None,},
        {'name': 'Blue', 'hex': '#0000FF', 'description': None,},
        {'name': 'Navy Blue', 'hex': '#000080', 'description': None,},
        {'name': 'Black', 'hex': '#000000', 'description': None,},
        {'name': 'Red', 'hex': '#FF0000', 'description': None,},
        {'name': 'Grey', 'hex': '#808080', 'description': None,},
        {'name': 'White', 'hex': '#FFFFFF', 'description': None,},
        {'name': 'Orange', 'hex': '#FFA500', 'description': None,},
        {'name': 'Purple', 'hex': '#800080', 'description': None,},
        {'name': 'Green', 'hex': '#00FF00', 'description': None,},
        {'name': 'Pink', 'hex': '#FFC0CB', 'description': None,},
        {'name': 'Brown', 'hex': '#A52A2A', 'description': None,},
        {'name': 'Silver', 'hex': '#C0C0C0', 'description': None,},
        {'name': 'Metallic', 'hex': '#C0C0C0', 'description': 'same as Silver idk',},
        {'name': 'Beige', 'hex': '#F5F5DC', 'description': None,},
        {'name': 'Yellow', 'hex': '#FFFF00', 'description': None,},
        {'name': 'Maroon', 'hex': '#800000', 'description': None,},
        {'name': 'Cream', 'hex': '#FFFDD0', 'description': None,},
        {'name': 'Tan', 'hex': '#D2B48C', 'description': None,},
        {'name': 'Olive', 'hex': '#808000', 'description': None,},
        {'name': 'Gold', 'hex': '#FFD700', 'description': None,},
        {'name': 'Peach', 'hex': '#FFE5B4', 'description': None,},
        {'name': 'Charcoal', 'hex': '#36454F', 'description': None,},
        {'name': 'Grey Melange', 'hex': '#BEBEBE', 'description': None,},
        {'name': 'Teal', 'hex': '#008080', 'description': None,},
        {'name': 'Mustard', 'hex': '#FFDB58', 'description': None,},
        {'name': 'Mauve', 'hex': '#E0B0FF', 'description': None,},
        {'name': 'Magenta', 'hex': '#FF00FF', 'description': None,},
        {'name': 'Khaki', 'hex': '#F0E68C', 'description': None,},
        {'name': 'Burgundy', 'hex': '#800020', 'description': None,},
        {'name': 'Steel', 'hex': '#4682B4', 'description': None,},
        {'name': 'Copper', 'hex': '#B87333', 'description': None,},
        {'name': 'Lavender', 'hex': '#E6E6FA', 'description': None,},
        {'name': 'Coffee Brown', 'hex': '#4B3621', 'description': None,},
        {'name': 'Turquoise Blue', 'hex': '#40E0D0', 'description': None,},
        {'name': 'Taupe', 'hex': '#483C32', 'description': None,},
        {'name': 'Off White', 'hex': '#F8F8FF', 'description': None,},
        {'name': 'Nude', 'hex': '#F5CBA7', 'description': None,},
        {'name': 'Bronze', 'hex': '#CD7F32', 'description': None,},
        {'name': 'Fluorescent Green', 'hex': '#39FF14', 'description': None,},
        {'name': 'Rust', 'hex': '#B7410E', 'description': None,},
        {'name': 'Skin', 'hex': '#FFDFC4', 'description': None,},
        {'name': 'Sea Green', 'hex': '#2E8B57', 'description': None,},
        {'name': 'Lime Green', 'hex': '#32CD32', 'description': None,},
        {'name': 'Mushroom Brown', 'hex': '#B7A69E', 'description': None,},
        {'name': 'Rose', 'hex': '#FF007F', 'description': None,}
    ],
    'seasons': [
        {'name': 'Winter'},
        {'name': 'Spring'},
        {'name': 'Summer'},
        {'name': 'Fall'},
    ],
    'uses': [
        {'name': 'Sports'},
        {'name': 'Casual'},
        {'name': 'Travel'},
        {'name': 'Formal'},
        {'name': 'Smart Casual'},
        {'name': 'Ethnic'},
        {'name': 'Party'},
        {'name': 'Home'}
    ]
}

# see https://gist.github.com/jsmsalt/26bf25844870d59eee17997727e3a631

def initialize_table(target, connection, **kw):
    """Insert initial data after table creation"""
    tablename = str(target)
    if tablename in INITIAL_DATA and len(INITIAL_DATA[tablename]) > 0:
        connection.execute(target.insert(), INITIAL_DATA[tablename])
