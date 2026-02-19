import streamlit as st
import pandas as pd
import json
import time
import os
import subprocess
import random

# --- CONFIGURATION ---
st.set_page_config(page_title="Phoenix Mission Control", layout="wide", page_icon="🔥")

# Paths
METRICS_FILE = "phoenix_metrics.json"
PROJECT_ROOT = os.path.join("..", "target-app")

# --- CUSTOM CSS (Cyberpunk Theme) ---
st.markdown("""
    <style>
        .stMetric { background-color: #0E1117; border: 1px solid #30333F; padding: 15px; border-radius: 5px; }
        .stAlert { padding: 10px; border-radius: 5px; }
        h1, h2, h3 { font-family: 'Segoe UI', sans-serif; }
    </style>
""", unsafe_allow_html=True)

# Header
col_logo, col_title = st.columns([1, 6])
with col_logo:
    st.markdown("<h1>🔥</h1>", unsafe_allow_html=True)
with col_title:
    st.title("Phoenix: Autonomous Infrastructure Agent")
    st.markdown("**Live Observability & Self-Healing Engine**")

# --- DATA LOADERS ---
def load_metrics():
    if not os.path.exists(METRICS_FILE): return []
    try:
        with open(METRICS_FILE, "r") as f: return json.load(f)
    except: return []

def get_git_graph_data():
    """Fetches commit data suitable for building a graph."""
    try:
        # Get last 7 commits: Hash | ParentHash | Subject | Time
        cmd = 'git log -7 --pretty=format:"%h|%p|%s|%cr"'
        log = subprocess.check_output(cmd, cwd=PROJECT_ROOT, shell=True).decode()
        commits = []
        for line in log.split('\n'):
            if "|" in line:
                parts = line.split("|")
                commits.append({
                    "id": parts[0],
                    "parent": parts[1].split()[0] if parts[1] else None, # Take first parent
                    "msg": parts[2],
                    "time": parts[3]
                })
        return commits
    except: return []

# --- TELEMETRY SIMULATION ---
if "cpu_history" not in st.session_state:
    st.session_state.cpu_history = [random.randint(20, 40) for _ in range(50)]
if "mem_history" not in st.session_state:
    st.session_state.mem_history = [random.randint(400, 500) for _ in range(50)]

def update_telemetry():
    new_cpu = random.randint(20, 45)
    if random.random() > 0.9: new_cpu += 30
    st.session_state.cpu_history.append(new_cpu)
    st.session_state.cpu_history.pop(0)
    
    new_mem = st.session_state.mem_history[-1] + random.randint(-5, 10)
    if new_mem > 800: new_mem = 400
    st.session_state.mem_history.append(new_mem)
    st.session_state.mem_history.pop(0)

# --- MAIN LOOP ---
placeholder = st.empty()

while True:
    data = load_metrics()
    commits = get_git_graph_data()
    update_telemetry()
    
    with placeholder.container():
        # --- ROW 1: KPI ---
        crashes = [d for d in data if d['event'] == 'CRASH']
        fixes = [d for d in data if d['event'] == 'FIX']
        
        mttr = 0
        if fixes:
            mttr = round(sum(f['duration_seconds'] for f in fixes) / len(fixes), 2)

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("🔥 Active Incidents", "0" if len(crashes) == len(fixes) else "1", delta_color="inverse")
        m2.metric("🛡️ Total Auto-Heals", len(fixes))
        m3.metric("⏱️ MTTR", f"{mttr}s", delta="-0.2s")
        m4.metric("🤖 AI Model", "GPT-4o", "Active")

        st.divider()

        # --- ROW 2: TELEMETRY & ARCHITECTURE ---
        t1, t2, t3 = st.columns([2, 2, 1.5])
        with t1:
            st.subheader("🖥️ CPU Load")
            st.area_chart(st.session_state.cpu_history, height=150, color="#FF4B4B")
        with t2:
            st.subheader("💾 Memory Usage")
            st.area_chart(st.session_state.mem_history, height=150, color="#00FFAA")
        with t3:
            st.subheader("System Architecture")
            st.graphviz_chart('''
                digraph {
                    rankdir=LR; bgcolor="#0E1117";
                    node [shape=box, style=filled, fillcolor="#262730", fontcolor="white", fontname="sans-serif"];
                    edge [color="gray"];
                    App [label="Spring Boot", fillcolor="#d62728"];
                    Sup [label="Supervisor", fillcolor="#1f77b4"];
                    AI [label="GPT-4o", fillcolor="#9467bd"];
                    Git [label="GitOps", fillcolor="#2ca02c"];
                    App -> Sup -> AI -> Git -> App;
                }
            ''')

        # --- ROW 3: METRICS & VISUAL GIT TREE ---
        b1, b2 = st.columns([1, 1])

        with b1:
            st.subheader("📈 Recovery Analysis")
            if fixes:
                df = pd.DataFrame(fixes)
                st.bar_chart(df, x="timestamp", y="duration_seconds", color="#4B0082")
            else:
                st.info("System Healthy. Waiting for events...")

            st.subheader("📝 Live Logs")
            if data:
                last = data[-1]
                if last['event'] == 'CRASH': st.error(f"🚨 {last['details']}")
                elif last['event'] == 'FIX': st.success(f"✅ {last['details']} ({last['duration_seconds']}s)")
                else: st.info(f"ℹ️ {last['details']}")
            else:
                st.text("Initializing...")

        with b2:
            st.subheader("🐙 Live Git Topology")
            # DYNAMIC GRAPH GENERATION
            if commits:
                dot_code = 'digraph G {\n'
                dot_code += '  rankdir=TB;\n' # Top to Bottom
                dot_code += '  bgcolor="#0E1117";\n'
                dot_code += '  node [shape=note, style=filled, fontname="sans-serif", fontcolor="white"];\n'
                dot_code += '  edge [color="#555555"];\n'

                for c in commits:
                    # Color Logic: Green for Fixes, Blue for regular
                    fill = "#2ca02c" if "AI Auto-Fix" in c['msg'] else "#1f77b4"
                    label = f"{c['msg']}\\n({c['time']})"
                    # Clean label for Graphviz (remove special chars)
                    label = label.replace('"', '').replace("'", "")
                    
                    dot_code += f'  "{c["id"]}" [label="{label}", fillcolor="{fill}"];\n'
                    
                    # Draw Edge to Parent
                    if c['parent']:
                        # Only draw if parent is in our list (to avoid broken graphs)
                        if any(pc['id'] == c['parent'] for pc in commits):
                             dot_code += f'  "{c["id"]}" -> "{c["parent"]}";\n'

                dot_code += '}'
                st.graphviz_chart(dot_code)
            else:
                st.text("Waiting for Git history...")

    time.sleep(1)
