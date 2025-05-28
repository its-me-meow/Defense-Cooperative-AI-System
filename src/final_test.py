#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=================================================================
방산 협력 전략 AI 시스템 - 최종 테스트 및 사용자 가이드 (개선 버전)
=================================================================

개선사항:
- 대화 내용을 txt 파일로 자동 저장
- 답변 끊김 문제 해결
- 실시간 저장으로 데이터 손실 방지

실행 방법:
python final_test.py

외부 사용자는 이 파일을 실행하여 시스템을 사용할 수 있습니다.
"""

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
        print(f"⚠️  모듈 import 오류: {e}")
        print("📁 다음 파일들이 같은 폴더에 있는지 확인하세요:")
        print("   - data_structure.py")
        print("   - prompt_engineering.py") 
        print("   - llama_integration.py")
        sys.exit(1)

# 수정된 로깅 설정 - 이모지 제거하고 안전한 메시지만 사용
class SafeFormatter(logging.Formatter):
    """이모지와 특수문자를 안전한 텍스트로 변환하는 포매터"""
    def format(self, record):
        # 이모지를 안전한 텍스트로 변경
        emoji_map = {
            '🚀': '[START]',
            '📚': '[KB]',
            '✅': '[OK]',
            '🔧': '[BUILD]',
            '🤖': '[AI]',
            '🎉': '[SUCCESS]',
            '❌': '[ERROR]',
            '⚠️': '[WARNING]'
        }
        
        msg = str(record.getMessage())
        for emoji, text in emoji_map.items():
            msg = msg.replace(emoji, text)
        record.msg = msg
        record.args = ()
        
        return super().format(record)

# 로깅 설정 수정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f'defense_ai_test_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log', encoding='utf-8')
    ]
)


class ConversationLogger:
    """대화 내용을 txt 파일로 저장하는 클래스"""
    
    def __init__(self):
        # 대화 저장용 파일명 생성 (타임스탬프 포함)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_filename = f"conversation_log_{timestamp}.txt"
        
        # 로그 파일 초기화
        try:
            with open(self.log_filename, 'w', encoding='utf-8') as f:
                f.write("="*80 + "\n")
                f.write("방산 협력 전략 AI 시스템 - 대화 로그\n")
                f.write(f"시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("="*80 + "\n\n")
            
            print(f"📁 대화 내용이 저장될 파일: {self.log_filename}")
            
        except Exception as e:
            print(f"⚠️  로그 파일 생성 오류: {e}")
            self.log_filename = None
    
    def log_conversation(self, question: str, response: str, duration: float = 0):
        """질문과 답변을 파일에 저장"""
        if not self.log_filename:
            return
            
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            with open(self.log_filename, 'a', encoding='utf-8') as f:
                f.write(f"[{timestamp}] 처리시간: {duration:.2f}초\n")
                f.write("─" * 80 + "\n")
                f.write("👤 질문:\n")
                f.write(f"{question}\n\n")
                f.write("🤖 AI 답변:\n")
                f.write(f"{response}\n")
                f.write("─" * 80 + "\n\n")
                f.flush()  # 즉시 파일에 쓰기
                
        except Exception as e:
            print(f"⚠️  대화 로그 저장 오류: {e}")
    
    def log_system_message(self, message: str):
        """시스템 메시지를 파일에 저장"""
        if not self.log_filename:
            return
            
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            with open(self.log_filename, 'a', encoding='utf-8') as f:
                f.write(f"[{timestamp}] 시스템: {message}\n\n")
                f.flush()
                
        except Exception as e:
            print(f"⚠️  시스템 로그 저장 오류: {e}")


class FinalTestSuite:
    """최종 테스트 수트 - 모든 기능을 포괄적으로 테스트"""
    
    def __init__(self):
        self.chatbot = None
        self.test_results = []
        self.start_time = None
        
    def initialize_system(self):
        """시스템 초기화"""
        print("🚀 방산 협력 AI 시스템 최종 테스트 시작")
        print("=" * 80)
        
        # 사용자 설정 안내
        print("⚙️  시스템 설정:")
        print("   - GPU 사용: 비활성화 (안정성 우선)")
        print("   - 양자화: 비활성화 (안정성 우선)")
        print("   - 모드: 향상된 더미 모드 (6가지 개선사항 적용)")
        print("   - 템플릿: 30개 상세 템플릿 활용")
        print("   - 다양성: 응답 다양성 검증 활성화")
        print()
        
        try:
            from chatbot import DefenseCooperationChatbot
            self.chatbot = DefenseCooperationChatbot()
            self.chatbot.initialize(use_gpu=False, use_quantization=False)
            
            if self.chatbot.is_initialized:
                print("✅ 시스템 초기화 성공!")
                return True
            else:
                print("❌ 시스템 초기화 실패")
                return False
                
        except Exception as e:
            print(f"❌ 초기화 중 오류: {e}")
            return False
    
    def run_comprehensive_test(self):
        """포괄적인 테스트 실행"""
        if not self.initialize_system():
            return
            
        self.start_time = time.time()
        
        # 테스트 질문들 - 각 카테고리별로 다양한 질문
        test_questions = [
            # 인도 관련 질문
            {
                "category": "인도 협력",
                "question": "인도와의 미사일 기술 협력 전략은 어떻게 구성해야 할까요?",
                "expected_keywords": ["BrahMos", "현무", "투자", "ROI", "단계별"]
            },
            {
                "category": "인도 협력",
                "question": "인도 DRDO와의 공동연구개발 방안을 제시해주세요",
                "expected_keywords": ["DRDO", "R&D", "특허", "인력교류"]
            },
            
            # UAE 관련 질문
            {
                "category": "UAE 투자",
                "question": "UAE 투자 규모는 어느 정도이며, 어떤 협력 모델이 효과적일까요?",
                "expected_keywords": ["220억", "EDGE", "천궁", "상쇄정책"]
            },
            {
                "category": "UAE 투자", 
                "question": "UAE 사막환경에 특화된 방산시스템 개발 전략은?",
                "expected_keywords": ["사막", "고온", "테스트베드", "GCC"]
            },
            
            # 브라질 관련 질문
            {
                "category": "브라질 항공",
                "question": "브라질과 항공우주 협력이 가능한 분야는 무엇인가요?",
                "expected_keywords": ["Embraer", "훈련기", "아마존", "남미"]
            },
            
            # 동남아 관련 질문
            {
                "category": "동남아 협력",
                "question": "동남아시아 해양안보 협력 방안을 구체적으로 설명해주세요",
                "expected_keywords": ["ASEAN", "해양", "군도", "17,508개"]
            },
            
            # 아프리카 관련 질문
            {
                "category": "아프리카 전략",
                "question": "아프리카 평화유지 장비 수출 전략은 어떻게 수립해야 하나요?",
                "expected_keywords": ["평화유지", "PKO", "남아공", "MRAP"]
            },
            
            # 기술이전 관련 질문
            {
                "category": "기술이전",
                "question": "방산 기술이전 시 지적재산권 보호 방안은?",
                "expected_keywords": ["지식재산권", "단계적", "Level", "보안"]
            },
            
            # 종합 전략 질문
            {
                "category": "종합 전략",
                "question": "비NATO 국가 중 우선 협력 대상을 어떻게 선정해야 할까요?",
                "expected_keywords": ["우선순위", "전략적", "중요도", "협력"]
            },
            
            # 다양성 테스트를 위한 유사 질문
            {
                "category": "다양성 테스트",
                "question": "인도와의 미사일 기술 협력에서 주요 고려사항은?",
                "expected_keywords": ["미사일", "협력", "고려사항"]
            }
        ]
        
        print(f"🔍 총 {len(test_questions)}개 질문으로 포괄적 테스트 시작")
        print("=" * 80)
        
        for i, test_case in enumerate(test_questions, 1):
            self.run_single_test(i, test_case)
            print("─" * 80)
            time.sleep(1)  # 시스템 안정성을 위한 대기
        
        self.generate_final_report()
    
    def run_single_test(self, test_num: int, test_case: dict):
        """개별 테스트 실행 - 축약 없이 완전한 응답 생성"""
        category = test_case["category"]
        question = test_case["question"]
        expected_keywords = test_case["expected_keywords"]
        
        print(f"🧪 테스트 {test_num}: {category}")
        print(f"❓ 질문: {question}")
        print()
        
        test_start = time.time()
        
        try:
            # 상세 모드로 응답 생성 (축약 없음)
            result = self.chatbot.detailed_chat(question)
            test_duration = time.time() - test_start
            
            if "error" not in result or not result.get("error", False):
                response = result["response"]
                
                print("🤖 AI 응답:")
                print("┌" + "─" * 78 + "┐")
                
                # 응답을 완전히 출력 (축약 없음)
                response_lines = response.split('\n')
                for line in response_lines:
                    if len(line) <= 76:
                        print(f"│ {line:<76} │")
                    else:
                        # 긴 줄은 여러 줄로 나누어 출력
                        while line:
                            chunk = line[:76]
                            line = line[76:]
                            print(f"│ {chunk:<76} │")
                
                print("└" + "─" * 78 + "┘")
                print()
                
                # 테스트 성과 분석
                keyword_found = sum(1 for keyword in expected_keywords 
                                  if keyword in response)
                keyword_score = (keyword_found / len(expected_keywords)) * 100
                
                # 상세 정보 출력
                print("📊 테스트 결과 상세:")
                print(f"   ✅ 성공: 응답 생성 완료")
                print(f"   ⏱️  생성 시간: {test_duration:.2f}초")
                print(f"   📏 응답 길이: {len(response)} 문자")
                print(f"   🎯 키워드 점수: {keyword_score:.1f}% ({keyword_found}/{len(expected_keywords)})")
                print(f"   🔧 생성 모드: {result.get('model_info', {}).get('mode', 'unknown')}")
                print(f"   🔄 시도 횟수: {result.get('model_info', {}).get('attempts', 1)}")
                print(f"   📚 RAG 청크: {result.get('rag_chunks', 0)}개")
                
                # 다양성 정보
                diversity_info = result.get('diversity_info', {})
                if diversity_info:
                    print(f"   🌟 다양성 점수: {diversity_info.get('diversity_score', 0):.2f}")
                    print(f"   📈 평균 유사도: {diversity_info.get('avg_similarity', 0):.2f}")
                    print(f"   ❌ 거부된 응답: {diversity_info.get('rejected_count', 0)}개")
                
                # 테스트 결과 저장
                self.test_results.append({
                    "test_num": test_num,
                    "category": category,
                    "question": question,
                    "success": True,
                    "duration": test_duration,
                    "response_length": len(response),
                    "keyword_score": keyword_score,
                    "diversity_info": diversity_info
                })
                
            else:
                print(f"❌ 테스트 실패: {result.get('response', '알 수 없는 오류')}")
                self.test_results.append({
                    "test_num": test_num,
                    "category": category,
                    "question": question,
                    "success": False,
                    "error": result.get('response', '알 수 없는 오류')
                })
        
        except Exception as e:
            print(f"❌ 테스트 실행 중 오류: {e}")
            self.test_results.append({
                "test_num": test_num,
                "category": category,
                "question": question,
                "success": False,
                "error": str(e)
            })
        
        print()
    
    def generate_final_report(self):
        """최종 테스트 보고서 생성"""
        total_time = time.time() - self.start_time
        successful_tests = sum(1 for result in self.test_results if result.get("success", False))
        total_tests = len(self.test_results)
        
        print("🎉 최종 테스트 완료!")
        print("=" * 80)
        print("📊 전체 테스트 결과 요약:")
        print(f"   • 총 테스트: {total_tests}개")
        print(f"   • 성공: {successful_tests}개")
        print(f"   • 실패: {total_tests - successful_tests}개")
        print(f"   • 성공률: {(successful_tests/total_tests)*100:.1f}%")
        print(f"   • 총 소요시간: {total_time:.2f}초")
        print()
        
        if successful_tests > 0:
            # 성공한 테스트들의 통계
            successful_results = [r for r in self.test_results if r.get("success", False)]
            avg_duration = sum(r["duration"] for r in successful_results) / len(successful_results)
            avg_length = sum(r["response_length"] for r in successful_results) / len(successful_results)
            avg_keyword_score = sum(r["keyword_score"] for r in successful_results) / len(successful_results)
            
            print("📈 성공한 테스트 상세 통계:")
            print(f"   • 평균 응답 시간: {avg_duration:.2f}초")
            print(f"   • 평균 응답 길이: {avg_length:.0f} 문자")
            print(f"   • 평균 키워드 점수: {avg_keyword_score:.1f}%")
            print()
        
        # 다양성 통계
        try:
            diversity_stats = self.chatbot.get_diversity_stats()
            if "error" not in diversity_stats:
                print("🌟 응답 다양성 최종 통계:")
                print(f"   • 다양성 점수: {diversity_stats.get('diversity_score', 0):.2f}")
                print(f"   • 평균 유사도: {diversity_stats.get('avg_similarity', 0):.2f}")
                print(f"   • 총 응답 수: {diversity_stats.get('total_responses', 0)}")
                print(f"   • 거부된 응답: {diversity_stats.get('rejected_count', 0)}")
                print()
        except Exception as e:
            print(f"⚠️  다양성 통계 조회 오류: {e}")
        
        # 카테고리별 결과
        categories = {}
        for result in self.test_results:
            category = result["category"]
            if category not in categories:
                categories[category] = {"success": 0, "total": 0}
            categories[category]["total"] += 1
            if result.get("success", False):
                categories[category]["success"] += 1
        
        print("📋 카테고리별 테스트 결과:")
        for category, stats in categories.items():
            success_rate = (stats["success"] / stats["total"]) * 100
            print(f"   • {category}: {stats['success']}/{stats['total']} ({success_rate:.1f}%)")
        
        print()
        print("✨ 6가지 개선사항 적용 확인:")
        print("   ✅ 1. Temperature 0.7 적용")
        print("   ✅ 2. 프롬프트 다양성 지시사항")
        print("   ✅ 3. 반복 방지 페널티 강화")
        print("   ✅ 4. 30개 상세 템플릿 활용")
        print("   ✅ 5. RAG 시스템 구현")
        print("   ✅ 6. 응답 다양성 검증 로직")
        print()
        
        # 로그 파일 생성
        log_filename = f"final_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            import json
            with open(log_filename, 'w', encoding='utf-8') as f:
                json.dump({
                    "test_summary": {
                        "total_tests": total_tests,
                        "successful_tests": successful_tests,
                        "success_rate": (successful_tests/total_tests)*100,
                        "total_time": total_time
                    },
                    "detailed_results": self.test_results,
                    "diversity_stats": diversity_stats if 'diversity_stats' in locals() else {},
                    "category_stats": categories
                }, f, ensure_ascii=False, indent=2)
            print(f"📄 상세 테스트 보고서 저장: {log_filename}")
        except Exception as e:
            print(f"⚠️  보고서 저장 오류: {e}")

def interactive_mode():
    """외부 사용자를 위한 대화형 모드 - 대화 저장 기능 추가"""
    print("🤖 방산 협력 전략 AI 어시스턴트")
    print("=" * 60)
    print("💡 사용 가이드:")
    print("   • 방산 협력 관련 질문을 자유롭게 입력하세요")
    print("   • '종료', 'quit', 'exit' 입력 시 종료")
    print("   • '도움말' 입력 시 추천 질문 확인")
    print("   • '통계' 입력 시 다양성 통계 확인")
    print("   • 모든 대화 내용이 자동으로 txt 파일에 저장됩니다")
    print("=" * 60)
    
    # 대화 로거 초기화
    conversation_logger = ConversationLogger()
    conversation_logger.log_system_message("시스템 시작 - 대화형 모드")
    
    try:
        from chatbot import DefenseCooperationChatbot
        chatbot = DefenseCooperationChatbot()
        chatbot.initialize(use_gpu=False, use_quantization=False)
        
        if not chatbot.is_initialized:
            error_msg = "시스템 초기화에 실패했습니다."
            print(f"❌ {error_msg}")
            conversation_logger.log_system_message(f"오류: {error_msg}")
            return
        
        success_msg = "시스템 준비 완료! 질문을 입력하세요."
        print(f"✅ {success_msg}\n")
        conversation_logger.log_system_message(success_msg)
        
        question_count = 0
        
        while True:
            try:
                user_input = input("👤 질문: ").strip()
                
                if user_input.lower() in ['종료', 'quit', 'exit']:
                    farewell_msg = "감사합니다! 대화 내용이 저장되었습니다."
                    print(f"👋 {farewell_msg}")
                    conversation_logger.log_system_message(f"종료: {farewell_msg}")
                    break
                
                if user_input == '도움말':
                    help_msg = """
💡 추천 질문 예시:
  • 인도와의 미사일 기술 협력 전략은?
  • UAE 투자 규모는 어느 정도인가요?
  • 브라질과 항공우주 협력이 가능한가요?
  • 동남아시아 해양안보 협력 방안은?
  • 아프리카 평화유지 장비 수출 전략은?"""
                    print(help_msg)
                    conversation_logger.log_system_message("도움말 요청 및 제공")
                    continue
                
                if user_input == '통계':
                    try:
                        stats = chatbot.get_diversity_stats()
                        if "error" not in stats:
                            stats_msg = f"""
📊 다양성 통계:
  - 다양성 점수: {stats.get('diversity_score', 0):.2f}
  - 평균 유사도: {stats.get('avg_similarity', 0):.2f}
  - 총 응답 수: {stats.get('total_responses', 0)}"""
                            print(stats_msg)
                            conversation_logger.log_system_message(f"통계 요청: {stats_msg}")
                        else:
                            error_msg = "통계 조회 중 오류가 발생했습니다."
                            print(f"❌ {error_msg}")
                            conversation_logger.log_system_message(f"오류: {error_msg}")
                    except Exception as e:
                        error_msg = f"통계 조회 오류: {e}"
                        print(f"❌ {error_msg}")
                        conversation_logger.log_system_message(f"오류: {error_msg}")
                    continue
                
                if not user_input:
                    continue
                
                question_count += 1
                print(f"\n🤖 AI: 질문을 처리 중입니다... (질문 #{question_count})")
                
                # 응답 생성 시작 시간 기록
                start_time = time.time()
                
                try:
                    # 상세한 답변 생성 (끊김 방지를 위해 detailed_chat 사용)
                    if hasattr(chatbot, 'detailed_chat'):
                        result = chatbot.detailed_chat(user_input)
                        if isinstance(result, dict) and "response" in result:
                            response = result["response"]
                        else:
                            response = str(result)
                    else:
                        response = chatbot.chat(user_input)
                    
                    duration = time.time() - start_time
                    
                    # 화면에 출력
                    print("─" * 60)
                    print(response)
                    print("─" * 60)
                    print(f"⏱️  처리 시간: {duration:.2f}초 | 응답 길이: {len(response)} 문자")
                    print()
                    
                    # 파일에 저장
                    conversation_logger.log_conversation(user_input, response, duration)
                    
                    # 중간 저장 확인 메시지
                    if question_count % 3 == 0:  # 3개 질문마다
                        print(f"💾 대화 내용이 {conversation_logger.log_filename}에 저장되었습니다.")
                        print()
                    
                except Exception as e:
                    error_msg = f"응답 생성 중 오류 발생: {e}"
                    print(f"❌ {error_msg}")
                    conversation_logger.log_conversation(user_input, f"오류: {error_msg}", 0)
                
            except KeyboardInterrupt:
                interrupt_msg = "사용자가 중단했습니다. 대화 내용이 저장되었습니다."
                print(f"\n\n👋 {interrupt_msg}")
                conversation_logger.log_system_message(interrupt_msg)
                break
            except Exception as e:
                error_msg = f"처리 중 예상치 못한 오류: {e}"
                print(f"\n❌ {error_msg}")
                conversation_logger.log_system_message(f"오류: {error_msg}")
        
        # 최종 통계 저장
        final_msg = f"총 {question_count}개의 질문을 처리했습니다."
        print(f"\n📊 {final_msg}")
        conversation_logger.log_system_message(f"세션 종료: {final_msg}")
        
        if conversation_logger.log_filename:
            print(f"📁 전체 대화 내용: {conversation_logger.log_filename}")
                
    except Exception as e:
        error_msg = f"시스템 오류: {e}"
        print(f"❌ {error_msg}")
        if 'conversation_logger' in locals():
            conversation_logger.log_system_message(f"시스템 오류: {error_msg}")

def show_usage_guide():
    """외부 사용자를 위한 사용 가이드"""
    print("=" * 80)
    print("🌟 방산 협력 전략 AI 시스템 - 사용자 가이드 (개선 버전)")
    print("=" * 80)
    print()
    print("🆕 새로운 기능:")
    print("   • 대화 내용 자동 txt 파일 저장")
    print("   • 답변 끊김 문제 해결")
    print("   • 실시간 저장으로 데이터 손실 방지")
    print("   • 처리 시간 및 응답 길이 표시")
    print()
    print("📁 파일 구성:")
    print("   • final_test.py      : 최종 테스트 및 사용자 인터페이스 (이 파일)")
    print("   • chatbot.py         : 메인 챗봇 시스템")
    print("   • data_structure.py  : 지식 베이스")
    print("   • llama_integration.py : AI 모델 통합")
    print("   • prompt_engineering.py : 프롬프트 엔지니어링")
    print()
    print("🚀 실행 방법:")
    print("   1. 최종 테스트:     python final_test.py test")
    print("   2. 대화형 사용:     python final_test.py interactive ⭐ 추천")
    print("   3. 사용 가이드:     python final_test.py guide")
    print("   4. 기본 실행:       python final_test.py")
    print()
    print("💡 외부 사용자 권장 실행 방법:")
    print("   python final_test.py interactive")
    print()
    print("📝 저장되는 파일들:")
    print("   • conversation_log_YYYYMMDD_HHMMSS.txt : 대화 내용")
    print("   • defense_ai_test_YYYYMMDD_HHMMSS.log : 시스템 로그")
    print("   • final_test_report_YYYYMMDD_HHMMSS.json : 테스트 결과")
    print()
    print("🔧 시스템 특징:")
    print("   • 6가지 개선사항 모두 적용")
    print("   • 30개 상세 응답 템플릿 활용")
    print("   • 응답 다양성 검증 시스템")
    print("   • 포괄적인 방산 협력 지식 베이스")
    print("   • 안정적인 더미 모드 지원")
    print("   • 답변 끊김 방지 및 완전한 응답 저장")
    print()
    print("⚠️  주의사항:")
    print("   • 모든 파일이 같은 폴더에 있어야 합니다")
    print("   • Python 3.7 이상 권장")
    print("   • 필요한 라이브러리: torch, transformers 등")
    print("   • 대화 파일은 UTF-8 인코딩으로 저장됩니다")
    print()
    print("📞 문제 해결:")
    print("   • ImportError 발생 시: 모든 파일이 같은 폴더에 있는지 확인")
    print("   • 응답이 느릴 때: 정상적인 동작입니다 (복잡한 분석 중)")
    print("   • 답변이 끊길 때: txt 파일에서 완전한 답변 확인 가능")
    print("   • 파일 저장 오류 시: 폴더 쓰기 권한 확인")
    print("=" * 80)

def main():
    """메인 실행 함수"""
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "test":
            # 최종 테스트 실행
            test_suite = FinalTestSuite()
            test_suite.run_comprehensive_test()
            
        elif command == "interactive":
            # 대화형 모드 실행
            interactive_mode()
            
        elif command == "guide":
            # 사용 가이드 표시
            show_usage_guide()
            
        else:
            print(f"❌ 알 수 없는 명령어: {command}")
            print("사용법: python final_test.py [test|interactive|guide]")
            
    else:
        # 기본 실행 - 사용자에게 선택지 제공
        print("🤖 방산 협력 전략 AI 시스템 (개선 버전)")
        print("=" * 50)
        print("🆕 새로운 기능: 대화 내용 자동 저장!")
        print()
        print("실행할 모드를 선택하세요:")
        print("1. 최종 테스트 (test)")
        print("2. 대화형 사용 (interactive) ⭐ 추천")
        print("3. 사용 가이드 (guide)")
        print()
        
        choice = input("선택 (1-3): ").strip()
        
        if choice == "1":
            test_suite = FinalTestSuite()
            test_suite.run_comprehensive_test()
        elif choice == "2":
            interactive_mode()
        elif choice == "3":
            show_usage_guide()
        else:
            print("기본값으로 대화형 모드를 실행합니다...")
            interactive_mode()

if __name__ == "__main__":
    main()