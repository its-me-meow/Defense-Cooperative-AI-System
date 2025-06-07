import re
from typing import Dict, List, Tuple, Optional
from enum import Enum
import json

class QueryType(Enum):
    """질문 유형 분류"""
    COUNTRY_ANALYSIS = "국가별_분석"
    TECH_COMPARISON = "기술_비교"
    COOPERATION_STRATEGY = "협력_전략"
    MARKET_ANALYSIS = "시장_분석"
    INVESTMENT_ROI = "투자_수익"
    ROADMAP_TIMELINE = "로드맵_일정"
    POLICY_RECOMMENDATION = "정책_제언"
    RISK_ASSESSMENT = "리스크_평가"
    PRIORITY_RANKING = "우선순위_순위"  # 새로 추가

class LlamaPromptEngineer:
    """향상된 방산 협력 전략 프롬프트 엔지니어링 시스템"""
    
    def __init__(self, knowledge_base):
        self.kb = knowledge_base
        self.system_prompt = self._build_system_prompt()
        self.query_patterns = self._build_query_patterns()
        self.pdf_qa_database = self._build_pdf_qa_database()
        
    def _build_system_prompt(self) -> str:
        """시스템 프롬프트 구축"""
        return """당신은 대한민국 방산기술 수출 확대를 위한 국가별 협력 전략 전문가입니다.

## 역할 및 전문성
- 비NATO 국가와의 방산 협력 전략 수립
- 국가별 국방 능력, 기술 역량, 상보적 기술 분야 분석
- 방산 수출 시장 분석 및 투자 수익성 평가
- 단계적 협력 로드맵 및 정책 제언 제공

## 응답 원칙
1. **정확성**: 제공된 데이터와 분석에 기반한 사실적 정보 제공
2. **구체성**: 구체적 수치, 일정, 프로젝트명 포함
3. **실용성**: 실행 가능한 전략과 단계별 실행방안 제시
4. **균형성**: 기회와 리스크를 균형있게 평가
5. **완전성**: 질문에 대한 완전하고 포괄적인 답변 제공

## 중요: 지식 범위
- 방산 협력, 기술 이전, 국가별 전략에 관련된 질문만 답변
- 범위를 벗어난 질문에는 정중히 안내하고 관련 질문을 유도
- 불확실한 정보는 추측하지 말고 명시적으로 언급"""

    def _build_query_patterns(self) -> Dict[QueryType, List[str]]:
        """질문 유형별 패턴 정의 - 우선순위 패턴 추가"""
        return {
            QueryType.PRIORITY_RANKING: [
                r"우선순위.*?(국가|순위)",
                r"순위.*?(알려|제시|설명)",
                r"1순위|2순위|3순위",
                r"우선.*?(선정|선택|대상)"
            ],
            QueryType.COUNTRY_ANALYSIS: [
                r"(\w+)\s*(국가?|나라).*?(분석|평가|현황)",
                r"(\w+).*?(국방|방산).*?(능력|역량)",
                r"(\w+).*?(시장|투자|협력)\s*환경"
            ],
            QueryType.TECH_COMPARISON: [
                r"(기술|과학기술).*?(비교|차이|대비)",
                r"(\w+)\s*(기술|역량).*?(한국|우리나라)",
                r"상보적?.*?(기술|협력|분야)"
            ],
            QueryType.COOPERATION_STRATEGY: [
                r"협력.*?(전략|방안|계획)",
                r"공동.*?(개발|생산|프로젝트)",
                r"파트너십.*?(구축|강화)"
            ],
            QueryType.INVESTMENT_ROI: [
                r"투자.*?(규모|수익|효과)",
                r"ROI|수익률|경제.*?효과",
                r"비용.*?(편익|대비)"
            ]
        }

    def _build_pdf_qa_database(self) -> Dict[str, Dict]:
        """PDF 기반 질문-답변 데이터베이스"""
        return {
            "중동_우선순위": {
                "keywords": ["중동", "북아프리카", "우선순위", "순위"],
                "response": """중동 및 북아프리카 지역의 방산 수출 우선순위는 다음과 같습니다:

**1순위: UAE (아랍에미리트)**
- 방위산업 투자: 연간 약 220억 달러
- 중점 기술 영역: 미사일 방어, 전자전, 무인 시스템
- 상보적 기술: 고급 레이더 시스템, 전자정보 시스템
- 시장 기회: 기술 다변화 추진으로 새로운 파트너 모색 중
- 협력 용이성: 높음 (한-UAE 특별 전략적 파트너십)

**2순위: 이집트**
- 방위산업 투자: 연간 약 50억 달러 (아프리카 최대)
- 중점 기술 영역: 사막 환경 운용, 방공망 운용, 대테러 장비
- 상보적 기술: 극한 사막환경 장비 운용 노하우
- 시장 기회: K9 자주포 수출 등 기존 협력 경험

**3순위: 카타르**
- 방위산업 투자: 중간 규모이나 구매력 우수
- 중점 기술 영역: 방공, 해양 보안
- 협력 장벽: 지역 정치적 복잡성

**4순위: 모로코**
- 방위산업 투자: 상대적으로 제한적
- 중점 기술 영역: 국경 감시, 대테러
- 시장 기회: 아프리카 진출 교두보 가능"""
            },
            "남아시아_우선순위": {
                "keywords": ["남아시아", "동남아시아", "우선순위", "인도"],
                "response": """남아시아 및 동남아시아 지역의 방산 수출 우선순위는 다음과 같습니다:

**1순위: 인도**
- 방위산업 투자: 연간 약 730억 달러 (세계 3위)
- 중점 기술 영역: 미사일 기술, 항공우주, 전자전
- 상보적 기술: 미사일 유도 시스템, 소프트웨어 개발, 위성 기술
- 시장 기회: 'Make in India' 정책으로 공동생산 가능성 높음
- 전략적 중요성: 매우 높음

**2순위: 인도네시아**
- 방위산업 투자: 연간 약 90억 달러
- 중점 기술 영역: 해양 안보, 열대환경 장비
- 상보적 기술: 열대/해양 환경 최적화 기술
- 협력 경험: KF-21 공동개발 파트너
- 시장 기회: 아세안 최대 시장

**3순위: 태국**
- 방위산업 투자: 연간 약 70억 달러
- 중점 기술 영역: 국경 감시, 대테러 장비
- 기존 협력: K9 자주포 도입 경험
- 상보적 기술: 열대 환경 운용 기술

**4순위: 말레이시아**
- 방위산업 투자: 연간 약 40억 달러
- 중점 기술 영역: 해양 감시, 사이버 방어
- 협력 경험: FA-50 도입
- 시장 특성: 중급 규모이나 안정적"""
            },
            "인도_미사일_협력": {
                "keywords": ["인도", "미사일", "협력", "BrahMos", "현무"],
                "response": """### 🚀 현무-BrahMos 합동 미사일 개발 프로그램
- **인도 국방예산**: 730억 달러 (2024년 기준, 세계 3위)
- **BrahMos 기술력**: 마하 2.8~3.0 초음속 순항미사일, 러시아 합작 성공사례
- **현무 시리즈**: 사거리 300-800km, 한국 독자개발 정밀타격 무기체계
- **시장 잠재력**: 동남아-중동 정밀타격 시장 연 5.8% 성장, 118억 달러 규모

### 💰 3단계 투자 계획 (총 23억 달러)
**1단계: 공동연구개발 (2025-2026, 3억 달러)**
- 한국 투자: 1.8억 달러 (추진체, 시스템 통합)
- 인도 투자: 1.2억 달러 (유도시스템, AI 소프트웨어)
- 부산-첸나이 Twin R&D Center 설립
- 상호 기술진 파견: 한국 50명 ↔ 인도 60명

**2단계: 프로토타입 개발 (2026-2028, 8억 달러)**
- 50:50 투자 분담 (각 4억 달러)
- 목표 성능: 사거리 1,500km, CEP 1m 이하
- 시험장: 인도 칼람섬, 한국 안흥시험장
- MTCR 규제 대응: 300km 버전부터 단계적 개발

**3단계: 양산 및 수출 (2028-2030, 12억 달러)**
- 한국 생산분: 5억 달러 (연간 80기)
- 인도 생산분: 7억 달러 (연간 120기, Make in India 60% 현지화)
- 1차 수출 대상: 베트남 50기, 필리핀 30기, 태국 40기

### 📊 투자수익률 분석 (10년 기준)
- **직접 수출수익**: 40억 달러 (미사일 본체 판매)
- **기술 라이센싱**: 8억 달러 (현지생산 로열티 3-5%)
- **MRO 서비스**: 12억 달러 (20년 유지보수 계약)
- **총 ROI**: 332% (회수기간 4.8년)
- **고용창출**: 직간접 15,000명

### 🎯 기술 융합 혁신점
**추진체 기술 결합**
- 인도 램제트 엔진 + 한국 고체추진체
- 연료효율 35% 개선, 사거리 20% 연장
- 하이브리드 궤도: 초음속 순항 + 탄도미사일 복합

**AI 기반 정밀 유도**
- 인도 AI 소프트웨어 (93% 위협식별 정확도)
- 한국 하드웨어 플랫폼 (다중센서 융합)
- 실시간 표적 식별 및 부수피해 최소화

### 🌏 지정학적 의미
- **Quad 체제 강화**: 인도-태평양 전략에서 한국 역할 확대
- **중국 견제**: 동아시아-남아시아 연결축 형성  
- **기술 자립**: 서구 의존도 감소, 아시아 기술생태계 구축

*[AI 분석 - 인도 DRDO 공식 데이터 기반]*"""
            },
            "UAE_투자": {
                "keywords": ["UAE", "투자", "규모", "아랍에미리트"],
                "response": """### 🇦🇪 UAE와 한국의 기술 통합 전략 비즈니스 모델

## 1. 사막환경 최적화 통합 방공시스템
**협력 구조:**
- 한국: 천궁 미사일 시스템 + 시스템 통합 기술
- UAE: 고온환경 적응 기술 + 현지 맞춤화 기술
- 투자 규모: 총 7억 달러 (한국 4억, UAE 3억)
- 생산 분담: 한국 60%, UAE 40%

**비즈니스 모델:**
- Phase 1: 공동개발 (2년, 2억 달러)
- Phase 2: 시제품 제작 및 시험 (1년, 1.5억 달러)
- Phase 3: 양산 및 GCC 지역 마케팅 (3년, 3.5억 달러)

## 2. 통합 C4ISR 체계 개발
**협력 구조:**
- 한국: TICN 지휘통제 체계 + 네트워크 기술
- UAE: NASSR 고성능 레이더 + 극한기후 적응 기술
- 투자 규모: 총 8억 달러 (50:50 분담)

**수익 모델:**
- 기술 라이센싱: 생산액의 3-5% 로열티
- 유지보수 서비스: 연간 매출의 15-20%
- 업그레이드 패키지: 시스템 가격의 30-40%

## 3. 드론 방어 통합 솔루션
**혁신적 협력 모델:**
- 한국: 안티드론 레이더 + 하드웨어 플랫폼
- UAE: D-Fend 전자전 기술 + AI 기반 위협 분석
- 시장 확장: 군사용 → 민간 인프라 보호로 확대

**예상 효과:**
- 경제적: 10년간 90억 달러 수출 창출
- 기술적: 극한환경 기술 확보로 글로벌 경쟁력 강화
- 전략적: 중동 방산 협력 허브 구축"""
            }
        }
    
    def classify_query(self, user_query: str) -> Tuple[QueryType, Dict]:
        """사용자 질문 유형 분류 및 키워드 추출"""
        extracted_info = {
            "countries": [],
            "tech_fields": [],
            "keywords": []
        }
        
        # 국가명 추출
        countries = ["인도", "UAE", "브라질", "인도네시아", "말레이시아", 
                    "태국", "남아프리카공화국", "남아공", "이집트", "중동", 
                    "북아프리카", "남아시아", "동남아시아"]
        for country in countries:
            if country in user_query:
                extracted_info["countries"].append(country)
        
        # 기술 분야 추출
        tech_fields = ["미사일", "방공", "항공", "해군", "전자전", "사이버", 
                      "레이더", "무인", "드론", "C4ISR", "감시정찰"]
        for field in tech_fields:
            if field in user_query:
                extracted_info["tech_fields"].append(field)
        
        # 질문 유형 분류 - 우선순위 우선 검사
        for query_type, patterns in self.query_patterns.items():
            for pattern in patterns:
                if re.search(pattern, user_query):
                    return query_type, extracted_info
        
        return QueryType.COUNTRY_ANALYSIS, extracted_info
    
    def find_pdf_answer(self, user_query: str) -> Optional[str]:
        """PDF 데이터에서 정확한 답변 찾기"""
        query_lower = user_query.lower()
        
        for qa_key, qa_data in self.pdf_qa_database.items():
            keywords = qa_data["keywords"]
            # 키워드 매칭 점수 계산
            match_score = sum(1 for keyword in keywords if keyword in query_lower)
            keyword_threshold = len(keywords) * 0.5  # 50% 이상 매칭
            
            if match_score >= keyword_threshold:
                return qa_data["response"]
        
        return None
    
    def retrieve_context(self, query_type: QueryType, extracted_info: Dict) -> str:
        """질문 유형에 따른 관련 컨텍스트 검색"""
        context_parts = []
        
        if query_type == QueryType.COUNTRY_ANALYSIS or query_type == QueryType.PRIORITY_RANKING:
            for country in extracted_info["countries"]:
                if country in self.kb.countries:
                    profile = self.kb.countries[country]
                    context_parts.append(f"""
## {country} 국방 프로필
- 국방예산: {profile.defense_budget}
- 병력규모: {profile.military_personnel}  
- 주요 방산기업: {', '.join(profile.defense_companies)}
- 전략적 중요도: {profile.strategic_importance}
- 협력 용이성: {profile.cooperation_feasibility}
""")
        
        elif query_type == QueryType.TECH_COMPARISON:
            for country in extracted_info["countries"]:
                if country in self.kb.countries:
                    comp_tech = self.kb.countries[country].complementary_tech
                    context_parts.append(f"""
## {country} 기술 상보성 분석
### 한국 강점기술:
{chr(10).join(['- ' + tech for tech in comp_tech.korea_strengths])}

### {country} 강점기술:
{chr(10).join(['- ' + tech for tech in comp_tech.partner_strengths])}

### 공동개발 잠재분야:
{chr(10).join(['- ' + tech for tech in comp_tech.joint_potential])}
""")
        
        return "\n".join(context_parts) if context_parts else ""
    
    def generate_diversified_prompt(self, user_query: str, attempt: int = 0) -> str:
        """다양성이 강화된 프롬프트 생성"""
        # PDF 데이터에서 정확한 답변 찾기
        pdf_answer = self.find_pdf_answer(user_query)
        if pdf_answer:
            return pdf_answer
        
        query_type, extracted_info = self.classify_query(user_query)
        context = self.retrieve_context(query_type, extracted_info)
        
        # 다양성 지시사항
        diversity_instructions = [
            "PDF 데이터를 기반으로 정확하고 구체적인 정보를 제공하세요.",
            "실제 데이터와 수치를 포함하여 상세히 설명하세요.", 
            "단계별 실행 방안과 구체적 투자 규모를 제시하세요.",
            "기술적 상보성과 지정학적 의미를 함께 분석하세요.",
            "리스크와 기회를 균형있게 평가하여 제시하세요."
        ]
        
        # 응답 구조 다양화
        structure_variants = [
            "### 📊 핵심 분석\n### 🎯 전략적 제언\n### 📈 기대효과 및 리스크\n### 💡 추가 고려사항",
            "### 🔍 심층 분석\n### 🚀 추진 전략\n### 💰 수익성 분석\n### 🌟 차별화 방안",
            "### 📈 전략 분석\n### 📋 실행 방안\n### ⚖️ 장단점 평가\n### 🔮 미래 전망",
            "### 🎯 현황 평가\n### 🔄 협력 전략\n### 🎲 기회와 위험\n### 💎 혁신 방안",
            "### 💼 시장 분석\n### 💡 혁신 관점\n### 📊 투자 대비 효과\n### 🌐 글로벌 관점"
        ]
        
        selected_instruction = diversity_instructions[attempt % len(diversity_instructions)]
        selected_structure = structure_variants[attempt % len(structure_variants)]
        
        user_prompt = f"""## 배경 정보
{context}

## 사용자 질문
{user_query}

## 특별 지시사항
{selected_instruction}

## 요청사항
위 배경 정보를 바탕으로 다음 형식으로 완전하고 상세한 답변을 제공해주세요:

{selected_structure}

중요: 
- 모든 내용을 빠짐없이 포괄적으로 설명하세요
- 구체적인 수치와 데이터를 포함하세요
- 실행 가능한 구체적 방안을 제시하세요
- 답변을 중간에 자르지 말고 완전히 제공하세요
"""
        
        return user_prompt
    
    def generate_prompt(self, user_query: str) -> str:
        """기본 프롬프트 생성 (하위 호환성)"""
        # PDF 데이터 우선 확인
        pdf_answer = self.find_pdf_answer(user_query)
        if pdf_answer:
            return pdf_answer
            
        return self.generate_diversified_prompt(user_query, 0)

    def is_defense_related(self, query: str) -> bool:
        """방산 관련 질문인지 확인"""
        defense_keywords = [
            "방산", "미사일", "방어", "군사", "무기", "협력", "수출", "투자",
            "인도", "UAE", "브라질", "중동", "동남아", "아프리카", "기술이전",
            "사이버", "우주", "항공", "해양", "AI", "드론", "레이더", "방공"
        ]
        
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in defense_keywords)

def create_comprehensive_prompt_system(knowledge_base):
    """종합적인 프롬프트 시스템 생성"""
    engineer = LlamaPromptEngineer(knowledge_base)
    
    def get_response_prompt(user_query: str, attempt: int = 0) -> str:
        """사용자 쿼리에 대한 완전한 응답 프롬프트 생성"""
        return engineer.generate_diversified_prompt(user_query, attempt)
    
    def check_scope(user_query: str) -> bool:
        """질문이 방산 협력 범위 내인지 확인"""
        return engineer.is_defense_related(user_query)
    
    # 기존 방식도 지원
    engineer.get_response_prompt = get_response_prompt
    engineer.check_scope = check_scope
    return engineer