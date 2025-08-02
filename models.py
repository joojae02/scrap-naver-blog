from typing import List
from pydantic import BaseModel

class NaverBlogPost(BaseModel):
    title: str
    date: str
    content: str
    images: List[str]
