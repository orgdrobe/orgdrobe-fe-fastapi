def update_object_attributes(user_in, user):
    for attr, value in user_in.dict().items():
        setattr(user, attr, value)