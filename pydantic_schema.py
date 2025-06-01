from pydantic import BaseModel, HttpUrl

class CoachVideoRequest(BaseModel):
    exercise_id: int
    exercise_url: str
    coach_id: int


class UserVideoRequest(BaseModel):
    coach_exercise_id: int
    exercise_url: str
    user_exercise_id: int
    user_id: int