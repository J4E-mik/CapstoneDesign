import itertools
from services.session import user_session, user_locations

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
            
    def user_information(self, user_id: str):
        session_info = user_session.get(user_id,{})
        location = user_locations.get(user_id, (None, None))
        return {
            "user_id":user_id,
            "session":session_info,
            "location":{
                "lon":location[0],
                "lat":location[1]
            }
        }

user_service = UserService()