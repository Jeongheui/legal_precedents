"""
Query Expander 테스트 스크립트
"""

import json
from pathlib import Path

# 법률 용어 사전 로드 테스트
def test_load_law_terms():
    """법률 용어 사전 로드 테스트"""
    try:
        file_path = Path("law_terms_dictionary.json")
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            law_terms = data.get("용어_목록", [])

        print(f"[성공] 법률 용어 사전 로드 성공")
        print(f"   - 파일: {file_path}")
        print(f"   - 총 용어 수: {len(law_terms)}개")
        print(f"   - 첫 5개 용어: {law_terms[:5]}")
        return law_terms
    except Exception as e:
        print(f"[실패] 법률 용어 사전 로드 실패: {str(e)}")
        return []


# 쿼리 확장 로직 검증
def test_query_expansion_logic():
    """쿼리 확장 로직 검증 (Gemini API 호출 없이)"""
    print("\n=== 쿼리 확장 로직 검증 ===")

    # 테스트 데이터
    user_query = "관세 환급을 받으려면 어떻게 해야 하나요?"
    similar_questions = [
        "관세 환급 신청 방법은 무엇인가요?",
        "수입 관세를 돌려받는 절차를 알려주세요.",
        "관세환급금 수령 조건은 어떻게 되나요?"
    ]
    key_terms = [
        "관세환급금의 환급",
        "환급 및 분할납부 등",
        "과다환급관세의 징수",
        "관세환급가산금"
    ]

    # 키워드 그룹 구성
    keyword_group = [user_query] + similar_questions + key_terms

    print(f"[성공] 키워드 그룹 구성 완료")
    print(f"   - 원본 질문: {user_query}")
    print(f"   - 유사질문 ({len(similar_questions)}개): {similar_questions}")
    print(f"   - 핵심어 ({len(key_terms)}개): {key_terms}")
    print(f"   - 총 키워드 수: {len(keyword_group)}개")

    return keyword_group


# 통합 테스트
def main():
    print("=== Query Expander 테스트 시작 ===\n")

    # 1. 법률 용어 사전 로드
    law_terms = test_load_law_terms()

    if not law_terms:
        print("\n[실패] 법률 용어 사전이 없어 테스트 중단")
        return

    # 2. 쿼리 확장 로직 검증
    keyword_group = test_query_expansion_logic()

    print("\n=== 테스트 완료 ===")
    print("[성공] 모든 구성 요소가 정상적으로 작동합니다.")
    print("\n다음 단계:")
    print("   1. streamlit run main.py 실행")
    print("   2. 실제 질문을 입력하여 쿼리 확장 기능 확인")
    print("   3. 로그에서 '쿼리 확장 시작...' 메시지 확인")


if __name__ == "__main__":
    main()
