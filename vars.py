"""自動生成的變數定義檔案
此檔案由 main.py 從 assets/templates.txt 自動生成，請勿手動編輯。
"""
from pydantic import BaseModel
from typing import Optional

class EchoInput(BaseModel):
    clothe: Optional[str] = None
    mood: Optional[str] = None
    weather: Optional[str] = None
