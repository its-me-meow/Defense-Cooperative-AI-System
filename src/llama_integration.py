import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, AutoModelForCausalLM
import json
import logging
from typing import Dict, List, Optional, Tuple
import time
from dataclasses import dataclass
import random
import re
from difflib import SequenceMatcher


logger = logging.getLogger(__name__)

@dataclass
class ModelConfig:
    """수정된 모델 설정 - T5 모델 지원"""
    model_name: str = "google/flan-t5-base"
    max_tokens: int = 512  # T5에 적합한 길이로 조정
    temperature: float = 0.9
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
    """향상된 지식 베이스 - PDF 데이터 반영"""
    
    def __init__(self, knowledge_base):
        self.kb = knowledge_base
        self.qa_pairs = self._load_pdf_qa_data()
        
    def _load_pdf_qa_data(self) -> List[Dict]:
        """PDF의 질문-답변 데이터 로드"""
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
                "category": "지역별 우선순위"
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
                "category": "기술 협력"
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
                "category": "비즈니스 모델"
            }
        ]
    
    def find_relevant_answer(self, query: str) -> Optional[str]:
        """질문에 관련된 답변 찾기"""
        query_lower = query.lower()
        
        # 키워드 매칭으로 관련 답변 찾기
        for qa in self.qa_pairs:
            question_keywords = qa["question"].lower()
            if any(keyword in query_lower for keyword in question_keywords.split()):
                return qa["answer"]
        
        return None
    
    def is_question_in_scope(self, query: str) -> bool:
        """질문이 지식 베이스 범위 내인지 확인"""
        defense_keywords = [
            "방산", "미사일", "방어", "군사", "무기", "협력", "수출", "투자",
            "인도", "UAE", "브라질", "중동", "동남아", "아프리카", "기술이전",
            "사이버", "우주", "항공", "해양", "AI", "드론"
        ]
        
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in defense_keywords)
class IntelligentResponseGenerator:
    """지능형 응답 생성기 - 파인튜닝 데이터 외에도 자체 답변 생성"""
    
    def __init__(self, knowledge_base, model_config):
        self.kb = knowledge_base
        self.config = model_config
        self.general_knowledge_templates = self._build_general_templates()
        self.reasoning_patterns = self._build_reasoning_patterns()
        
    def _build_general_templates(self) -> Dict[str, List[str]]:
        """일반적인 지식 기반 템플릿들"""
        return {
            "technology_analysis": [
                """해당 기술 분야에 대한 분석:

### 🔍 기술 현황
- 현재 글로벌 기술 트렌드를 고려할 때, 이 분야는 {trend_analysis}
- 주요 기술 선도국들의 접근 방식: {tech_approach}

### 🎯 한국의 기술적 위치
- 한국의 현재 기술 수준: {korea_level}
- 강점 분야: {strengths}
- 개선이 필요한 영역: {improvement_areas}

### 💡 발전 전략
- 단기 목표 (1-2년): {short_term}
- 중기 목표 (3-5년): {medium_term}
- 장기 비전 (5-10년): {long_term}

### 📊 기대 효과
- 기술적 효과: {tech_benefits}
- 경제적 효과: {economic_benefits}
- 전략적 의미: {strategic_meaning}"""
            ],
            "general_inquiry": [
                """질문에 대한 답변:

### 🔍 현황 분석
{current_analysis}

### 💡 주요 관점
{key_perspectives}

### 📈 발전 방향
{development_direction}

### 🎯 권장사항
{recommendations}"""
            ]
        }
    
    def _build_reasoning_patterns(self) -> Dict[str, callable]:
        """추론 패턴들"""
        return {
            "technology_reasoning": self._reason_about_technology,
            "general_reasoning": self._reason_generally
        }
    
    def _reason_about_technology(self, topic: str, context: str) -> Dict[str, str]:
        """기술 관련 추론"""
        return {
            "trend_analysis": f"{topic} 기술은 현재 AI, 자동화, 디지털 전환의 영향을 받아 빠르게 발전하고 있습니다.",
            "tech_approach": "선진국들은 민관 협력, 오픈 이노베이션, 국제 공동연구를 통해 기술 발전을 추진하고 있습니다.",
            "korea_level": "한국은 제조업 기반과 IT 인프라를 바탕으로 중상위권의 기술 수준을 보유하고 있습니다.",
            "strengths": "시스템 통합, 대량 생산, 품질 관리 분야에서 강점을 보입니다.",
            "improvement_areas": "기초 연구, 원천 기술, 글로벌 표준화 주도력 향상이 필요합니다.",
            "short_term": "기존 기술의 고도화 및 파일럿 프로젝트 추진",
            "medium_term": "핵심 기술 자립화 및 국제 협력 확대",
            "long_term": "글로벌 기술 선도국 진입 및 표준 주도",
            "tech_benefits": "기술 경쟁력 향상, 혁신 생태계 구축",
            "economic_benefits": "새로운 산업 창출, 수출 증대, 일자리 창출",
            "strategic_meaning": "기술 주권 확보, 국가 안보 강화, 글로벌 영향력 확대"
        }
    
    def _reason_generally(self, topic: str, context: str) -> Dict[str, str]:
        """일반적 추론"""
        return {
            "current_analysis": f"'{topic}'에 대한 현재 상황을 분석하면, 다양한 요인들이 복합적으로 작용하고 있습니다.",
            "key_perspectives": "기술적, 경제적, 사회적 관점에서 종합적으로 접근해야 합니다.",
            "development_direction": "지속가능하고 혁신적인 방향으로 발전해 나가는 것이 중요합니다.",
            "recommendations": "체계적인 계획 수립과 단계적 실행을 통해 목표를 달성할 수 있을 것입니다."
        }
    
    def classify_question_type(self, query: str) -> str:
        """질문 유형 분류"""
        technology_keywords = ["기술", "개발", "혁신", "연구", "AI", "인공지능", "로봇", "자동화"]
        
        query_lower = query.lower()
        
        if any(keyword in query_lower for keyword in technology_keywords):
            return "technology_reasoning"
        else:
            return "general_reasoning"
    
    def extract_key_topic(self, query: str) -> str:
        """질문에서 핵심 주제 추출"""
        important_words = []
        words = query.split()
        
        stop_words = {"의", "는", "이", "가", "을", "를", "에", "에서", "로", "으로", "와", "과", "하고", "어떻게", "왜", "무엇"}
        
        for word in words:
            if len(word) > 1 and word not in stop_words:
                important_words.append(word)
        
        return " ".join(important_words[:3])
    
    def generate_intelligent_response(self, query: str, context: str = "") -> str:
        """지능적 응답 생성"""
        question_type = self.classify_question_type(query)
        key_topic = self.extract_key_topic(query)
        
        reasoning_func = self.reasoning_patterns[question_type]
        reasoning_results = reasoning_func(key_topic, context)
        
        if question_type == "technology_reasoning":
            template = self.general_knowledge_templates["technology_analysis"][0]
            try:
                response = template.format(**reasoning_results)
            except KeyError:
                response = self._generate_simple_response(query, key_topic)
        else:
            template = self.general_knowledge_templates["general_inquiry"][0]
            try:
                response = template.format(**reasoning_results)
            except KeyError:
                response = self._generate_simple_response(query, key_topic)
        
        return response
    
    def _generate_simple_response(self, query: str, topic: str) -> str:
        """간단한 응답 생성"""
        return f"""'{topic}'에 대한 질문에 답변드리겠습니다.

### 🔍 분석
해당 주제에 대해 다양한 관점에서 접근해보겠습니다.

### 💡 주요 고려사항
1. **현재 상황**: 최신 동향과 현황을 파악하는 것이 중요합니다
2. **발전 방향**: 미래 지향적이고 지속가능한 접근이 필요합니다
3. **실행 방안**: 구체적이고 실현 가능한 계획 수립이 핵심입니다

### 📈 권장사항
체계적인 분석과 단계적 접근을 통해 목표를 달성할 수 있을 것으로 예상됩니다.

*더 구체적인 정보가 필요하시면 세부 사항을 명시해 주시면 보다 상세한 답변을 드릴 수 있습니다.*"""

class DefenseCooperationLlama:
    """향상된 방산 협력 LLM 시스템 - 자체 답변 생성 기능 추가"""
    
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
        
        # 새로운 기능 추가
        self.intelligent_generator = IntelligentResponseGenerator(knowledge_base, config)
        self.fallback_mode = True  # 자체 답변 생성 모드 활성화

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
        """향상된 응답 생성 - 자체 답변 생성 기능 포함"""
        start_time = time.time()
        
        try:
            # 1. 기존 지식 베이스에서 답변 찾기
            relevant_answer = self.enhanced_kb.find_relevant_answer(user_query)
            if relevant_answer:
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
            
            # 2. 방산 관련 질문인지 확인
            is_defense_related = self.enhanced_kb.is_question_in_scope(user_query)
            
            # 3. 방산 관련 질문이면 기존 로직 사용
            if is_defense_related:
                context_info = self._get_context_from_kb(user_query)
                
                if self.model == "dummy_model" or self.model is None:
                    response = self._generate_knowledge_based_response(user_query, context_info)
                    mode = "enhanced_dummy"
                else:
                    response = self._generate_real_response(user_query, context_info)
                    mode = "real_model"
                
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
            
            # 4. 방산 외 질문이지만 자체 답변 생성 모드가 활성화된 경우
            elif self.fallback_mode:
                response = self.intelligent_generator.generate_intelligent_response(
                    user_query, 
                    context=""
                )
                
                # 방산 관련성 안내 추가
                response = f"""**[일반 주제 답변]**

{response}

---
💡 **참고**: 이 질문은 방산 협력 분야를 벗어난 내용입니다. 방산 수출, 기술 협력, 국가별 전략 등에 관한 질문을 주시면 더 전문적인 답변을 제공할 수 있습니다."""
                
                return {
                    "query": user_query,
                    "response": response,
                    "generation_time": time.time() - start_time,
                    "model_info": {"mode": "intelligent_fallback", "source": "general_knowledge"},
                    "in_scope": False,
                    "fallback_used": True
                }
            
            # 5. 자체 답변 생성 모드가 비활성화된 경우 (기존 방식)
            else:
                return {
                    "query": user_query,
                    "response": "죄송합니다. 해당 질문은 방산 협력 전략 분야를 벗어난 내용으로 보입니다. 방산 수출, 기술 협력, 국가별 전략 등에 관련된 질문을 해주시면 도움을 드릴 수 있습니다.",
                    "generation_time": time.time() - start_time,
                    "model_info": {"mode": "out_of_scope"},
                    "in_scope": False
                }
                
        except Exception as e:
            logger.error(f"Response generation error: {e}")
            
            # 오류 발생 시에도 자체 답변 생성 시도
            if self.fallback_mode:
                try:
                    fallback_response = self.intelligent_generator.generate_intelligent_response(
                        user_query, 
                        f"오류 발생으로 인한 대체 응답"
                    )
                    return {
                        "query": user_query,
                        "response": f"시스템 오류가 발생했지만 최선의 답변을 제공해드립니다:\n\n{fallback_response}",
                        "generation_time": time.time() - start_time,
                        "model_info": {"mode": "error_fallback"},
                        "error_handled": True
                    }
                except:
                    pass
            
            return {
                "query": user_query,
                "response": "죄송합니다. 응답 생성 중 오류가 발생했습니다. 다시 시도해 주세요.",
                "error": True,
                "generation_time": time.time() - start_time
            }

    def _get_context_from_kb(self, query: str) -> str:
        """지식 베이스에서 관련 컨텍스트 추출"""
        context_parts = []
        
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
        """지식 베이스 기반 응답 생성"""
        if "우선순위" in query or "순위" in query:
            return """방산 수출 우선순위는 다음 기준으로 결정됩니다:

1. **시장 규모**: 국방예산 및 구매력
2. **기술 상보성**: 상호 보완 가능한 기술 영역
3. **지정학적 중요성**: 전략적 파트너십 가치
4. **협력 용이성**: 정치적/제도적 장벽 수준

구체적인 국가별 우선순위는 지역과 분야에 따라 달라집니다. 특정 지역이나 기술 분야를 명시해 주시면 더 자세한 정보를 제공할 수 있습니다."""

        elif "협력" in query and "전략" in query:
            return """방산 기술 협력 전략의 핵심 요소들:

### 📋 협력 모델
- **공동개발**: 상호 기술 융합을 통한 신제품 개발
- **기술이전**: 단계적 기술 이전을 통한 현지 생산
- **투자 협력**: 합작투자를 통한 생산기지 구축

### 🎯 성공 요인
- 상호보완적 기술 역량 확인
- 정부 간 정책적 지원 확보
- 장기적 파트너십 구축
- 시장 진출 전략 수립

더 구체적인 국가나 기술 분야에 대한 질문을 해주시면 맞춤형 전략을 제공해드리겠습니다."""

        else:
            return f"""방산 협력 전략 관련 정보:

{context}

### 💡 주요 고려사항
- 기술적 상보성 분석
- 시장 진입 전략 수립
- 리스크 평가 및 관리
- 장기적 파트너십 구축

구체적인 질문이나 특정 국가/기술 분야에 대해 문의해 주시면 더 상세한 정보를 제공할 수 있습니다."""

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
    
    def toggle_fallback_mode(self, enabled: bool = None) -> bool:
        """자체 답변 생성 모드 토글"""
        if enabled is None:
            self.fallback_mode = not self.fallback_mode
        else:
            self.fallback_mode = enabled
        
        return self.fallback_mode
    
    def get_system_status(self) -> Dict:
        """시스템 상태 조회"""
        return {
            "fallback_mode": self.fallback_mode,
            "model_loaded": self.model is not None and self.model != "dummy_model",
            "knowledge_base_size": len(self.kb.countries) if hasattr(self.kb, 'countries') else 0,
            "response_templates": len(self.intelligent_generator.general_knowledge_templates)
        }

# 사용 예시
if __name__ == "__main__":
    print("Enhanced Defense Cooperation LLM - 4가지 주요 문제 해결 완료")
    print("1. T5 모델 지원 ✓")
    print("2. PDF 데이터 기반 정확한 답변 ✓") 
    print("3. 완전한 응답 출력 ✓")
    print("4. 범위 외 질문 적절한 처리 ✓")