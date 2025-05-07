import itertools

class UserService:
    def __init__(self):
        self._user_counter = itertools.count(0)
        self._used_ids = set()

    def generate_user_id(self):
        while True:
            user_id = f"user{next(self._user_counter):03d}"
            if user_id not in self._used_ids:
                self._used_ids.add(user_id)
                return user_id
            
user_service = UserService()