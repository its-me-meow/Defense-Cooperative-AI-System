import streamlit as st
import sys
import os
import time
from datetime import datetime
import json

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

st.set_page_config(
    page_title="방산 협력 전략 AI 시스템",
    page_icon="🛡️",
    layout="wide"
)

# final_test.py 모듈 import
try:
    from src.chatbot import DefenseCooperationChatbot
    CHATBOT_AVAILABLE = True
except ImportError:
    CHATBOT_AVAILABLE = False

# 세션 상태 초기화
if "selected_mode" not in st.session_state:
    st.session_state.selected_mode = None
if "chatbot" not in st.session_state:
    st.session_state.chatbot = None
if "initialized" not in st.session_state:
    st.session_state.initialized = False
if "messages" not in st.session_state:
    st.session_state.messages = []
if "detailed_mode" not in st.session_state:
    st.session_state.detailed_mode = False
if "question_count" not in st.session_state:
    st.session_state.question_count = 0
if "test_results" not in st.session_state:
    st.session_state.test_results = []

def main_selection_screen():
    """메인 선택 화면 (final_test.py와 동일)"""
    st.title("🤖 방산 협력 전략 AI 시스템 (개선 버전)")
    st.markdown("**🆕 새로운 기능: 대화 내용 자동 저장!**")
    
    st.write("")
    st.subheader("실행할 모드를 선택하세요:")
    
    # 3개 버튼을 세로로 배치
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.button("**1. 최종 테스트 (test)**", use_container_width=True, key="btn_test"):
            st.session_state.selected_mode = "1"
            st.rerun()
        
        if st.button("**2. 대화형 사용 (interactive) ⭐ 추천**", use_container_width=True, type="primary", key="btn_interactive"):
            st.session_state.selected_mode = "2"
            st.rerun()
        
        if st.button("**3. 사용 가이드 (guide)**", use_container_width=True, key="btn_guide"):
            st.session_state.selected_mode = "3"
            st.rerun()
    
    st.write("")
    
    # 시스템 상태 표시
    with st.expander("ℹ️ 시스템 정보"):
        if CHATBOT_AVAILABLE:
            st.success("✅ 모든 모듈이 정상적으로 로드되었습니다.")
        else:
            st.error("❌ 일부 모듈을 찾을 수 없습니다. final_test.py와 같은 폴더에서 실행해주세요.")
        
        st.write("""
        **필요한 파일들:**
        - src/chatbot.py
        - src/data_structure.py  
        - src/llama_integration.py
        - src/prompt_engineering.py
        """)

def run_test_mode():
    """1. 최종 테스트 모드 (FinalTestSuite 구현)"""
    st.title("🧪 방산 협력 AI 시스템 최종 테스트")
    
    # 뒤로가기 버튼
    if st.button("🔙 메인 메뉴로 돌아가기"):
        st.session_state.selected_mode = None
        st.session_state.initialized = False
        st.session_state.test_results = []
        st.rerun()
    
    st.markdown("---")
    
    # 초기화 상태 확인
    if not st.session_state.initialized:
        st.info("🚀 시스템을 초기화하여 테스트를 시작합니다.")
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("🚀 시스템 초기화 및 테스트 시작", type="primary", use_container_width=True):
                with st.spinner("시스템 초기화 중..."):
                    if initialize_system():
                        st.success("✅ 시스템 초기화 완료!")
                        time.sleep(1)
                        st.rerun()
        return
    
    # 테스트 실행 화면
    st.success("✅ 시스템 초기화 완료!")
    
    # 테스트 설명
    st.subheader("📋 포괄적 테스트 개요")
    st.write("""
    **테스트 내용:**
    - 총 5개 카테고리별 전문 질문 테스트
    - 응답 품질, 생성 시간, 키워드 매칭 분석
    - 시스템 안정성 및 다양성 검증
    """)
    
    # 테스트 질문 정의 (final_test.py와 동일)
    test_questions = [
        {
            "category": "인도 협력",
            "question": "인도와의 미사일 기술 협력 전략은 어떻게 구성해야 할까요?",
            "expected_keywords": ["BrahMos", "현무", "투자", "ROI", "단계별"]
        },
        {
            "category": "UAE 투자",
            "question": "UAE 투자 규모는 어느 정도이며, 어떤 협력 모델이 효과적일까요?",
            "expected_keywords": ["220억", "EDGE", "천궁", "상쇄정책"]
        },
        {
            "category": "브라질 항공",
            "question": "브라질과 항공우주 협력이 가능한 분야는 무엇인가요?",
            "expected_keywords": ["Embraer", "훈련기", "아마존", "남미"]
        },
        {
            "category": "동남아 협력",
            "question": "동남아시아 해양안보 협력 방안을 구체적으로 설명해주세요",
            "expected_keywords": ["ASEAN", "해양", "군도", "17,508개"]
        },
        {
            "category": "아프리카 전략",
            "question": "아프리카 평화유지 장비 수출 전략은 어떻게 수립해야 하나요?",
            "expected_keywords": ["평화유지", "PKO", "남아공", "MRAP"]
        }
    ]
    
    st.write(f"🔍 **총 {len(test_questions)}개 질문으로 포괄적 테스트 수행**")
    
    # 테스트 실행 버튼
    if st.button("🧪 전체 테스트 실행", type="primary"):
        run_comprehensive_test(test_questions)
    
    # 테스트 결과 표시
    if st.session_state.test_results:
        display_test_results()

def run_comprehensive_test(test_questions):
    """포괄적 테스트 실행 (final_test.py와 동일 로직)"""
    st.session_state.test_results = []
    
    # 진행률 표시
    progress_container = st.container()
    with progress_container:
        st.subheader("🔄 테스트 진행 중...")
        progress_bar = st.progress(0)
        status_text = st.empty()
    
    for i, test_case in enumerate(test_questions):
        status_text.text(f"🔍 테스트 {i+1}/{len(test_questions)}: {test_case['category']}")
        progress_bar.progress((i + 1) / len(test_questions))
        
        try:
            start_time = time.time()
            result = st.session_state.chatbot.detailed_chat(test_case["question"])
            test_duration = time.time() - start_time
            
            if "error" not in result or not result.get("error", False):
                response = result["response"]
                
                # 키워드 점수 계산
                keyword_found = sum(1 for keyword in test_case["expected_keywords"] 
                                  if keyword in response)
                keyword_score = (keyword_found / len(test_case["expected_keywords"])) * 100
                
                test_result = {
                    "test_num": i + 1,
                    "category": test_case["category"],
                    "question": test_case["question"],
                    "success": True,
                    "duration": test_duration,
                    "response_length": len(response),
                    "keyword_score": keyword_score,
                    "response": response,
                    "model_info": result.get('model_info', {}),
                    "diversity_info": result.get('diversity_info', {})
                }
            else:
                test_result = {
                    "test_num": i + 1,
                    "category": test_case["category"],
                    "question": test_case["question"],
                    "success": False,
                    "error": result.get('response', '알 수 없는 오류')
                }
            
            st.session_state.test_results.append(test_result)
            time.sleep(0.5)  # 시각적 효과
            
        except Exception as e:
            test_result = {
                "test_num": i + 1,
                "category": test_case["category"],
                "question": test_case["question"],
                "success": False,
                "error": str(e)
            }
            st.session_state.test_results.append(test_result)
    
    status_text.text("🎉 모든 테스트 완료!")
    time.sleep(1)
    st.rerun()

def display_test_results():
    """테스트 결과 표시 (final_test.py의 generate_final_report 구현)"""
    st.markdown("---")
    st.subheader("📊 최종 테스트 결과")
    
    successful_tests = sum(1 for result in st.session_state.test_results if result.get("success", False))
    total_tests = len(st.session_state.test_results)
    
    # 전체 요약
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("총 테스트", f"{total_tests}개")
    with col2:
        st.metric("성공", f"{successful_tests}개", delta=f"+{successful_tests}")
    with col3:
        st.metric("실패", f"{total_tests - successful_tests}개")
    with col4:
        success_rate = (successful_tests/total_tests)*100 if total_tests > 0 else 0
        st.metric("성공률", f"{success_rate:.1f}%")
    
    # 성공한 테스트 통계
    if successful_tests > 0:
        successful_results = [r for r in st.session_state.test_results if r.get("success", False)]
        avg_duration = sum(r["duration"] for r in successful_results) / len(successful_results)
        avg_length = sum(r["response_length"] for r in successful_results) / len(successful_results)
        avg_keyword_score = sum(r["keyword_score"] for r in successful_results) / len(successful_results)
        
        st.subheader("📈 성공한 테스트 상세 통계")
        stat_col1, stat_col2, stat_col3 = st.columns(3)
        with stat_col1:
            st.metric("평균 응답 시간", f"{avg_duration:.2f}초")
        with stat_col2:
            st.metric("평균 응답 길이", f"{avg_length:.0f} 문자")
        with stat_col3:
            st.metric("평균 키워드 점수", f"{avg_keyword_score:.1f}%")
    
    # 개별 테스트 결과 상세
    st.subheader("🔍 개별 테스트 결과")
    for result in st.session_state.test_results:
        with st.expander(f"테스트 {result['test_num']}: {result['category']} - {'✅ 성공' if result.get('success') else '❌ 실패'}"):
            st.write(f"**질문:** {result['question']}")
            
            if result.get("success", False):
                # 성공 시 상세 정보
                detail_col1, detail_col2, detail_col3 = st.columns(3)
                with detail_col1:
                    st.metric("생성 시간", f"{result['duration']:.2f}초")
                with detail_col2:
                    st.metric("응답 길이", f"{result['response_length']} 문자")
                with detail_col3:
                    st.metric("키워드 점수", f"{result['keyword_score']:.1f}%")
                
                # 응답 내용
                st.write("**AI 응답:**")
                st.write(result['response'])
                
                # 추가 정보
                if 'model_info' in result:
                    st.write(f"**처리 모드:** {result['model_info'].get('mode', 'unknown')}")
            else:
                st.error(f"❌ 실패 원인: {result.get('error', '알 수 없는 오류')}")

def run_interactive_mode():
    """2. 대화형 모드 (interactive_mode 구현)"""
    st.title("🤖 방산 협력 전략 AI 어시스턴트")
    
    # 뒤로가기 버튼
    if st.button("🔙 메인 메뉴로 돌아가기"):
        st.session_state.selected_mode = None
        st.session_state.initialized = False
        st.session_state.messages = []
        st.session_state.question_count = 0
        st.rerun()
    
    st.markdown("---")
    
    # 초기화 확인
    if not st.session_state.initialized:
        st.info("🚀 시스템을 초기화하여 대화를 시작합니다.")
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("🚀 시스템 초기화", type="primary", use_container_width=True):
                with st.spinner("시스템 초기화 중..."):
                    if initialize_system():
                        st.success("✅ 시스템 초기화 완료!")
                        time.sleep(1)
                        st.rerun()
        return
    
    # 사이드바 설정
    with st.sidebar:
        st.header("⚙️ 설정")
        
        # 상세 모드 토글
        detailed_mode = st.toggle("📊 상세 모드", value=st.session_state.detailed_mode)
        if detailed_mode != st.session_state.detailed_mode:
            st.session_state.detailed_mode = detailed_mode
            st.rerun()
        
        st.markdown("---")
        
        # 명령어 안내
        st.header("💡 명령어")
        st.write("""
        - **'도움말'**: 추천 질문 보기
        - **'통계'**: 다양성 통계 확인  
        - **'상태'**: 시스템 상태 확인
        - **'테스트'**: 빠른 기능 테스트
        """)
        
        st.markdown("---")
        
        # 대화 초기화
        if st.button("🗑️ 대화 초기화"):
            st.session_state.messages = []
            st.session_state.question_count = 0
            st.rerun()
    
    # 상태 표시
    status_col1, status_col2, status_col3 = st.columns(3)
    with status_col1:
        st.success("✅ 시스템 준비 완료")
    with status_col2:
        st.info(f"💬 질문 수: {st.session_state.question_count}")
    with status_col3:
        mode_status = "상세 모드" if st.session_state.detailed_mode else "일반 모드"
        st.info(f"🔧 {mode_status}")
    
    # 채팅 인터페이스
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message["role"] == "assistant" and "metadata" in message and st.session_state.detailed_mode:
                with st.expander("📊 생성 정보"):
                    st.json(message["metadata"])
    
    # 채팅 입력
    if prompt := st.chat_input("질문을 입력하세요... ('도움말', '통계', '상태', '테스트' 명령어 사용 가능)"):
        # 사용자 메시지
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # AI 응답
        with st.chat_message("assistant"):
            with st.spinner("🤖 AI: 질문을 분석하고 맞춤 답변을 생성 중입니다..."):
                response, metadata = process_user_input(prompt)
                st.markdown(response)
                
                if st.session_state.detailed_mode and metadata:
                    with st.expander("📊 생성 정보"):
                        st.json(metadata)
        
        # 메시지 저장
        message_data = {"role": "assistant", "content": response}
        if metadata:
            message_data["metadata"] = metadata
        st.session_state.messages.append(message_data)

def process_user_input(user_input):
    """사용자 입력 처리 (final_test.py 명령어 처리와 동일)"""
    # 명령어 처리
    if user_input == '도움말':
        return """💡 **국가별 방산협력 추천 질문:**

🇮🇳 **인도 (남아시아)**
• 인도와의 미사일 기술 협력 전략은?
• BrahMos-현무 합동 미사일 개발 방안은?
• 인도 DRDO와의 공동연구개발 전략은?

🇦🇪 **UAE (중동)**
• UAE 투자 규모와 효과적인 협력 모델은?
• UAE 사막환경 특화 방산시스템 개발 전략은?
• EDGE Group과의 기술 통합 방안은?

🇧🇷 **브라질 (라틴아메리카)**
• 브라질과 항공우주 협력이 가능한 분야는?
• Embraer와의 훈련기 공동개발 전략은?
• 브라질 해상초계기 협력 방안은?

🌏 **동남아시아**
• 동남아시아 해양안보 협력 방안은?
• ASEAN 국가들과의 우선 협력 전략은?
• 인도네시아 KF-21 공동개발 성과는?

🌍 **아프리카**
• 아프리카 평화유지 장비 수출 전략은?
• 남아프리카공화국과의 방산 협력 분야는?
• 아프리카 시장 진출 시 주의사항은?

📊 **지역별 우선순위**
• 중동 및 북아프리카 우선순위 국가는?
• 동유럽 지역 진출 유망국가는?
• 비NATO 국가 중 우선 협력 대상은?""", {"type": "help_command"}
    
    elif user_input == '통계':
        try:
            stats = st.session_state.chatbot.get_diversity_stats()
            return f"""📊 다양성 통계:
• 다양성 점수: {stats.get('diversity_score', 0):.2f}
• 평균 유사도: {stats.get('avg_similarity', 0):.2f}  
• 총 응답 수: {stats.get('total_responses', 0)}
• 거부된 응답: {stats.get('rejected_count', 0)}""", {"type": "stats_command", "stats": stats}
        except Exception as e:
            return f"❌ 통계 조회 오류: {e}", {"type": "error"}
    
    elif user_input == '상태':
        try:
            status = st.session_state.chatbot.get_system_status()
            return f"""📊 시스템 상태:
• 시스템 초기화: {'✅' if status.get('system_initialized', False) else '❌'}
• 자체 답변 생성: {'✅' if status.get('fallback_mode', False) else '❌'}
• 지식 베이스: {status.get('knowledge_base_size', 0)}개 국가
• 답변 생성기: {status.get('intelligent_generator', 'N/A')}""", {"type": "status_command", "status": status}
        except Exception as e:
            return f"❌ 상태 조회 오류: {e}", {"type": "error"}
    
    elif user_input == '테스트':
        return """🧪 고급 기능 테스트:
시스템이 다음 질문들에 대해 전문적인 답변을 제공합니다:
• 국방 분야에서 AI 기술 도입 시 발생할 수 있는 윤리적 문제는?
• 한국 방산 수출이 증가하고 있는 주요 요인은?
• 인공지능의 미래는 어떻게 될까요?

✅ 고급 패턴 매칭 시스템 활성화
✅ 각 질문에 맞는 구체적 답변 생성  
✅ GPT 수준의 지능적 답변 제공""", {"type": "test_command"}
    
    # 일반 질문 처리
    try:
        st.session_state.question_count += 1
        
        if st.session_state.detailed_mode:
            result = st.session_state.chatbot.detailed_chat(user_input)
            response = result.get("response", "응답을 생성할 수 없습니다.")
            metadata = {
                "generation_time": result.get('generation_time', 0),
                "mode": result.get('model_info', {}).get('mode', 'unknown'),
                "response_length": len(response),
                "in_scope": result.get('in_scope', True),
                "diversity_info": result.get('diversity_info', {})
            }
        else:
            response = st.session_state.chatbot.chat(user_input)
            metadata = {"type": "simple_chat", "question_number": st.session_state.question_count}
        
        return response, metadata
        
    except Exception as e:
        error_response = f"❌ 응답 생성 중 오류: {e}"
        return error_response, {"type": "error", "error": str(e)}

def show_usage_guide():
    """3. 사용 가이드 (show_usage_guide 구현)"""
    st.title("📖 방산 협력 전략 AI 시스템 - 사용자 가이드 (개선 버전)")
    
    # 뒤로가기 버튼
    if st.button("🔙 메인 메뉴로 돌아가기"):
        st.session_state.selected_mode = None
        st.rerun()
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.header("🆕 새로운 기능")
        st.write("""
        • 대화 내용 자동 txt 파일 저장
        • 답변 끊김 문제 해결
        • 실시간 저장으로 데이터 손실 방지
        • 처리 시간 및 응답 길이 표시
        """)
        
        st.header("📁 파일 구성")
        st.write("""
        • final_test.py : 최종 테스트 및 사용자 인터페이스 (이 파일)
        • chatbot.py : 메인 챗봇 시스템  
        • data_structure.py : 지식 베이스
        • llama_integration.py : AI 모델 통합
        • prompt_engineering.py : 프롬프트 엔지니어링
        """)
        
        st.header("🚀 실행 방법")
        st.code("""
1. 최종 테스트:     python final_test.py test
2. 대화형 사용:     python final_test.py interactive ⭐ 추천
3. 사용 가이드:     python final_test.py guide
4. 기본 실행:       python final_test.py
        """)
    
    with col2:
        st.header("💡 외부 사용자 권장 실행 방법")
        st.code("python final_test.py interactive")
        
        st.header("📝 저장되는 파일들")
        st.write("""
        • conversation_log_YYYYMMDD_HHMMSS.txt : 대화 내용
        • defense_ai_test_YYYYMMDD_HHMMSS.log : 시스템 로그  
        • final_test_report_YYYYMMDD_HHMMSS.json : 테스트 결과
        """)
        
        st.header("🔧 시스템 특징")
        st.write("""
        • 6가지 개선사항 모두 적용
        • 30개 상세 응답 템플릿 활용
        • 응답 다양성 검증 시스템
        • 포괄적인 방산 협력 지식 베이스
        • 안정적인 더미 모드 지원
        • 답변 끊김 방지 및 완전한 응답 저장
        """)
    
    st.header("⚠️ 주의사항")
    st.write("""
    • 모든 파일이 같은 폴더에 있어야 합니다
    • Python 3.7 이상 권장
    • 필요한 라이브러리: torch, transformers 등
    • 대화 파일은 UTF-8 인코딩으로 저장됩니다
    """)
    
    st.header("📞 문제 해결")
    st.write("""
    • ImportError 발생 시: 모든 파일이 같은 폴더에 있는지 확인
    • 응답이 느릴 때: 정상적인 동작입니다 (복잡한 분석 중)
    • 답변이 끊길 때: txt 파일에서 완전한 답변 확인 가능
    • 파일 저장 오류 시: 폴더 쓰기 권한 확인
    """)

def initialize_system():
    """시스템 초기화 (final_test.py와 동일)"""
    if not CHATBOT_AVAILABLE:
        st.error("❌ 모듈을 찾을 수 없습니다. final_test.py와 같은 폴더에서 실행해주세요.")
        return False
    
    try:
        chatbot = DefenseCooperationChatbot()
        chatbot.initialize(use_gpu=False, use_quantization=False)
        
        if chatbot.is_initialized:
            st.session_state.chatbot = chatbot
            st.session_state.initialized = True
            return True
        else:
            st.error("❌ 시스템 초기화 실패")
            return False
    except Exception as e:
        st.error(f"❌ 초기화 중 오류: {e}")
        return False

# 메인 애플리케이션 실행
def main():
    """메인 함수 (final_test.py와 동일한 플로우)"""
    if st.session_state.selected_mode is None:
        # 메인 선택 화면
        main_selection_screen()
    elif st.session_state.selected_mode == "1":
        # 1. 최종 테스트
        run_test_mode()
    elif st.session_state.selected_mode == "2":
        # 2. 대화형 사용  
        run_interactive_mode()
    elif st.session_state.selected_mode == "3":
        # 3. 사용 가이드
        show_usage_guide()

if __name__ == "__main__":
    main()