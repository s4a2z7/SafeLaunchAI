"""
SafeLaunch AI — JSON → SQLite 마이그레이션 스크립트

기존 database/*.json 파일의 데이터를 새 관계형 DB(safelaunch.db)로 이관합니다.

사용법:
    python migrate_json_to_db.py              # 실행 (dry-run 아님)
    python migrate_json_to_db.py --dry-run    # 미리보기만 (DB 변경 없음)

이관 대상:
    - database/laws.json        → laws + document_chunks 테이블
    - database/precedents.json  → precedents + document_chunks 테이블
    - database/store_policies.json → store_policies + document_chunks 테이블

※ 기존 JSON 파일은 삭제하지 않으며 VectorStore(TF-IDF)와 병행 운영 가능합니다.
"""

import json
import os
import sys
import argparse

# 프로젝트 루트를 패스에 추가
sys.path.insert(0, os.path.dirname(__file__))

from core.database import DatabaseManager, _new_id, _now
from core.store_policy_data import APPLE_POLICIES, GOOGLE_POLICIES

DATABASE_DIR = os.path.join(os.path.dirname(__file__), "database")


def load_json(filename: str) -> dict:
    """JSON 파일 로드"""
    path = os.path.join(DATABASE_DIR, filename)
    if not os.path.exists(path):
        print(f"  [SKIP] {filename} — 파일 없음")
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def migrate_laws(db: DatabaseManager, dry_run: bool = False) -> dict:
    """laws.json → laws + document_chunks"""
    print("\n" + "=" * 50)
    print("📚 법령 데이터 마이그레이션")
    print("=" * 50)

    data = load_json("laws.json")
    if not data:
        return {"docs": 0, "chunks": 0, "skipped": 0}

    # 메타데이터 기반으로 고유 법령 추출
    law_groups: dict[str, list] = {}  # law_id → [chunks]
    for chunk_hash, chunk_data in data.items():
        meta = chunk_data.get("metadata", {})
        law_id = meta.get("law_id", "")
        if not law_id:
            continue
        if law_id not in law_groups:
            law_groups[law_id] = []
        law_groups[law_id].append({
            "hash": chunk_hash,
            "text": chunk_data.get("text", ""),
            "metadata": meta,
        })

    print(f"  발견: {len(law_groups)}개 법령, {len(data)}개 청크")

    if dry_run:
        for law_id, chunks in list(law_groups.items())[:3]:
            meta = chunks[0]["metadata"]
            print(f"    - {meta.get('law_name', '?')} (ID: {law_id}, {len(chunks)}청크)")
        return {"docs": len(law_groups), "chunks": len(data), "skipped": 0}

    # 실제 마이그레이션
    docs_count = 0
    chunks_count = 0

    for law_id, chunks in law_groups.items():
        meta = chunks[0]["metadata"]

        # 법령 레코드 생성
        db_law_id = db.upsert_law(
            law_id=law_id,
            law_name=meta.get("law_name", ""),
            proclamation_date=meta.get("proclamation_date"),
            enforcement_date=meta.get("enforcement_date"),
            source_url=meta.get("source_url"),
        )
        docs_count += 1

        # 청크 생성
        for chunk in chunks:
            db.upsert_chunk(
                chunk_hash=chunk["hash"],
                source_type="law",
                source_id=db_law_id,
                chunk_index=chunk["metadata"].get("chunk_index", 0),
                content=chunk["text"],
                metadata=chunk["metadata"],
            )
            chunks_count += 1

    print(f"  완료: {docs_count}개 법령, {chunks_count}개 청크 이관")
    return {"docs": docs_count, "chunks": chunks_count, "skipped": 0}


def migrate_precedents(db: DatabaseManager, dry_run: bool = False) -> dict:
    """precedents.json → precedents + document_chunks"""
    print("\n" + "=" * 50)
    print("⚖️  판례 데이터 마이그레이션")
    print("=" * 50)

    data = load_json("precedents.json")
    if not data:
        return {"docs": 0, "chunks": 0, "skipped": 0}

    # 메타데이터 기반으로 고유 판례 추출
    prec_groups: dict[str, list] = {}
    for chunk_hash, chunk_data in data.items():
        meta = chunk_data.get("metadata", {})
        prec_seq = meta.get("precedent_seq", "")
        if not prec_seq:
            continue
        if prec_seq not in prec_groups:
            prec_groups[prec_seq] = []
        prec_groups[prec_seq].append({
            "hash": chunk_hash,
            "text": chunk_data.get("text", ""),
            "metadata": meta,
        })

    print(f"  발견: {len(prec_groups)}개 판례, {len(data)}개 청크")

    if dry_run:
        for prec_seq, chunks in list(prec_groups.items())[:3]:
            meta = chunks[0]["metadata"]
            print(f"    - {meta.get('case_name', '?')} ({meta.get('court_name', '?')}, {len(chunks)}청크)")
        return {"docs": len(prec_groups), "chunks": len(data), "skipped": 0}

    docs_count = 0
    chunks_count = 0

    for prec_seq, chunks in prec_groups.items():
        meta = chunks[0]["metadata"]

        db_prec_id = db.upsert_precedent(
            precedent_seq=prec_seq,
            case_name=meta.get("case_name", ""),
            court_name=meta.get("court_name"),
            judgment_date=meta.get("judgment_date"),
            case_number=meta.get("case_number"),
            case_type=meta.get("case_type"),
            source_url=meta.get("source_url"),
        )
        docs_count += 1

        for chunk in chunks:
            db.upsert_chunk(
                chunk_hash=chunk["hash"],
                source_type="precedent",
                source_id=db_prec_id,
                chunk_index=chunk["metadata"].get("chunk_index", 0),
                content=chunk["text"],
                metadata=chunk["metadata"],
            )
            chunks_count += 1

    print(f"  완료: {docs_count}개 판례, {chunks_count}개 청크 이관")
    return {"docs": docs_count, "chunks": chunks_count, "skipped": 0}


def migrate_store_policies(db: DatabaseManager, dry_run: bool = False) -> dict:
    """store_policies.json + 하드코딩 정책 → store_policies + document_chunks"""
    print("\n" + "=" * 50)
    print("🏪 스토어 정책 마이그레이션")
    print("=" * 50)

    # 1. 하드코딩된 정책 데이터 (store_policy_data.py)
    all_policies = APPLE_POLICIES + GOOGLE_POLICIES
    print(f"  하드코딩 정책: Apple {len(APPLE_POLICIES)}개 + Google {len(GOOGLE_POLICIES)}개 = {len(all_policies)}개")

    if dry_run:
        for p in all_policies[:3]:
            meta = p["metadata"]
            print(f"    - [{meta['store']}] {meta['section']} > {meta.get('subsection', '')}")
        return {"docs": len(all_policies), "chunks": 0, "skipped": 0}

    docs_count = 0
    chunks_count = 0

    for policy in all_policies:
        meta = policy["metadata"]
        db_policy_id = db.upsert_store_policy(
            store=meta["store"],
            section=meta["section"],
            subsection=meta.get("subsection", ""),
            content=policy["text"],
            policy_name=meta.get("policy_name", ""),
            effective_date=meta.get("effective_date"),
        )
        docs_count += 1

    # 2. JSON 청크 데이터
    data = load_json("store_policies.json")
    if data:
        for chunk_hash, chunk_data in data.items():
            meta = chunk_data.get("metadata", {})

            # 매칭되는 정책의 DB ID를 찾기 위해 store+section으로 검색
            with db.connection() as conn:
                row = conn.execute(
                    "SELECT id FROM store_policies WHERE store=? AND section=? LIMIT 1",
                    (meta.get("store", ""), meta.get("section", "")),
                ).fetchone()
                source_id = row["id"] if row else "unknown"

            db.upsert_chunk(
                chunk_hash=chunk_hash,
                source_type="store_policy",
                source_id=source_id,
                chunk_index=meta.get("chunk_index", 0),
                content=chunk_data.get("text", ""),
                metadata=meta,
            )
            chunks_count += 1

    print(f"  완료: {docs_count}개 정책, {chunks_count}개 청크 이관")
    return {"docs": docs_count, "chunks": chunks_count, "skipped": 0}


def main():
    parser = argparse.ArgumentParser(description="JSON → SQLite 마이그레이션")
    parser.add_argument("--dry-run", action="store_true", help="미리보기만 (DB 변경 없음)")
    args = parser.parse_args()

    print("=" * 60)
    print("SafeLaunch AI — JSON → SQLite 마이그레이션")
    print("=" * 60)

    if args.dry_run:
        print("\n⚠️  DRY-RUN 모드: DB 변경 없이 미리보기만 실행합니다.\n")
        db = None
    else:
        db = DatabaseManager()
        print(f"\n데이터베이스: {db.db_path}\n")

        # 동기화 로그 기록
        sync_id = db.start_sync(
            sync_type="full",
            queries=["json_migration"],
            triggered_by="migration_script",
        )

    # 마이그레이션 실행
    results = {}

    if args.dry_run:
        # dry-run은 DB 없이 파일만 분석
        dummy_db = type("DummyDB", (), {})()
        results["laws"] = migrate_laws(dummy_db, dry_run=True)
        results["precedents"] = migrate_precedents(dummy_db, dry_run=True)
        results["store_policies"] = migrate_store_policies(dummy_db, dry_run=True)
    else:
        results["laws"] = migrate_laws(db)
        results["precedents"] = migrate_precedents(db)
        results["store_policies"] = migrate_store_policies(db)

        # 동기화 완료 기록
        total_docs = sum(r["docs"] for r in results.values())
        total_chunks = sum(r["chunks"] for r in results.values())
        db.complete_sync(
            sync_id=sync_id,
            items_added=total_docs,
            chunks_created=total_chunks,
        )

    # 결과 요약
    print("\n" + "=" * 60)
    print("마이그레이션 결과 요약")
    print("=" * 60)
    print(f"{'컬렉션':<20} {'문서':>8} {'청크':>8} {'스킵':>8}")
    print("-" * 50)
    for name, r in results.items():
        print(f"{name:<20} {r['docs']:>8} {r['chunks']:>8} {r['skipped']:>8}")
    print("-" * 50)
    total_docs = sum(r["docs"] for r in results.values())
    total_chunks = sum(r["chunks"] for r in results.values())
    print(f"{'합계':<20} {total_docs:>8} {total_chunks:>8}")

    if not args.dry_run:
        print(f"\n데이터베이스 통계:")
        stats = db.get_stats()
        for key, val in stats.items():
            print(f"  {key}: {val}")

    print("\n" + "=" * 60)
    print("완료!")
    print("=" * 60)


if __name__ == "__main__":
    main()
