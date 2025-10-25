# 쿼리 확장 시스템 가이드

## 개요

법률 용어 사전(law_terms_dictionary.json)을 활용하여 TF-IDF 검색의 한계를 극복하는 쿼리 확장 시스템이 구현되었습니다.

## 주요 개선 사항

### 기존 방식의 문제점
- TF-IDF는 사용자 질문의 단어와 정확히 일치하는 판례만 검색
- 유사한 의미의 다른 표현으로 작성된 판례 놓침
- 법률 용어의 다양한 표현 방식을 인식하지 못함

### 새로운 방식의 해결책
1. **유사질문 생성**: Gemini 2.0 Flash를 사용하여 사용자 질문과 유사한 질문 3개 생성
2. **핵심어 추출**: 법률 용어 사전에서 관련 핵심어 5개 이내 추출
3. **키워드 그룹 구성**: 원본 질문 + 유사질문 3개 + 핵심어 5개 = 총 9개 키워드
4. **확장 검색**: 키워드 그룹 전체를 사용하여 판례 검색
5. **정확도 향상**: 더 많은 관련 판례를 찾아 AI 에이전트에게 제공

## 시스템 구조

### 1. 데이터 로드 (data_loader.py)
```python
def load_data():
    # KCS 판례 로드
    # MOLEG 판례 로드
    # 법률 용어 사전 로드 (NEW)
    return court_cases, tax_cases, preprocessed_data, law_terms
```

### 2. 쿼리 확장 (query_expander.py)
```python
def expand_query(client, user_query, law_terms):
    # 1. 유사질문 3개 생성 (Gemini 2.0 Flash)
    similar_questions = generate_similar_questions(client, user_query, law_terms)

    # 2. 핵심어 5개 이내 추출 (Gemini 2.0 Flash)
    key_terms = extract_key_terms(client, user_query, law_terms)

    # 3. 키워드 그룹 구성
    keyword_group = [user_query] + similar_questions + key_terms

    return {
        "original_query": user_query,
        "similar_questions": similar_questions,
        "key_terms": key_terms,
        "keyword_group": keyword_group
    }
```

### 3. 검색 (vectorizer.py)
```python
def search_relevant_data(query, preprocessed_data, chunk_info,
                        top_n=5, conversation_history="",
                        keyword_group=None):
    # keyword_group이 있으면 확장 검색
    # keyword_group이 없으면 기존 방식 (하위 호환성)

    if keyword_group:
        # 모든 키워드를 하나로 결합하여 벡터화
        combined_query = " ".join(processed_keywords)
        query_vec = vectorizer.transform([combined_query])
    else:
        # 기존 방식
        query_vec = vectorizer.transform([query])

    # 코사인 유사도 계산 및 상위 N개 반환
```

### 4. 에이전트 실행 (agent.py)
```python
def run_parallel_agents(client, court_cases, tax_cases,
                       preprocessed_data, user_query,
                       conversation_history="", law_terms=None):
    # 법률 용어 사전이 있으면 쿼리 확장
    if law_terms:
        expansion_result = expand_query(client, user_query, law_terms)
        keyword_group = expansion_result["keyword_group"]

    # 6개 에이전트 병렬 실행 (키워드 그룹 전달)
    for i in range(6):
        run_agent(..., keyword_group=keyword_group)
```

## 처리 흐름

```
사용자 질문 입력
    ↓
[쿼리 확장]
├─ Gemini 2.0 Flash 호출 → 유사질문 3개 생성
├─ Gemini 2.0 Flash 호출 → 핵심어 5개 추출
└─ 키워드 그룹 구성 (9개 키워드)
    ↓
[키워드 그룹 기반 TF-IDF 검색]
├─ 키워드 그룹 전체를 하나로 결합
├─ TF-IDF 벡터화
└─ 코사인 유사도 계산 → 상위 5개 판례 선택
    ↓
[에이전트 답변 생성]
├─ 6개 에이전트 병렬 실행 (각각 다른 청크)
├─ 각 에이전트가 확장된 검색 결과로 답변 생성
└─ Head Agent가 통합 답변 생성
    ↓
사용자에게 최종 답변 표시
```

## 예시

### 입력
```
사용자 질문: "관세 환급을 받으려면 어떻게 해야 하나요?"
```

### 쿼리 확장 결과
```
키워드 그룹 (9개):
1. 관세 환급을 받으려면 어떻게 해야 하나요? (원본)

2. 관세 환급 신청 방법은 무엇인가요? (유사질문1)
3. 수입 관세를 돌려받는 절차를 알려주세요. (유사질문2)
4. 관세환급금 수령 조건은 어떻게 되나요? (유사질문3)

5. 관세환급금의 환급 (핵심어1)
6. 환급 및 분할납부 등 (핵심어2)
7. 과다환급관세의 징수 (핵심어3)
8. 관세환급가산금 (핵심어4)
9. 계약 내용과 다른 물품 등에 대한 관세 환급 (핵심어5)
```

### 검색 개선
- **기존 방식**: "관세 환급 받으려면" 단어만 매칭 → 제한적 검색
- **새 방식**: 9개 키워드로 확장 검색 → 더 많은 관련 판례 발견

## 성능 영향

### 추가 API 호출
- Gemini 2.0 Flash 호출 2회 (유사질문 생성 + 핵심어 추출)
- 사용자 질문당 1회만 호출 (6개 에이전트 실행 전)
- 빠른 모델 사용으로 지연 시간 최소화 (약 1-2초)

### 검색 정확도
- TF-IDF 검색 범위 확대
- 더 다양한 관련 판례 검색 가능
- AI 에이전트에게 더 풍부한 컨텍스트 제공

## 테스트 방법

### 1. 기본 테스트
```bash
python test_query_expander.py
```

### 2. 실제 실행
```bash
streamlit run main.py
```

### 3. 로그 확인
애플리케이션 실행 시 다음 로그 확인:
```
쿼리 확장 시작...
  - 유사질문: ['...', '...', '...']
  - 핵심어: ['...', '...', '...', '...', '...']
  - 총 키워드 수: 9
키워드 그룹 검색 (9개 키워드)
```

## 하위 호환성

법률 용어 사전(law_terms_dictionary.json)이 없어도 시스템은 정상 작동합니다:
- 용어 사전 없음 → 쿼리 확장 비활성화
- 기존 TF-IDF 방식으로 자동 전환
- 로그에 "법률 용어 사전이 없어 쿼리 확장 비활성화" 메시지 표시

## 파일 구조

```
legal_precedents/
├── law_terms_dictionary.json        # 법률 용어 사전 (483개 용어)
├── utils/
│   ├── query_expander.py           # 쿼리 확장 모듈 (NEW)
│   ├── data_loader.py              # 용어 사전 로드 기능 추가
│   ├── vectorizer.py               # 키워드 그룹 검색 지원
│   ├── agent.py                    # 쿼리 확장 통합
│   └── __init__.py                 # query_expander export 추가
├── main.py                         # 용어 사전 로드 및 전달
└── test_query_expander.py          # 테스트 스크립트 (NEW)
```

## 주요 기능

### 1. load_law_terms_dictionary()
- law_terms_dictionary.json 파일 로드
- 483개 관세법 관련 용어 반환

### 2. generate_similar_questions()
- Gemini 2.0 Flash 사용
- 법률 용어 목록 참조하여 유사질문 3개 생성
- Temperature: 0.7 (다양성 확보)

### 3. extract_key_terms()
- Gemini 2.0 Flash 사용
- 법률 용어 목록에서 핵심어 5개 이내 추출
- Temperature: 0.3 (정확성 우선)

### 4. expand_query()
- 위 두 함수 통합
- 키워드 그룹 구성 및 반환

## 설정 가능한 파라미터

### query_expander.py
```python
# 유사질문 생성
temperature=0.7      # 다양성 조절
max_output_tokens=500

# 핵심어 추출
temperature=0.3      # 정확성 우선
max_output_tokens=300

# 법률 용어 목록 크기
terms_str = ", ".join(law_terms[:200])  # 처음 200개만 사용
```

### vectorizer.py
```python
# 키워드 그룹 검색
keyword_group=None   # None이면 기존 방식 사용
```

## 문제 해결

### Q: 쿼리 확장이 작동하지 않습니다
A: 다음을 확인하세요:
1. law_terms_dictionary.json 파일이 프로젝트 루트에 있는지 확인
2. 로그에서 "법률 용어 사전 로드 완료" 메시지 확인
3. Gemini API 키가 올바르게 설정되었는지 확인

### Q: 응답이 너무 느립니다
A: Gemini 2.0 Flash 호출이 추가되어 1-2초 지연될 수 있습니다. 이는 정상입니다.

### Q: 쿼리 확장을 비활성화하고 싶습니다
A: law_terms_dictionary.json 파일을 삭제하거나 이름을 변경하면 자동으로 기존 방식으로 전환됩니다.

## 향후 개선 사항

1. **캐싱**: 동일한 질문에 대한 쿼리 확장 결과 캐싱
2. **튜닝**: 유사질문 개수, 핵심어 개수 조절 가능하도록 설정 추가
3. **모니터링**: 쿼리 확장 효과 측정 지표 추가
4. **최적화**: 법률 용어 목록 크기 동적 조절

## 라이선스

이 프로젝트는 기존 legal_precedents 프로젝트의 일부입니다.
