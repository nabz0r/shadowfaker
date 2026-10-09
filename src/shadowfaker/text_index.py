"""Private multilingual full-text index of factual timeline summaries and sourced notes."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import sqlite3

from tqdm import tqdm

from .config import CONFIG
from .state_matrix import DB

ROOT = CONFIG.root / "data" / "text"
INDEX = ROOT / "game_text.sqlite"


def connect(path: Path = INDEX) -> sqlite3.Connection:
    path.parent.mkdir(parents=True,exist_ok=True)
    db=sqlite3.connect(path)
    db.execute("""CREATE VIRTUAL TABLE IF NOT EXISTS documents USING fts5(
        source_key UNINDEXED, language UNINDEXED, content,
        source_kind UNINDEXED, provenance UNINDEXED, status UNINDEXED,
        tokenize='unicode61 remove_diacritics 2')""")
    return db


def insert(db: sqlite3.Connection, key: str, language: str, content: str,
           kind: str, provenance: str, status: str) -> None:
    if not content.strip(): raise ValueError("Empty note")
    db.execute("DELETE FROM documents WHERE source_key=?",(key,))
    db.execute("INSERT INTO documents VALUES (?,?,?,?,?,?)",
               (key,language,content,kind,provenance,status))


def factual_summary(db: sqlite3.Connection, mid: str, language: str) -> str:
    match=db.execute("SELECT queue_id,map_id,champion_id,state_count,transition_count FROM matches WHERE match_id=?",(mid,)).fetchone()
    if not match: raise KeyError(mid)
    starts=db.execute("SELECT frame_index,own_cell64,own_gold,team_gold-enemy_gold,team_xp-enemy_xp FROM states WHERE match_id=? ORDER BY frame_index",(mid,)).fetchall()
    events=Counter(dict(db.execute("SELECT category,COUNT(*) FROM events WHERE match_id=? GROUP BY category",(mid,))))
    moves=db.execute("SELECT from_cell64,to_cell64 FROM transitions WHERE match_id=? AND from_cell64 IS NOT NULL",(mid,)).fetchall()
    distances=[((a%64-b%64)**2+(a//64-b//64)**2)**.5 for a,b in moves]
    near={}
    for role in ("JUNGLE","BOTTOM","UTILITY","TOP"):
        value=db.execute("""SELECT COUNT(*) FROM actors a JOIN states s ON s.match_id=a.match_id AND s.frame_index=a.frame_index
          WHERE a.match_id=? AND a.side='ally' AND a.role=? AND a.x IS NOT NULL AND s.own_x IS NOT NULL
          AND ((a.x-s.own_x)*(a.x-s.own_x)+(a.y-s.own_y)*(a.y-s.own_y)) < ?""",
          (mid,role,(2500/15000)**2)).fetchone()[0]
        near[role]=value
    start,end=starts[0],starts[-1]
    categories=("faker_kill","faker_death","ally_kill","enemy_kill","dragon","baron","herald","grubs","building","ward_placed")
    counts=", ".join(f"{name.replace('_',' ')}={events[name]}" for name in categories)
    if language=="fr":
        return (f"Résumé factuel de la partie ranked solo {mid}. Compte cible : Hide on bush#KR1, champion ID {match[2]}. "
                f"{match[3]} états échantillonnés et {match[4]} transitions observées sur la carte ID {match[1]}; "
                f"début case 64×64 {start[1]}, fin {end[1]}. Déplacement médian {sorted(distances)[len(distances)//2] if distances else 0:.1f} cases entre deux frames. "
                f"Différence d'or équipe au début {start[3]:+.0f}, à la fin {end[3]:+.0f}; différence XP finale {end[4]:+.0f}. "
                f"Événements enregistrés : {counts}. États où le compte est à moins de 2500 unités d'un allié : "
                f"jungle {near['JUNGLE']}, bot carry {near['BOTTOM']}, support {near['UTILITY']}, top {near['TOP']}. "
                "Ce sont des observations de timeline, pas des clics, intentions, communications ou preuves causales.")
    return (f"Factual ranked solo game summary {mid}. Target account Hide on bush#KR1, champion ID {match[2]}. "
            f"{match[3]} sampled states and {match[4]} observed transitions on map ID {match[1]}; "
            f"start 64x64 cell {start[1]}, end {end[1]}. Median movement {sorted(distances)[len(distances)//2] if distances else 0:.1f} cells between frames. "
            f"Team gold difference at start {start[3]:+.0f}, at end {end[3]:+.0f}; final XP difference {end[4]:+.0f}. "
            f"Recorded events: {counts}. States with target within 2500 units of an ally: "
            f"jungle {near['JUNGLE']}, bot carry {near['BOTTOM']}, support {near['UTILITY']}, top {near['TOP']}. "
            "These are timeline observations, not clicks, intentions, communications or causal proof.")


def generate(limit: int | None = None, index: Path = INDEX, state_db: Path = DB) -> dict:
    source=sqlite3.connect(state_db)
    target=connect(index)
    ids=[x[0] for x in source.execute("SELECT match_id FROM matches ORDER BY match_id")]
    if limit is not None: ids=ids[:limit]
    folder=ROOT/"raw"/"generated";folder.mkdir(parents=True,exist_ok=True)
    errors={}
    for mid in tqdm(ids,desc="multilingual game summaries",unit="game"):
        try:
            with target:
                for language in ("en","fr"):
                    content=factual_summary(source,mid,language)
                    path=folder/f"{mid}.{language}.txt"
                    if not path.exists() or path.read_text()!=content: path.write_text(content,encoding="utf-8")
                    insert(target,f"generated:{mid}:{language}",language,content,"riot_timeline_derived",
                           "local ranked solo match+timeline; deterministic summary v1","observed")
        except Exception as exc: errors[mid]=str(exc)
    report={"games":len(ids)-len(errors),"generated_documents":2*(len(ids)-len(errors)),
            "languages_generated":["en","fr"],"external_languages_supported":"UTF-8 originals with source metadata",
            "errors":errors,"private_index":str(index)}
    (ROOT/"summary.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    source.close();target.close()
    return report


def import_note(path: Path, metadata_path: Path | None = None, index: Path = INDEX) -> dict:
    metadata_path=metadata_path or path.with_suffix(".json")
    metadata=json.loads(metadata_path.read_text(encoding="utf-8"))
    for required in ("language","source_kind","provenance","status"):
        if not metadata.get(required): raise ValueError(f"Missing {required} in metadata")
    content=path.read_text(encoding="utf-8")
    digest=hashlib.sha256((str(path.resolve())+content).encode()).hexdigest()[:20]
    key=f"external:{digest}"
    db=connect(index)
    with db: insert(db,key,metadata["language"],content,metadata["source_kind"],metadata["provenance"],metadata["status"])
    db.close()
    return {"source_key":key,"language":metadata["language"],"status":metadata["status"]}


def search(query: str, language: str | None = None, limit: int = 10, index: Path = INDEX) -> list[dict]:
    query=query.strip()
    if not query: return []
    db=connect(index)
    # Quote the complete user string so FTS syntax cannot change the query.
    phrase='"'+query.replace('"','""')+'"'
    try:
        rows=db.execute("SELECT source_key,language,content,source_kind,provenance,status FROM documents WHERE documents MATCH ? AND (? IS NULL OR language=?) LIMIT ?",
                        (phrase,language,language,min(limit,50))).fetchall()
    except sqlite3.OperationalError:
        rows=[]
    # Unicode FTS tokenization cannot segment every script. Literal search is a
    # deterministic fallback for CJK originals and short technical terms.
    if not rows:
        rows=db.execute("SELECT source_key,language,content,source_kind,provenance,status FROM documents WHERE content LIKE ? AND (? IS NULL OR language=?) LIMIT ?",
                        ("%"+query+"%",language,language,min(limit,50))).fetchall()
    db.close()
    return [dict(zip(("source_key","language","content","source_kind","provenance","status"),row)) for row in rows]


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("stage",choices=("generate","search","import"))
    parser.add_argument("--limit",type=int)
    parser.add_argument("--query")
    parser.add_argument("--language")
    parser.add_argument("--file",type=Path)
    parser.add_argument("--metadata",type=Path)
    args=parser.parse_args()
    if args.stage=="generate": print(generate(args.limit))
    elif args.stage=="search": print(json.dumps(search(args.query or "",args.language,args.limit or 10),ensure_ascii=False,indent=2))
    else: print(import_note(args.file,args.metadata))


if __name__=="__main__":main()
