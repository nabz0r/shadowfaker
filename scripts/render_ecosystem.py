#!/usr/bin/env python3
"""Static public figures from aggregate pressure and synthetic scenario data."""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"docs"/"data"
FIGURES=ROOT/"docs"/"figures"
BG="#100c13";PANEL="#24141f";TEXT="#fff8f5";MUTED="#ceb7c0";RED="#ff536b";GOLD="#ffd895"

def style(ax):
    ax.set_facecolor(PANEL)
    ax.tick_params(colors=MUTED)
    for spine in ax.spines.values(): spine.set_color("#815164")
    ax.grid(axis="y",color="#754456",alpha=.35)

def pressure():
    data=json.loads((DATA/"public_pressure.json").read_text())
    phases=[data["phases"][p] for p in ("early","middle","late")]
    fig,axes=plt.subplots(1,2,figsize=(14,5.6),facecolor=BG)
    for ax in axes: style(ax)
    x=np.arange(3);width=.34
    axes[0].bar(x-width/2,[p["mean_near_enemies"] for p in phases],width,color=RED,label="Enemy players within 2,500 units")
    axes[0].bar(x+width/2,[p["arrival_rate_per_frame"] for p in phases],width,color=GOLD,label="Entries into radius per frame")
    axes[0].set_xticks(x,["0–10 min","10–20 min","20+ min"])
    axes[0].set_title("Opponent presence changes by phase",color=TEXT,fontsize=16,weight="bold")
    axes[0].legend(facecolor=PANEL,edgecolor="#815164",labelcolor=TEXT,fontsize=9)
    keys=("0/1","0/2","other");slices=data["score_slices"]
    axes[1].bar(keys,[slices[k]["mean_near_enemies"] for k in keys],color=(GOLD,RED,"#b7718c"))
    for i,key in enumerate(keys):
        axes[1].text(i,slices[key]["mean_near_enemies"]+.025,f"n={slices[key]['frames']:,}",ha="center",color=MUTED,fontsize=10)
    axes[1].set_ylim(0,max(slices[k]["mean_near_enemies"] for k in keys)*1.25)
    axes[1].set_title("Faker at 0/1 or 0/2: observed proximity",color=TEXT,fontsize=16,weight="bold")
    fig.suptitle("THE OTHER FIVE · local pressure around Faker",x=.045,ha="left",color=TEXT,fontsize=19,weight="bold")
    fig.text(.045,.025,"Descriptive proximity from full timelines; no spell-use, intent, or causal claim. Score slices differ in game phase.",color=MUTED,fontsize=9)
    fig.subplots_adjust(left=.055,right=.98,bottom=.2,top=.78,wspace=.2)
    fig.savefig(FIGURES/"enemy_pressure.png",dpi=180,facecolor=BG);plt.close(fig)

def challenge():
    data=json.loads((DATA/"challenge_scenarios.json").read_text())
    fig,ax=plt.subplots(figsize=(13,5.6),facecolor=BG);style(ax)
    palette={"five_top":"#e392ac","five_mid":"#f36b8a","five_jungle":"#ffd895","five_bot":"#b5637f","five_faker":"#ff536b"}
    for key in palette:
        rows=data["scenarios"][key]["2"]["0.7"]
        ax.plot([r["minute"] for r in rows],[r["composite"] for r in rows],lw=3,color=palette[key],label=key.replace("five_","5 "))
    ax.set(xlabel="Game minute",ylabel="Synthetic composite · arbitrary 0–1 units",ylim=(0,1))
    ax.xaxis.label.set_color(MUTED);ax.yaxis.label.set_color(MUTED)
    ax.legend(facecolor=PANEL,edgecolor="#815164",labelcolor=TEXT,ncol=5,fontsize=10,loc="upper center")
    fig.suptitle("FIVE FORMATIONS · a thought experiment",x=.06,ha="left",color=TEXT,fontsize=20,weight="bold")
    fig.text(.06,.025,"Synthetic allocations with a 10-minute opponent reaction and 70% resource sharing. Not calibrated to games or win rates.",color=MUTED,fontsize=9)
    fig.subplots_adjust(left=.08,right=.98,bottom=.2,top=.76)
    fig.savefig(FIGURES/"challenge_scenarios.png",dpi=180,facecolor=BG);plt.close(fig)

if __name__=="__main__":
    FIGURES.mkdir(parents=True,exist_ok=True)
    pressure();challenge()
    print("Rendered enemy pressure and synthetic formation figures")
