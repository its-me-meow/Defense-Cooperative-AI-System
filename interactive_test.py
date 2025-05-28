from src.data_structure import build_knowledge_base
from src.prompt_engineering import create_comprehensive_prompt_system
import time

print("🤖 방산 협력 AI 대화 테스트")
print("=" * 40)

# 시스템 초기화
kb = build_knowledge_base()
prompt_engineer = create_comprehensive_prompt_system(kb)

def generate_smart_response(query):
    """지능적 더미 응답 생성"""
    start_time = time.time()
    
    if "인도" in query and ("미사일" in query or "협력" in query):
        response = """### 📊 핵심 분석
- 인도는 BrahMos 초음속 미사일로 유도시스템 분야 고도 기술 보유
- 한국은 현무 시리즈로 고체추진체 기술 세계 수준 달성
- 양국 기술 결합 시 성능 15-20% 향상, 개발기간 30% 단축 가능
- 인도 국방예산 730억 달러로 충분한 투자 여력 보유

### 🎯 전략적 제언
**단기전략 (1-2년)**
- 한-인도 미사일기술협력 공동위원회 설치
- 현무-BrahMos 기술통합 가능성 연구 착수
- 투자규모: 3억 달러 (한국 1.8억, 인도 1.2억)

**중기전략 (3-5년)**  
- 현무-인도 합금미사일 프로토타입 개발
- 시험발사 및 성능검증 단계

### 📈 기대효과 및 리스크
**기대효과**: 직접 수출수익 10년간 40억 달러 예상
**주요 리스크**: 인도의 복잡한 관료주의로 인한 의사결정 지연

*[AI 더미 응답 - 실제 모델 연결 시 더욱 정교해집니다]*"""
        
    elif "UAE" in query:
        response = """### 📊 핵심 분석
- UAE 국방예산 220억 달러, 천궁-II 수출 성공(38억 달러)
- EDGE Group과의 협력을 통한 현지 생산 모델 가능

### 🎯 전략적 제언
- 사막환경 최적화 통합 방공시스템 공동 개발
- 총 투자: 2.4조원, 예상 ROI: 321%

### 📈 기대효과 및 리스크
**기대효과**: 10년간 90억 달러 수출 예상
**주요 리스크**: 미국/서방 무기체계 호환성 요구

*[AI 더미 응답 - 실제 모델 연결 시 더욱 정교해집니다]*"""
        
    elif "브라질" in query:
        response = """### 📊 핵심 분석
- 브라질 국방예산 290억 달러 (남미 최대)
- Embraer의 뛰어난 항공기 설계 능력과 한국 전자장비 기술 상호보완성

### 🎯 전략적 제언
- KF/E 공동개발 훈련기: Embraer 설계 + 한국 전자장비
- 중형 해상초계기 공동 개발

### 📈 기대효과 및 리스크
**기대효과**: 10년간 60억 달러 수출 예상
**주요 리스크**: 행정적 복잡성, 예산 불안정성

*[AI 더미 응답 - 실제 모델 연결 시 더욱 정교해집니다]*"""
        
    else:
        response = """### 📊 핵심 분석
- 비NATO 국가와의 방산 협력은 한국 방산 수출 다변화의 핵심
- 상호보완적 기술 협력을 통한 윈-윈 모델 구축 가능

### 🎯 전략적 제언
- 국가별 맞춤형 협력 전략 수립
- 기술이전과 공동개발을 통한 장기적 파트너십 구축

### 📈 기대효과 및 리스크
**기대효과**: 방산 수출 다변화 및 기술 역량 강화
**주요 리스크**: 정치적 변동 및 기술 통제 이슈

*[AI 더미 응답 - 실제 모델 연결 시 더욱 정교해집니다]*"""
    
    generation_time = time.time() - start_time
    return {
        "response": response,
        "generation_time": generation_time
    }

print("✅ 시스템 준비 완료!")
print("질문을 입력하세요 ('종료'로 끝내기):")
print("💡 추천 질문:")
print("  - 인도와의 미사일 기술 협력 전략은?")
print("  - UAE 투자 규모는?")
print("  - 브라질과 항공우주 협력이 가능한가요?")

while True:
    user_input = input("\n👤 질문: ").strip()
    
    if user_input.lower() in ['종료', 'quit', 'exit']:
        print("👋 감사합니다!")
        break
    
    if not user_input:
        continue
    
    print("🤖 AI: ")
    result = generate_smart_response(user_input)
    print(result['response'])
    print(f"\n⏱ 생성 시간: {result['generation_time']:.2f}초")