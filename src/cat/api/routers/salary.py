from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import FileResponse
from pydantic import BaseModel
import pandas as pd
import tempfile
import shutil

router = APIRouter()

# ---------------------------
# 1. Tính lương net
# ---------------------------
class SalaryInput(BaseModel):
    gross: float

@router.post("/calculate-net")
def calculate_net_salary(data: SalaryInput):
    bhxh = data.gross * 0.08
    bhyt = data.gross * 0.015
    bhtn = data.gross * 0.01
    insurance_total = bhxh + bhyt + bhtn
    taxable_income = data.gross - insurance_total - 11000000  # Personal deduction
    personal_income_tax = 0

    if taxable_income > 0:
        if taxable_income <= 5000000:
            personal_income_tax = taxable_income * 0.05
        elif taxable_income <= 10000000:
            personal_income_tax = 250000 + (taxable_income - 5000000) * 0.1
        else:
            personal_income_tax = 250000 + 500000 + (taxable_income - 10000000) * 0.15

    net_salary = data.gross - insurance_total - personal_income_tax

    return {
        "gross": data.gross,
        "bhxh": round(bhxh, 2),
        "bhyt": round(bhyt, 2),
        "bhtn": round(bhtn, 2),
        "insurance_total": round(insurance_total, 2),
        "tax": round(personal_income_tax, 2),
        "net": round(net_salary, 2)
    }

# ---------------------------
# 2. Upload Excel và lưu dữ liệu nhập từ form
# ---------------------------
@router.post("/upload-excel/")
async def upload_excel_and_fill_data(
    file: UploadFile = File(...),
    ten: str = Form(...),
    luong: float = Form(...),
    thuong: float = Form(...),
    tong: float = Form(...)
):
    temp_input = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
    temp_output = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")

    with open(temp_input.name, "wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        df = pd.read_excel(temp_input.name)
        if df.empty or len(df.columns) != 4:
            df = pd.DataFrame(columns=["Tên", "Lương", "Thưởng", "Tổng"])
    except:
        df = pd.DataFrame(columns=["Tên", "Lương", "Thưởng", "Tổng"])

    # 💥 CHỈ sử dụng biến `ten` bên trong hàm!
    df.loc[len(df)] = [ten, luong, thuong, tong]

    df.to_excel(temp_output.name, index=False)

    return FileResponse(
        temp_output.name,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename="ketqua.xlsx"
    )
