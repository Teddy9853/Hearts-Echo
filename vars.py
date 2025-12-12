"""自動生成的變數定義檔案
此檔案由 main.py 從 assets/templates.txt 自動生成，請勿手動編輯。
"""
from pydantic import BaseModel
from typing import Optional, List

# 變數定義
# accessory
# activity
# clothe
# color
# companion
# companyMood
# emotionIntensity
# location
# mood
# occasion
# outfitStyle
# temperature
# timeOfDay
# transport
# weather
class EchoInput(BaseModel):
    accessory: Optional[str] = None
    activity: Optional[str] = None
    clothe: Optional[str] = None
    color: Optional[str] = None
    companion: Optional[str] = None
    companyMood: Optional[str] = None
    emotionIntensity: Optional[str] = None
    location: Optional[str] = None
    mood: Optional[str] = None
    occasion: Optional[str] = None
    outfitStyle: Optional[str] = None
    temperature: Optional[str] = None
    timeOfDay: Optional[str] = None
    transport: Optional[str] = None
    weather: Optional[str] = None
    required: Optional[List[str]] = None  # List of parameter names that must be present in selected templates
