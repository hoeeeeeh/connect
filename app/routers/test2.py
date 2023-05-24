from typing import List

from fastapi import APIRouter, UploadFile
import pandas as pd


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


async def calculate_all(user_answer):
    # 질문1. 지원받고 싶은 정부지원사업의 사업유형을 선택해주세요.(중복가능)
    """
    선택지1. 사업화, R&D, 시설/공간/보육, 멘토링/컨설팅, 행사/네트워크, 융자, 인력, 글로벌
    안내문구. 각 사업유형에 대해 자세하게 알고 싶다면 아래의 링크를 클릭해보세요.(링크 주소~)
    """
    calc_contain(user_answer[0], TARGET_TYPE_COLUMNS)

    # 질문2. 본인의 아이템과 관련있는 키워드를 선택해주세요.(중복가능)
    """
    선택지2. 해당없음, 4차산업혁명, SW, 기술창업(기술을 보유, 혁신 기술), ICT(ICT 기반 융복합분야),
    데이터(Data), Network, 인공지능(AI), 공공기술, 공간정보, 소재, 부품, 장비, 예술, 콘텐츠
    """
    calc_contain(user_answer[1])

    # 질문3. 본인의 아이템과 관련있는 키워드를 선택해주세요.(중복가능)
    """
    선택지3. 해당없음, 바이오, 헬스, 스포츠, 농업, 농촌, 식품, 보건, 해양수산, 전통문화, 녹색, 산림, 로컬크리에이터, 물산업, 관광
    """
    calc_contain(user_answer[2])

    # 질문4. 본인의 아이템과 관련있는 키워드를 선택해주세요.(중복가능)
    """
    선택지4. 해당없음, 글로벌(해외, 현지매출), 사회적, 비대면
    """
    calc_contain(user_answer[3])

    # 질문5. 현재 보유하고 있는 것을 선택해주세요.(중복가능)
    """
    선택지5. 해당없음, 특허권(특허), 품종보호권, 지식재산권
    (주석 : 선택하면 개수 입력 창 생기게 하기)
    """
    calc_contain(user_answer[4])

    # 질문6. 폐업한 경험이 있나요?(중복불가)
    """
    선택지6. O(재창업), X[X인 경우 ‘장애’가 들어간 행 제외하고 재창업 관련 키워드가 들어간 행 모두 제거)
    """
    calc_drop_specific(SPECIFIC_SIX_DROP_WORDS, SPECIFIC_SIX_EXCEPT_WORDS) if user_answer[5] else None

    # 질문7. 사업자등록을 한적이 있나요? ※개인사업자, 법인 모두 포함 (중복불가)
    """
    선택지7. O[O인 경우 생애최초가 들어간 행 모두 제거], X(생애최초)
    """
    calc_drop(DROP_SEVEN_WORDS) if user_answer[6] else None

    # 질문8. 창업기간을 적어주세요.(중복불가) ※창업기간은 사업자등록일로부터 오늘까지 기준 (중복불가)
    """
    선택지8.
    - 예비창업(미창업, (예비)) : 예비창업(미창업, (예비))가 들어간 행 제외하고 ‘가, 나, 다, 라, 마, 바’가 들어간 행 제거
    - 기창업 : 입력 - X년 X개월
    - 0년 1~11개월 + 1년 0개월 : ‘예비창업자 제외, 가, 나, 다, 라’가 들어간 행 제외하고 ‘예비창업(미창업, (예비)), 마, 바’가 들어간 행 제거
    - 1년 1~11개월 + 2년 0개월 : ‘예비창업자 제외, 가, 나, 다, 라’가 들어간 행 제외하고 ‘예비창업(미창업, (예비)), 마, 바’가 들어간 행 제거
    - 2년 1~11개월 + 3년 0개월 : ‘예비창업자 제외, 나, 다, 라’가 들어간 행 제외하고 ‘예비창업자(미창업, (예비)), 가, 마, 바’가 들어간 행 제거
    - 3년 1~11개월 + 4년 0개월 : ‘예비창업자 제외, 다, 라, 마’가 들어간 행 제외하고 '예비창업(미창업, (예비)), 가, 나, 바‘가 들어간 행 제거
    - 4년 1~11개월 + 5년 0개월(’예비창업자 제외, 다, 라, 마, 바‘가 들어간 행 제외하고 ’예비창업(미창업, (예비)), 가, 나‘가 들어간 행 제거
    - 5년 1~11개월 + 6년 0개월 : ’예비창업자 제외, 라, 마, 바‘가 들어간 행 제외하고 ’예비창업(미창업, (예비)), 가, 나, 다‘가 들어간 행 제거
    - 6년 1~11개월 + 7년 0개월(’예비창업자 제외, 라, 마, 바‘가 들어간 행 제외하고 ’예비창업(미창업, (예비)), 가, 나, 다‘가 들어간 행 제거
    - 7년 1개월 이후(’예비창업(미창업, (예비)), 가, 나, 다, 라, 마, 바‘가 들어간 행 제거
    - 가. 2년 이내
    - 나. 3년 이내(3년 미만, ~3년, 초기기업, 3년 이하)
    - 다. 5년 미만(5년이내)
    - 라. 7년 이내(7년 미만, 7년 이하, 7년이내)
    - 마. 3년~7년(성장기업, 3년 초과 7년 이내)
    - 바. 4~7년차
    """

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


    # 가 = 0
    # 나 = 1
    # 다 = 2
    # 라 = 3
    # 마 = 4
    # 바 = 5

    # 질문9. 대표자의 연령을 적어주세요. ※만 나이 기준
    """
    # 선택지9. 만 X세
    # - 만 12세 이하 : ’다, 라, 바‘가 들어간 행 제외하고 ’가, 나, 마‘가 들어간 행 제거
    # - 만 13세 이상~18세 이하 : ’가, 다, 라, 바‘가 들어간 행 제외하고 ’나, 마‘가 들어간 행 제거
    # - 만 19세 이상~29세 이하 : ’나, 다, 라, 바‘가 들어간 행 제외하고 ’가, 마‘가 들어간 행 제거
    # - 만 30세 이상~39세 이하 : ’나, 라, 바‘가 들어간 행 제외하고 ’가, 다, 마‘가 들어간 행 제거
    # - 만 40세 이상~65세 이하 : ’마, 바‘가 들어간 행 제외하고 ’가, 나, 다, 라‘가 들어간 행 제거
    # - 만 66세 이상 : ’마‘가 들어간 행 제외하고 ’가, 나, 다, 라, 바‘가 들어간 행 제거
    # - 가. 만 13세 이상 ~ 만 18세 이하(만13~15세, 청소년)
    # - 나. 만 19세 이상 39세 이하(만 18세이상 ~ 39세 이하, 청년)
    # - 다. 만 29세 이하
    # - 라. 만 39세 이하
    # - 마. 만 40세 이상(중장년)
    # - 바. 만 65세 이하
    """
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
    """
    선택지10. 해당없음, 엑셀러레이터, 초중고등학생, 대학, 휴학생, 교육자, 민간창업기획자
    """
    calc_contain(user_answer[9])

    # 질문11. 대표자의 상황과 관련있는 키워드를 선택해주세요.(중복가능)
    """
    선택지11. 해당없음. 장애, 취약계층, 귀산촌인, 외국
    """
    calc_contain(user_answer[10])

    # 질문12. 대표자의 성별을 선택해주세요.(중복불가)
    """
    선택지12. 남성, 여성
    """
    # TODO: 남성, 여성으로 분류해서 calc_contain 해야하는지 체크 필요

    # 질문13. 본인의 기업에 근무하는 상시근로자 수를 적어주세요.
    """
    선택지13. X명
    - 0명 : ’가‘가 들어간 행 제외하고 ’나‘가 들어간 행 제거
    - 1명 이상 ~ 3명 미만 : ’가, 나‘가 들어간 행 제거
    - 3명 이상 ~ 10명 미만 : ’나‘가 들어간 행 제외하고 ’가‘가 들어간 행 제거
    - 10명 이상 ~ 20명 미만 : ’나‘가 들어간 행 제외하고 ’가‘가 들어간 행 제거
    - 20명 이상 ~ 50명 미만 : ’나‘가 들어간 행 제외하고 ’가‘가 들어간 행 제거
    - 50명 이상 ~ 100명 미만 : ’나‘가 들어간 행 제외하고 ’가‘가 들어간 행 제거
    - 100명 이상 : ’나‘가 들어간 행 제외하고 ’가‘가 들어간 행 제거
    - 가. 1인 창조기업 
    - 나. 상시근로자 3인 이상
    """

    # 가 : 0
    # 나 : 1
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
    """
    선택지14. O, X[X 경우 원자력/방사선/에너지 관련 전공 1인 키워드가 들어간 행 제거]
    """
    calc_drop(DROP_FOURTEEN_DEGREE) if not(user_answer[13]) else None

    # 질문15. 전년도 기준 연매출을 적어주세요.
    """
    선택지15. X억원
    - 0.1억원 미만 : ’가‘가 들어간 행을 제외하고 ’나‘가 들어간 행 제거
    - 0.1억원 이상 0.5억원 미만 : ’가‘가 들어간 행을 제외하고 ’나‘가 들어간 행 제거
    - 0.5억원 이상 1억원 미만 : ’가‘가 들어간 행을 제외하고 ’나‘가 들어간 행 제거
    - 1억원 이상 5억원 미만 
    - 5억원 이상 10억원 미만 
    - 10억원 이상 20억원 미만 
    - 20억원 이상 50억원 미만 : ’나‘가 들어간 행을 제외하고 ’가‘가 들어간 행 제거
    - 50억원 이상 100억원 미만 : ’나‘가 들어간 행을 제외하고 ’가‘가 들어간 행 제거
    - 100억원 이상 억원 미만 : ’나‘가 들어간 행을 제외하고 ’가‘가 들어간 행 제거
    - 가. 전년도 매출액 20억원 미만
    - 나. 매출액 1억원 이상
    """

    # 질문16. 투자받은 누적 금액을 적어주세요.
    """
    선택지16. X억원
    - 0.5억원 이상 1억원 미만 : ’가‘가 들어간 행 제거
    - 1억원 이상 5억원 미만 : ’가‘가 들어간 행 제거
    - 5억원 이상 10억원 미만 : ’가‘가 들어간 행 제거
    - 10억원 이상 20억원 미만 : ’가‘가 들어간 행 제거
    - 20억원 이상 50억원 미만 
    - 50억원 이상 100억원 미만 
    - 100억원 이상 : ’가‘가 들어간 행 제거
    - 가. 투자실적(20억이상 100억 미만)
    """

    # 질문17. 본인의 기업 형태와 관련있는 키워드를 선택해주세요.(중복가능)
    """
    선택지17. 해당없음, 개인사업자, 법인, 사내벤처, 거점대학, 초중고등학교, 대안학교, 학교밖센터, 전환창업
    """

    # 질문18. 지자체 주관 정부지원사업 관련해서 관심있는 지역을 선택해주세요.(중복가능)
    """
    선택지18. (필터 : 지자체는 선택된 지역에 대해 소관부처 열로 단순 필터함)
    - 해당없음
    - 전체
    - 서울
    - 전체, 서초, 송파, 도봉, 동작, 마포, 서대문, 양천, 은평, 종로, 중구, 중랑, 구로
    - 부산
    - 전체, 긴구, 금정, 사상
    - 대구
    - 인천
    - 전체, 강화, 남동
    - 광주
    - 전체, 북구, 동구
    - 대전
    - 세종
    - 울산
    - 전체, 북구, 울주
    - 경기
    - 전체, 용인, 군포, 성남, 부천, 의왕, 안양, 안산
    - 강원
    - 전체, 춘천, 강릉, 횡성, 평창, 철원, 홍천, 고성, 인제, 속초
    - 충청북도
    - 보은
    - 충청남도
    - 태안
    - 전라북도
    - 전체, 군산, 익산, 남원, 정읍, 순창, 진안, 고창, 부안
    - 전라남도
    - 전체, 목포, 영암, 여수, 진도, 무안, 영광, 신안
    - 경상북도
    - 전체, 영양, 김천, 고령, 포항, 군위, 봉화, 도청, 영천
    - 경상남도
    - 전체, 창원, 진주, 김해, 거제, 함양, 양산
    - 제주도
    """

    # 질문19. 현재 입주하고 있는 센터가 있다면 선택해주세요.(중복가능)
    """
    선택지19. 해당없음, 국가물산산업클러스터 창업보육센터, 팁스(TIPS)
    """

    # 질문20. 이메일을 작성해주세요.
    """
    선택지20. X@X.X
    """

    # 질문21. 전화번호를 작성해주세요.
    """
    선택지21. XXX-XXXX-XXXX
    """

    # 질문22. 개인정보 제공 동의(필수) ※동의해주셔야 지원받을 수 있는 정부지원사업을 정리한 엑셀 파일을 보내드릴 수 있습니다.
    """
    선택지22. 체크박스
    """

    # 질문23. 마케팅 활용 동의(선택) ※마케팅 활용 동의를 해주시면 정부지원사업 관련된 유용한 정보를 보내드립니다.
    """
    선택지23. 체크박스
    """
