import argparse
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
import numpy as np
import torch
from PIL import Image, ImageDraw

from .config import CONFIG
from .evaluate import load_model
from .util import read_json
from .util import atomic_json
from .features import position, number
from .events64 import event_category, position_cell
from .geometry64 import local_metric
from .ioc import ITEM_TYPES, inventory_snapshots

TRACE_SCHEMA_VERSION = 11


def _item_kind(descriptor: dict) -> str:
    """A display grouping from played-patch Data Dragon, never an inferred action."""
    tags = set(descriptor.get("tags") or [])
    name = str(descriptor.get("name") or "").lower()
    if "Vision" in tags or "Trinket" in tags: return "vision"
    if "potion" in name: return "potion"
    if "Consumable" in tags: return "consumable"
    return "equipment"


def _cached_patch_items(match: dict, raw: Path) -> tuple[str, dict, tuple[Path, ...]]:
    """Read the played patch's official static catalog without needing a live API key."""
    version = str((match.get("info") or {}).get("gameVersion") or "")
    patch = ".".join(version.split(".")[:2])
    versions_path = raw / "ddragon" / "versions.json"
    versions = read_json(versions_path) or []
    release = next((v for v in versions if isinstance(v, str) and v.startswith(patch + ".")), "")
    path = raw / "ddragon" / release / "en_US_item.json" if release else None
    if not path or not path.is_file():
        return "", {}, (versions_path,) if versions_path.is_file() else ()
    source = read_json(path) or {}
    return release, source.get("data") or {}, (versions_path, path)


def _source_fingerprint(*paths: Path) -> str:
    """Bind a cached trace to the exact processed and raw files it displays."""
    digest = hashlib.sha256()
    for path in paths:
        digest.update(path.name.encode("utf-8"))
        digest.update(b"\0")
        with path.open("rb") as source:
            for chunk in iter(lambda: source.read(1024 * 1024), b""):
                digest.update(chunk)
    return digest.hexdigest()


def _observed_context(match: dict, timeline: dict, puuid: str, minute: float,
                      inventories=None, timed_events=None) -> dict:
    """Display the complete observed transition, keeping the future separate."""
    players = (match.get("info") or {}).get("participants") or []
    own = next(p for p in players if p.get("puuid") == puuid)
    pid = int(own["participantId"])
    team_id = int(own["teamId"])
    teams = {int(p["participantId"]):int(p["teamId"]) for p in players}
    roles = {int(p["participantId"]):str(p.get("teamPosition") or "UNKNOWN") for p in players}
    champions = {int(p["participantId"]):str(p.get("championName") or p.get("championId") or "?") for p in players}
    frames = (timeline.get("info") or {}).get("frames") or []
    index = min(range(len(frames)-1),key=lambda j:abs(number(frames[j].get("timestamp"),j*60000)/60000-minute))
    current,next_frame = frames[index:index+2]
    if inventories is None: inventories = inventory_snapshots(timeline)[0]
    prev = frames[index-1] if index else None
    def actors(frame, frame_index):
        pf = frame.get("participantFrames") or {}
        result=[]
        for p in sorted(teams,key=lambda p:(0 if p==pid else 1 if teams[p]==team_id else 2,roles[p],p)):
            data=pf.get(str(p)) or pf.get(p) or {}
            xy=position(data)
            stats=data.get("championStats") or {}
            max_health=number(stats.get("healthMax"))
            health=number(stats.get("health"))
            result.append({"participant":p,"team_id":teams[p],"side":"faker" if p==pid else "ally" if teams[p]==team_id else "enemy",
                           "role":roles[p],"champion":champions[p],
                           "xy":None if xy is None else [round(float(v),5) for v in xy],
                           "gold":int(number(data.get("totalGold"))),"xp":int(number(data.get("xp"))),
                           "level":int(number(data.get("level"))),
                           "health_fraction":round(max(0.0,min(1.0,health/max_health)),3) if max_health>0 else None,
                           "items":[item for item, count in sorted(inventories[frame_index][p].items()) for _ in range(count)]})
        return result
    now_actors,next_actors=actors(current,index),actors(next_frame,index+1)
    own_xy=next(a["xy"] for a in now_actors if a["side"]=="faker")
    previous_xy=None
    if prev is not None:
        prior=position((prev.get("participantFrames") or {}).get(str(pid)) or {})
        if prior is not None: previous_xy=prior.tolist()
    allies=[a["xy"] for a in now_actors if a["side"]=="ally" and a["role"] in ("JUNGLE","BOTTOM","UTILITY") and a["xy"]]
    metric=local_metric(own_xy,previous_xy,allies) if own_xy else None
    low=number(current.get("timestamp"),index*60000)
    high=number(next_frame.get("timestamp"),(index+1)*60000)
    # Riot sometimes places a boundary event in the following frame. Assign
    # events by their own timestamp rather than by their container frame.
    if timed_events is None:
        timed_events=[e for frame in frames for e in frame.get("events") or []]
    raw_events=[e for e in timed_events if low<number(e.get("timestamp"),high)<=high]
    def display_events(events):
        shown=[]
        for event in events:
            if event.get("type") in (*ITEM_TYPES,"SKILL_LEVEL_UP") and int(event.get("participantId") or 0) not in teams:
                continue
            category=event_category(event,pid,team_id,teams)
            if category is None and event.get("type") not in (*ITEM_TYPES,"SKILL_LEVEL_UP"): continue
            event_xy=position(event)
            actor_id=int(event.get("participantId") or event.get("killerId") or event.get("creatorId") or 0)
            event_type=event.get("type")
            owner_team=int(event.get("teamId") or 0) if event_type=="BUILDING_KILL" else 0
            if event_type=="ELITE_MONSTER_KILL":
                acting_team=int(event.get("killerTeamId") or teams.get(actor_id) or 0)
                attribution="riot_team" if int(event.get("killerTeamId") or 0) in (100,200) else "actor"
            elif event_type=="BUILDING_KILL" and owner_team in (100,200):
                acting_team=300-owner_team
                attribution="opposite_of_destroyed_team"
            else:
                acting_team=teams.get(actor_id,0)
                attribution="actor" if acting_team else "unknown"
            if acting_team not in (100,200): acting_team=0
            shown.append({"time_seconds":round(number(event.get("timestamp"),high)/1000,3),
                          "seconds_after_t":round((number(event.get("timestamp"),high)-low)/1000,1),
                          "category":category or event.get("type"),"cell64":position_cell(event),
                          "xy":None if event_xy is None else [round(float(v),5) for v in event_xy],
                          "actor_id":actor_id,"victim_id":int(event.get("victimId") or 0),
                          "assisting_ids":[int(v) for v in event.get("assistingParticipantIds") or []
                                           if str(v).isdigit() and int(v) in teams],
                          "acting_team_id":acting_team,"team_attribution":attribution,
                          "destroyed_team_id":owner_team if owner_team in (100,200) else 0,
                          "monster_subtype":str(event.get("monsterSubType") or ""),
                          "building_type":str(event.get("buildingType") or ""),
                          "lane_type":str(event.get("laneType") or ""),
                          "tower_type":str(event.get("towerType") or ""),
                          "ward_type":str(event.get("wardType") or ""),
                          "item_id":int(event.get("itemId") or 0),
                          "before_item_id":int(event.get("beforeId") or 0),
                          "after_item_id":int(event.get("afterId") or 0),
                          "skill_slot":int(event.get("skillSlot") or 0)})
        return shown
    shown=display_events(raw_events)
    initial=display_events([e for e in timed_events if number(e.get("timestamp"),0)<=low]) if index==0 else []
    own_events=[e for e in raw_events if int(e.get("participantId") or 0)==pid]
    purchases=[int(e["itemId"]) for e in own_events if e.get("type")=="ITEM_PURCHASED" and e.get("itemId")]
    skills=[int(e["skillSlot"]) for e in own_events if e.get("type")=="SKILL_LEVEL_UP" and e.get("skillSlot")]
    return {"actors_t":now_actors,"actors_next":next_actors,"events_next":shown,
            "events_initial":initial,
            "frame_seconds":round(low/1000,3),"next_frame_seconds":round(high/1000,3),
            "first_item_next":purchases[0] if purchases else None,
            "first_skill_next":skills[0] if skills else None,"metric_t":metric,
            "source_frame_index":index}


def export_trace(processed: Path = CONFIG.processed, models: Path = CONFIG.models,
                 artifacts: Path = CONFIG.artifacts, match_id: str | None = None,
                 max_frames: int = 30, allow_any: bool = False) -> Path:
    """Export one local test game's observed minute states and model forecasts.

    The output is ignored by Git and served only on localhost. It is a replay
    of sampled positions and precisely timed events, never a claim of
    second-level positions or player POV.
    """
    meta = read_json(processed / "meta.json")
    if not meta:
        raise FileNotFoundError("Process matches first")
    mid = match_id or meta["splits"]["test"][0]
    if mid not in meta["counts"] or (not allow_any and mid not in meta["splits"]["test"]):
        raise ValueError("Trace match must belong to the eligible split")
    checkpoint = models / "best.pt"
    checkpoint_hash = hashlib.sha256(checkpoint.read_bytes()).hexdigest()
    raw = processed.parent / "raw"
    match = json.loads((raw / "matches" / f"{mid}.json").read_text())
    catalog_release, catalog, catalog_paths = _cached_patch_items(match, raw)
    source_paths = (processed / "matches" / f"{mid}.npz",
                    raw / "matches" / f"{mid}.json", raw / "timelines" / f"{mid}.json",
                    raw / "manifest.json", processed / "meta.json", *catalog_paths)
    source_hash = _source_fingerprint(*source_paths)
    output = artifacts / "replays" / mid / "trace.json" if allow_any else artifacts / "replay_trace.json"
    existing = read_json(output)
    if (existing and existing.get("schema_version") == TRACE_SCHEMA_VERSION and existing.get("split")
            and existing.get("match_id") == mid and existing.get("checkpoint_sha256") == checkpoint_hash
            and existing.get("source_sha256") == source_hash and existing.get("max_frames") == max_frames
            and existing.get("rows")
            and all((artifacts / "replay_frames" / row["image"]).is_file() for row in existing["rows"])):
        return output
    model = load_model(meta, checkpoint)
    with np.load(processed / "matches" / f"{mid}.npz") as arrays:
        x = torch.from_numpy(arrays["x_oracle" if model.view == "oracle" else "x"].copy())
        champion = torch.from_numpy(arrays["champion"].copy())
        actual = arrays["region"].copy()
        minute = arrays["minute"].copy()
    count = min(max_frames, len(actual))
    timeline = json.loads((raw / "timelines" / f"{mid}.json").read_text())
    inventories = inventory_snapshots(timeline)[0]
    timed_events = [event for frame in (timeline.get("info") or {}).get("frames") or []
                    for event in frame.get("events") or []]
    puuid = read_json(raw / "manifest.json")["account"]["puuid"]
    with torch.no_grad():
        outputs = [model(x[i:i + 128], champion[i:i + 128]) for i in range(0, count, 128)]
        probabilities = torch.cat([o[0].softmax(-1) for o in outputs]).numpy()
        values = torch.cat([o[3].sigmoid() for o in outputs]).numpy()
    vmax = max(.04, float(probabilities.max()))
    folder = artifacts / "replay_frames" / mid if allow_any else artifacts / "replay_frames"
    folder.mkdir(parents=True, exist_ok=True)
    palette = plt.get_cmap("magma")
    rows = []
    for i in range(count):
        p = probabilities[i]
        image = Image.new("RGB", (512, 512), "#091526")
        draw = ImageDraw.Draw(image)
        for region in range(256):
            col, row = region % 16, region // 16
            strength = min(1.0, float(p[region]) / vmax) ** .55
            colour = tuple(int(v * 255) for v in palette(strength)[:3])
            xy = (col * 32, (15 - row) * 32, (col + 1) * 32 - 1, (16 - row) * 32 - 1)
            draw.rectangle(xy, fill=colour, outline="#23334a", width=1)
        current = x[i, -1].numpy()
        for ally in range(5):
            offset = 17 + ally * 9
            if current[offset + 2] <= .5:
                continue
            cx, cy = float(current[offset]) * 512, (1 - float(current[offset + 1])) * 512
            radius = 7 if ally == 0 else 4
            colour = "#5ff0df" if ally == 0 else "#63a5d9"
            draw.ellipse((cx-radius, cy-radius, cx+radius, cy+radius), fill=colour, outline="white", width=1)
            if ally == 0:
                draw.text((min(480, cx + 9), max(2, cy - 17)), "START", fill="#d5fff6", stroke_width=1, stroke_fill="#091526")
        actual_region = int(actual[i])
        guess_region = int(p.argmax())
        for region, colour in ((actual_region, "#ff95bd"), (guess_region, "#ffffff")):
            cx, cy = (region % 16 + .5) * 32, (15 - region // 16 + .5) * 32
            radius = 12 if region == actual_region else 8
            draw.ellipse((cx-radius, cy-radius, cx+radius, cy+radius), outline=colour, width=3)
            draw.text((min(480, cx + radius + 3), max(2, cy - 8)),
                      "REAL" if region == actual_region else "MODEL", fill=colour,
                      stroke_width=1, stroke_fill="#091526")
        filename = f"{mid}/{i:02d}.png" if allow_any else f"{i:02d}.png"
        image.save(folder / f"{i:02d}.png")
        entropy = -float(np.sum(p * np.log(np.maximum(p, 1e-12))) / np.log(256))
        rows.append({"minute": float(minute[i]), **_observed_context(match,timeline,puuid,float(minute[i]),inventories,timed_events),
                     "actual_region": actual_region,
                     "predicted_region": guess_region, "actual_probability": float(p[actual_region]),
                     "predicted_probability": float(p[guess_region]), "forecast_entropy_0_1": entropy,
                     "gold_diff": round(float(current[7] * 30000)), "xp_diff": round(float(current[109] * 50000)),
                     "level": round(float(current[2] * 18)), "cs": round(float(current[4] * 400)),
                     "estimated_final_win_probability": float(values[i]), "image": filename})
    artifacts.mkdir(parents=True, exist_ok=True)
    referenced_items={item for row in rows for actor in (*row["actors_t"],*row["actors_next"])
                      for item in actor["items"]}
    referenced_items.update(event["item_id"] for row in rows
                            for event in (*row["events_initial"],*row["events_next"])
                            if event["item_id"])
    referenced_items.update(event[key] for row in rows
                            for event in (*row["events_initial"],*row["events_next"])
                            for key in ("before_item_id","after_item_id") if event[key])
    item_descriptors={str(item):{"name":str(catalog[str(item)].get("name") or ""),
                                 "cost":int((catalog[str(item)].get("gold") or {}).get("total") or 0),
                                 "tags":list(catalog[str(item)].get("tags") or []),
                                 "kind":_item_kind(catalog[str(item)])}
                      for item in referenced_items if str(item) in catalog}
    atomic_json(output, {"schema_version": TRACE_SCHEMA_VERSION, "match_id": mid, "max_frames": max_frames,
                         "checkpoint_sha256": checkpoint_hash, "source_sha256": source_hash,
                         "source_step_seconds": 60,
                         "played_patch":".".join(str((match.get("info") or {}).get("gameVersion") or "").split(".")[:2]),
                         "item_catalog_release":catalog_release,"item_catalog":item_descriptors,
                         "view": model.view,
                         "split": next(k for k,v in meta["splits"].items() if mid in v),
                         "rows": rows})
    return output


def demo(processed: Path = CONFIG.processed, models: Path = CONFIG.models,
         artifacts: Path = CONFIG.artifacts, match_id: str | None = None, max_frames: int = 30) -> Path:
    meta = read_json(processed / "meta.json")
    if not meta:
        raise FileNotFoundError("Process matches first")
    match_id = match_id or meta["splits"]["test"][0]
    if match_id not in meta["splits"]["test"]:
        raise ValueError("Demo match must belong to the held-out test split")
    model = load_model(meta, models / "best.pt")
    with np.load(processed / "matches" / f"{match_id}.npz") as z:
        x = torch.from_numpy(z["x_oracle" if model.view == "oracle" else "x"].copy())
        champ = torch.from_numpy(z["champion"].copy())
        actual = z["region"].copy()
        minutes = z["minute"].copy()
        won = bool(z["win"][0])
    with torch.no_grad():
        predictions = [model(x[i:i + 128], champ[i:i + 128]) for i in range(0, len(x), 128)]
        probs = torch.cat([out[0].softmax(-1) for out in predictions]).numpy()
        value = torch.cat([out[3].sigmoid() for out in predictions]).numpy()
    frames = min(max_frames, len(actual))
    fig, (ax, value_ax) = plt.subplots(1, 2, figsize=(11.5, 5.8), gridspec_kw={"width_ratios": [1.2, 1]})
    heat = ax.imshow(probs[0].reshape(16, 16), origin="lower", extent=(0, 16, 0, 16), vmin=0, vmax=max(.04, float(probs.max())), cmap="viridis")
    dot_actual, = ax.plot([], [], "ro", markersize=10, label="Actual next region")
    dot_pred, = ax.plot([], [], "wx", markersize=10, markeredgewidth=2, label="Predicted top-1")
    ax.set(xlim=(0, 16), ylim=(0, 16), xlabel="Map grid X", ylabel="Map grid Y")
    ax.legend(loc="upper left")
    fig.colorbar(heat, ax=ax, label="Predicted probability")
    value_ax.plot(minutes, value, color="tab:blue", lw=2, label="Estimated eventual win P")
    value_ax.axhline(float(won), color="tab:green", linestyle="--", alpha=.6, label=f"Final outcome: {'win' if won else 'loss'}")
    marker, = value_ax.plot([], [], "o", color="tab:red", markersize=9)
    value_ax.set(xlim=(0, max(1, float(minutes[-1]))), ylim=(-.03, 1.03), xlabel="Game minute", ylabel="P(eventual win)",
                 title="Estimated eventual win probability\n(state association, not action value)")
    value_ax.legend(loc="lower right", fontsize=8)

    def update(i):
        heat.set_data(probs[i].reshape(16, 16))
        r = int(actual[i]); p = int(probs[i].argmax())
        dot_actual.set_data([r % 16 + .5], [r // 16 + .5])
        dot_pred.set_data([p % 16 + .5], [p // 16 + .5])
        ax.set_title(f"Held-out match {match_id}\nMinute {minutes[i]:.0f}: next region")
        marker.set_data([minutes[i]], [value[i]])
        return heat, dot_actual, dot_pred, marker

    animation = FuncAnimation(fig, update, frames=frames, interval=500, blit=False)
    artifacts.mkdir(parents=True, exist_ok=True)
    output = artifacts / "predicted_vs_actual.gif"
    animation.save(output, writer=PillowWriter(fps=2))
    plt.close(fig)
    return output


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--match-id")
    parser.add_argument("--max-frames", type=int, default=30)
    args = parser.parse_args()
    print(demo(match_id=args.match_id, max_frames=args.max_frames))


if __name__ == "__main__":
    main()
