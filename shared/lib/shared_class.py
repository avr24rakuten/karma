from pydantic import BaseModel
from typing import Optional

class InputProduct(BaseModel):
    description: str
    image_link: Optional[str] = None