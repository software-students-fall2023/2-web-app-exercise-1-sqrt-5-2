class User:

    def __init__(self, first_name, last_name, email, password):

        self.id = 0
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password

    @classmethod
    def from_db(cls, obj):
        return cls(obj.first_name, obj.last_name, obj.email, obj.password)
    