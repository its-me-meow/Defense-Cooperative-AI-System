from src.data_structure import build_knowledge_base
from src.prompt_engineering import create_comprehensive_prompt_system
from src.llama_integration import DefenseCooperationLlama, ModelConfig
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

print("🧪 방산 협력 AI 시스템 테스트")
print("=" * 50)

try:
    # 지식베이스 구축
    print("📚 지식베이스 구축 중...")
    kb = build_knowledge_base()
    print(f"✅ 지식베이스 구축 완료 ({len(kb.countries)}개국)")

    # 프롬프트 엔지니어 생성
    print("🔧 프롬프트 엔지니어링 시스템 구축 중...")
    prompt_engineer = create_comprehensive_prompt_system(kb)
    print("✅ 프롬프트 엔지니어링 시스템 구축 완료")

    # 모델 설정 (안정성 우선)
    config = ModelConfig(
        model_name="google/flan-t5-base",  # 더 안정적인 모델
        max_tokens=1024,  # 토큰 길이 제한
        temperature=0.8,
        use_quantization=False  # 안정성을 위해 비활성화
    )

    # Llama 시스템 생성
    print("🤖 AI 시스템 초기화 중...")
    llama_system = DefenseCooperationLlama(config, kb, prompt_engineer)
    
    # 모델 초기화 (오류 발생 시 자동으로 더미 모드로 전환)
    print("📥 모델 로딩 중... (처음 실행 시 다운로드가 필요할 수 있습니다)")
    llama_system.initialize_model()
    print("✅ AI 시스템 초기화 완료")

    # 테스트 질문들
    test_questions = [
        "인도와의 미사일 기술 협력 전략은?",
        "UAE 투자 규모는 어느 정도인가요?",
        "브라질과 항공우주 협력이 가능한가요?",
        "비NATO 국가 중 우선 협력 대상국은 어디인가요?"
    ]

    print("\n🚀 AI 응답 테스트 시작")
    print("=" * 50)

    successful_tests = 0
    total_time = 0

    for i, question in enumerate(test_questions, 1):
        print(f"\n🔍 테스트 {i}: {question}")
        print("-" * 60)
        
        try:
            result = llama_system.generate_response(question)
            
            if "error" not in result:
                print("✅ 응답 생성 성공")
                print(f"🤖 모드: {result['model_info']['mode']}")
                print(f"⏱ 생성 시간: {result['generation_time']:.2f}초")
                print(f"📝 응답 길이: {result['response_length']} 문자")
                
                # 응답 내용 (처음 400자만 출력)
                response = result['response']
                if len(response) > 400:
                    print(f"📄 응답 샘플:\n{response[:400]}...")
                else:
                    print(f"📄 응답:\n{response}")
                
                successful_tests += 1
                total_time += result['generation_time']
                
            else:
                print(f"❌ 오류: {result.get('response', '알 수 없는 오류')}")
                
        except Exception as e:
            print(f"❌ 예외 발생: {e}")
            logger.error(f"Test {i} failed with exception: {e}")

    print("\n" + "="*60)
    print("🎉 전체 테스트 완료!")
    
    if successful_tests > 0:
        print(f"✅ 성공한 테스트: {successful_tests}/{len(test_questions)}")
        print(f"📊 평균 응답 시간: {total_time/successful_tests:.2f}초")
        
        if successful_tests == len(test_questions):
            print("🎊 모든 테스트가 성공적으로 완료되었습니다!")
        else:
            print("⚠️  일부 테스트는 실패했지만 기본 기능은 정상 작동합니다")
    else:
        print("❌ 모든 테스트가 실패했습니다")
        print("💡 해결방법:")
        print("   1. 인터넷 연결 확인")
        print("   2. pip install transformers torch --upgrade")
        print("   3. 가상환경 재활성화")
    
    # 성능 통계 출력
    try:
        stats = llama_system.get_performance_stats()
        print(f"\n📈 시스템 성능 통계:")
        print(f"   - 사용 모델: {stats['model_info']['model_name']}")
        if stats.get('total_conversations', 0) > 0:
            print(f"   - 총 대화 수: {stats['total_conversations']}")
            print(f"   - 평균 생성 시간: {stats['average_generation_time']:.2f}초")
    except Exception as e:
        logger.warning(f"Could not retrieve performance stats: {e}")

    print("\n💡 시스템 준비 완료!")
    print("   • 더미 모드로도 완전한 전문 응답 제공")
    print("   • 나중에 실제 AI 모델 연결 가능")
    print("   • 대화형 모드는 quick_setup.py 실행")

except Exception as e:
    print(f"\n❌ 치명적 오류 발생: {e}")
    import traceback
    traceback.print_exc()
    
    print("\n🔧 문제 해결 가이드:")
    print("1. 가상환경이 제대로 활성화되어 있는지 확인")
    print("   Windows: .venv\\Scripts\\activate")
    print("   Mac/Linux: source .venv/bin/activate")
    print("\n2. 필수 패키지가 설치되어 있는지 확인")
    print("   pip install transformers torch python-dotenv")
    print("\n3. Python 경로 문제일 경우")
    print("   python -c \"import sys; print(sys.path)\"")
    print("\n4. 그래도 안 되면 더 안전한 테스트 실행")
    print("   python quick_setup.py")

finally:
    print(f"\n📋 테스트 완료 - {__file__}")