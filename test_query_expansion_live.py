"""
Query Expansion Live Test - Gemini API 실제 호출 테스트
"""

import os
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types

# 환경 변수 로드
load_dotenv()
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

if not GOOGLE_API_KEY:
    print("[오류] GOOGLE_API_KEY가 설정되지 않았습니다.")
    exit(1)

# Gemini client 초기화
client = genai.Client(api_key=GOOGLE_API_KEY)

# 법률 용어 사전 로드
print("=== 법률 용어 사전 로드 ===")
try:
    with open("law_terms_dictionary.json", 'r', encoding='utf-8') as f:
        data = json.load(f)
        law_terms = data.get("용어_목록", [])
    print(f"[성공] {len(law_terms)}개 용어 로드 완료")
except Exception as e:
    print(f"[실패] {e}")
    exit(1)

# 테스트 질문
user_query = "가산세 면제에 대해 논의한 판례"
print(f"\n=== 테스트 질문 ===")
print(f"질문: {user_query}")

# 법률 용어 목록 (처음 200개)
terms_str = ", ".join(law_terms[:200])

# ========== 1. 유사질문 생성 테스트 ==========
print(f"\n=== 1. 유사질문 생성 테스트 ===")

prompt_similar = f"""# 역할
당신은 관세법 전문가입니다. 사용자의 질문을 분석하여 유사한 질문을 생성하는 역할을 합니다.

# 작업
사용자 질문과 동일한 의도를 가진 유사질문 3개를 생성하세요.

# 제약사항
1. 반드시 아래 '법률 용어 목록'에서 관련 용어를 선택하여 사용하세요
2. 유사질문은 원래 질문과 의도는 같지만 표현 방식을 다르게 해야 합니다
3. 각 질문은 한 줄로 작성하세요
4. 번호나 불릿 없이 질문만 작성하세요
5. 정확히 3개의 질문만 생성하세요

# 법률 용어 목록
{terms_str}

# 사용자 질문
{user_query}

# 출력 형식 (예시)
질문1
질문2
질문3

위 형식으로 3개 질문만 출력하세요."""

try:
    print("[진행] Gemini API 호출 중 (유사질문)...")
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt_similar,
        config=types.GenerateContentConfig(
            temperature=0.7,
            top_k=10,
            top_p=0.9,
            max_output_tokens=500
        )
    )

    print(f"\n[Gemini 원본 응답 - 유사질문]")
    print("=" * 60)
    print(response.text)
    print("=" * 60)

    # 응답 파싱
    similar_questions = []
    lines = response.text.strip().split('\n')
    print(f"\n[디버그] 전체 줄 수: {len(lines)}")

    for i, line in enumerate(lines):
        line = line.strip()
        print(f"  줄 {i}: '{line}'")

        if line and not line.startswith('#'):
            # 숫자와 점 제거
            cleaned = line.lstrip('0123456789.-) ').strip()
            if cleaned:
                similar_questions.append(cleaned)
                print(f"    -> 추출: '{cleaned}'")

    # 정확히 3개만 반환
    similar_questions = similar_questions[:3]

    # 3개 미만이면 원본 질문으로 채움
    while len(similar_questions) < 3:
        similar_questions.append(user_query)

    print(f"\n[결과] 유사질문 {len(similar_questions)}개:")
    for i, q in enumerate(similar_questions, 1):
        print(f"  {i}. {q}")

except Exception as e:
    print(f"[오류] {e}")
    import traceback
    print(traceback.format_exc())
    similar_questions = [user_query, user_query, user_query]


# ========== 2. 핵심어 추출 테스트 ==========
print(f"\n=== 2. 핵심어 추출 테스트 ===")

prompt_keywords = f"""# 역할
당신은 관세법 전문가입니다. 사용자의 질문에서 핵심 법률 용어를 추출하는 역할을 합니다.

# 작업
사용자 질문에서 핵심이 되는 법률 용어를 추출하세요.

# 제약사항
1. 반드시 아래 '법률 용어 목록'에서만 선택하세요
2. 사용자 질문과 직접 관련된 용어만 선택하세요
3. 최대 5개까지만 선택하세요 (5개 이하도 가능)
4. 각 용어는 한 줄에 하나씩 작성하세요
5. 번호나 불릿 없이 용어만 작성하세요

# 법률 용어 목록
{terms_str}

# 사용자 질문
{user_query}

# 출력 형식 (예시)
용어1
용어2
용어3

위 형식으로 핵심 용어만 출력하세요 (최대 5개)."""

try:
    print("[진행] Gemini API 호출 중 (핵심어)...")
    response = client.models.generate_content(
        model="gemini-2.0-flash-exp",
        contents=prompt_keywords,
        config=types.GenerateContentConfig(
            temperature=0.3,
            top_k=5,
            top_p=0.8,
            max_output_tokens=300
        )
    )

    print(f"\n[Gemini 원본 응답 - 핵심어]")
    print("=" * 60)
    print(response.text)
    print("=" * 60)

    # 응답 파싱
    key_terms = []
    lines = response.text.strip().split('\n')
    print(f"\n[디버그] 전체 줄 수: {len(lines)}")

    for i, line in enumerate(lines):
        line = line.strip()
        print(f"  줄 {i}: '{line}'")

        if line and not line.startswith('#'):
            # 숫자와 점 제거
            cleaned = line.lstrip('0123456789.-) ').strip()
            if cleaned:
                key_terms.append(cleaned)
                print(f"    -> 추출: '{cleaned}'")

    # 최대 5개만 반환
    key_terms = key_terms[:5]

    print(f"\n[결과] 핵심어 {len(key_terms)}개:")
    for term in key_terms:
        print(f"  - {term}")

except Exception as e:
    print(f"[오류] {e}")
    import traceback
    print(traceback.format_exc())
    key_terms = []


# ========== 3. 최종 결과 ==========
print(f"\n{'=' * 60}")
print("=== 최종 결과 ===")
print(f"{'=' * 60}")
print(f"\n원본 질문:")
print(f"  {user_query}")
print(f"\n유사질문 ({len(similar_questions)}개):")
for i, q in enumerate(similar_questions, 1):
    print(f"  {i}. {q}")
print(f"\n핵심어 ({len(key_terms)}개):")
for term in key_terms:
    print(f"  - {term}")

keyword_group = [user_query] + similar_questions + key_terms
print(f"\n총 키워드 그룹: {len(keyword_group)}개")
print(f"  (원본 1개 + 유사질문 {len(similar_questions)}개 + 핵심어 {len(key_terms)}개)")
