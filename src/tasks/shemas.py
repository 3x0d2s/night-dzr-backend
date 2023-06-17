from pydantic import BaseModel, Field


class TaskBase(BaseModel):
    level: int
    mystery_of_place: str = Field(min_length=1, max_length=1024)
    place: str = Field(min_length=1, max_length=1024)
    answer: str = Field(min_length=1, max_length=64)


class TaskCreate(TaskBase):
    pass


class TaskRead(TaskBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True


class TaskUpdate(TaskBase):
    pass
