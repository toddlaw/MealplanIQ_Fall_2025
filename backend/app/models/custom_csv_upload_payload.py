from pydantic import BaseModel

class CsvUploadPayload(BaseModel):
    user_id: str | int
    meal_id: int
    ingredients_filename: str
    ingredients_csv: str
    instructions_filename: str
    instructions_csv: str
