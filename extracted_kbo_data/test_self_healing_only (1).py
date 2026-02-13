"""
Self-healing RAG만 테스트 (ANTHROPIC_API_KEY)
"""

import sys
import os
import io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

# .env 로드
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(PROJECT_ROOT, '.env'))
except ImportError:
    pass

print("=" * 60)
print("Self-healing RAG 테스트 (ANTHROPIC_API_KEY)")
print("=" * 60)

key = os.getenv("ANTHROPIC_API_KEY")
if not key:
    print("\n[오류] ANTHROPIC_API_KEY가 설정되지 않았습니다.")
    sys.exit(1)
print(f"\n[OK] API 키 확인됨: {key[:20]}...")

try:
    from core.self_healing_rag import evaluate_context_fitness, expand_query
    
    sample_contexts = [{
        "text": "저작권법 제2조 제1호에서는 저작물을 인간의 사상 또는 감정을 표현한 창작물로 정의합니다.",
        "metadata": {"source_type": "law", "law_name": "저작권법"},
        "score": 0.7,
    }]
    query = "앱에서 사용자가 만든 콘텐츠의 저작권은 누구에게 있나요?"
    
    print("\n[1] Context 적합도 평가...")
    fitness = evaluate_context_fitness(query, sample_contexts, llm_provider="anthropic")
    print(f"    적합도: {fitness.fitness_score:.2f}")
    print(f"    이유: {fitness.reason or '-'}")
    
    print("\n[2] 쿼리 확장...")
    expansion = expand_query(query, llm_provider="anthropic")
    print(f"    확장 쿼리: {expansion.expanded_query}")
    
    print("\n" + "=" * 60)
    print("Self-healing RAG 테스트 통과!")
    print("=" * 60)

except Exception as e:
    print(f"\n[실패] {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
