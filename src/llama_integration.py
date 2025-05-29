import streamlit as st
import sys
import os
from dotenv import load_dotenv
import time
import logging

# 환경 변수 로드
load_dotenv()

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def initialize_custom_system():
    """자체 방산 협력 AI 시스템 초기화"""
    try:
        from src.chatbot import DefenseCooperationChatbot
        
        if 'custom_chatbot' not in st.session_state:
            with st.spinner('🚀 방산 협력 AI 시스템 초기화 중...'):
                chatbot = DefenseCooperationChatbot()
                chatbot.initialize(use_gpu=False, use_quantization=False)
                
                if chatbot.is_initialized:
                    st.session_state.custom_chatbot = chatbot
                    st.success('✅ 시스템 초기화 완료!')
                    return True
                else:
                    st.error('❌ 시스템 초기화 실패')
                    return False
        return True
        
    except ImportError as e:
        st.error(f"❌ 모듈 import 오류: {e}")
        st.error("src 폴더의 모든 파일이 올바른 위치에 있는지 확인하세요.")
        return False
    except Exception as e:
        st.error(f"❌ 시스템 초기화 오류: {e}")
        return False

def initialize_openai_system(api_key):
    """OpenAI 시스템 초기화"""
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        st.session_state.openai_client = client
        return True
    except Exception as e:
        st.error(f"❌ OpenAI 클라이언트 초기화 실패: {e}")
        return False

def get_custom_response(user_input):
    """자체 시스템 응답 생성"""
    try:
        chatbot = st.session_state.custom_chatbot
        result = chatbot.detailed_chat(user_input)
        
        if isinstance(result, dict) and "response" in result:
            return {
                "response": result["response"],
                "generation_time": result.get("generation_time", 0),
                "mode": result.get("model_info", {}).get("mode", "unknown"),
                "response_length": result.get("response_length", 0)
            }
        else:
            return {"response": str(result), "generation_time": 0}
            
    except Exception as e:
        logger.error(f"Custom response error: {e}")
        return {"response": f"응답 생성 중 오류가 발생했습니다: {str(e)}", "generation_time": 0}

def get_openai_response(messages, model="gpt-3.5-turbo"):
    """OpenAI 응답 생성"""
    try:
        client = st.session_state.openai_client
        
        # 방산 협력 전문가 시스템 프롬프트 추가
        system_message = {
            "role": "system", 
            "content": """당신은 대한민국 방산기술 수출 확대를 위한 국가별 협력 전략 전문가입니다.
            
주요 전문 분야:
- 비NATO 국가(인도, UAE, 브라질, 동남아시아 등)와의 방산 협력 전략
- 국가별 국방 능력 및 기술 역량 분석  
- 방산 수출 시장 분석 및 투자 수익성 평가
- 단계별 협력 로드맵 및 정책 제언

응답 원칙:
1. 구체적 수치와 데이터 기반 분석 제공
2. 실행 가능한 전략과 단계별 방안 제시
3. 기회와 리스크를 균형있게 평가
4. 장기적 관점에서 국가 이익 고려"""
        }
        
        # 시스템 메시지를 포함한 전체 대화
        full_messages = [system_message] + messages
        
        response = client.chat.completions.create(
            model=model,
            messages=full_messages,
            temperature=0.7,
            max_tokens=2000
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        logger.error(f"OpenAI response error: {e}")
        return f"OpenAI 응답 생성 중 오류가 발생했습니다: {str(e)}"

# Streamlit 페이지 설정
st.set_page_config(
    page_title="한국 방산 협력 전략 AI 챗봇",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 사이드바 설정
with st.sidebar:
    st.title("⚙️ 시스템 설정")
    
    # AI 시스템 선택
    ai_system = st.radio(
        "AI 시스템 선택:",
        ["자체 방산 협력 AI", "OpenAI GPT-3.5"],
        help="자체 시스템: 방산 협력 전문 지식베이스 활용\nOpenAI: 범용 AI 모델 사용"
    )
    
    st.divider()
    
    # API 키 설정
    if ai_system == "OpenAI GPT-3.5":
        # .env 파일에서 먼저 확인
        env_openai_key = os.getenv('OPENAI_API_KEY')
        
        if env_openai_key:
            st.success("✅ .env 파일에서 OpenAI API 키 감지됨")
            openai_api_key = env_openai_key
        else:
            openai_api_key = st.text_input(
                "OpenAI API Key:", 
                type="password",
                help="OpenAI API 키를 입력하세요 (또는 .env 파일에 OPENAI_API_KEY로 저장)"
            )
        
        if openai_api_key:
            if initialize_openai_system(openai_api_key):
                st.success("✅ OpenAI 연결 완료")
            system_ready = bool(openai_api_key)
        else:
            st.info("OpenAI API 키를 입력하거나 .env 파일에 설정하세요")
            system_ready = False
    
    else:
        # 자체 시스템 사용
        huggingface_token = os.getenv('HUGGINGFACE_TOKEN')
        if huggingface_token:
            st.success("✅ HuggingFace 토큰 감지됨")
        else:
            st.warning("⚠️ .env 파일에 HUGGINGFACE_TOKEN이 없습니다")
        
        system_ready = initialize_custom_system()
    
    st.divider()
    
    # 시스템 정보
    st.subheader("💡 사용 가이드")
    if ai_system == "자체 방산 협력 AI":
        st.write("""
        **전문 질문 예시:**
        - 인도와의 미사일 기술 협력 전략은?
        - UAE 투자 규모는 어느 정도인가요?
        - 브라질과 항공우주 협력이 가능한가요?
        - 동남아시아 해양안보 협력 방안은?
        """)
    else:
        st.write("""
        **OpenAI GPT-3.5 사용:**
        - 방산 협력 전문 시스템 프롬프트 적용
        - 범용 지식 기반 응답 생성
        - 실시간 인터넷 정보 접근 불가
        """)

# 메인 페이지
st.title("🛡️ 한국 방산 협력 전략 AI 챗봇")
st.markdown("""
**대한민국 방산기술 수출 확대를 위한 전문 AI 어시스턴트**

이 챗봇은 비NATO 국가들과의 방산 협력 전략, 시장 분석, 투자 수익성 평가 등에 대한 
전문적인 분석과 제언을 제공합니다.
""")

# 시스템 상태 표시
if system_ready:
    if ai_system == "자체 방산 협력 AI":
        st.success("🚀 자체 방산 협력 AI 시스템 준비 완료")
    else:
        st.success("🤖 OpenAI GPT-3.5 시스템 준비 완료")
else:
    st.error("❌ 시스템이 준비되지 않았습니다. 사이드바에서 설정을 확인하세요.")
    st.stop()

# 채팅 기록 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

# 이전 대화 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
        # 자체 시스템의 경우 추가 정보 표시
        if message["role"] == "assistant" and "metadata" in message:
            metadata = message["metadata"]
            with st.expander("📊 응답 상세 정보"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("생성 시간", f"{metadata.get('generation_time', 0):.2f}초")
                with col2:
                    st.metric("응답 길이", f"{metadata.get('response_length', 0)} 문자")
                with col3:
                    st.metric("모드", metadata.get('mode', 'unknown'))

# 채팅 입력
if prompt := st.chat_input("방산 협력 전략에 대해 질문하세요..."):
    # 사용자 메시지 저장 및 표시
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # AI 응답 생성 및 표시
    with st.chat_message("assistant"):
        with st.spinner("🤔 분석 중..."):
            start_time = time.time()
            
            if ai_system == "자체 방산 협력 AI":
                # 자체 시스템 사용
                result = get_custom_response(prompt)
                response = result["response"]
                
                # 응답 표시
                st.markdown(response)
                
                # 메타데이터 표시
                generation_time = time.time() - start_time
                with st.expander("📊 응답 상세 정보"):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("생성 시간", f"{generation_time:.2f}초")
                    with col2:
                        st.metric("응답 길이", f"{len(response)} 문자")
                    with col3:
                        st.metric("모드", result.get('mode', 'enhanced_dummy'))
                
                # 메시지 저장
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": response,
                    "metadata": {
                        "generation_time": generation_time,
                        "response_length": len(response),
                        "mode": result.get('mode', 'enhanced_dummy')
                    }
                })
                
            else:
                # OpenAI 사용
                messages_for_api = [
                    {"role": m["role"], "content": m["content"]} 
                    for m in st.session_state.messages[:-1]  # 마지막 사용자 메시지 제외
                ]
                messages_for_api.append({"role": "user", "content": prompt})
                
                response = get_openai_response(messages_for_api)
                
                # 응답 표시
                st.markdown(response)
                
                # 메타데이터 표시
                generation_time = time.time() - start_time
                with st.expander("📊 응답 상세 정보"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("생성 시간", f"{generation_time:.2f}초")
                    with col2:
                        st.metric("응답 길이", f"{len(response)} 문자")
                
                # 메시지 저장
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": response,
                    "metadata": {
                        "generation_time": generation_time,
                        "response_length": len(response),
                        "mode": "openai_gpt35"
                    }
                })

# 하단 정보
st.divider()
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🔄 대화 초기화"):
        st.session_state.messages = []
        st.rerun()

with col2:
    if ai_system == "자체 방산 협력 AI" and 'custom_chatbot' in st.session_state:
        try:
            stats = st.session_state.custom_chatbot.get_diversity_stats()
            st.metric("다양성 점수", f"{stats.get('diversity_score', 0):.2f}")
        except:
            pass

with col3:
    st.metric("총 대화 수", len([m for m in st.session_state.messages if m["role"] == "user"]))

# 푸터
st.markdown("""
---
**🛡️ 한국 방산 협력 전략 AI 챗봇** | 
방산 기술 수출 확대를 위한 전문 AI 어시스턴트 | 
Made with Streamlit & 🇰🇷
""")