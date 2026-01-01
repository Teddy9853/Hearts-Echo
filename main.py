from functools import cache
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Tuple
import uvicorn
import markdown
from pathlib import Path
import random
import re
from pathlib import Path
from vars import EchoInput

app = FastAPI(title="Hearts Echo API", version="1.0.0")

# 定義輸出模型
class EchoOutput(BaseModel):
    text: str
    used: List[str]
    ignore: List[str]

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@cache
def load_index_html() -> str:
    # 讀取 Markdown 文件
    md_file = Path("assets/index.md")
    md_content = md_file.read_text(encoding="utf-8")
    return f"""
    <!DOCTYPE html>
    <html lang="en-US">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Hearts Echo</title>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                line-height: 1.6;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                color: #333;
            }}
            h1 {{ color: #2c3e50; }}
            h2 {{ color: #34495e; margin-top: 30px; }}
            code {{
                background-color: #f4f4f4;
                padding: 2px 6px;
                border-radius: 3px;
            }}
        </style>
    </head>
    <body>
        {markdown.markdown(md_content, extensions=['extra', 'codehilite'])}
    </body>
    </html>
    """

@app.get("/", response_class=HTMLResponse)
async def root():
    return load_index_html()

@app.post("/echo", response_model=EchoOutput)
async def echo(data: EchoInput):
    """
    接收包含服裝、天氣、心情和日期的資料,生成自然語言描述。
    會使用 clothe, weather, mood 這些欄位，並忽略 date。
    """
    # 從範本檔案載入欄位定義
    all_templates = load_templates(lang=data.lang)
    
    # Extract 'required' field separately and exclude it from available_data
    required_params = data.required if data.required else []
    available_data = {k: v for k, v in data.model_dump(exclude_none=True).items() if v is not None and k != 'required'}
    
    if not available_data:
        return EchoOutput(
            text="No data provided to generate description.",
            used=[],
            ignore=list(EchoInput.model_fields.keys())
        )
    
    # 篩選出可以滿足的範本
    valid_templates: List[Tuple[str, List[str]]] = []
    weights: List[int] = []
    for template_str, template_params in all_templates:
        # 檢查是否所有必需參數都存在且有值
        if all(param in available_data and available_data[param] for param in template_params):
            # If 'required' is specified, check that all required params are in the template
            if required_params:
                if not all(req_param in template_params for req_param in required_params):
                    continue  # Skip this template as it doesn't contain all required params
            
            weight = len(template_params) ** 2  # 參數數量的平方作為權重
            valid_templates.append((template_str, template_params))
            weights.append(weight)
    
    # 如果有滿足條件的範本,根據權重隨機選擇一個
    if valid_templates:
        template_str, params = random.choices(valid_templates, weights=weights, k=1)[0]
        exclude_fields = set(EchoInput.model_fields.keys()) - set(params) - {'required'}
        return EchoOutput(
            text=template_str.format(**available_data),
            used=params,
            ignore=list(exclude_fields)
        )
    
    # 如果沒有滿足條件的範本，回傳預設訊息
    return EchoOutput(
        text="Failed to generate description with the provided information.",
        used=[],
        ignore=list(available_data.keys())
    )


@app.get("/fields")
async def get_fields():
    """
    列出 EchoInput 模型的所有欄位名稱
    """
    return {"fields": list(EchoInput.model_fields.keys())}

class TemplateInfo(BaseModel):
    template: str
    params: List[str]

@app.get("/templates")
async def get_templates() -> List[TemplateInfo]:
    """
    列出所有可用的句子範本
    """
    templates = load_templates()
    
    # 將範本轉換為更友善的格式
    template_list: List[TemplateInfo] = []
    for template_str, params in templates:
        template_list.append(TemplateInfo(
            template=template_str,
            params=params
        ))
    
    return template_list

# ==============================
# Helper Functions
# ==============================
@cache
def load_templates(lang:str = "en-us") -> List[Tuple[str, List[str]]]:
    """
    載入句子模板並解析參數
    回傳格式: (使用欄位列表, 未使用欄位列表, [(模板字串, [參數列表]), ...])
    """
    if lang == "en-us":
        file_path = Path("assets/templates.txt")
    else:
        file_path = Path(f"assets/templates.{lang}.txt")

    if not file_path.exists():
        file_path = Path("assets/templates.txt")

    content = file_path.read_text(encoding="utf-8")
    templates: List[Tuple[str, List[str]]] = []
    
    for line in content.split('\n'):
        line = line.strip()
        if not line:
            continue
            
        # 使用正則表達式找出所有 {參數名} 格式的參數
        params = re.findall(r'\{(\w+)\}', line)
        
        # 檢查是否包含保留字 'required'
        if 'required' in params or 'lang' in params:
            raise ValueError(f"Template contains reserved word 'required'or'lang': {line}")
        
        templates.append((line, params))
    
    return templates

# 在啟動時生成 vars.py
def generate_vars_file() -> None:
    """
    讀取 templates.txt，解析所有變數，並生成 vars.py
    """
    template_file = Path("assets/templates.txt")
    content = template_file.read_text(encoding="utf-8")
    
    # 收集所有變數
    variables: set[str] = set()
    for line in content.split('\n'):
        line = line.strip()
        if not line:
            continue
        # 使用正則表達式找出所有 {參數名} 格式的參數
        params = re.findall(r'\{(\w+)\}', line)
        
        # 檢查是否包含保留字 'required'
        if 'required' in params:
            raise ValueError(f"Template contains reserved word 'required': {line}")
        
        variables.update(params)
    
    # 生成 vars.py 內容
    vars_content = '''"""自動生成的變數定義檔案
此檔案由 main.py 從 assets/templates.txt 自動生成，請勿手動編輯。
"""
from pydantic import BaseModel
from typing import Optional, List

# 變數定義
'''
    # 按字母順序排序變數以保持一致性
    for var in sorted(variables):
        vars_content += f'# {var}\n'
    
    vars_content += 'class EchoInput(BaseModel):\n'

    for var in sorted(variables):
        vars_content += f'    {var}: Optional[str] = None\n'
    
    # Add the 'required' field as a special parameter
    vars_content += '    required: Optional[List[str]] = None  # List of parameter names that must be present in selected templates\n'
    
    # 寫入 vars.py
    vars_file = Path("vars.py")
    vars_file.write_text(vars_content, encoding="utf-8")
    print(f"Generated vars.py with variables: {sorted(variables)}")

 
if __name__ == "__main__":
    generate_vars_file()
    print(os.environ)
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
