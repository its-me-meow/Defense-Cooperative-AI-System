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

class LlamaPromptEngineer:
    """Llama3.1을 위한 방산 협력 전략 프롬프트 엔지니어링 시스템"""
    
    def __init__(self, knowledge_base):
        self.kb = knowledge_base
        self.system_prompt = self._build_system_prompt()
        self.query_patterns = self._build_query_patterns()
        
    def _build_system_prompt(self) -> str:
        """시스템 프롬프트 구축"""
        return """<|begin_of_text|><|start_header_id|>system<|end_header_id|>

당신은 대한민국 방산기술 수출 확대를 위한 국가별 협력 전략 전문가입니다.

## 역할 및 전문성
- 비NATO 국가(인도, UAE, 브라질, 인도네시아, 말레이시아, 태국, 남아프리카공화국, 이집트)와의 방산 협력 전략 수립
- 국가별 국방 능력, 기술 역량, 상보적 기술 분야 분석
- 방산 수출 시장 분석 및 투자 수익성 평가
- 단계적 협력 로드맵 및 정책 제언 제공

## 응답 원칙
1. **정확성**: 제공된 데이터와 분석에 기반한 사실적 정보 제공
2. **구체성**: 구체적 수치, 일정, 프로젝트명 포함
3. **실용성**: 실행 가능한 전략과 단계별 실행방안 제시
4. **균형성**: 기회와 리스크를 균형있게 평가
5. **전략적 시각**: 장기적 관점에서 국가 이익 고려

## 응답 다양성 지침
- 매번 다른 관점과 접근 방식을 사용하여 답변하세요
- 이전 답변과 구별되는 새로운 분석 프레임워크를 적용하세요
- 다양한 헤더와 구조를 활용하여 내용을 구성하세요
- 창의적이고 혁신적인 해결책을 제시하세요

<|eot_id|>"""

    def _build_query_patterns(self) -> Dict[QueryType, List[str]]:
        """질문 유형별 패턴 정의"""
        return {
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
            QueryType.MARKET_ANALYSIS: [
                r"시장.*?(규모|전망|분석)",
                r"수출.*?(가능성|기회|확대)",
                r"경쟁.*?(환경|업체|우위)"
            ],
            QueryType.INVESTMENT_ROI: [
                r"투자.*?(규모|수익|효과)",
                r"ROI|수익률|경제.*?효과",
                r"비용.*?(편익|대비)"
            ]
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
                    "태국", "남아프리카공화국", "남아공", "이집트"]
        for country in countries:
            if country in user_query:
                extracted_info["countries"].append(country)
        
        # 기술 분야 추출
        tech_fields = ["미사일", "방공", "항공", "해군", "전자전", "사이버", 
                      "레이더", "무인", "드론", "C4ISR", "감시정찰"]
        for field in tech_fields:
            if field in user_query:
                extracted_info["tech_fields"].append(field)
        
        # 질문 유형 분류
        for query_type, patterns in self.query_patterns.items():
            for pattern in patterns:
                if re.search(pattern, user_query):
                    return query_type, extracted_info
        
        return QueryType.COUNTRY_ANALYSIS, extracted_info
    
    def retrieve_context(self, query_type: QueryType, extracted_info: Dict) -> str:
        """질문 유형에 따른 관련 컨텍스트 검색"""
        context_parts = []
        
        if query_type == QueryType.COUNTRY_ANALYSIS:
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
        
        return "\n".join(context_parts)
    
    def generate_diversified_prompt(self, user_query: str, attempt: int = 0) -> str:
        """다양성이 강화된 프롬프트 생성"""
        query_type, extracted_info = self.classify_query(user_query)
        context = self.retrieve_context(query_type, extracted_info)
        
        # 다양성 지시사항
        diversity_instructions = [
            "창의적이고 혁신적인 관점에서 분석하세요.",
            "이전 답변과는 완전히 다른 새로운 접근 방식을 사용하세요.", 
            "참신하고 독창적인 해결책을 제시하세요.",
            "다각도에서 종합적으로 검토하고 재조명해주세요.",
            "기존 틀을 벗어난 혁신적 시각으로 문제를 분석하세요."
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
        
        user_prompt = f"""<|start_header_id|>user<|end_header_id|>

## 배경 정보
{context}

## 사용자 질문
{user_query}

## 특별 지시사항
{selected_instruction}

## 요청사항
위 배경 정보를 바탕으로 다음 형식으로 답변해주세요:

{selected_structure}

<|eot_id|><|start_header_id|>assistant<|end_header_id|>

"""
        
        return self.system_prompt + user_prompt
    
    def generate_prompt(self, user_query: str) -> str:
        """기본 프롬프트 생성 (하위 호환성)"""
        return self.generate_diversified_prompt(user_query, 0)

def create_comprehensive_prompt_system(knowledge_base):
    """종합적인 프롬프트 시스템 생성"""
    engineer = LlamaPromptEngineer(knowledge_base)
    
    def get_response_prompt(user_query: str, attempt: int = 0) -> str:
        """사용자 쿼리에 대한 완전한 응답 프롬프트 생성"""
        return engineer.generate_diversified_prompt(user_query, attempt)
    
    # 기존 방식도 지원
    engineer.get_response_prompt = get_response_prompt
    return engineer