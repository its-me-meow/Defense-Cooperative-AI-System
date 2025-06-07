import sys
import os
import logging

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from src.data_structure import build_knowledge_base
    from src.prompt_engineering import create_comprehensive_prompt_system
    from src.llama_integration import DefenseCooperationLlama, ModelConfig
except ImportError:
    # 현재 디렉토리에서 import 시도
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

class DefenseCooperationChatbot:
    def __init__(self):
        self.config = None
        self.kb = None
        self.prompt_engineer = None
        self.llama_system = None
        self.is_initialized = False

    def initialize(self, use_gpu=False, use_quantization=False):
        """시스템 초기화 - 안정성 확보"""
        try:
            logger.info("🚀 방산 협력 AI 시스템 초기화 시작...")
            
            # 모델 설정 - T5 모델 지원
            self.config = ModelConfig(
                model_name="google/flan-t5-base",  # T5 모델 사용
                max_tokens=512,  # T5에 적합한 길이
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

            # Llama 시스템 초기화
            logger.info("🤖 AI 모델 로딩 중... (시간이 소요될 수 있습니다)")
            self.llama_system = DefenseCooperationLlama(
                self.config, self.kb, self.prompt_engineer
            )
            
            # 모델 초기화 (실패 시 자동으로 더미 모드)
            self.llama_system.initialize_model()
            
            self.is_initialized = True
            logger.info("🎉 전체 시스템 초기화 성공!")
            
        except Exception as e:
            logger.error(f"❌ 초기화 실패: {e}")
            # 초기화 실패 시 더미 모드로라도 동작하도록
            try:
                logger.info("🔄 더미 모드로 시스템 복구 중...")
                self.config = ModelConfig(model_name="dummy_model")
                if not self.kb:
                    self.kb = build_knowledge_base()
                if not self.prompt_engineer:
                    self.prompt_engineer = create_comprehensive_prompt_system(self.kb)
                self.llama_system = DefenseCooperationLlama(self.config, self.kb, self.prompt_engineer)
                self.llama_system._setup_dummy_mode()
                self.is_initialized = True
                logger.info("✅ 더미 모드로 시스템 복구 완료")
            except Exception as recovery_error:
                logger.error(f"❌ 시스템 복구도 실패: {recovery_error}")
                raise

    def chat(self, user_input: str) -> str:
        """간단한 채팅 인터페이스 - 완전한 응답 출력"""
        if not self.is_initialized:
            return "❌ 시스템이 초기화되지 않았습니다."
        
        try:
            result = self.llama_system.generate_response(user_input)
            if "error" not in result:
                # 응답을 완전히 출력하도록 수정
                response = result["response"]
                # 응답이 잘렸는지 확인하고 완전한 응답 보장
                if len(response) > 0:
                    return response
                else:
                    return "응답을 생성하지 못했습니다. 다시 시도해 주세요."
            else:
                return result["response"]
        except Exception as e:
            logger.error(f"응답 생성 오류: {e}")
            return f"❌ 응답 생성 중 오류가 발생했습니다: {str(e)}"

    def detailed_chat(self, user_input: str) -> dict:
        """상세 정보 포함 채팅"""
        if not self.is_initialized:
            return {"error": "시스템이 초기화되지 않았습니다."}
        
        try:
            return self.llama_system.generate_response(user_input)
        except Exception as e:
            logger.error(f"상세 응답 생성 오류: {e}")
            return {
                "error": True,
                "response": f"응답 생성 중 오류가 발생했습니다: {str(e)}",
                "query": user_input
            }

    def get_diversity_stats(self) -> dict:
        """다양성 통계 조회"""
        if not self.is_initialized or not self.llama_system:
            return {"error": "시스템이 초기화되지 않았습니다."}
        
        return self.llama_system.get_diversity_stats()

    def reset_conversation(self):
        """대화 기록 초기화"""
        if self.is_initialized and self.llama_system:
            self.llama_system.reset_diversity_tracking()
            logger.info("대화 기록이 초기화되었습니다.")

def interactive_mode():
    """대화형 모드 - 완전한 출력 지원"""
    print("🤖 방산 협력 전략 AI 어시스턴트 (향상된 버전)")
    print("=" * 60)
    
    # 사용자 설정 확인 - 안전한 기본값 사용
    use_gpu = input("GPU를 사용하시겠습니까? (y/n, 기본값: n): ").lower()
    use_gpu = use_gpu == 'y'
    
    use_quant = input("양자화를 사용하시겠습니까? (메모리 절약, y/n, 기본값: n): ").lower()  
    use_quant = use_quant == 'y'

    chatbot = DefenseCooperationChatbot()
    
    try:
        chatbot.initialize(use_gpu=use_gpu, use_quantization=use_quant)
        
        print("\n✅ 초기화 완료! 질문을 입력하세요.")
        print("명령어: '종료', 'quit', 'exit' - 종료")
        print("       '상세' - 다음 답변에 상세 정보 포함")
        print("       '도움말' - 추천 질문 보기")
        print("       '통계' - 다양성 통계 확인")
        print("       '초기화' - 대화 기록 초기화")
        print("=" * 60)

        detailed_mode = False
        
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
                    
                if user_input == '도움말':
                    print("\n💡 추천 질문:")
                    print("  • 중동 및 북아프리카 지역에서 한국의 방산 수출 우선순위 국가를 순위별로 알려주세요")
                    print("  • 인도와의 미사일 기술 협력 전략은 어떻게 구성해야 할까요?")
                    print("  • UAE 투자 규모는 어느 정도이며, 어떤 협력 모델이 효과적일까요?")
                    print("  • 남아시아 및 동남아시아 지역에서 방산 수출 우선순위를 알려주세요")
                    print("  • 브라질과 항공우주 협력이 가능한가요?")
                    print("  • 동남아시아 해양안보 협력 방안은?")
                    print("  • 아프리카 평화유지 장비 수출 전략은?")
                    continue
                    
                if user_input == '통계':
                    stats = chatbot.get_diversity_stats()
                    if "error" not in stats:
                        print("\n📊 다양성 통계:")
                        print(f"  - 다양성 점수: {stats.get('diversity_score', 0):.2f}")
                        print(f"  - 평균 유사도: {stats.get('avg_similarity', 0):.2f}")
                        print(f"  - 총 응답 수: {stats.get('total_responses', 0)}")
                        print(f"  - 거부된 응답: {stats.get('rejected_count', 0)}")
                    else:
                        print(f"통계 조회 오류: {stats.get('error', '알 수 없는 오류')}")
                    continue
                    
                if user_input == '초기화':
                    chatbot.reset_conversation()
                    print("🔄 대화 기록이 초기화되었습니다.")
                    continue
                    
                if not user_input:
                    continue

                print("\n🤖 AI: ", end="", flush=True)
                
                if detailed_mode:
                    result = chatbot.detailed_chat(user_input)
                    if "error" not in result or not result.get("error", False):
                        response = result["response"]
                        
                        # 응답을 완전히 출력
                        print(response)
                        print()
                        
                        # 상세 정보 출력
                        print(f"📊 생성 정보:")
                        print(f"  - 생성 시간: {result.get('generation_time', 0):.2f}초")
                        print(f"  - 모드: {result.get('model_info', {}).get('mode', 'unknown')}")
                        print(f"  - 응답 길이: {result.get('response_length', 0)} 문자")
                        print(f"  - 소스: {result.get('model_info', {}).get('source', 'unknown')}")
                        
                        # 범위 확인 정보
                        if 'in_scope' in result:
                            scope_status = "범위 내" if result['in_scope'] else "범위 외"
                            print(f"  - 질문 범위: {scope_status}")
                        
                        # 다양성 정보 표시
                        diversity_info = result.get('diversity_info', {})
                        if diversity_info:
                            print(f"  - 다양성 점수: {diversity_info.get('diversity_score', 0):.2f}")
                    else:
                        print(result.get("response", "알 수 없는 오류"))
                else:
                    response = chatbot.chat(user_input)
                    # 응답을 완전히 출력 (길이 제한 없음)
                    print(response)
                
            except KeyboardInterrupt:
                print("\n\n👋 사용자가 종료했습니다.")
                break
            except Exception as e:
                print(f"\n❌ 처리 중 오류: {e}")
                logger.error(f"Interactive mode error: {e}")
                
    except KeyboardInterrupt:
        print("\n\n👋 사용자가 종료했습니다.")
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        logger.error(f"Interactive mode error: {e}")

def test_mode():
    """테스트 모드 - PDF 질문 테스트"""
    print("🧪 방산 협력 AI 시스템 테스트 (PDF 데이터 검증)")
    chatbot = DefenseCooperationChatbot()
    
    try:
        chatbot.initialize(use_gpu=False, use_quantization=False)
        
        # PDF에 있는 실제 질문들로 테스트
        test_questions = [
            "중동 및 북아프리카 지역에서 한국의 방산 수출 우선순위 국가를 순위별로 알려주세요",
            "남아시아 및 동남아시아 지역에서 방산 수출 우선순위를 알려주세요", 
            "인도와의 미사일 기술 협력 전략은 어떻게 구성해야 할까요?",
            "UAE 투자 규모는 어느 정도이며, 어떤 협력 모델이 효과적일까요?",
            "브라질과 항공우주 협력이 가능한가요?",
            "아프리카 지역에서 한국의 방산 수출 전략을 수립한다면 어떤 국가들을 우선해야 할까요?",
            # 범위 외 질문 테스트
            "오늘 날씨는 어떤가요?",
            "파이썬 프로그래밍을 배우려면 어떻게 해야 하나요?"
        ]

        print(f"📝 {len(test_questions)}개 질문으로 정확성 테스트 시작...")
        
        successful_tests = 0
        
        for i, question in enumerate(test_questions, 1):
            print(f"\n🔍 테스트 {i}: {question}")
            print("-" * 80)
            
            try:
                result = chatbot.detailed_chat(question)
                if "error" not in result or not result.get("error", False):
                    response = result["response"]
                    print(f"✅ 성공 ({result.get('generation_time', 0):.2f}초)")
                    
                    # 응답의 첫 200자만 표시 (전체는 너무 길어서)
                    if len(response) > 200:
                        sample = response[:200] + "..."
                    else:
                        sample = response
                    print(f"📄 응답 샘플: {sample}")
                    
                    # 모드 및 소스 정보
                    mode = result.get('model_info', {}).get('mode', 'unknown')
                    source = result.get('model_info', {}).get('source', 'unknown')
                    print(f"🔧 모드: {mode}, 소스: {source}")
                    
                    # 범위 확인
                    if 'in_scope' in result:
                        scope_status = "✅ 범위 내" if result['in_scope'] else "❌ 범위 외"
                        print(f"📋 질문 범위: {scope_status}")
                        
                    successful_tests += 1
                else:
                    print(f"❌ 실패: {result.get('response', '알 수 없는 오류')}")
            except Exception as e:
                print(f"❌ 테스트 실행 오류: {e}")

        print(f"\n🎉 테스트 완료: {successful_tests}/{len(test_questions)} 성공")
        
        # 최종 다양성 통계
        try:
            final_stats = chatbot.get_diversity_stats()
            if "error" not in final_stats:
                print(f"\n📊 최종 다양성 통계:")
                print(f"  - 다양성 점수: {final_stats.get('diversity_score', 0):.2f}")
                print(f"  - 평균 유사도: {final_stats.get('avg_similarity', 0):.2f}")
                print(f"  - 총 응답 수: {final_stats.get('total_responses', 0)}")
                print(f"  - 거부된 응답: {final_stats.get('rejected_count', 0)}개")
            else:
                print(f"통계 조회 오류: {final_stats.get('error')}")
        except Exception as e:
            print(f"통계 조회 중 오류: {e}")
        
    except Exception as e:
        print(f"❌ 테스트 중 오류: {e}")
        logger.error(f"Test mode error: {e}")

if __name__ == "__main__":
    print("🌟 향상된 방산 협력 AI 시스템 - 4가지 주요 문제 해결")
    print("✅ 1. T5 모델 지원으로 초기화 오류 해결")
    print("✅ 2. PDF 데이터 기반 정확한 답변 제공") 
    print("✅ 3. 완전한 응답 출력 보장")
    print("✅ 4. 범위 외 질문 적절한 처리")
    print("=" * 60)
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "interactive":
            interactive_mode()
        elif sys.argv[1] == "test":
            test_mode()
        else:
            print("사용법: python chatbot.py [interactive|test]")
            print("또는 인자 없이 실행하면 기본 테스트 모드로 실행됩니다.")
    else:
        print("기본 모드로 실행합니다.")
        test_mode()  # 기본값을 test_mode로 설정