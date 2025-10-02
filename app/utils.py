def update_object_attributes(obj_in, obj_out):
    for attr, value in obj_in.dict().items():
        setattr(obj_out, attr, value)