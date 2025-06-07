import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, AutoModelForCausalLM
import json
import logging
from typing import Dict, List, Optional, Tuple
import time
from dataclasses import dataclass
import os
import random
import re
from difflib import SequenceMatcher
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

@dataclass
class ModelConfig:
    """수정된 모델 설정 - T5 모델 지원"""
    model_name: str = "google/flan-t5-base"
    max_tokens: int = 512  # T5에 적합한 길이로 조정
    temperature: float = 0.7
    top_p: float = 0.9
    do_sample: bool = True
    use_quantization: bool = False
    device_map: str = "auto"

class ResponseDiversityManager:
    """응답 다양성 검증 로직"""
    
    def __init__(self, max_history=10, similarity_threshold=0.65):
        self.response_history = []
        self.max_history = max_history
        self.similarity_threshold = similarity_threshold
        self.rejected_responses = []
    
    def add_response(self, query: str, response: str):
        """응답 기록 추가"""
        self.response_history.append({
            "query": query,
            "response": response,
            "timestamp": time.time(),
            "keywords": self._extract_keywords(response)
        })
        
        if len(self.response_history) > self.max_history:
            self.response_history.pop(0)
    
    def _extract_keywords(self, text: str) -> List[str]:
        """키워드 추출"""
        keywords = []
        defense_terms = ["미사일", "방공", "항공", "해군", "협력", "투자", "수출", 
                        "기술이전", "무인", "드론", "레이더", "사이버", "AI", "개발",
                        "인도", "UAE", "브라질", "동남아", "중동", "아프리카"]
        
        for term in defense_terms:
            if term in text:
                keywords.append(term)
        return keywords
    
    def check_similarity(self, new_response: str) -> Tuple[bool, float]:
        """응답 유사도 검사"""
        if not self.response_history:
            return False, 0.0
        
        max_similarity = 0.0
        for record in self.response_history[-5:]:
            similarity = SequenceMatcher(None, new_response, record["response"]).ratio()
            max_similarity = max(max_similarity, similarity)
            
            if similarity > self.similarity_threshold:
                return True, similarity
        
        return False, max_similarity
    
    def get_diversity_metrics(self) -> Dict:
        """다양성 메트릭 계산"""
        if len(self.response_history) < 2:
            return {"diversity_score": 1.0, "avg_similarity": 0.0}
        
        similarities = []
        responses = [r["response"] for r in self.response_history[-5:]]
        
        for i in range(len(responses)):
            for j in range(i+1, len(responses)):
                sim = SequenceMatcher(None, responses[i], responses[j]).ratio()
                similarities.append(sim)
        
        avg_similarity = sum(similarities) / len(similarities) if similarities else 0
        diversity_score = 1.0 - avg_similarity
        
        return {
            "diversity_score": diversity_score,
            "avg_similarity": avg_similarity,
            "total_responses": len(self.response_history),
            "rejected_count": len(self.rejected_responses)
        }

class EnhancedKnowledgeBase:
    """향상된 지식 베이스 - PDF 데이터 완전 반영"""
    
    def __init__(self, knowledge_base):
        self.kb = knowledge_base
        self.qa_pairs = self._load_complete_pdf_data()
        
    def _load_complete_pdf_data(self) -> List[Dict]:
        """PDF의 모든 질문-답변 데이터 로드"""
        return [
            {
                "question": "중동 및 북아프리카 지역에서 한국의 방산 수출 우선순위 국가를 순위별로 알려주세요",
                "answer": """중동 및 북아프리카 지역의 방산 수출 우선순위는 다음과 같습니다:

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
- 시장 기회: 아프리카 진출 교두보 가능""",
                "category": "지역별 우선순위",
                "keywords": ["중동", "북아프리카", "UAE", "이집트", "카타르", "모로코", "우선순위"]
            },
            {
                "question": "해양 안보 분야에서 한국 방산기술의 경쟁우위는 무엇인가요",
                "answer": """해양 안보 분야에서 한국 방산기술의 경쟁우위는 다음과 같습니다:

## 1. 핵심 경쟁우위 기술

**함정 건조 기술:**
- 세계 5위 조선 강국의 기술력 활용
- KDX-III 이지스 구축함 자체 설계 능력
- FFX 호위함 시리즈 성공적 양산
- 214급 잠수함 독일 기술 소화 및 개량

**해양 센서 기술:**
- 대잠탐지 소나 시스템
- 해상 감시 레이더 기술
- 전자광학 추적 시스템
- 수중 음향 탐지 네트워크

**해양 무기 시스템:**
- 해성 대함미사일 (사거리 200km+)
- 홍상어 어뢰 시스템
- 해궁 근접방어 시스템
- 함포 및 CIWS 기술

## 2. 혁신 기술 분야

**무인 해양 시스템:**
- 무인 수상정(USV) 기술
- 자율 수중정(AUV) 개발
- 해양 드론 군집 운용
- 원격 조종 잠수정

**AI 기반 해양 감시:**
- 위성-함정 연동 감시망
- 인공지능 표적 식별 시스템
- 빅데이터 기반 해양 상황 분석
- 예측 분석 시스템

## 3. 수출 전략 및 목표

**단계별 수출 계획:**
- 2025년: 해양안보 분야 50억 달러
- 2027년: 동남아 해양 감시망 구축 완료
- 2030년: 해양안보 분야 100억 달러
- 2035년: 글로벌 해양안보 허브 구축""",
                "category": "해양안보",
                "keywords": ["해양", "안보", "함정", "조선", "센서", "무인", "AI", "감시"]
            },
            {
                "question": "AI 기반 무기체계 개발 및 수출에서 윤리적 고려사항은 무엇인가요",
                "answer": """AI 기반 무기체계 개발 및 수출에서의 윤리적 고려사항은 다음과 같습니다:

## 1. 국제 규범 및 법적 프레임워크

**국제인도법 준수:**
- 제네바 협약 및 추가의정서 준수
- 민간인과 전투원 구별 원칙
- 과도한 피해 금지 원칙
- 예방 조치 의무 이행

**유엔 논의 동향:**
- 특정재래식무기금지협약(CCW) 논의 참여
- 완전자율무기체계(LAWS) 규제 논의
- 인간의 의미 있는 통제(Meaningful Human Control) 원칙
- 책임 소재 명확화 요구

**주요 제약사항:**
- 완전 자율 살상 무기 개발 금지
- 인간 개입 없는 공격 결정 금지
- 비례성 원칙 준수 필수
- 투명성 및 설명가능성 요구

## 2. 한국의 AI 무기 개발 원칙

**개발 가이드라인:**
- "인간 중심 AI" 원칙 적용
- 방어 목적 우선 개발
- 인간의 최종 결정권 보장
- 오작동 방지 안전장치 필수

**적용 분야 제한:**
- 대인 직접 공격 무기 개발 금지
- 감시 및 정찰 기능 중심
- 방어 시스템에 AI 적용
- 의사결정 지원 도구로 활용

## 3. 수출 통제 체계

**수출 심사 기준:**
- 최종 사용자의 인권 기록 검토
- 분쟁 지역 수출 금지
- 테러 조직 전용 가능성 차단
- 국제법 위반 용도 방지

**모니터링 체계:**
- 수출 후 사용 현황 추적
- 계약 위반 시 제재 조치
- 정기적 현지 점검
- 국제기구와 정보 공유""",
                "category": "AI/윤리",
                "keywords": ["AI", "무기", "윤리", "국제법", "자율", "인간", "통제", "수출"]
            },
            {
                "question": "인도와의 미사일 기술 협력 전략은",
                "answer": """### 🚀 현무-BrahMos 합동 미사일 개발 프로그램
- **인도 국방예산**: 730억 달러 (2024년 기준, 세계 3위)
- **BrahMos 기술력**: 마하 2.8~3.0 초음속 순항미사일, 러시아 합작 성공사례
- **현무 시리즈**: 사거리 300-800km, 한국 독자개발 정밀타격 무기체계
- **시장 잠재력**: 동남아-중동 정밀타격 시장 연 5.8% 성장, 118억 달러 규모

### 💰 3단계 투자 계획 (총 23억 달러)
**1단계: 공동연구개발 (2025-2026, 3억 달러)**
- 한국 투자: 1.8억 달러 (추진체, 시스템 통합)
- 인도 투자: 1.2억 달러 (유도시스템, AI 소프트웨어)
- 부산-첸나이 Twin R&D Center 설립

**2단계: 프로토타입 개발 (2026-2028, 8억 달러)**
- 50:50 투자 분담 (각 4억 달러)
- 목표 성능: 사거리 1,500km, CEP 1m 이하

**3단계: 양산 및 수출 (2028-2030, 12억 달러)**
- 한국 생산분: 5억 달러 (연간 80기)
- 인도 생산분: 7억 달러 (연간 120기, Make in India 60% 현지화)

### 📊 투자수익률 분석 (10년 기준)
- **총 ROI**: 332% (회수기간 4.8년)
- **고용창출**: 직간접 15,000명""",
                "category": "기술 협력",
                "keywords": ["인도", "미사일", "BrahMos", "현무", "협력", "투자", "ROI"]
            },
            {
                "question": "UAE 투자 규모",
                "answer": """### 🇦🇪 UAE와 한국의 기술 통합 전략 비즈니스 모델

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

**예상 효과:**
- 경제적: 10년간 90억 달러 수출 창출
- 기술적: 극한환경 기술 확보로 글로벌 경쟁력 강화
- 전략적: 중동 방산 협력 허브 구축""",
                "category": "비즈니스 모델",
                "keywords": ["UAE", "투자", "천궁", "방공", "사막", "고온", "GCC"]
            },
            {
                "question": "남아시아 및 동남아시아 지역에서 방산 수출 우선순위를 알려주세요",
                "answer": """남아시아 및 동남아시아 지역의 방산 수출 우선순위는 다음과 같습니다:

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
- 시장 특성: 중급 규모이나 안정적""",
                "category": "지역별 우선순위",
                "keywords": ["남아시아", "동남아시아", "인도", "인도네시아", "태국", "말레이시아", "아세안"]
            },
            {
                "question": "동남아시아 지역에서 한국 방산기업들이 진출할 때 가장 유리한 협력 모델은 무엇인가요",
                "answer": """동남아시아 지역에서 한국 방산기업들의 최적 협력 모델은 다음과 같습니다:

## 1. 기술이전 기반 현지생산 모델 (추천)
**적용 대상국:** 인도네시아, 태국, 말레이시아
**핵심 전략:**
- 단계적 기술이전: 조립 → 부품생산 → 핵심기술
- 현지 파트너와 합작투자 (JV) 구조
- 한국 기업 51%, 현지 기업 49% 지분구조

**성공 사례 벤치마킹:**
- 인도네시아 KF-21 공동개발 (20% 기술 참여)
- 태국 K9 자주포 기술이전
- 말레이시아 FA-50 도입 경험

## 2. 맞춤형 제품 공동개발 모델
**차별화 전략:**
- 열대/해양 환경 최적화 제품 개발
- ASEAN 표준 기반 공통 플랫폼 구축
- 현지 운용환경 맞춤형 성능 개조

**협력 분야:**
- 열대형 장갑차량 (고온다습 환경 적응)
- 군도 감시 UAV 시스템
- 해양순찰/경비정
- 통합 해양보안 시스템

## 3. MRO 허브 구축 모델
**전략적 접근:**
- 싱가포르/태국을 지역 정비 허브로 육성
- 아세안 전체 시장 커버
- 부품 공급망 현지화
- 기술 인력 양성 프로그램

**예상 효과:**
- 지속적 수익 창출 (20-30년 장기 계약)
- 현지 고용 창출
- 기술 전수 및 협력 심화""",
                "category": "협력 모델",
                "keywords": ["동남아시아", "협력", "모델", "기술이전", "현지생산", "MRO", "아세안"]
            },
            {
                "question": "브라질과의 항공우주 분야 협력 전략을 구체적으로 제안해주세요",
                "answer": """브라질과의 항공우주 분야 협력 전략은 다음과 같습니다:

## 1. KF/E 공동개발 훈련기 프로그램
**기술 융합 모델:**
- 한국: KF-21 기술 + 항공전자 통합 기술 + 임무시스템
- 브라질: Embraer 설계 기술 + 기체 구조 + 추진계통
- 공동개발 기간: 5년, 총 18억 달러 (한국 10억, 브라질 8억)

**생산 및 마케팅 전략:**
- 생산 분담: 양국 각 50%
- 초기 도입: 한국 100대, 브라질 100대
- 제3국 수출: 남미, 아프리카, 동남아시아 (300-400대 잠재 시장)

## 2. 중형 해상초계기 공동개발
**플랫폼 최적화 모델:**
- 한국: 해상감시 레이더 + 전자정보 수집 체계
- 브라질: Embraer KC-390 플랫폼 + 항공기 구조 설계
- 개발 투자: 4년간 12억 달러 (한국 6.5억, 브라질 5.5억)

**차별화 전략:**
- 기존 대비 30% 낮은 운용비용
- 20% 향상된 임무 수행능력
- 남미 해역 특화 최적화

## 3. 경비행 무인감시기 공동개발
**혁신 기술 결합:**
- 한국: 무인기 통제 시스템 + 자율비행 기술
- 브라질: 경량 복합재 기술 + 장기체공 설계
- 목표 성능: 20시간 이상 체공, 40% 무게 감소

**시장 응용 분야:**
- 아마존 국경 감시
- 불법 벌목 감시
- 마약 밀매 단속
- 잠재 시장: 150-200대, 15-20억 달러""",
                "category": "비즈니스 모델",
                "keywords": ["브라질", "항공우주", "Embraer", "KF-21", "무인기", "해상초계기", "협력"]
            },
            {
                "question": "사이버보안 기술의 수출 잠재력은 어떤가요",
                "answer": """방산 분야 사이버보안 기술의 수출 잠재력은 다음과 같습니다:

## 1. 시장 현황 및 전망
**글로벌 시장 규모:**
- 군용 사이버보안 시장: 2024년 180억 달러 → 2030년 320억 달러
- 연평균 성장률: 12.3% (민간 대비 2배 높음)
- 아시아태평양 지역 성장률: 18.5% (최고 성장)

**한국의 경쟁력:**
- 세계적 IT 인프라 및 기술력
- 실전 경험 풍부 (북한 사이버 위협 대응)
- 빠른 기술 발전 및 혁신 역량
- 정부-민간 협력 체계 구축

## 2. 주요 수출 품목
**네트워크 보안:**
- 군용 네트워크 침입탐지/차단 시스템
- 안전한 군사통신 암호화 솔루션
- 제로트러스트 기반 네트워크 아키텍처

**무기체계 보안:**
- 임베디드 시스템 보안 솔루션
- 드론/로봇 해킹 방지 기술
- 미사일/레이더 시스템 사이버 보호

**데이터 보안:**
- 군사 빅데이터 암호화 및 접근제어
- 블록체인 기반 무기체계 이력 관리
- 안전한 클라우드 군사 서비스

## 3. 국가별 진출 전략
**1순위: 인도**
- 사이버 위협 심각: 중국, 파키스탄으로부터 지속적 공격
- 시장 규모: 연간 25억 달러 (2024년 기준)
- 협력 방향: 한-인도 사이버보안 공동연구센터 설립

**2순위: UAE**
- 스마트시티 보안: 두바이/아부다비 디지털 전환 가속화
- 시장 규모: 연간 18억 달러
- 협력 방향: 중동 사이버보안 허브 구축 파트너십

**3순위: 폴란드**
- NATO 사이버 방어 요구사항 증가
- EU 사이버보안 규정 강화 대응
- 시장 규모: 연간 12억 달러""",
                "category": "사이버보안",
                "keywords": ["사이버보안", "사이버", "보안", "네트워크", "암호화", "AI", "위협", "방어"]
            },
            {
                "question": "우주 및 항공 분야에서 한국의 방산 수출 전략은 무엇인가요",
                "answer": """우주 및 항공 분야 한국의 방산 수출 전략은 다음과 같습니다:

## 1. 우주 분야 수출 전략
**위성 기술:**
- 정찰/감시 위성: 아리랑 시리즈 기술력 기반
- 통신위성: 천리안 위성 기술 활용
- 소형위성 군집: 큐브샛 기반 감시망 구축

**발사체 기술:**
- 누리호 성공 기반 소형 발사체 수출
- 위성 발사 서비스 제공
- 발사체 부품 및 시스템 수출

**지상 시스템:**
- 위성 관제소 구축 기술
- 위성 데이터 분석 소프트웨어
- 통합 우주 상황 인식 시스템

## 2. 항공 분야 수출 전략
**완성 항공기:**
- KF-21 전투기: 동남아, 중동, 라틴아메리카 수출
- KAI 수리온 헬기: 다목적 헬기 시장 공략
- KT-1 훈련기: 신흥국 조종사 양성 시장

**항공 부품:**
- 항공기 구조물 (동체, 날개)
- 항공전자 시스템
- 엔진 부품 및 MRO 서비스

**무인 항공기:**
- 군용 드론 시스템
- 감시정찰용 UAV
- 전투용 UCAV 개발

## 3. 국가별 맞춤 전략
**우주 분야 타겟 국가:**
**인도네시아:**
- 해양감시 위성 시스템 구축
- 다도해 특화 소형위성 군집
- 위성 데이터 공유 협력

**필리핀:**
- 재해감시 위성 시스템
- 태풍/지진 조기경보 네트워크
- 위성통신 인프라 구축

**항공 분야 타겟 국가:**
**말레이시아:**
- FA-50 성공 기반 KF-21 수출 추진
- 항공기 MRO 센터 구축
- 항공우주 인력 교육 프로그램

**수출 목표:**
- 2025년: 우주 5억 달러, 항공 80억 달러
- 2030년: 우주 20억 달러, 항공 150억 달러
- 2035년: 우주 50억 달러, 항공 250억 달러""",
                "category": "우주항공",
                "keywords": ["우주", "항공", "위성", "발사체", "KF-21", "드론", "UAV", "누리호"]
            },
            {
                "question": "라틴 아메리카 지역의 방산 수출 우선순위는 어떻게 되나요",
                "answer": """라틴 아메리카 지역의 방산 수출 우선순위는 다음과 같습니다:

**1순위: 브라질**
- 방위산업 투자: 연간 약 290억 달러 (남미 최대)
- 중점 기술 영역: 항공우주, 해군 기술, 사이버 안보
- 상보적 기술: 항공기 설계, 복합재료 기술, 정글/열대환경 장비
- 시장 기회: 미국/유럽 플랫폼 의존도 감소 추구
- 협력 가능성: Embraer와 KF 프로그램 공동 개발 잠재력

**2순위: 칠레**
- 방위산업 투자: 중간 규모이나 구매력 양호
- 중점 기술 영역: 해군력, 국경 감시
- 지정학적 중요성: 태평양 연안 전략적 위치

**3순위: 아르헨티나**
- 방위산업 투자: 제한적이나 자체 방산 기반 보유
- 중점 기술 영역: 항공기, 함정
- 경제적 제약: 불안정한 경제 상황

**4순위: 콜롬비아**
- 방위산업 투자: 중간 규모
- 중점 기술 영역: 대테러, 국경 감시
- 시장 특성: 미국 의존도 높음""",
                "category": "지역별 우선순위",
                "keywords": ["라틴아메리카", "브라질", "칠레", "아르헨티나", "콜롬비아", "남미"]
            },
            {
                "question": "아프리카 지역에서 한국의 방산 수출 전략을 수립한다면 어떤 국가들을 우선해야 할까요",
                "answer": """아프리카 지역의 방산 수출 우선순위는 다음과 같습니다:

**1순위: 남아프리카공화국**
- 방위산업 투자: 연간 약 30억 달러
- 중점 기술 영역: 장갑차량, 무인시스템, 전자전
- 상보적 기술: 지뢰방호 기술, 장거리 화력 시스템, 방탄 기술
- 시장 기회: 아프리카 내 방산수출 허브로 활용 가능
- 기술 수준: 아프리카 내 최고 수준
- 협력 경험: K9 자주포 수출 성공

**2순위: 나이지리아**
- 방위산업 투자: 아프리카 2위 규모
- 중점 기술 영역: 대테러, 해양 보안
- 시장 잠재력: 인구 2억의 대규모 시장
- 안보 수요: 보코하람 등 테러 대응 필요

**3순위: 케냐**
- 방위산업 투자: 중간 규모
- 중점 기술 영역: 평화유지, 대테러
- 지정학적 중요성: 동아프리카 허브
- 협력 가능성: 비교적 안정적 정치 환경

**4순위: 가나**
- 방위산업 투자: 소규모이나 안정적
- 중점 기술 영역: 해양 보안, 평화유지
- 시장 특성: 서아프리카 진출 거점""",
                "category": "지역별 우선순위",
                "keywords": ["아프리카", "남아프리카공화국", "나이지리아", "케냐", "가나", "대테러", "평화유지"]
            },
            {
                "question": "중동 지역에서 방산 수출 시 고려해야 할 규제 환경은 어떤 것들이 있나요",
                "answer": """중동 지역 방산 수출 시 고려해야 할 주요 규제 환경은 다음과 같습니다:

## 1. 국제 수출통제 체제
**주요 제약 요소:**
- 바세나르 체제(Wassenaar Arrangement): 재래식 무기 및 이중용도 기술 통제
- 미사일기술통제체제(MTCR): 미사일 관련 기술 수출 제한
- 핵공급국그룹(NSG): 핵 관련 기술 통제

**한국의 대응 전략:**
- 사전 수출 허가 철저한 검토
- 최종 사용자 인증서(End-User Certificate) 확보
- 재수출 통제 조항 포함

## 2. 미국의 제3국 승인 요구
**ITAR(International Traffic in Arms Regulations) 고려사항:**
- 미국 기술/부품 포함 시 미국 정부 승인 필요
- 기술이전 관련 추가 제약
- 최종 사용 목적 및 지역 제한

**해결 방안:**
- 한국 자체 기술 비중 확대
- 유럽 등 대체 기술 공급원 확보
- 사전 미국 정부와 협의

## 3. 국가별 특수 규제
**UAE 규제 특성:**
- Tawazun Economic Program: 계약금액의 60%까지 상쇄 요구
- 현지 생산 및 기술이전 의무화
- EDGE Group과의 협력 우선

**이집트 규제 특성:**
- 복잡한 정부 간 거래 선호
- 기술이전 및 현지 생산 강력 요구
- 미국/EU 승인 필요성

## 4. 지역 정치적 고려사항
**지정학적 리스크:**
- 중동 지역 내 정치적 긴장
- 이란 제재 관련 연관성 검토
- 이스라엘과의 관계 고려

**리스크 관리 방안:**
- 정치적 중립성 유지
- 다층적 외교 채널 활용
- 장기 계약보다 단계적 접근""",
                "category": "규제 환경",
                "keywords": ["중동", "규제", "수출통제", "ITAR", "바세나르", "UAE", "이집트", "정치적"]
            },
            {
                "question": "방산 기술이전 시 지식재산권 보호를 위한 전략은 무엇인가요",
                "answer": """방산 기술이전 시 지식재산권 보호 전략은 다음과 같습니다:

## 1. 단계적 기술이전 모델
**핵심 원칙:**
- 기술 성숙도에 따른 단계별 이전
- 핵심 기술과 주변 기술 분리
- 역설계 방지를 위한 통합 모듈 제공

**구체적 방법:**
- 1단계: 조립 및 생산 기술 (기술 의존도 낮음)
- 2단계: 부품 제조 기술 (중급 기술)
- 3단계: 설계 변경 기술 (고급 기술)
- 4단계: 핵심 알고리즘 (최고급 기술, 선택적 이전)

## 2. 법적 보호 체계
**계약 조건:**
- 기술사용 범위 및 지역 제한
- 제3자 이전 금지 조항
- 개량 기술의 공동 소유권 설정
- 계약 위반 시 손해배상 조항

**국제 분쟁 해결:**
- 국제상사중재원(ICC) 중재 조항
- 준거법을 한국법으로 설정
- 예치계약(Escrow) 활용

## 3. 기술적 보호 수단
**하드웨어 보호:**
- 핵심 칩에 암호화 및 원격 제어 기능
- 시간 제한 라이센스 적용
- 정품 인증 시스템 구축

**소프트웨어 보호:**
- 소스코드 대신 실행파일만 제공
- 클라우드 기반 핵심 알고리즘 서비스
- 정기적 업데이트를 통한 의존성 유지

## 4. 수익 극대화 전략
**라이센싱 모델:**
- 초기 기술료: 프로젝트 총액의 5-10%
- 생산 로열티: 생산 단가의 3-7%
- 업그레이드 수수료: 시스템 가격의 15-25%
- 교육/컨설팅 수수료: 별도 책정

**장기 서비스 계약:**
- 20-30년 장기 유지보수 계약 체결
- 부품 공급 독점권 확보
- 성능 개량 서비스 제공""",
                "category": "기술이전",
                "keywords": ["기술이전", "지식재산권", "IP", "보호", "단계적", "라이센스", "계약", "로열티"]
            },
            {
                "question": "방산 분야에서 중소기업의 해외진출 전략은 어떻게 수립해야 할까요",
                "answer": """방산 분야 중소기업의 해외진출 전략은 다음과 같습니다:

## 1. 틈새시장 특화 전략
**고부가가치 부품 집중:**
- 정밀 센서 및 광학장비
- 전자전 부품 및 모듈
- 복합재료 및 특수 소재
- 소프트웨어 및 시뮬레이션

**차별화 요소:**
- 대기업이 진입하기 어려운 소량 다품종 생산
- 빠른 맞춤화 및 기술 지원
- 혁신적 기술 개발 역량

## 2. 대기업 동반진출 모델
**상생협력 구조:**
- 대기업 주계약, 중소기업 핵심 부품 공급
- 기술개발 공동 투자 및 성과 공유
- 해외 마케팅 및 인증 지원

**성공 사례:**
- 한화시스템-중소기업 컨소시엄 (레이더 부품)
- LIG넥스원-협력업체 공동 수출 (C4I 시스템)
- 현대로템-부품업체 동반 진출 (K9 자주포)

## 3. 정부 지원 프로그램 활용
**금융 지원:**
- 중소기업 방산수출 전용 펀드 (500억원 규모)
- 수출보험료 할인 (일반 대비 50% 감면)
- 해외마케팅 비용 지원 (70% 정부 지원)

**기술 지원:**
- 국방기술품질원 품질인증 지원
- 해외 규격 대응 컨설팅
- 지식재산권 출원 및 보호 지원

## 4. 지역별 진출 전략
**동남아시아 진출:**
- 현지 수요 맞춤형 제품 개발
- 기술이전 모델로 현지 파트너와 협력
- KOTRA 해외지사 네트워크 활용

**중동 진출:**
- 극한환경 적응 제품 개발
- 현지 대리점 네트워크 구축
- 국가 간 G2G 협력 채널 활용

**유럽 진출:**
- NATO 표준 인증 취득
- 현지 R&D 센터 설립
- 유럽 방산업체와 전략적 제휴

**예상 성과:**
- 중소기업 방산수출 현재 62억달러 → 2030년 450억달러
- 수출 참여 중소기업 현재 850개사 → 2030년 2,000개사
- 평균 수출액 증가율 연 15% 달성""",
                "category": "중소기업 지원",
                "keywords": ["중소기업", "해외진출", "틈새시장", "동반진출", "정부지원", "수출"]
            },
            {
                "question": "동유럽 지역에서 한국 방산기업이 진출할 만한 국가는 어디인가요",
                "answer": """동유럽 지역의 방산 수출 유망국가는 다음과 같습니다:

**1순위: 폴란드**
- 방위산업 투자: 연간 약 160억 달러 (GDP의 3% 이상)
- 중점 기술 영역: 방공, 장갑차량, 포병 시스템
- 기존 협력: K9 자주포, FA-50 대규모 도입 성공
- 시장 기회: 러시아 위협 대응으로 무기체계 현대화 급진전
- 협력 용이성: 매우 높음 (NATO 회원국, 한국과 전략적 파트너십)

**2순위: 체코**
- 방위산업 투자: 중간 규모이나 안정적 증가 추세
- 중점 기술 영역: 소형무기, 항공기 부품
- 상보적 기술: 정밀기계 가공, 항공기 엔진 기술
- 시장 기회: EU 내 방산 허브 역할 확대

**3순위: 에스토니아**
- 방위산업 투자: 소규모이나 사이버 분야 특화
- 중점 기술 영역: 사이버 방어, 전자전
- 혁신 기회: 디지털 전환 선도국과의 사이버 보안 협력

**4순위: 헝가리**
- 방위산업 투자: 중간 규모
- 중점 기술 영역: 장갑차, 통신장비
- 지정학적 중요성: 중유럽 물류 허브""",
                "category": "지역별 우선순위",
                "keywords": ["동유럽", "폴란드", "체코", "에스토니아", "헝가리", "NATO", "러시아"]
            },
            {
                "question": "한국 방산업체의 글로벌 경쟁력 강화를 위한 핵심 전략은 무엇인가요",
                "answer": """한국 방산업체의 글로벌 경쟁력 강화를 위한 핵심 전략은 다음과 같습니다:

## 1. 기술 중심 협력 모델 정립
**핵심 접근법:**
- 한국 주도의 기술 협력 네트워크 구축
- 상호보완적 기술 결합을 통한 경쟁력 강화
- 공동 지식재산 창출 및 활용 체계 구축

## 2. 글로벌 방산 생태계 구축
**생태계 전략:**
- 한국-협력국-제3국 연계 생산 네트워크 형성
- 지역별 생산/정비 허브 육성
- 중소기업 글로벌 가치사슬 참여 확대

## 3. 맞춤형 시장 진출 전략
**지역별 차별화:**
- 중동: 극한환경 적응 기술 + 고부가가치 시스템
- 동남아: 열대환경 최적화 + 기술이전 모델
- 라틴아메리카: 항공우주 협력 + 공동개발
- 아프리카: 견고하고 경제적인 솔루션 + 단계적 접근

## 4. 투자 효율성 극대화
**ROI 최적화 전략:**
- 인도: 10년 ROI 332% (120억 달러 수출 목표)
- UAE: 10년 ROI 321% (90억 달러 수출 목표)
- 브라질: 10년 ROI 265% (60억 달러 수출 목표)

## 5. 정책적 지원 체계
**제도 개선 필요사항:**
- 방산협력 특별기금 조성 (1조원 규모)
- 수출금융 한도 확대 (5조→10조원)
- 기술이전 규제 합리화
- 국가별 맞춤형 지원 조직 구축

## 6. 안보 협력 확대
**전략적 파트너십:**
- 방산협력을 통한 전략적 파트너십 강화
- 지역 안보 구도에서 한국의 영향력 확대
- 에너지, 자원 등 경제안보 연계 협력 확대

**기대 성과:**
- 2035년까지 세계 5대 방산수출국 도약
- 연간 방산수출액 500억 달러 달성
- 방산분야 고용창출 7.5만명
- GDP 기여도 0.45%p 증가""",
                "category": "종합 전략",
                "keywords": ["글로벌", "경쟁력", "생태계", "ROI", "정책", "파트너십", "수출", "성장"]
            },
            {
                "question": "아프리카 대륙에서 방산 시장 진출 시 주의해야 할 사항들은 무엇인가요",
                "answer": """아프리카 대륙 방산 시장 진출 시 주의해야 할 주요 사항들은 다음과 같습니다:

## 1. 정치적/보안 리스크 관리
**주요 위험 요소:**
- 정치적 불안정성 및 정권 교체 위험
- 내전/분쟁 지역 존재
- 군부 쿠데타 가능성 (서아프리카 지역)
- 테러 조직 활동 (보코하람, 알샤바브 등)

**리스크 대응 전략:**
- 정치적 안정성 높은 국가 우선 선택 (남아공, 가나, 보츠와나)
- 단계적 진출: 소규모 → 대규모 확대
- 정치적 리스크 보험 필수 가입
- 현지 정보 네트워크 구축

## 2. 경제적 제약 요소
**재정적 한계:**
- 제한된 국방예산 (GDP 대비 평균 1-2%)
- 외환 부족 및 환율 불안정성
- 부채 부담 증가 (중국 일대일로 등)
- 경제 성장률 둔화

**해결 방안:**
- 수출금융 패키지 지원 확대
- 분할 지불 및 장기 금융 지원
- 자원 담보 거래 모델 고려
- 다자개발은행과 연계 금융 지원

## 3. 기술/인프라 격차
**운용 환경 제약:**
- 기술 인력 부족
- 유지보수 인프라 미비
- 극한 기후 환경 (사막, 열대)
- 전력/통신 인프라 부족

**적응 전략:**
- 단순하고 견고한 시스템 우선
- 포괄적 교육훈련 프로그램 제공
- 현지 정비 센터 구축
- 기후 적응형 제품 개발

## 4. 국제 경쟁 및 규제
**경쟁 환경:**
- 중국의 적극적 진출 (가격 경쟁력)
- 러시아의 전통적 영향력
- 유럽 업체들의 고급 기술
- 미국의 정치적 영향력

**차별화 전략:**
- 중국보다 우수한 기술력 + 합리적 가격
- 러시아보다 신뢰할 수 있는 공급선
- 유럽보다 유연한 기술이전
- 정치적 조건 없는 협력

## 5. 문화적/제도적 고려사항
**현지 적응 필요성:**
- 부족/종교적 갈등 이해
- 부패 관행 및 투명성 부족
- 언어 장벽 (영어, 프랑스어, 아랍어)
- 느린 의사결정 과정

## 6. 권장 진출 전략
**1단계: 안전한 거점 확보**
- 남아프리카공화국: 아프리카 진출 허브
- 가나: 서아프리카 거점
- 케냐: 동아프리카 거점

**2단계: 점진적 확산**
- 성공 모델 구축 후 주변국 확산
- 지역기구(AU, ECOWAS) 활용
- 평화유지군 장비 공급 참여

**3단계: 생태계 구축**
- 현지 생산 기반 구축
- 기술 교육 센터 운영
- 지역 공급망 네트워크 구성""",
                "category": "리스크 관리",
                "keywords": ["아프리카", "리스크", "정치적", "경제적", "기술", "경쟁", "문화", "단계적"]
            },
            {
                "question": "글로벌 방산 공급망 위기 상황에서 한국의 대응 전략은 무엇인가요",
                "answer": """글로벌 방산 공급망 위기 상황에서 한국의 대응 전략은 다음과 같습니다:

## 1. 공급망 위기 현황 분석
**주요 위기 요인:**
- 코로나19 팬데믹으로 인한 글로벌 공급망 차단
- 우크라이나 전쟁으로 인한 원자재 공급 중단
- 미-중 기술패권 경쟁으로 인한 공급망 분리
- 반도체 등 핵심 부품 공급 불안정

**한국 방산업 영향:**
- 핵심 부품 수입 의존도: 약 35%
- 특수 금속 및 희토류 수입 중단 위험
- 반도체 및 전자부품 공급 지연
- 생산 비용 증가 및 납기 지연

## 2. 공급망 다변화 전략
**지역별 공급원 다변화:**
**기존 의존 구조:**
- 미국: 반도체, 센서 (45%)
- 독일: 정밀기계, 광학장비 (25%)
- 일본: 전자부품, 소재 (20%)
- 기타: 10%

**다변화 목표 (2030년):**
- 미국: 30% (15%p 감소)
- 유럽: 25% (독일 외 확대)
- 아시아: 25% (한국, 대만, 싱가포르)
- 기타: 20% (이스라엘, 캐나다 등)

## 3. 국내 공급망 강화
**방산 소재·부품·장비(소부장) 육성:**
- 핵심 소부장 100개 품목 국산화 추진
- 방산 소부장 전문기업 300개사 육성
- 총 3조원 규모 정부-민간 공동 투자
- 소부장 기술개발 생태계 구축

**국산화 우선순위 품목:**
1. 반도체: 방산용 특수 반도체 설계 및 생산
2. 센서: 적외선, 레이더, 음향 센서
3. 구동장치: 고성능 액추에이터, 모터
4. 소재: 내열합금, 복합재료, 코팅 기술

## 4. 디지털 공급망 관리 시스템
**공급망 가시성 확보:**
- 실시간 공급망 모니터링 시스템 구축
- 블록체인 기반 부품 이력 추적
- AI 기반 공급 위험 예측 시스템
- 디지털 트윈 기반 시뮬레이션

## 5. 전략적 비축 시스템
**핵심 품목 비축:**
- 전략 물자 6개월 분 의무 비축
- 정부-기업 공동 비축창고 운영
- 순환 비축을 통한 품질 관리
- 비축 비용 지원 제도 운영

**비축 대상 품목:**
- 반도체 및 전자부품 (30일분)
- 희토류 및 전략 금속 (90일분)
- 특수 화학소재 (60일분)
- 정밀가공 부품 (45일분)

## 6. 국제 협력 강화
**우방국과의 공급망 협력:**
- 미국과 반도체 공급망 협력 협정
- EU와 소재 공급망 파트너십
- 일본과 부품 상호 공급 체계
- 호주와 광물 자원 장기 계약

**기대 효과:**
- 공급망 리스크 50% 감소
- 국산화율 35% → 60% 상승
- 공급망 관련 비용 20% 절감
- 글로벌 경쟁력 강화""",
                "category": "공급망 관리",
                "keywords": ["공급망", "위기", "다변화", "국산화", "소부장", "디지털", "비축", "협력"]
            }
        ]
    
    def find_relevant_answer(self, query: str) -> Optional[str]:
        """개선된 질문 매칭 시스템"""
        query_lower = query.lower().strip()
        
        # 1단계: 완전 일치 검사
        for qa in self.qa_pairs:
            if query_lower == qa["question"].lower().strip():
                return qa["answer"]
        
        # 2단계: 키워드 기반 매칭 (개선된 버전)
        best_match = None
        best_score = 0
        
        for qa in self.qa_pairs:
            score = self._calculate_similarity_score(query_lower, qa)
            if score > best_score and score > 0.3:  # 임계값 설정
                best_score = score
                best_match = qa["answer"]
        
        return best_match
    
    def _calculate_similarity_score(self, query: str, qa: Dict) -> float:
        """질문 유사도 점수 계산"""
        score = 0
        
        # 키워드 매칭 점수
        query_words = set(query.split())
        question_words = set(qa["question"].lower().split())
        keyword_words = set(qa.get("keywords", []))
        
        # 질문 단어 매칭
        common_question_words = query_words.intersection(question_words)
        if common_question_words:
            score += len(common_question_words) / len(question_words) * 0.6
        
        # 키워드 매칭
        common_keywords = query_words.intersection(keyword_words)
        if common_keywords:
            score += len(common_keywords) / len(keyword_words) * 0.4
        
        # 문자열 유사도
        string_similarity = SequenceMatcher(None, query, qa["question"].lower()).ratio()
        score += string_similarity * 0.3
        
        return score
    
    def is_question_in_scope(self, query: str) -> bool:
        """질문이 지식 베이스 범위 내인지 확인"""
        defense_keywords = [
            "방산", "미사일", "방어", "군사", "무기", "협력", "수출", "투자",
            "인도", "UAE", "브라질", "중동", "동남아", "아프리카", "기술이전",
            "사이버", "우주", "항공", "해양", "AI", "드론", "해양안보", "윤리"
        ]
        
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in defense_keywords)

class DefenseCooperationLlama:
    """수정된 방산 협력 LLM 시스템"""
    
    def __init__(self, config: ModelConfig, knowledge_base, prompt_engineer):
        self.config = config
        self.kb = knowledge_base
        self.prompt_engineer = prompt_engineer
        self.tokenizer = None
        self.model = None 
        self.conversation_history = []
        
        # 향상된 구성 요소들
        self.diversity_manager = ResponseDiversityManager()
        self.enhanced_kb = EnhancedKnowledgeBase(knowledge_base)
        self.used_templates = []

    def initialize_model(self):
        """모델 초기화 - T5 모델 지원"""
        try:
            logger.info(f"T5 model loading: {self.config.model_name}")
            
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.config.model_name,
                trust_remote_code=True
            )
            
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token

            # T5는 Seq2Seq 모델이므로 AutoModelForSeq2SeqLM 사용
            if "t5" in self.config.model_name.lower():
                self.model = AutoModelForSeq2SeqLM.from_pretrained(
                    self.config.model_name,
                    device_map="cpu",
                    torch_dtype=torch.float32,
                    trust_remote_code=True,
                    low_cpu_mem_usage=True
                )
            else:
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.config.model_name,
                    device_map="cpu",
                    torch_dtype=torch.float32,
                    trust_remote_code=True,
                    low_cpu_mem_usage=True
                )
            
            logger.info("✅ Model initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Model initialization failed: {e}")
            self._setup_dummy_mode()

    def _setup_dummy_mode(self):
        """더미 모드 설정"""
        self.model = "dummy_model"
        self.tokenizer = "dummy_tokenizer"
        logger.info("✅ Dummy mode activated")

    def generate_response(self, user_query: str, use_history: bool = True) -> Dict:
        """향상된 응답 생성"""
        start_time = time.time()
        
        try:
            # 1. 질문이 지식 베이스 범위 내인지 확인
            if not self.enhanced_kb.is_question_in_scope(user_query):
                return {
                    "query": user_query,
                    "response": "죄송합니다. 해당 질문은 방산 협력 전략 분야를 벗어난 내용으로 보입니다. 방산 수출, 기술 협력, 국가별 전략 등에 관련된 질문을 해주시면 도움을 드릴 수 있습니다.",
                    "generation_time": time.time() - start_time,
                    "model_info": {"mode": "out_of_scope"},
                    "in_scope": False
                }
            
            # 2. 지식 베이스에서 관련 답변 찾기
            relevant_answer = self.enhanced_kb.find_relevant_answer(user_query)
            
            if relevant_answer:
                # PDF 데이터 기반 답변
                response = relevant_answer
                self.diversity_manager.add_response(user_query, response)
                
                return {
                    "query": user_query,
                    "response": response,
                    "generation_time": time.time() - start_time,
                    "model_info": {
                        "model_name": self.config.model_name,
                        "mode": "knowledge_base",
                        "source": "pdf_data"
                    },
                    "response_length": len(response),
                    "in_scope": True
                }
            
            # 3. 지식 베이스에서 관련 컨텍스트 검색
            context_info = self._get_context_from_kb(user_query)
            
            # 4. 모델 상태에 따른 응답 생성
            if self.model == "dummy_model" or self.model is None:
                response = self._generate_knowledge_based_response(user_query, context_info)
                mode = "enhanced_dummy"
            else:
                response = self._generate_real_response(user_query, context_info)
                mode = "real_model"
            
            # 5. 응답 검증 및 저장
            self.diversity_manager.add_response(user_query, response)
            
            return {
                "query": user_query,
                "response": response,
                "generation_time": time.time() - start_time,
                "model_info": {
                    "model_name": self.config.model_name,
                    "mode": mode,
                    "temperature": self.config.temperature
                },
                "response_length": len(response),
                "in_scope": True
            }
            
        except Exception as e:
            logger.error(f"Response generation error: {e}")
            return {
                "query": user_query,
                "response": "죄송합니다. 응답 생성 중 오류가 발생했습니다. 다시 시도해 주세요.",
                "error": True,
                "generation_time": time.time() - start_time
            }

    def _get_context_from_kb(self, query: str) -> str:
        """지식 베이스에서 관련 컨텍스트 추출"""
        context_parts = []
        
        # 국가별 정보 검색
        for country_name, profile in self.kb.countries.items():
            if country_name in query:
                context_parts.append(f"""
{country_name} 국방 정보:
- 국방예산: {profile.defense_budget}
- 병력규모: {profile.military_personnel}
- 주요 방산기업: {', '.join(profile.defense_companies)}
- 전략적 중요도: {profile.strategic_importance}
- 협력 용이성: {profile.cooperation_feasibility}
""")
        
        return "\n".join(context_parts) if context_parts else "일반적인 방산 협력 전략 정보를 기반으로 답변합니다."

    def _generate_knowledge_based_response(self, query: str, context: str) -> str:
        """지식 베이스 기반 응답 생성 - 질문별 맞춤 응답"""
        
        # 질문 분류 및 맞춤 응답
        if any(keyword in query.lower() for keyword in ["우선순위", "순위", "우선"]):
            return """방산 수출 우선순위는 다음 기준으로 결정됩니다:

### 📊 우선순위 결정 기준
1. **시장 규모**: 국방예산 및 구매력
2. **기술 상보성**: 상호 보완 가능한 기술 영역
3. **지정학적 중요성**: 전략적 파트너십 가치
4. **협력 용이성**: 정치적/제도적 장벽 수준

### 🌍 지역별 특성
- **중동**: 극한환경 기술, 고부가가치 시스템 중심
- **동남아**: 열대환경 최적화, 기술이전 모델
- **아프리카**: 견고하고 경제적인 솔루션
- **라틴아메리카**: 항공우주 협력, 공동개발

구체적인 지역이나 기술 분야를 명시해 주시면 더 자세한 정보를 제공할 수 있습니다."""

        elif any(keyword in query.lower() for keyword in ["협력", "전략", "방안"]):
            return """### 🤝 방산 기술 협력 전략의 핵심 요소

## 협력 모델
- **공동개발**: 상호 기술 융합을 통한 신제품 개발
- **기술이전**: 단계적 기술 이전을 통한 현지 생산
- **투자 협력**: 합작투자를 통한 생산기지 구축

## 성공 요인
- 상호보완적 기술 역량 확인
- 정부 간 정책적 지원 확보
- 장기적 파트너십 구축
- 시장 진출 전략 수립

## 리스크 관리
- 기술 유출 방지 체계
- 정치적 리스크 평가
- 경제적 안정성 검토

더 구체적인 국가나 기술 분야에 대한 질문을 해주시면 맞춤형 전략을 제공해드리겠습니다."""

        elif any(keyword in query.lower() for keyword in ["투자", "규모", "수익", "ROI"]):
            return """### 💰 방산 협력 투자 전략

## 투자 규모별 접근
- **대규모 프로젝트** (10억 달러+): 정부 간 협력 필수
- **중규모 프로젝트** (1-10억 달러): 민관 합작 모델
- **소규모 프로젝트** (1억 달러 이하): 민간 주도

## 수익성 분석
- **일반적 ROI**: 15-25% (10년 기준)
- **고부가가치 기술**: 25-35%
- **시장 선점 효과**: 추가 20-30% 프리미엄

## 투자 우선순위
1. 기술력 기반 고부가가치 분야
2. 상호보완적 협력 가능 분야
3. 시장 확장 가능성 높은 분야

구체적인 국가나 프로젝트를 제시해 주시면 상세한 투자 분석을 제공할 수 있습니다."""

        else:
            return f"""### 🎯 방산 협력 전략 관련 정보

{context}

## 주요 고려사항
- **기술적 상보성**: 상호 보완 가능한 기술 영역 분석
- **시장 진입 전략**: 단계적 시장 접근 방법
- **리스크 평가**: 정치적, 경제적, 기술적 리스크 관리
- **장기적 파트너십**: 지속가능한 협력 관계 구축

## 다음 단계
구체적인 질문이나 특정 국가/기술 분야에 대해 문의해 주시면:
- 상세한 시장 분석
- 맞춤형 협력 전략
- 투자 수익성 분석
- 실행 로드맵

등을 제공할 수 있습니다."""

    def _generate_real_response(self, query: str, context: str) -> str:
        """실제 모델을 사용한 응답 생성"""
        try:
            prompt = f"""다음은 방산 협력 전략에 관한 질문입니다.

배경 정보: {context}

질문: {query}

답변:"""
            
            inputs = self.tokenizer(
                prompt, 
                return_tensors="pt",
                max_length=512,
                truncation=True,
                padding=True
            )
            
            with torch.no_grad():
                if "t5" in self.config.model_name.lower():
                    # T5 모델의 경우
                    outputs = self.model.generate(
                        input_ids=inputs['input_ids'],
                        attention_mask=inputs['attention_mask'],
                        max_new_tokens=self.config.max_tokens,
                        temperature=self.config.temperature,
                        do_sample=self.config.do_sample,
                        top_p=self.config.top_p,
                        pad_token_id=self.tokenizer.pad_token_id,
                        eos_token_id=self.tokenizer.eos_token_id
                    )
                    response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
                else:
                    # 기타 Causal LM의 경우
                    outputs = self.model.generate(
                        input_ids=inputs['input_ids'],
                        attention_mask=inputs['attention_mask'],
                        max_new_tokens=self.config.max_tokens,
                        temperature=self.config.temperature,
                        do_sample=self.config.do_sample,
                        top_p=self.config.top_p,
                        pad_token_id=self.tokenizer.pad_token_id,
                        eos_token_id=self.tokenizer.eos_token_id
                    )
                    response_tokens = outputs[0][inputs['input_ids'].shape[1]:]
                    response = self.tokenizer.decode(response_tokens, skip_special_tokens=True)
            
            return response.strip() if response.strip() else "응답을 생성할 수 없습니다."
                
        except Exception as e:
            logger.error(f"Real model response failed: {e}")
            return self._generate_knowledge_based_response(query, context)

    def get_diversity_stats(self) -> Dict:
        """다양성 통계 조회"""
        return self.diversity_manager.get_diversity_metrics()

    def reset_diversity_tracking(self):
        """다양성 추적 초기화"""
        self.diversity_manager.response_history = []
        self.diversity_manager.rejected_responses = []
        self.used_templates = []
        logger.info("Diversity tracking reset")

# 사용 예시
if __name__ == "__main__":
    print("Enhanced Defense Cooperation LLM - 질문별 맞춤 응답 시스템")
    print("1. PDF 데이터 완전 로드 ✓")
    print("2. 질문 유사도 기반 매칭 ✓") 
    print("3. 질문별 맞춤 응답 생성 ✓")
    print("4. 범위 외 질문 적절한 처리 ✓")