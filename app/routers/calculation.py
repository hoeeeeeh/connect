from typing import List

from fastapi import APIRouter, UploadFile
import pandas as pd

router = APIRouter(
    prefix="/calculation",
    tags=["calculation"],
)

data = pd.read_excel("../../data.xlsx")

# CONSTANT
# 1번 질문
TARGET_TYPE_COLUMNS = ["유형"]

# 2~5번 질문
TARGET_DEFAULT_COLUMNS = ["사업명", "사업개요", "지원대상"]

# 6번 질문
SPECIFIC_SIX_DROP_WORDS = ["재창업"]
SPECIFIC_SIX_EXCEPT_WORDS = ["장애"]

# 7번 질문
DROP_SEVEN_WORDS = ["생애최초"]

# 8번 질문
SPECIFIC_EIGHT_PERIOD = [
    # 가
    "2년 이내",
    # 나
    "3년 미만/~3년/초기기업/3년 이하",
    # 다
    "5년 미만/5년 이내",
    # 라
    "7년 이내/7년 미만/7년 이하/7년이내",
    # 마
    "3년~7년/성장기업/3년 초과 7년 이내",
    # 바
    "4~7년차"
]

SPECIFIC_EIGHT_PRE = ["예비창업자", "미창업", "(예비)"]

# 9번 질문
SPECIFIC_NINE_AGE = [
    "만 13세 이상 ~ 만 18세 이하/만13~15세/청소년",
    "만 19세 이상 39세 이하/만 18세이상 ~ 39세 이하/청년",
    "만 29세 이하",
    "만 39세 이하",
    "만 40세 이상/중장년",
    "만 65세 이하",
]

# 13번 질문
SPECIFIC_THIRTEEN_WORKER = [
        "1인 창조기업",
        "상시근로자 3인 이상"
]

# 14번 질문
DROP_FOURTEEN_DEGREE = ["원자력/방사선/에너지 관련 전공 1인"]


def calc_contain(contain_strs, target_columns=TARGET_DEFAULT_COLUMNS):
    global data
    data = data[data[target_columns].apply(
        lambda row: any(
            [contain_str in val for contain_str in contain_strs for val in row]
        ), axis=1)]


def calc_drop(drop_strs, target_columns=TARGET_DEFAULT_COLUMNS):
    global data
    data = data[data[target_columns].apply(
        lambda row: all(
            [drop_str not in val for drop_str in drop_strs for val in row]
        ), axis=1)]


def calc_drop_specific(drop_strs, except_strs, target_columns=TARGET_DEFAULT_COLUMNS):
    global data
    data = data[data[target_columns].apply(
        lambda row: not (
                any(_str in val for val in row for drop_str in drop_strs for _str in drop_str.split("/")) and
                all(_str not in val for val in row for except_str in except_strs for _str in except_str.split("/"))
        ), axis=1)]


@router.get("/")
async def main():
    return {"TEST": "success"}


@router.post("/calculation")
async def calculate_all(user_answer):
    # 질문1. 지원받고 싶은 정부지원사업의 사업유형을 선택해주세요.(중복가능)
    calc_contain(user_answer[0], TARGET_TYPE_COLUMNS)

    # 질문2. 본인의 아이템과 관련있는 키워드를 선택해주세요.(중복가능)
    calc_contain(user_answer[1])

    # 질문3. 본인의 아이템과 관련있는 키워드를 선택해주세요.(중복가능)
    calc_contain(user_answer[2])

    # 질문4. 본인의 아이템과 관련있는 키워드를 선택해주세요.(중복가능)
    calc_contain(user_answer[3])

    # 질문5. 현재 보유하고 있는 것을 선택해주세요.(중복가능)
    calc_contain(user_answer[4])

    # 질문6. 폐업한 경험이 있나요?(중복불가)
    calc_drop_specific(SPECIFIC_SIX_DROP_WORDS, SPECIFIC_SIX_EXCEPT_WORDS) if user_answer[5] else None

    # 질문7. 사업자등록을 한적이 있나요? ※개인사업자, 법인 모두 포함 (중복불가)
    calc_drop(DROP_SEVEN_WORDS) if user_answer[6] else None

    # 질문8. 창업기간을 적어주세요.(중복불가) ※창업기간은 사업자등록일로부터 오늘까지 기준 (중복불가)
    if user_answer[7] == 0 or user_answer[7] == 1:
        calc_drop_specific(SPECIFIC_EIGHT_PRE + SPECIFIC_EIGHT_PERIOD[4:],
                           SPECIFIC_EIGHT_PERIOD[0:4])
    elif user_answer[7] == 2:
        calc_drop_specific(SPECIFIC_EIGHT_PRE + SPECIFIC_EIGHT_PERIOD[0:1, 4:],
                           SPECIFIC_EIGHT_PERIOD[1:4])
    elif user_answer[7] == 3:
        calc_drop_specific(SPECIFIC_EIGHT_PRE + SPECIFIC_EIGHT_PERIOD[0:2, 5:],
                           SPECIFIC_EIGHT_PERIOD[2:5])
    elif user_answer[7] == 4:
        calc_drop_specific(SPECIFIC_EIGHT_PRE + SPECIFIC_EIGHT_PERIOD[0:2],
                           SPECIFIC_EIGHT_PERIOD[2:])
    elif user_answer[7] == 5 or user_answer[7] == 6:
        calc_drop_specific(SPECIFIC_EIGHT_PRE + SPECIFIC_EIGHT_PERIOD[0:3],
                           SPECIFIC_EIGHT_PERIOD[3:])
    elif user_answer[7] == 7:
        calc_drop(SPECIFIC_EIGHT_PRE +
                  SPECIFIC_EIGHT_PERIOD)

    # 질문9. 대표자의 연령을 적어주세요. ※만 나이 기준
    if user_answer[7] <= 12:
        calc_drop_specific(SPECIFIC_NINE_AGE[0:2, 4:5], SPECIFIC_NINE_AGE[2:4, 5:])
    elif 13 <= user_answer[7] <= 18:
        calc_drop_specific(SPECIFIC_NINE_AGE[1:2, 4:5], SPECIFIC_NINE_AGE[0:1, 2:4, 5:])
    elif 19 <= user_answer[7] <= 29:
        calc_drop_specific(SPECIFIC_NINE_AGE[0:1, 4:5], SPECIFIC_NINE_AGE[1:4, 5:])
    elif 30 <= user_answer[7] <= 39:
        calc_drop_specific(SPECIFIC_NINE_AGE[0:1, 2:3, 4:5], SPECIFIC_NINE_AGE[1:2, 3:4, 5:])
    elif 40 <= user_answer[7] <= 65:
        calc_drop_specific(SPECIFIC_NINE_AGE[0:4], SPECIFIC_NINE_AGE[4:])
    elif 66 <= user_answer[7]:
        calc_drop_specific(SPECIFIC_NINE_AGE[0:4, 5:], SPECIFIC_NINE_AGE[4:5])

    # 질문10. 대표자의 직업과 관련있는 키워드를 선택해주세요.(중복가능)
    calc_contain(user_answer[9])

    # 질문11. 대표자의 상황과 관련있는 키워드를 선택해주세요.(중복가능)
    calc_contain(user_answer[10])

    # 질문12. 대표자의 성별을 선택해주세요.(중복불가)
    # TODO: 남성, 여성으로 분류해서 calc_contain 해야하는지 체크 필요

    # 질문13. 본인의 기업에 근무하는 상시근로자 수를 적어주세요.
    if user_answer[12] == 0:
        calc_drop_specific(SPECIFIC_THIRTEEN_WORKER[1:], SPECIFIC_THIRTEEN_WORKER[0:1])
    elif 1 <= user_answer[12] < 3:
        calc_drop(SPECIFIC_THIRTEEN_WORKER)
    elif 3 <= user_answer[12] < 10:
        calc_drop_specific(SPECIFIC_THIRTEEN_WORKER[0:1], SPECIFIC_THIRTEEN_WORKER[1:])
    elif 10 <= user_answer[12] < 20:
        calc_drop_specific(SPECIFIC_THIRTEEN_WORKER[0:1], SPECIFIC_THIRTEEN_WORKER[1:])
    elif 20 <= user_answer[12] < 50:
        calc_drop_specific(SPECIFIC_THIRTEEN_WORKER[0:1], SPECIFIC_THIRTEEN_WORKER[1:])
    elif 50 <= user_answer[12] < 100:
        calc_drop_specific(SPECIFIC_THIRTEEN_WORKER[0:1], SPECIFIC_THIRTEEN_WORKER[1:])
    elif 100 <= user_answer[12]:
        calc_drop_specific(SPECIFIC_THIRTEEN_WORKER[0:1], SPECIFIC_THIRTEEN_WORKER[1:])

    # 질문14. 본인의 직원 중 원자력/방사선/에너지 관련 전공인 사람이 있나요?(중복불가)

    # 질문15. 전년도 기준 연매출을 적어주세요.

    # 질문16. 투자받은 누적 금액을 적어주세요.

    # 질문17. 본인의 기업 형태와 관련있는 키워드를 선택해주세요.(중복가능)

    # 질문18. 지자체 주관 정부지원사업 관련해서 관심있는 지역을 선택해주세요.(중복가능)

    # 질문19. 현재 입주하고 있는 센터가 있다면 선택해주세요.(중복가능)

    # 질문20. 이메일을 작성해주세요.

    # 질문21. 전화번호를 작성해주세요.

    # 질문22. 개인정보 제공 동의(필수) ※동의해주셔야 지원받을 수 있는 정부지원사업을 정리한 엑셀 파일을 보내드릴 수 있습니다.

    # 질문23. 마케팅 활용 동의(선택) ※마케팅 활용 동의를 해주시면 정부지원사업 관련된 유용한 정보를 보내드립니다.