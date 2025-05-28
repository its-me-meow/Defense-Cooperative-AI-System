# quick_setup.py - 빠른 설치 및 테스트 스크립트

import subprocess
import sys
import os

def install_packages():
    """필요한 패키지 설치"""
    packages = [
        "torch",
        "transformers",
        "accelerate",
        "python-dotenv",
        "huggingface-hub"
    ]
    
    print("📦 필요한 패키지 설치 중...")
    for package in packages:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✅ {package} 설치 완료")
        except subprocess.CalledProcessError:
            print(f"❌ {package} 설치 실패")

def test_basic_functionality():
    """기본 기능 테스트"""
    print("\n🧪 기본 기능 테스트 시작")
    print("=" * 40)
    
    try:
        # 데이터 구조 테스트
        print("1. 지식베이스 테스트...")
        from src.data_structure import build_knowledge_base
        kb = build_knowledge_base()
        print(f"   ✅ 지식베이스 구축 성공 ({len(kb.countries)}개국)")
        
        # 프롬프트 엔지니어링 테스트
        print("2. 프롬프트 엔지니어링 테스트...")
        from src.prompt_engineering import create_comprehensive_prompt_system
        prompt_engineer = create_comprehensive_prompt_system(kb)
        print("   ✅ 프롬프트 시스템 생성 성공")
        
        # 간단한 프롬프트 생성 테스트
        test_prompt = prompt_engineer.generate_prompt("인도와의 협력 전략은?")
        print(f"   ✅ 프롬프트 생성 성공 ({len(test_prompt)} 문자)")
        
        # AI 시스템 테스트 (더미 모드)
        print("3. AI 시스템 테스트...")
        from src.llama_integration import DefenseCooperationLlama, ModelConfig
        
        config = ModelConfig(
            model_name="dummy_model",  # 더미 모드로 시작
            use_quantization=False
        )
        
        llama_system = DefenseCooperationLlama(config, kb, prompt_engineer)
        llama_system._setup_dummy_mode()  # 더미 모드 강제 설정
        
        # 테스트 응답 생성
        result = llama_system.generate_response("인도와의 미사일 기술 협력 전략은?")
        if "error" not in result:
            print("   ✅ AI 응답 생성 성공")
            print(f"   📝 응답 길이: {len(result['response'])} 문자")
        else:
            print(f"   ❌ AI 응답 생성 실패: {result['response']}")
        
        print("\n🎉 모든 기본 기능 테스트 통과!")
        return True
        
    except Exception as e:
        print(f"\n❌ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_interactive_demo():
    """대화형 데모 실행"""
    print("\n🤖 대화형 데모 시작")
    print("=" * 40)
    
    try:
        from src.data_structure import build_knowledge_base
        from src.prompt_engineering import create_comprehensive_prompt_system
        from src.llama_integration import DefenseCooperationLlama, ModelConfig
        
        # 시스템 초기화
        kb = build_knowledge_base()
        prompt_engineer = create_comprehensive_prompt_system(kb)
        
        config = ModelConfig(model_name="dummy_model")
        llama_system = DefenseCooperationLlama(config, kb, prompt_engineer)
        llama_system._setup_dummy_mode()
        
        print("✅ 시스템 준비 완료!")
        print("\n💡 추천 질문:")
        print("  - 인도와의 미사일 기술 협력 전략은?")
        print("  - UAE 투자 규모는?")
        print("  - 브라질과 항공우주 협력이 가능한가요?")
        print("\n질문을 입력하세요 ('종료'로 끝내기):")
        
        while True:
            user_input = input("\n👤 질문: ").strip()
            
            if user_input.lower() in ['종료', 'quit', 'exit', '']:
                print("👋 데모를 종료합니다!")
                break
                
            if not user_input:
                continue
                
            print("🤖 AI: ", end="")
            result = llama_system.generate_response(user_input)
            
            if "error" not in result:
                print(result['response'])
                print(f"⏱ 생성 시간: {result['generation_time']:.2f}초")
            else:
                print(f"오류: {result['response']}")
        
    except Exception as e:
        print(f"❌ 데모 실행 오류: {e}")

def main():
    """메인 실행 함수"""
    print("🚀 방산 협력 AI 시스템 빠른 설정")
    print("=" * 50)
    
    # 사용자 선택
    print("다음 중 선택하세요:")
    print("1. 패키지 설치 및 기본 테스트")
    print("2. 기본 테스트만 실행")
    print("3. 대화형 데모 실행")
    print("4. 전체 실행 (설치 → 테스트 → 데모)")
    
    choice = input("\n선택 (1-4): ").strip()
    
    if choice == "1":
        install_packages()
        if test_basic_functionality():
            print("\n✅ 설치 및 테스트 완료!")
    elif choice == "2":
        if test_basic_functionality():
            print("\n✅ 테스트 완료!")
    elif choice == "3":
        run_interactive_demo()
    elif choice == "4":
        install_packages()
        if test_basic_functionality():
            print("\n계속하려면 Enter를 누르세요...")
            input()
            run_interactive_demo()
    else:
        print("❌ 잘못된 선택입니다.")

if __name__ == "__main__":
    main()