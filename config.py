DEFAULT_LOGIN_URL = "https://sn.devuser.sothis.co.kr/login"

LOGIN_ID_FIELD_ID = "id"
LOGIN_PW_FIELD_ID = "pass"

# Breakpoint 정의 (최소 너비 기준)
DEFAULT_BREAKPOINTS = {
    "XL": 1280,
    "LG": 1024, # 1024 ~ 1279
    "MD": 768,  # 768 ~ 1023
    "SM": 360   # 360 ~ 767
}

# Breakpoint 유효 범위
BREAKPOINT_VALID_RANGES = {
    "XL": (1280, None),
    "LG": (1024, 1279),
    "MD": (768, 1023),
    "SM": (360, 767)
}

# Breakpoint를 너비 기준으로 정렬하여 반환하는 함수
def get_sorted_breakpoints(breakpoints_dict):
    # 너비를 기준으로 내림차순 정렬
    sorted_items = sorted(breakpoints_dict.items(), key=lambda item: item[1], reverse=True)
    # (너비, 이름) 튜플 리스트로 반환
    return [(width, name) for name, width in sorted_items]
