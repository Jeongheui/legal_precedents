"""
법령용어사전 추출 스크립트

customs_investigation.json의 제목 필드에서 법령용어를 추출하여
중복을 제거한 용어사전을 생성합니다.

제목 구조: "대분류, 중분류, 소분류" (쉼표로 구분)
추출 방법: 쉼표로 분리하여 각 계층의 용어를 추출
"""

import json
from pathlib import Path
from datetime import datetime


def extract_law_terms(input_file, output_file):
    """
    JSON 파일에서 법령용어를 추출하여 사전 생성

    Args:
        input_file: 입력 JSON 파일 경로
        output_file: 출력 JSON 파일 경로
    """
    PROJECT_ROOT = Path(__file__).parent.parent
    input_path = PROJECT_ROOT / input_file
    output_path = PROJECT_ROOT / output_file

    print(f"입력 파일 로드 중: {input_path}")

    # JSON 파일 로드
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 제목 필드 추출
    titles = [item['제목'] for item in data['관세법']['data']]
    print(f"총 {len(titles)}개 조문 발견")

    # 용어 추출: 쉼표로 분리
    all_terms = []
    for title in titles:
        # 쉼표로 분리하고 앞뒤 공백 제거
        terms = [term.strip() for term in title.split(',')]
        all_terms.extend(terms)

    print(f"총 용어 수 (중복 포함): {len(all_terms)}")

    # 중복 제거 및 정렬
    unique_terms = sorted(set(all_terms))
    print(f"고유 용어 수 (중복 제거): {len(unique_terms)}")

    # 결과 데이터 구성
    result = {
        "메타데이터": {
            "생성일시": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "원본파일": input_file,
            "총_조문수": len(titles),
            "총_용어수_중복포함": len(all_terms),
            "고유_용어수": len(unique_terms),
            "추출방식": "쉼표 기준 분리 (의미 단위 유지)"
        },
        "용어_목록": unique_terms
    }

    # JSON 파일 저장
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\n법령용어사전 저장 완료: {output_path}")
    print(f"\n=== 통계 정보 ===")
    print(f"총 조문 수: {len(titles)}")
    print(f"총 용어 수 (중복 포함): {len(all_terms)}")
    print(f"고유 용어 수: {len(unique_terms)}")
    print(f"\n처음 30개 용어:")
    for i, term in enumerate(unique_terms[:30], 1):
        print(f"  {i}. {term}")

    return result


if __name__ == "__main__":
    # 입력/출력 파일 설정
    INPUT_FILE = "customs_investigation.json"
    OUTPUT_FILE = "law_terms_dictionary.json"

    # 용어 추출 실행
    result = extract_law_terms(INPUT_FILE, OUTPUT_FILE)

    print(f"\n작업 완료!")
