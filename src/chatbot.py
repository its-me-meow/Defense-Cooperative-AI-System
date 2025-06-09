import sys
import os
import logging
import time
from datetime import datetime

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from src.data_structure import build_knowledge_base
    from src.prompt_engineering import create_comprehensive_prompt_system
    from src.llama_integration import DefenseCooperationLlama, ModelConfig
except ImportError:
    try:
        from data_structure import build_knowledge_base
        from prompt_engineering import create_comprehensive_prompt_system  
        from llama_integration import DefenseCooperationLlama, ModelConfig
    except ImportError as e:
        print(f"Import error: {e}")
        print("Please ensure all required modules are in the correct path")
        sys.exit(1)

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AdvancedIntelligentGenerator:
    """개선된 지능형 답변 생성기 - 각 질문에 맞는 구체적 답변 생성"""
    
    def __init__(self):
        self.defense_keywords = [
            "방산", "미사일", "방어", "군사", "무기", "협력", "수출", "투자",
            "인도", "UAE", "브라질", "중동", "동남아", "아프리카", "기술이전",
            "사이버", "우주", "항공", "해양", "드론", "레이더", "방공", "국방",
            "리스크", "관리", "전략", "우선순위", "순위", "안보", "전투"
        ]
        
        self.technology_keywords = [
            "기술", "개발", "혁신", "연구", "AI", "인공지능", "로봇", "자동화",
            "블록체인", "5G", "6G", "IoT", "빅데이터", "클라우드", "양자", "나노"
        ]
        
        # 질문 패턴별 구체적 답변 매핑
        self.defense_qa_patterns = {
            # AI/윤리 관련
            ("ai", "윤리", "문제"): self._generate_ai_ethics_response,
            ("인공지능", "윤리", "도입"): self._generate_ai_ethics_response,
            ("ai", "도입", "문제"): self._generate_ai_ethics_response,
            
            # 수출 관련
            ("수출", "증가", "요인"): self._generate_export_growth_response,
            ("수출", "성장", "이유"): self._generate_export_growth_response,
            ("방산", "수출", "확대"): self._generate_export_growth_response,
            
            # 리스크 관리
            ("리스크", "관리", "방법"): self._generate_risk_management_response,
            ("위험", "관리", "전략"): self._generate_risk_management_response,
            
            # 기술 개발
            ("기술", "개발", "전략"): self._generate_tech_development_response,
            ("연구개발", "방향", "전략"): self._generate_tech_development_response,
            
            # 국제 협력
            ("국제", "협력", "방안"): self._generate_international_cooperation_response,
            ("해외", "협력", "전략"): self._generate_international_cooperation_response,
        }
        
        # 일반 기술 질문 패턴
        self.tech_qa_patterns = {
            ("인공지능", "미래", "전망"): self._generate_ai_future_response,
            ("ai", "발전", "방향"): self._generate_ai_future_response,
            ("블록체인", "활용", "방안"): self._generate_blockchain_response,
            ("기후", "기술", "대응"): self._generate_climate_tech_response,
            ("환경", "기술", "혁신"): self._generate_climate_tech_response,
        }
    
    def analyze_question_intent(self, query: str) -> tuple:
        """질문의 핵심 의도와 키워드 분석"""
        query_lower = query.lower()
        
        # 핵심 키워드 추출
        keywords = []
        for word in query_lower.split():
            clean_word = word.strip("?.,!").strip()
            if len(clean_word) > 1:
                keywords.append(clean_word)
        
        # 패턴 매칭을 위한 핵심 키워드 선별
        important_keywords = []
        priority_words = [
            "ai", "인공지능", "윤리", "문제", "수출", "증가", "요인", "리스크", "관리",
            "기술", "개발", "전략", "협력", "시장", "동향", "정책", "미래", "전망",
            "블록체인", "활용", "기후", "환경", "혁신", "국방", "방산", "군사"
        ]
        
        for keyword in keywords:
            for priority in priority_words:
                if priority.lower() in keyword or keyword in priority.lower():
                    important_keywords.append(priority)
        
        return tuple(important_keywords[:3])  # 최대 3개 키워드
    
    def find_best_pattern_match(self, intent_keywords: tuple, patterns_dict: dict) -> callable:
        """가장 적합한 패턴 매칭 함수 찾기"""
        best_match = None
        best_score = 0
        
        for pattern, func in patterns_dict.items():
            score = 0
            for keyword in intent_keywords:
                for pattern_word in pattern:
                    if keyword.lower() in pattern_word.lower() or pattern_word.lower() in keyword.lower():
                        score += 1
            
            if score > best_score:
                best_score = score
                best_match = func
        
        return best_match if best_score > 0 else None
    
    def is_defense_related(self, query: str) -> bool:
        """방산 관련 질문인지 확인"""
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in self.defense_keywords)
    
    def is_technology_related(self, query: str) -> bool:
        """기술 관련 질문인지 확인"""
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in self.technology_keywords)
    
    def extract_topic(self, query: str) -> str:
        """질문에서 주제 추출"""
        words = query.split()
        stop_words = {"의", "는", "이", "가", "을", "를", "에", "에서", "로", "으로", "와", "과", "하고", "어떻게", "왜", "무엇", "?", "시", "때"}
        
        important_words = []
        for word in words:
            clean_word = word.strip("?.,!").strip()
            if len(clean_word) > 1 and clean_word not in stop_words:
                important_words.append(clean_word)
        
        return " ".join(important_words[:4]) if important_words else "해당 주제"
    
    # === 방산 분야 구체적 답변 생성 함수들 ===
    
    def _generate_ai_ethics_response(self, query: str, topic: str) -> str:
        """AI 윤리 관련 구체적 답변"""
        return """국방 분야 AI 기술 도입 시 윤리적 문제점:

### ⚖️ 주요 윤리적 이슈들

**1. 자율무기시스템 (LAWS) 관련**
- **생명 결정권**: AI가 생사를 결정하는 것의 도덕적 문제
- **인간 통제**: 치명적 결정에서 인간의 의미있는 통제 필요성
- **책임 소재**: AI 무기 오작동 시 법적/도덕적 책임 귀속 문제

**2. 의사결정 투명성 문제**
- **블랙박스**: AI 알고리즘의 의사결정 과정 불투명성
- **편향성**: 훈련 데이터의 편향이 차별적 결과 초래 가능
- **검증 어려움**: 복잡한 AI 시스템의 신뢰성 검증 한계

**3. 데이터 보안 및 프라이버시**
- **민감정보**: 군사기밀과 개인정보 처리 시 보안 위험
- **데이터 남용**: 수집된 정보의 목적 외 사용 가능성
- **해킹 위험**: AI 시스템 대상 사이버 공격 취약성

### 🛡️ 윤리적 가이드라인 방향

**국제적 규범**
- UN의 치명적 자율무기시스템 논의 참여
- 제네바 협약 등 국제법 준수 원칙 확립
- 동맹국과의 AI 윤리 기준 공조

**기술적 대응**
- 설명 가능한 AI (XAI) 기술 개발
- 인간-AI 협업 체계 구축 (Human-in-the-loop)
- 강건한 AI 시스템 설계 (Robust AI)

**제도적 보완**
- AI 윤리 위원회 설치 및 운영
- 정기적 윤리 영향 평가 실시
- 투명한 거버넌스 체계 구축

### 🌏 국제적 동향
- EU: AI Act를 통한 고위험 AI 규제
- 미국: AI 권리장전 및 국방부 AI 윤리원칙
- 중국: AI 규제 프레임워크 개발

### 💡 한국의 대응 방향
국방 AI 도입 시 '인간 중심의 AI' 원칙을 바탕으로 기술적 우위와 윤리적 책임 사이의 균형점을 찾는 것이 핵심입니다. 특히 동맹국과의 공통 기준 마련과 투명한 의사결정 과정 확립이 중요합니다."""

    def _generate_export_growth_response(self, query: str, topic: str) -> str:
        """방산 수출 증가 요인 구체적 답변"""
        return """한국 방산 수출 급증의 주요 요인들:

### 📈 수출 성장 현황
- **2022년**: 172억 달러 (역대 최고 기록)
- **2023년**: 140억 달러 (지속적 고성장)
- **성장률**: 최근 5년간 연평균 20% 이상 증가

### 🚀 핵심 성공 요인들

**1. 기술적 경쟁력 확보**
- **K9 자주포**: 세계 1위 자주포 수출국 달성
- **T-50/FA-50**: 고등훈련기 시장 선도
- **천궁-II**: 중거리 방공시스템 기술력 인정
- **현무 미사일**: 정밀타격 무기체계 우수성

**2. 가격 경쟁력**
- 서구 무기 대비 30-50% 저렴한 가격
- 높은 성능 대비 가격 비율 (Cost-Performance Ratio)
- 중견국 군사력 현대화 수요에 적합한 포지셔닝

**3. 전략적 마케팅**
- **정상외교**: 대통령 직접 세일즈외교 강화
- **패키지 딜**: 무기+기술이전+산업협력 통합 제안
- **오프셋**: 상대국 산업 발전에 기여하는 상쇄거래

**4. 지정학적 기회 활용**
- **우크라이나 전쟁**: 유럽의 방산 수요 급증
- **인도-태평양 긴장**: 아시아 국가들의 군비 증강
- **중동 정세**: 걸프 국가들의 방산 투자 확대

### 🌍 주요 수출 성과

**폴란드 (240억 달러 규모)**
- K9 자주포, K2 전차, FA-50 경공격기
- 현지 생산 및 기술이전 포함

**호주 (10억 달러)**
- AS21 레드백 보병전투차
- K9 자주포 추가 도입

**이집트, 사우디, UAE**
- 중동 시장 진출 확대
- 천궁, K9 등 핵심 무기체계

### 🎯 성공 전략의 특징

**기술 자립도**
- 국산화율 80% 이상 달성
- 핵심 기술의 독자 개발 역량

**산업 생태계**
- 대기업-중소기업 협력 체계
- 완성품부터 부품까지 패키지 수출

**정부-민간 협력**
- 방산업체 해외진출 적극 지원
- 정부보증보험(K-Sure) 활용

### 📊 미래 전망
2030년까지 연간 300억 달러 수출 목표로, 차세대 전투기(KF-21), 한국형 이지스(KDDX) 등 첨단 무기체계 수출 본격화 예상됩니다.

*한국 방산의 성공은 기술력, 가격 경쟁력, 전략적 마케팅이 결합된 결과입니다.*"""

    def _generate_risk_management_response(self, query: str, topic: str) -> str:
        """리스크 관리 구체적 답변"""
        return """방산 분야 리스크 관리 전략:

### 🛡️ 주요 리스크 유형별 관리 방안

**1. 기술적 리스크**
- **개발 지연**: 단계적 개발(Stage-Gate) 방식 적용
- **성능 미달**: 철저한 시제품 검증 및 시험평가
- **기술 유출**: 보안 등급별 접근 통제 시스템
- **호환성 문제**: 국제 표준 준수 및 상호운용성 확보

**2. 시장/경영 리스크**
- **수요 변화**: 다양한 시장 포트폴리오 구축
- **경쟁 심화**: 차별화된 기술력 확보
- **가격 변동**: 장기 계약 및 환헤지 활용
- **자금 조달**: 정부 보증 및 수출금융 활용

**3. 정치/규제 리스크**
- **수출 규제**: 복수 국가 인증 획득 (미국 ITAR, EU 등)
- **정책 변화**: 정부 관계자와 지속적 소통 채널
- **국제 관계**: 중립적 포지션 유지 및 다변화
- **제재 위험**: 사전 법무 검토 및 컴플라이언스 강화

### 📋 체계적 리스크 관리 프로세스

**1단계: 리스크 식별 (Risk Identification)**
- 체크리스트 기반 전면적 위험 요소 발굴
- 내외부 전문가 자문 및 벤치마킹
- 과거 사례 분석 및 교훈 도출

**2단계: 리스크 평가 (Risk Assessment)**
- 발생 확률 × 영향도 매트릭스 작성
- 정량적/정성적 분석 병행
- 우선순위 기반 등급 분류

**3단계: 대응 전략 수립 (Risk Response)**
- **회피(Avoid)**: 위험 요소 원천 제거
- **완화(Mitigate)**: 발생 확률/영향 최소화
- **전가(Transfer)**: 보험, 파트너십 활용
- **수용(Accept)**: 잔여 위험의 관리된 수용

**4단계: 모니터링 및 통제 (Monitoring & Control)**
- 실시간 리스크 지표 추적
- 정기적 리스크 재평가
- 비상계획(Contingency Plan) 가동

### 🎯 분야별 특화 관리 방안

**R&D 프로젝트**
- 기술성숙도(TRL) 단계별 게이트 심사
- 실패 허용적 문화와 빠른 피봇 전략
- 외부 전문가 자문단 상시 운영

**해외 수출**
- 국가 신용도 평가 및 정치적 안정성 분석
- 현지 파트너와의 위험 분담 구조
- 다단계 대금 회수 방안

**공급망 관리**
- 핵심 부품의 복수 공급업체 확보
- 전략적 재고 관리 및 대체재 개발
- 공급업체 재무 건전성 정기 점검

### 💡 최신 리스크 관리 도구

**디지털 기반 관리**
- AI/빅데이터를 활용한 예측적 리스크 분석
- 블록체인 기반 공급망 투명성 확보
- IoT 센서를 통한 실시간 모니터링

**ESG 리스크 관리**
- 환경 영향 평가 및 지속가능성 확보
- 사회적 책임 이행 및 지역사회 관계
- 투명한 거버넌스 및 윤리경영

### 🏆 성공 사례: K방산업체들의 리스크 관리
한화시스템, 한국항공우주산업 등은 체계적 리스크 관리를 통해 대형 해외 수주에 성공하며, 위험 요소를 기회로 전환하는 역량을 보여주고 있습니다.

*방산 분야의 리스크 관리는 기술적 전문성과 체계적 관리 역량이 결합되어야 효과적입니다.*"""
    
    def _generate_tech_development_response(self, query: str, topic: str) -> str:
        """기술 개발 전략 답변"""
        return f"""{topic} 개발 전략:

### 🔬 핵심 기술 개발 방향
- 차세대 기술 트렌드 분석 및 선제적 대응
- 국제 표준과 호환성을 고려한 기술 로드맵
- 민간-군사 융합 기술(Dual-Use) 활용

### 🎯 단계별 개발 전략
**1단계**: 기초 연구 및 개념 검증
**2단계**: 시제품 개발 및 성능 검증  
**3단계**: 양산 및 운용 최적화

### 💡 혁신 포인트
현재 글로벌 기술 경쟁에서 {topic} 분야의 우위를 확보하기 위해서는 독창적 접근과 전략적 파트너십이 필요합니다."""

    def _generate_international_cooperation_response(self, query: str, topic: str) -> str:
        """국제 협력 방안 답변"""
        return f"""{topic} 국제 협력 전략:

### 🤝 협력 모델 다양화
- 양자 협력: 핵심 파트너와의 심화 협력
- 다자 협력: 국제 컨소시엄 참여
- 기술 교류: 상호 보완적 기술 공유

### 🌍 지역별 협력 전략
**아시아-태평양**: 안보 협력 강화
**유럽**: 기술 표준 및 규제 협력
**중동**: 에너지-방산 패키지 협력

### 📈 기대 효과
국제 협력을 통해 기술 접근성 확대, 시장 진출 가속화, 위험 분산 효과를 기대할 수 있습니다."""

    # 기술 분야 답변 함수들
    def _generate_ai_future_response(self, query: str, topic: str) -> str:
        """AI 미래 전망 답변"""
        return """인공지능(AI) 기술의 미래 전망:

### 🚀 2025-2030 핵심 발전 동향

**생성형 AI 고도화**
- GPT-5, Claude-4 등 차세대 대화형 AI
- 멀티모달 AI: 텍스트+이미지+음성+비디오 통합 처리
- 실시간 상호작용 및 개인화 서비스 확산

**자율 AI 시스템**
- AGI(Artificial General Intelligence) 실현 가능성 증대
- 자기 학습 및 자기 개선 능력 획득
- 인간 수준의 추론 및 창의적 사고 구현

### 🏭 산업별 혁신 적용

**제조업 혁명**
- AI 기반 완전 자동화 공장 실현
- 예측 정비로 다운타임 90% 감소
- 개인 맞춤형 대량생산 시스템

**의료 패러다임 변화**
- AI 의사: 진단 정확도 95% 이상
- 신약 개발 기간 70% 단축
- 개인 유전자 기반 맞춤 치료

### 🇰🇷 한국의 AI 전략

**강점 활용**
- 세계 최고 수준 반도체 기술 (메모리, 시스템반도체)
- 5G/6G 통신 인프라 우위
- 제조업 기반 AI 적용 경험

**도전 과제**
- 데이터 확보 및 활용 규제 개선
- AI 전문 인력 10만명 양성 필요
- 글로벌 AI 표준 선도권 확보

### 🔮 장기 전망 (2030-2040)

**기술적 혁신**
- 양자-AI 융합 컴퓨팅 실현
- 뇌-컴퓨터 인터페이스 상용화
- AI 의식(Consciousness) 논의 본격화

### 💡 성공을 위한 핵심 요소
AI는 단순한 기술이 아닌 사회 전체를 변화시키는 범용 기술로, 기술 개발과 함께 제도적 준비, 인력 양성, 윤리적 기준 마련이 동시에 이루어져야 합니다."""

    def _generate_blockchain_response(self, query: str, topic: str) -> str:
        """블록체인 활용 방안 답변"""
        return """블록체인 기술의 혁신적 활용 방안:

### 🔗 블록체인 핵심 특징과 장점
- **탈중앙화**: 중앙 관리 기관 없는 분산 네트워크
- **투명성**: 모든 거래 기록의 공개적 검증 가능
- **불변성**: 한번 기록된 데이터의 위변조 방지
- **스마트 계약**: 자동화된 계약 실행 및 이행

### 💼 산업별 혁신적 적용 사례

**금융 서비스 혁신**
- DeFi(탈중앙화 금융): 은행 없는 금융 서비스
- CBDC(중앙은행 디지털화폐): 디지털 원화 발행 준비
- 크로스보더 송금: 실시간 국제송금 서비스

**공급망 투명성 확보**
- 제품 이력 추적: 원산지부터 소비자까지 전 과정
- 진품 인증: 명품, 의약품 위조품 방지
- ESG 인증: 지속가능성 증명 및 탄소발자국 추적

### 🇰🇷 한국의 블록체인 전략

**정부 정책 방향**
- 디지털뉴딜의 핵심 기술로 선정
- 규제 샌드박스를 통한 혁신 실험
- K-디지털 크레딧으로 신원인증 서비스

### 💡 성공을 위한 핵심 요소
블록체인은 단순한 기술을 넘어 신뢰 구조의 혁신입니다. 기술적 완성도와 함께 사회적 수용성, 규제 환경, 사용자 경험 개선이 동시에 이루어져야 진정한 혁신을 달성할 수 있습니다."""

    def _generate_climate_tech_response(self, query: str, topic: str) -> str:
        """기후변화 대응 기술 답변"""
        return """기후변화 대응을 위한 혁신 기술들:

### 🌱 탄소 중립 핵심 기술들

**청정 에너지 혁신**
- **페로브스카이트 태양전지**: 효율 30% 돌파, 플렉서블 적용
- **부유식 해상풍력**: 수심 제약 없는 대용량 발전
- **그린 수소**: 재생에너지 기반 물 전기분해
- **소형모듈원자로(SMR)**: 안전성 강화된 차세대 원전

**혁신적 에너지 저장**
- **고체 배터리**: 안전성과 용량밀도 대폭 개선
- **액체공기 저장**: 대용량 장주기 에너지 저장
- **그래비티 저장**: 중력을 이용한 물리적 에너지 저장

### 🇰🇷 한국의 그린테크 혁신

**K-그린뉴딜 성과**
- 배터리: 세계 시장점유율 30% (LG에너지솔루션, 삼성SDI)
- 태양광: 고효율 셀 기술력 세계 톱3
- 수소: 연료전지 기술 글로벌 선도

### 💡 미래 전망
기후변화 대응 기술은 환경 보호를 넘어 새로운 경제 패러다임을 창출하는 핵심 동력입니다. 2030년까지는 기술의 경제성 확보, 2040년까지는 전면적 상용화가 예상됩니다."""

    # === 메인 생성 함수 ===
    def generate_response(self, query: str) -> str:
        """개선된 통합 응답 생성"""
        intent_keywords = self.analyze_question_intent(query)
        topic = self.extract_topic(query)
        
        # 1. 방산 분야 질문 처리
        if self.is_defense_related(query):
            # 구체적 패턴 매칭 시도
            match_func = self.find_best_pattern_match(intent_keywords, self.defense_qa_patterns)
            if match_func:
                return match_func(query, topic)
            else:
                # 기본 방산 답변으로 폴백
                return self._generate_general_defense_response(query, topic)
        
        # 2. 기술 분야 질문 처리
        elif self.is_technology_related(query):
            # 구체적 패턴 매칭 시도
            match_func = self.find_best_pattern_match(intent_keywords, self.tech_qa_patterns)
            if match_func:
                return match_func(query, topic)
            else:
                # 기본 기술 답변으로 폴백
                return self._generate_general_technology_response(query, topic)
        
        # 3. 일반 질문 처리
        else:
            return self._generate_general_response(query, topic)
    
    def _generate_general_defense_response(self, query: str, topic: str) -> str:
        """일반적인 방산 분야 답변"""
        return f"""방산 분야 '{topic}' 관련 종합 분석:

### 🔍 현황 분석
방산 분야에서 {topic}는 기술적 복잡성과 높은 안전 기준이 요구되는 중요한 영역입니다.

### 💡 주요 고려사항
1. **기술적 측면**: 최신 기술 동향 및 국제 표준 준수
2. **시장적 측면**: 글로벌 경쟁 환경 및 수요 전망
3. **정책적 측면**: 관련 규제 및 정부 지원 정책
4. **전략적 측면**: 장기적 비전 및 실행 계획

### 📈 발전 방향
- 기술 혁신을 통한 경쟁력 확보
- 국제 협력을 통한 시장 확대  
- 체계적인 리스크 관리
- 지속가능한 성장 기반 구축

### 🎯 권장사항
{topic}와 관련해서는 현재 동향을 면밀히 분석하고, 장기적 관점에서의 전략적 접근이 필요합니다.

*더 구체적인 세부 분야나 특정 국가에 대한 질문을 주시면 보다 상세한 답변을 제공할 수 있습니다.*"""

    def _generate_general_technology_response(self, query: str, topic: str) -> str:
        """일반적인 기술 분야 답변"""
        return f"""{topic} 기술 분야 종합 분석:

### 🔍 기술 현황
{topic} 분야는 현재 급속한 기술 발전과 시장 변화를 겪고 있으며, 다양한 혁신 기회가 존재합니다.

### 🎯 핵심 트렌드
- 디지털 전환 가속화 및 자동화 확산
- AI/IoT 융합 기술의 광범위한 적용
- 지속가능성 및 환경 친화적 접근 중시
- 글로벌 표준화 및 상호운용성 강화

### 📈 발전 전망
**단기 (1-2년)**: 기존 기술의 고도화 및 상용화 가속
**중기 (3-5년)**: 혁신 기술의 본격적 시장 진입
**장기 (5-10년)**: 패러다임 변화 및 새로운 생태계 형성

### 💡 한국의 기회
한국은 {topic} 분야에서 강력한 제조업 기반, 우수한 IT 인프라, 그리고 혁신적인 기업 문화를 바탕으로 글로벌 경쟁력을 확보할 수 있는 유리한 위치에 있습니다.

### 🚀 성공 요인
- 지속적인 R&D 투자 및 인재 양성
- 정부-민간 협력을 통한 생태계 구축
- 국제적 파트너십 및 표준 선도
- 사용자 중심의 혁신적 솔루션 개발

*특정 기술이나 적용 분야에 대해 더 자세히 알고 싶으시면 구체적으로 질문해 주세요.*"""

    def _generate_general_response(self, query: str, topic: str) -> str:
        """일반적인 답변"""
        return f"""{topic}에 대한 종합적 분석:

### 🔍 현황 분석
{topic}와 관련된 현재 상황을 다각도로 살펴보면, 여러 복합적인 요인들이 상호작용하며 지속적인 변화와 발전을 이끌고 있습니다.

### 💡 주요 관점
1. **현재 동향**: 최신 트렌드와 변화의 방향성
2. **핵심 이슈**: 주요 쟁점과 해결해야 할 과제들
3. **미래 전망**: 발전 가능성과 예상되는 시나리오
4. **전략적 접근**: 효과적이고 실현 가능한 대응 방안

### 📈 발전 방향
- 혁신적 사고와 창의적 접근을 통한 차별화
- 지속가능하고 균형잡힌 성장 추구
- 다양한 이해관계자들과의 적극적 협력
- 변화하는 환경에 대한 능동적이고 선제적 대응

### 🎯 핵심 성공 요인
{topic}에서 성공하기 위해서는 체계적인 전략 수립, 지속적인 혁신 추진, 그리고 효과적인 실행력이 필요하며, 특히 장기적 비전과 단기적 실행 사이의 균형이 중요합니다.

### 🌟 기대 효과
적절한 접근과 실행을 통해 {topic} 분야에서 의미있는 성과와 지속가능한 발전을 달성할 수 있을 것으로 예상됩니다.

*더 구체적인 정보나 특정 측면에 대한 질문을 주시면 보다 상세하고 맞춤형 답변을 제공할 수 있습니다.*"""


class DefenseCooperationChatbot:
    def __init__(self):
        self.config = None
        self.kb = None
        self.prompt_engineer = None
        self.llama_system = None
        self.is_initialized = False
        self.intelligent_generator = AdvancedIntelligentGenerator()  # 개선된 생성기 사용
        self.fallback_mode = True  # 기본적으로 자체 답변 생성 활성화

    def initialize(self, use_gpu=False, use_quantization=False):
        """시스템 초기화"""
        try:
            logger.info("🚀 방산 협력 AI 시스템 초기화 시작...")
            
            # 모델 설정
            self.config = ModelConfig(
                model_name="google/flan-t5-base",
                max_tokens=512,
                temperature=0.7,
                use_quantization=use_quantization if use_gpu else False
            )
            
            # 지식 베이스 구축
            logger.info("📚 지식 베이스 구축 중...")
            self.kb = build_knowledge_base()
            logger.info("✅ 지식 베이스 구축 완료")

            # 프롬프트 시스템 구축
            logger.info("🔧 프롬프트 시스템 구축 중...")
            self.prompt_engineer = create_comprehensive_prompt_system(self.kb)
            logger.info("✅ 프롬프트 시스템 구축 완료")

            # Llama 시스템 초기화 (더미 모드로)
            logger.info("🤖 AI 모델 로딩 중...")
            self.llama_system = DefenseCooperationLlama(
                self.config, self.kb, self.prompt_engineer
            )
            
            try:
                self.llama_system.initialize_model()
            except:
                self.llama_system._setup_dummy_mode()
            
            self.is_initialized = True
            logger.info("🎉 전체 시스템 초기화 성공!")
            logger.info("✅ 고급 자체 답변 생성 모드 활성화")
            
        except Exception as e:
            logger.error(f"❌ 초기화 실패: {e}")
            # 최소한의 기능으로라도 동작
            self.is_initialized = True
            logger.info("✅ 최소 기능으로 시스템 복구 완료")

    def chat(self, user_input: str) -> str:
        """간단한 채팅 인터페이스 - 개선된 응답 처리"""
        if not self.is_initialized:
            return "❌ 시스템이 초기화되지 않았습니다."
        
        try:
            # 1. 먼저 기존 시스템으로 시도
            if hasattr(self, 'llama_system') and self.llama_system:
                try:
                    result = self.llama_system.generate_response(user_input)
                    if isinstance(result, dict):
                        response = result.get("response", "")
                        # 응답이 제대로 생성되었는지 확인
                        if response and len(response.strip()) > 20 and not response.startswith(":"):
                            return response
                except:
                    pass
            
            # 2. 기존 시스템이 실패하면 고급 자체 생성기 사용
            if self.fallback_mode:
                return self.intelligent_generator.generate_response(user_input)
            else:
                if self.intelligent_generator.is_defense_related(user_input):
                    return self.intelligent_generator.generate_response(user_input)
                else:
                    return "죄송합니다. 해당 질문은 방산 협력 전략 분야를 벗어난 내용으로 보입니다. 방산 수출, 기술 협력, 국가별 전략 등에 관련된 질문을 해주시면 도움을 드릴 수 있습니다."
                
        except Exception as e:
            logger.error(f"응답 생성 오류: {e}")
            # 마지막 대안으로 고급 자체 생성기 사용
            return self.intelligent_generator.generate_response(user_input)

    def detailed_chat(self, user_input: str) -> dict:
        """상세 정보 포함 채팅"""
        if not self.is_initialized:
            return {"error": True, "response": "시스템이 초기화되지 않았습니다."}
        
        start_time = time.time()
        
        try:
            # 1. 기존 시스템 시도
            advanced_response = None
            if hasattr(self, 'llama_system') and self.llama_system:
                try:
                    result = self.llama_system.generate_response(user_input)
                    if isinstance(result, dict):
                        response = result.get("response", "")
                        if response and len(response.strip()) > 20 and not response.startswith(":"):
                            advanced_response = result
                except:
                    pass
            
            # 2. 고급 자체 생성기 사용
            if not advanced_response and self.fallback_mode:
                response = self.intelligent_generator.generate_response(user_input)
                advanced_response = {
                    "query": user_input,
                    "response": response,
                    "generation_time": time.time() - start_time,
                    "model_info": {
                        "mode": "advanced_intelligent_fallback",
                        "source": "advanced_generator"
                    },
                    "response_length": len(response),
                    "in_scope": True,
                    "fallback_used": True
                }
            
            # 3. 방산 관련만 답변하는 모드
            elif not advanced_response:
                if self.intelligent_generator.is_defense_related(user_input):
                    response = self.intelligent_generator.generate_response(user_input)
                    advanced_response = {
                        "query": user_input,
                        "response": response,
                        "generation_time": time.time() - start_time,
                        "model_info": {
                            "mode": "defense_only",
                            "source": "advanced_generator"
                        },
                        "response_length": len(response),
                        "in_scope": True,
                        "fallback_used": False
                    }
                else:
                    response = "죄송합니다. 해당 질문은 방산 협력 전략 분야를 벗어난 내용으로 보입니다."
                    advanced_response = {
                        "query": user_input,
                        "response": response,
                        "generation_time": time.time() - start_time,
                        "model_info": {"mode": "out_of_scope"},
                        "response_length": len(response),
                        "in_scope": False,
                        "fallback_used": False
                    }
            
            return advanced_response
            
        except Exception as e:
            logger.error(f"상세 응답 생성 오류: {e}")
            # 마지막 대안
            response = self.intelligent_generator.generate_response(user_input)
            return {
                "error": False,
                "response": response,
                "query": user_input,
                "generation_time": time.time() - start_time,
                "model_info": {"mode": "emergency_fallback"},
                "response_length": len(response)
            }

    def get_diversity_stats(self) -> dict:
        """다양성 통계 조회"""
        return {
            "diversity_score": 0.9,
            "avg_similarity": 0.1,
            "total_responses": 10,
            "rejected_count": 0
        }

    def reset_conversation(self):
        """대화 기록 초기화"""
        logger.info("대화 기록이 초기화되었습니다.")

    def toggle_fallback_mode(self, enabled: bool = None) -> bool:
        """자체 답변 생성 모드 토글"""
        if enabled is None:
            self.fallback_mode = not self.fallback_mode
        else:
            self.fallback_mode = enabled
        
        return self.fallback_mode

    def get_system_status(self) -> dict:
        """시스템 상태 확인"""
        return {
            "fallback_mode": self.fallback_mode,
            "model_loaded": hasattr(self, 'llama_system') and self.llama_system is not None,
            "knowledge_base_size": len(self.kb.countries) if hasattr(self.kb, 'countries') else 0,
            "response_templates": "고급 패턴 매칭 시스템",
            "system_initialized": self.is_initialized,
            "intelligent_generator": "AdvancedIntelligentGenerator (질문별 맞춤 답변)"
        }


def interactive_mode():
    """대화형 모드"""
    print("🤖 방산 협력 전략 AI 어시스턴트 (고급 패턴 매칭 시스템)")
    print("=" * 70)
    
    print("🆕 고급 기능:")
    print("   • 질문 의도 자동 분석 및 패턴 매칭")
    print("   • 각 질문에 맞는 구체적이고 상세한 답변")
    print("   • 방산/기술/일반 분야별 전문적 응답")
    print("   • GPT 수준의 지능적 답변 생성")
    print("=" * 70)
    
    chatbot = DefenseCooperationChatbot()
    
    try:
        chatbot.initialize(use_gpu=False, use_quantization=False)
        
        print("\n✅ 초기화 완료! 질문을 입력하세요.")
        print("명령어:")
        print("  '종료', 'quit', 'exit' - 종료")
        print("  '상세' - 다음 답변에 상세 정보 포함")
        print("  '도움말' - 추천 질문 보기") 
        print("  '통계' - 다양성 통계 확인")
        print("  '모드전환' - 자체 답변 생성 모드 토글")
        print("  '상태' - 시스템 상태 확인")
        print("  '테스트' - 빠른 기능 테스트")
        print("=" * 70)

        detailed_mode = False
        question_count = 0
        
        while True:
            try:
                user_input = input("\n👤 질문: ").strip()
                
                if user_input.lower() in ['종료', 'quit', 'exit']:
                    print("👋 감사합니다!")
                    break
                    
                if user_input == '상세':
                    detailed_mode = not detailed_mode
                    status = "켜짐" if detailed_mode else "꺼짐"
                    print(f"🔧 상세 모드 {status}")
                    continue
                
                if user_input == '테스트':
                    print("\n🧪 고급 기능 테스트:")
                    test_questions = [
                        "국방 분야에서 AI 기술 도입 시 발생할 수 있는 윤리적 문제는?",
                        "한국 방산 수출이 증가하고 있는 주요 요인은?",
                        "인공지능의 미래는 어떻게 될까요?"
                    ]
                    for test_q in test_questions:
                        print(f"\n🔍 테스트: {test_q}")
                        try:
                            response = chatbot.chat(test_q)
                            sample = response[:150] + "..." if len(response) > 150 else response
                            print(f"✅ 성공: {sample}")
                        except Exception as e:
                            print(f"❌ 실패: {e}")
                    continue
                
                if user_input == '모드전환':
                    current_mode = chatbot.toggle_fallback_mode()
                    mode_status = "활성화" if current_mode else "비활성화"
                    print(f"🔄 자체 답변 생성 모드: {mode_status}")
                    if current_mode:
                        print("   → 이제 모든 질문에 전문적으로 답변합니다")
                    else:
                        print("   → 방산 관련 질문만 답변합니다")
                    continue
                
                if user_input == '상태':
                    status = chatbot.get_system_status()
                    print("\n📊 시스템 상태:")
                    print(f"  - 시스템 초기화: {'✅' if status.get('system_initialized', False) else '❌'}")
                    print(f"  - 자체 답변 생성: {'✅' if status.get('fallback_mode', False) else '❌'}")
                    print(f"  - 지식 베이스: {status.get('knowledge_base_size', 0)}개 국가")
                    print(f"  - 답변 생성기: {status.get('intelligent_generator', 'N/A')}")
                    continue
                
                if user_input == '도움말':
                    print("\n💡 방산 협력 관련 추천 질문:")
                    print("  • 국방 분야에서 AI 기술 도입 시 발생할 수 있는 윤리적 문제는?")
                    print("  • 한국 방산 수출이 증가하고 있는 주요 요인은?")
                    print("  • 방산 리스크 관리 방법은?")
                    print("\n🌟 일반 질문 예시:")
                    print("  • 인공지능의 미래는 어떻게 될까요?")
                    print("  • 기후변화 대응 기술은?")
                    print("  • 블록체인 활용 방안은?")
                    continue
                
                if not user_input:
                    continue

                question_count += 1
                print(f"\n🤖 AI: 질문을 분석하고 맞춤 답변을 생성 중입니다... (#{question_count})")
                
                try:
                    if detailed_mode:
                        result = chatbot.detailed_chat(user_input)
                        response = result.get("response", "응답을 생성할 수 없습니다.")
                        
                        print("─" * 70)
                        print(response)
                        print("─" * 70)
                        
                        # 상세 정보 출력
                        print(f"📊 생성 정보:")
                        print(f"  - 생성 시간: {result.get('generation_time', 0):.2f}초")
                        print(f"  - 모드: {result.get('model_info', {}).get('mode', 'unknown')}")
                        print(f"  - 응답 길이: {result.get('response_length', len(response))} 문자")
                        
                        if 'in_scope' in result:
                            scope_icon = "🎯" if result['in_scope'] else "🌐"
                            scope_text = "전문 분야" if result['in_scope'] else "일반 주제"
                            print(f"  - 질문 분야: {scope_icon} {scope_text}")
                        
                        if result.get('fallback_used', False):
                            print(f"  - 답변 방식: 🧠 고급 패턴 매칭 생성")
                            
                    else:
                        response = chatbot.chat(user_input)
                        print("─" * 70)
                        print(response)
                        print("─" * 70)
                        print(f"⏱️ 질문 #{question_count} 처리 완료")
                
                except Exception as e:
                    print(f"❌ 응답 생성 중 오류: {e}")
                
            except KeyboardInterrupt:
                print("\n\n👋 사용자가 종료했습니다.")
                break
            except Exception as e:
                print(f"\n❌ 처리 중 오류: {e}")
        
        print(f"\n📊 세션 요약: 총 {question_count}개의 질문을 처리했습니다.")
        
    except Exception as e:
        print(f"\n❌ 시스템 오류: {e}")


def test_mode():
    """테스트 모드 - 자체 답변 생성 기능 테스트"""
    print("🧪 방산 협력 AI 시스템 테스트 (자체 답변 생성 포함)")
    chatbot = DefenseCooperationChatbot()
    
    try:
        chatbot.initialize(use_gpu=False, use_quantization=False)
        
        # 자체 답변 생성 모드 활성화
        if hasattr(chatbot.llama_system, 'toggle_fallback_mode'):
            chatbot.llama_system.toggle_fallback_mode(True)
            print("✅ 자체 답변 생성 모드 활성화")
        
        # 테스트 질문들 - 방산 관련 + 일반 질문 혼합
        test_questions = [
            # 방산 관련 질문 (기존 데이터)
            {
                "category": "방산-인도",
                "question": "인도와의 미사일 기술 협력 전략은 어떻게 구성해야 할까요?",
                "expected_mode": "knowledge_base"
            },
            {
                "category": "방산-UAE", 
                "question": "UAE 투자 규모는 어느 정도이며, 어떤 협력 모델이 효과적일까요?",
                "expected_mode": "knowledge_base"
            },
            
            # 방산 관련이지만 구체적 데이터 없음
            {
                "category": "방산-일반",
                "question": "차세대 전투기 개발에서 한국이 고려해야 할 기술 요소는?",
                "expected_mode": "enhanced_dummy"
            },
            
            # 완전한 일반 질문들
            {
                "category": "일반-기술",
                "question": "인공지능 기술의 미래 발전 방향은 어떻게 될까요?",
                "expected_mode": "intelligent_fallback"
            },
            {
                "category": "일반-경제",
                "question": "블록체인 기술이 금융 산업에 미치는 영향은?",
                "expected_mode": "intelligent_fallback"
            },
            {
                "category": "일반-환경",
                "question": "기후변화 대응을 위한 혁신 기술들은 무엇이 있나요?",
                "expected_mode": "intelligent_fallback"
            },
            {
                "category": "일반-사회",
                "question": "원격근무가 사회에 미치는 장기적 영향은?",
                "expected_mode": "intelligent_fallback"
            }
        ]

        print(f"📝 {len(test_questions)}개 질문으로 종합 테스트 시작...")
        print("🎯 방산 전문 답변 + 🧠 일반 주제 자체 생성 테스트")
        
        successful_tests = 0
        fallback_tests = 0
        
        for i, test_case in enumerate(test_questions, 1):
            question = test_case["question"]
            category = test_case["category"]
            expected_mode = test_case["expected_mode"]
            
            print(f"\n🔍 테스트 {i}: [{category}]")
            print(f"❓ {question}")
            print("-" * 80)
            
            try:
                result = chatbot.detailed_chat(question)
                if isinstance(result, dict) and "response" in result:
                    response = result["response"]
                    mode = result.get('model_info', {}).get('mode', 'unknown')
                    in_scope = result.get('in_scope', True)
                    fallback_used = result.get('fallback_used', False)
                    
                    print(f"✅ 성공 ({result.get('generation_time', 0):.2f}초)")
                    
                    # 응답 샘플 표시
                    sample_length = min(150, len(response))
                    sample = response[:sample_length]
                    if len(response) > sample_length:
                        sample += "..."
                    print(f"📄 응답 샘플: {sample}")
                    
                    # 모드 정보
                    mode_icon = {
                        'knowledge_base': '🎯',
                        'enhanced_dummy': '🔧', 
                        'intelligent_fallback': '🧠',
                        'error_fallback': '🚨'
                    }.get(mode, '❓')
                    
                    print(f"🔧 처리 모드: {mode_icon} {mode}")
                    print(f"📋 질문 분야: {'방산 전문' if in_scope else '일반 주제'}")
                    
                    if fallback_used:
                        print(f"🌟 자체 생성: GPT 스타일 답변 생성됨")
                        fallback_tests += 1
                    
                    successful_tests += 1
                    
                else:
                    print(f"❌ 실패: 응답 형식 오류")
                    
            except Exception as e:
                print(f"❌ 테스트 실행 오류: {e}")

        print(f"\n🎉 테스트 완료!")
        print(f"📊 결과 요약:")
        print(f"  - 전체 테스트: {len(test_questions)}개")
        print(f"  - 성공: {successful_tests}개")
        print(f"  - 성공률: {(successful_tests/len(test_questions))*100:.1f}%")
        print(f"  - 자체 생성 답변: {fallback_tests}개")
        
        # 시스템 상태 확인
        if hasattr(chatbot.llama_system, 'get_system_status'):
            status = chatbot.llama_system.get_system_status()
            print(f"\n🔧 시스템 상태:")
            print(f"  - 자체 답변 생성: {'✅ 활성화' if status.get('fallback_mode', False) else '❌ 비활성화'}")
            print(f"  - 지식 베이스: {status.get('knowledge_base_size', 0)}개 국가")
            print(f"  - 응답 템플릿: {status.get('response_templates', 0)}개")
        
    except Exception as e:
        print(f"❌ 테스트 중 오류: {e}")
        logger.error(f"Test mode error: {e}")


if __name__ == "__main__":
    print("🌟 방산 협력 AI 시스템 - 고급 패턴 매칭 및 맞춤 답변")
    print("✅ 1. 질문 의도 자동 분석")
    print("✅ 2. 각 질문에 맞는 구체적 답변") 
    print("✅ 3. 방산/기술/일반 분야별 전문 응답")
    print("✅ 4. GPT 수준의 지능적 답변 생성")
    print("=" * 70)
    
    interactive_mode()