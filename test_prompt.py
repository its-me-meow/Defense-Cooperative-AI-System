from src.data_structure import build_knowledge_base
from src.prompt_engineering import create_comprehensive_prompt_system

print("=== 프롬프트 시스템 테스트 ===")

try:
    kb = build_knowledge_base()
    prompt_engineer = create_comprehensive_prompt_system(kb)
    
    test_query = "인도와의 미사일 기술 협력 전략은?"
    prompt = prompt_engineer.generate_prompt(test_query)
    
    print("✅ 프롬프트 생성 성공!")
    print("프롬프트 길이:", len(prompt), "문자")
    print("\n--- 생성된 프롬프트 일부 ---")
    print(prompt[:500] + "...")
    
except Exception as e:
    print(f"❌ 오류 발생: {e}")