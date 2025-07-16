from pydantic import BaseModel, constr
from typing import Optional


class InfoQueryParams(BaseModel):
    name: Optional[constr(strip_whitespace=True, min_length=1, max_length=100)]
