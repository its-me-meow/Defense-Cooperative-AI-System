import json
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Union
from enum import Enum

class TechMaturityLevel(Enum):
    INITIAL = "초기"
    DEVELOPING = "발전"
    INTERMEDIATE = "중간"
    ADVANCED = "고도"
    CUTTING_EDGE = "최첨단"

class CooperationLevel(Enum):
    LOW = "하"
    MEDIUM = "중"
    HIGH = "상"

@dataclass
class TechnologyCapability:
    """기술 역량 데이터 구조"""
    field: str
    maturity_level: str
    key_programs: List[str]
    strengths: List[str]
    
@dataclass
class ComplementaryTech:
    """상보적 기술 분야"""
    korea_strengths: List[str]
    partner_strengths: List[str]
    joint_potential: List[str]
    complementarity_score: str

@dataclass
class CountryDefenseProfile:
    """국가별 국방 프로필"""
    country_name: str
    defense_budget: str
    military_personnel: str
    key_military_assets: Dict[str, List[str]]
    defense_companies: List[str]
    tech_capabilities: List[TechnologyCapability]
    complementary_tech: ComplementaryTech
    cooperation_barriers: List[str]
    cooperation_opportunities: List[str]
    strategic_importance: str
    cooperation_feasibility: str

@dataclass
class CooperationProject:
    """협력 프로젝트 정보"""
    project_name: str
    target_countries: List[str]
    tech_focus: List[str]
    investment_required: Dict[str, float]
    expected_roi: float
    timeline: Dict[str, str]
    market_potential: str
    success_factors: List[str]
    risk_factors: List[str]

class DefenseCooperationKnowledgeBase:
    """방산 협력 전략 지식 베이스"""
    
    def __init__(self):
        self.countries = {}
        self.cooperation_projects = {}
        self.market_analysis = {}
        self.policy_recommendations = []
        
    def add_country_profile(self, profile: CountryDefenseProfile):
        """국가 프로필 추가"""
        self.countries[profile.country_name] = profile
        
    def add_cooperation_project(self, project: CooperationProject):
        """협력 프로젝트 추가"""
        self.cooperation_projects[project.project_name] = project
        
    def get_country_capabilities(self, country: str, tech_field: str = None) -> Dict:
        """특정 국가의 기술 역량 조회"""
        if country not in self.countries:
            return {}
            
        profile = self.countries[country]
        if tech_field:
            relevant_caps = [cap for cap in profile.tech_capabilities 
                           if tech_field.lower() in cap.field.lower()]
            return {
                "country": country,
                "field": tech_field,
                "capabilities": relevant_caps
            }
        return asdict(profile)
        
    def find_complementary_opportunities(self, tech_field: str) -> List[Dict]:
        """기술 분야별 상보적 협력 기회 탐색"""
        opportunities = []
        for country, profile in self.countries.items():
            for cap in profile.tech_capabilities:
                if tech_field.lower() in cap.field.lower():
                    opportunities.append({
                        "country": country,
                        "capability": cap,
                        "complementary_tech": profile.complementary_tech,
                        "strategic_importance": profile.strategic_importance
                    })
        return opportunities

def build_knowledge_base():
    """문서 내용을 바탕으로 지식 베이스 구축"""
    kb = DefenseCooperationKnowledgeBase()
    
    # 인도 프로필 생성
    india_profile = CountryDefenseProfile(
        country_name="인도",
        defense_budget="약 730억 달러 (2024년 기준, 세계 3위)",
        military_personnel="정규군 140만 명, 예비군 210만 명",
        key_military_assets={
            "육군": ["T-90, T-72 전차", "BMP-2 장갑차", "Pinaka 다연장로켓시스템"],
            "해군": ["항공모함 2척", "원자력 잠수함 2척", "구축함 10척"],
            "공군": ["Su-30MKI, Rafale, Tejas 전투기", "S-400 방공시스템"]
        },
        defense_companies=["HAL", "BEL", "DRDO"],
        tech_capabilities=[
            TechnologyCapability("미사일 기술", "고도", 
                               ["Agni 탄도미사일", "BrahMos 순항미사일"], 
                               ["정밀 유도", "초음속 기술"]),
            TechnologyCapability("사이버 안보", "고도", 
                               ["AI 기반 위협 탐지"], 
                               ["방위 사이버 에이전시"])
        ],
        complementary_tech=ComplementaryTech(
            korea_strengths=["함정 추진 및 전투시스템", "정밀 타격 무기", "방공 시스템"],
            partner_strengths=["미사일 유도 시스템", "우주 발사체 기술", "AI 기반 위협 탐지"],
            joint_potential=["대함 미사일 시스템", "AESA 레이더", "무인 전투 시스템"],
            complementarity_score="상"
        ),
        cooperation_barriers=["복잡한 관료주의", "러시아 무기체계 호환성", "높은 기술이전 요구"],
        cooperation_opportunities=["Make in India 정책", "제3국 공동 수출", "상호 R&D 센터"],
        strategic_importance="상",
        cooperation_feasibility="중"
    )
    
    # UAE 프로필 생성
    uae_profile = CountryDefenseProfile(
        country_name="UAE",
        defense_budget="약 220억 달러 (2024년 기준)",
        military_personnel="정규군 6.3만 명, 예비군 2.4만 명",
        key_military_assets={
            "육군": ["Leclerc 전차", "BMP-3 장갑차"],
            "해군": ["코르벳", "미사일 고속정"],
            "공군": ["F-16E/F Block 60", "Mirage 2000-9"]
        },
        defense_companies=["EDGE Group", "Tawazun Economic Council"],
        tech_capabilities=[
            TechnologyCapability("무인 시스템", "고도", 
                               ["무인항공기", "해양 무인시스템"], 
                               ["드론 기술", "자율 시스템"]),
            TechnologyCapability("사이버 방어", "고도", 
                               ["사이버 보안 솔루션"], 
                               ["군용 보안 네트워크"])
        ],
        complementary_tech=ComplementaryTech(
            korea_strengths=["함정 설계/건조", "미사일 체계", "전투기 부품 제조"],
            partner_strengths=["첨단 레이더 기술", "전자전 및 사이버 방어", "무인기 시스템"],
            joint_potential=["중동 환경 특화 방공 시스템", "연안 방어 시스템", "통합 C4ISR"],
            complementarity_score="상"
        ),
        cooperation_barriers=["미국/유럽 무기체계 호환성", "제3국 승인 필요"],
        cooperation_opportunities=["한-UAE 특별 전략적 파트너십", "EDGE Group 합작 투자"],
        strategic_importance="상",
        cooperation_feasibility="상"
    )
    
    # 브라질 프로필 생성
    brazil_profile = CountryDefenseProfile(
        country_name="브라질",
        defense_budget="약 290억 달러 (2024년 기준, 남미 최대)",
        military_personnel="정규군 36만 명, 예비군 170만 명",
        key_military_assets={
            "육군": ["Leopard 1A5 전차", "VBTP-MR Guarani 장갑차"],
            "해군": ["항공모함 1척", "잠수함 5척"],
            "공군": ["Gripen E/F", "AMX", "Super Tucano"]
        },
        defense_companies=["Embraer", "AVIBRAS", "Iveco-Fiat"],
        tech_capabilities=[
            TechnologyCapability("항공우주", "고도", 
                               ["Super Tucano", "KC-390"], 
                               ["항공기 설계", "복합재료"]),
            TechnologyCapability("해양 플랫폼", "중간", 
                               ["Riachuelo급 잠수함"], 
                               ["잠수함 건조"])
        ],
        complementary_tech=ComplementaryTech(
            korea_strengths=["첨단 전자장비", "함정 추진 및 전투체계", "정밀 유도무기"],
            partner_strengths=["항공기 설계/통합", "복합재료 기술", "정글/열대 환경 장비"],
            joint_potential=["훈련/경공격기", "중형 해상초계기", "무인 감시정찰 시스템"],
            complementarity_score="상"
        ),
        cooperation_barriers=["행정적 복잡성", "브라질 국내 생산 우선 정책"],
        cooperation_opportunities=["한국-브라질 전략적 파트너십", "제3시장 공동 진출"],
        strategic_importance="중",
        cooperation_feasibility="중"
    )
    
    # 지식 베이스에 추가
    kb.add_country_profile(india_profile)
    kb.add_country_profile(uae_profile)
    kb.add_country_profile(brazil_profile)
    
    # 협력 프로젝트 추가
    brahmos_project = CooperationProject(
        project_name="현무-인도 합동 미사일 개발",
        target_countries=["인도"],
        tech_focus=["미사일 추진체", "유도 시스템"],
        investment_required={
            "1단계": 3.0,
            "2단계": 8.0,
            "3단계": 12.0
        },
        expected_roi=332.0,
        timeline={
            "1단계": "2025-26",
            "2단계": "2026-28", 
            "3단계": "2028-30"
        },
        market_potential="동남아, 중동 시장 공동 진출 시 50-80억 달러",
        success_factors=["기술 상보성", "정부 간 협력", "시장 수요"],
        risk_factors=["정치적 변동", "기술 통제", "비용 초과"]
    )
    
    kb.add_cooperation_project(brahmos_project)
    
    return kb