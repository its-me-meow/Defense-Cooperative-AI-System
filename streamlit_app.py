import streamlit as st

st.set_page_config(
    page_title="한국 방산 협력 전략 AI 챗봇",
    page_icon="🛡️",
    layout="wide"
)

import time
import random

# 방산 협력 응답 템플릿 (src 모듈 사용 안함)
RESPONSE_TEMPLATES = {
    "인도": """### 🚀 한-인도 미사일 기술 협력 전략
- **인도 국방예산**: 730억 달러 (2024년 기준, 세계 3위)
- **BrahMos 기술력**: 마하 2.8~3.0 초음속 순항미사일
- **현무 시리즈**: 사거리 300-800km, 한국 독자개발

### 💰 3단계 투자 계획 (총 23억 달러)
**1단계: 공동연구개발 (2025-2026, 3억 달러)**
- 한국 투자: 1.8억 달러 (추진체, 시스템 통합)
- 인도 투자: 1.2억 달러 (유도시스템, AI 소프트웨어)

**2단계: 프로토타입 개발 (2026-2028, 8억 달러)**
- 50:50 투자 분담, 목표 성능: 사거리 1,500km

### 📊 투자수익률 (10년 기준)
- **직접 수출수익**: 40억 달러
- **총 ROI**: 332% (회수기간 4.8년)
- **고용창출**: 직간접 15,000명

*[AI 전략 컨설턴트 분석]*""",

    "UAE": """### 🏜️ UAE 사막환경 특화 방산시스템 개발
- **UAE 국방예산**: 220억 달러 (2024년 기준)
- **천궁-II 성공사례**: 38억 달러 수출계약

### 💎 단계별 투자전략 (총 2.4조원)
**1단계: 기반구축 (2025-2026, 1,500억원)**
- 알아인 사막환경 테스트베드 구축
- 아부다비 한-UAE 공동연구센터 설립

**2단계: 기술개발 (2026-2028, 6,500억원)**
- 천궁-III 사막형 개량: 고온내구성 전자부품
- AESA 레이더 열관리 시스템 최적화

### 📈 투자수익률 (10년 기준, ROI 521%)
- **직접 수출수익**: 7.5조원
- **기술료 수입**: 1.8조원
- **MRO 서비스**: 3.2조원

*[중동 전문가 분석]*""",

    "브라질": """### ✈️ 한-브라질 Embraer 항공우주 전략협력
- **브라질 국방예산**: 290억 달러 (남미 최대)
- **Embraer 글로벌 위상**: 세계 3위 항공기 제조사
- **상호보완성**: 브라질 기체설계 + 한국 항공전자

### 🛩️ 3대 공동개발 프로젝트
**1. KF/E 경제형 훈련기 (투자 18억 달러)**
- 기술분담: 한국 60% (항공전자), 브라질 40% (기체)
- 개발기간: 5년 (2025-2030)
- 생산계획: 양국 각 100대, 제3국 수출 300-400대

### 💰 투자 및 수익구조
- **총 투자**: 33.5억 달러
- **예상 수익**: 80억 달러 (15년 누적)
- **ROI**: 265% (회수기간 5.3년)

*[항공산업 전문가 분석]*""",

    "동남아": """### 🌏 ASEAN-Korea 방산협력 통합플랫폼
- **ASEAN 시장**: 6.7억 인구, 연간 150억 달러 방산수요
- **해양국가 특성**: 인도네시아 17,508개 섬, 필리핀 7,641개 섬

### 🏢 ASEAN-Korea 방산협력센터 설립
**싱가포르 본부**
- 총투자: 1억 달러, 연간 운영비 5천만 달러
- 기능: 전략기획, 정책조율, 기술표준화

### 💰 ASEAN 방산펀드 (총 100억 달러)
- 한국 기여: 40억 달러 (40%)
- ASEAN 기여: 50억 달러 (50%)
- 국제기구: 10억 달러

*[ASEAN 협력 전문가 분석]*""",

    "기본": """### 📊 비NATO 국가 방산협력 전략
- **글로벌 방산시장**: 연간 5,800억 달러, 연 4.2% 성장
- **한국 방산수출**: 2023년 172억 달러 (세계 9위)
- **비NATO 시장**: 전체 시장의 65%, 성장 잠재력 높음

### 🎯 우선 협력 대상국
**1순위: 인도, UAE, 폴란드**
- 대규모 국방예산, 기술이전 의지, 정치적 안정성

**2순위: 브라질, 인도네시아, 말레이시아**
- 지역 허브 국가, 제3국 수출 기반

### 📈 기대효과
- **수출 목표**: 2030년 350억 달러
- **기술 자립도**: 90% 달성
- **고용창출**: 15만명 직간접 고용

*[방산 전략 전문가 분석]*"""
}

def get_ai_response(user_input):
    """AI 응답 생성"""
    input_lower = user_input.lower()
    
    if "인도" in input_lower:
        template = RESPONSE_TEMPLATES["인도"]
    elif "uae" in input_lower or "아랍" in input_lower:
        template = RESPONSE_TEMPLATES["UAE"]
    elif "브라질" in input_lower:
        template = RESPONSE_TEMPLATES["브라질"]
    elif any(country in input_lower for country in ["동남아", "인도네시아", "태국", "말레이시아"]):
        template = RESPONSE_TEMPLATES["동남아"]
    else:
        template = RESPONSE_TEMPLATES["기본"]
    
    return template

# 메인 UI
st.title("🛡️ 한국 방산 협력 전략 AI 챗봇")
st.markdown("**방산기술 수출 확대를 위한 전문 AI 어시스턴트**")
st.success("🚀 방산 협력 AI 시스템 준비 완료")

# 사용 가이드
with st.expander("💡 사용 가이드"):
    st.write("""
    **전문 질문 예시:**
    - 인도와의 미사일 기술 협력 전략은?
    - UAE 투자 규모는 어느 정도인가요?
    - 브라질과 항공우주 협력이 가능한가요?
    - 동남아시아 해양안보 협력 방안은?
    """)

# 채팅 기록
if "messages" not in st.session_state:
    st.session_state.messages = []

# 이전 대화 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 채팅 입력
if prompt := st.chat_input("방산 협력 전략에 대해 질문하세요..."):
    # 사용자 메시지
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # AI 응답
    with st.chat_message("assistant"):
        with st.spinner("🤔 분석 중..."):
            start_time = time.time()
            response = get_ai_response(prompt)
            generation_time = time.time() - start_time
            
            st.markdown(response)
            
            # 응답 정보
            col1, col2 = st.columns(2)
            with col1:
                st.caption(f"⏱️ 생성시간: {generation_time:.2f}초")
            with col2:
                st.caption(f"📝 길이: {len(response)} 문자")
    
    st.session_state.messages.append({"role": "assistant", "content": response})

# 하단 컨트롤
st.divider()
col1, col2 = st.columns(2)

with col1:
    if st.button("🔄 대화 초기화"):
        st.session_state.messages = []
        st.rerun()

with col2:
    st.metric("총 대화 수", len([m for m in st.session_state.messages if m["role"] == "user"]))