class User():
    def __init__(self,social_id, nickname, email):
        self.social_id = social_id
        self.nickname = nickname
        self.email = email

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.social_id
