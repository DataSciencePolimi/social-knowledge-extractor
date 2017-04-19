class User():
    def __init__(self,id,social_id, nickname, email, access_token, access_token_secret, profile_img):
        self._id = id
        self.social_id = social_id
        self.nickname = nickname
        self.email = email
        self.access_token = access_token
        self.access_token_secret = access_token_secret
        self.profile_img = profile_img

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.social_id
