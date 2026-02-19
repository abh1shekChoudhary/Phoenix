import os
import re
import time
import subprocess
import json
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI

# --- CONFIGURATION ---
load_dotenv(dotenv_path="../.env")
API_KEY = os.getenv("OPENAI_API_KEY")

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
TARGET_APP_DIR = os.path.join(PROJECT_ROOT, "..", "target-app")
LOG_FILE = os.path.join(PROJECT_ROOT, "phoenix.log")
METRICS_FILE = os.path.join(PROJECT_ROOT, "phoenix_metrics.json")

if not API_KEY:
    raise ValueError("CRITICAL: OPENAI_API_KEY not found in .env file!")

client = OpenAI(api_key=API_KEY)

# --- METRICS ---
def log_metric(event_type, details=None, duration=0):
    entry = {
        "timestamp": datetime.now().isoformat(),
        "event": event_type, 
        "details": details,
        "duration_seconds": duration
    }
    data = []
    if os.path.exists(METRICS_FILE):
        try:
            with open(METRICS_FILE, "r") as f: data = json.load(f)
        except: data = []
    data.append(entry)
    with open(METRICS_FILE, "w") as f: json.dump(data, f, indent=2)

def log_event(message):
    timestamp = time.strftime("[%H:%M:%S]")
    print(f"{timestamp} {message}")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{timestamp} {message}\n")

# --- GIT ---
def ensure_git_repo():
    git_dir = os.path.join(TARGET_APP_DIR, ".git")
    if not os.path.exists(git_dir):
        log_event("⚙️ [GIT] Initializing repository...")
        subprocess.run("git init", cwd=TARGET_APP_DIR, shell=True)
        subprocess.run("git add .", cwd=TARGET_APP_DIR, shell=True)
        subprocess.run('git commit -m "Initial State"', cwd=TARGET_APP_DIR, shell=True)

def commit_fix(file_name, branch_name):
    try:
        subprocess.run(f"git checkout -b {branch_name}", cwd=TARGET_APP_DIR, shell=True)
        subprocess.run("git add .", cwd=TARGET_APP_DIR, shell=True)
        subprocess.run(f'git commit -m "AI Auto-Fix for {file_name}"', cwd=TARGET_APP_DIR, shell=True)
        subprocess.run("git checkout master", cwd=TARGET_APP_DIR, shell=True)
        subprocess.run(f"git merge {branch_name}", cwd=TARGET_APP_DIR, shell=True)
        log_event("✅ [GIT] Merge Successful.")
    except Exception as e:
        log_event(f"❌ [GIT ERROR] {e}")

# --- THE BRAIN (Now reads Configs too!) ---
class ProjectBrain:
    def __init__(self, root_dir):
        self.root_dir = root_dir
        self.file_map = {} 
        self.full_context = "" 

    def scan_codebase(self):
        self.file_map = {}
        self.full_context = ""
        
        # 1. Scan Source Code
        src_path = os.path.join(self.root_dir, "src")
        for root, dirs, files in os.walk(src_path):
            for file in files:
                if file.endswith(".java") or file.endswith(".properties"):
                    full_path = os.path.join(root, file)
                    self.file_map[file] = full_path
                    with open(full_path, "r", encoding="utf-8") as f:
                        self.full_context += f"\n--- FILE: {file} ---\n{f.read()}\n"

        # 2. Scan Root Configs (pom.xml)
        for root_file in ["pom.xml"]:
            full_path = os.path.join(self.root_dir, root_file)
            if os.path.exists(full_path):
                self.file_map[root_file] = full_path
                with open(full_path, "r", encoding="utf-8") as f:
                    self.full_context += f"\n--- FILE: {root_file} ---\n{f.read()}\n"

    def get_context(self): return self.full_context
    def get_file_path(self, filename):
        # Exact match first
        if filename in self.file_map: return self.file_map[filename]
        # Fuzzy match
        for f, path in self.file_map.items():
            if filename in f: return path
        return None

def ai_triage_error(error_line):
    prompt = f"""
    Analyze this Java Log: "{error_line}"
    Is it a Critical System Crash (Startup Fail, Port in Use, NullPointer) -> Reply "CRASH"
    Is it a Safe User Validation Error (IllegalArgument, BadRequest) -> Reply "SAFE"
    Reply ONLY with the word.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=5,
            temperature=0
        )
        return "CRASH" in response.choices[0].message.content.strip().upper()
    except: return True 

# --- AI HEALER ---
def heal_project(crash_log, context_hint, brain, start_time):
    log_event(f"🚑 [PHOENIX] Diagnosing issue related to {context_hint}...")
    brain.scan_codebase()
    
    # Updated Prompt to handle Configs
    system_prompt = """You are an Expert SRE. 
    1. Analyze the CRASH LOG.
    2. If it's a code bug, fix the Java file.
    3. If it's a Config issue (Port in use), change 'application.properties' (e.g. server.port=8081).
    4. Return ONLY the code inside ```java ... ``` or ```properties ... ``` blocks.
    5. Start response with 'FILE: <filename>'."""
    
    user_prompt = f"PROJECT:\n{brain.get_context()}\nCRASH:\n{crash_log}\nTASK: Fix the issue."

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]
        )
        ai_reply = response.choices[0].message.content
        
        lines = ai_reply.split('\n')
        target_file = None
        for line in lines:
            if "FILE:" in line:
                fname = line.split("FILE:")[1].strip()
                target_file = brain.get_file_path(fname)
        
        if not target_file and context_hint:
             target_file = brain.get_file_path(context_hint)

        if target_file:
            # Extract content from code blocks (java, xml, properties)
            content = re.search(r"```\w+\n(.*?)```", ai_reply, re.DOTALL)
            if content:
                fixed_code = content.group(1).strip()
                with open(target_file, "w", encoding="utf-8") as f:
                    f.write(fixed_code)
                
                log_event(f"💾 [DISK] Patch applied to {os.path.basename(target_file)}")
                
                end_time = time.time()
                recovery_time = round(end_time - start_time, 2)
                log_metric("FIX", f"Fixed {os.path.basename(target_file)}", recovery_time)
                commit_fix(os.path.basename(target_file), f"fix/auto-{int(time.time())}")
                return True
            
    except Exception as e:
        log_event(f"❌ [AI ERROR] {e}")
        return False

# --- SUPERVISOR ---
def run_supervisor():
    open(LOG_FILE, "w").close()
    ensure_git_repo()
    brain = ProjectBrain(TARGET_APP_DIR)
    
    log_event("🚀 [PHOENIX] Supervisor Active (Universal Mode).")
    log_metric("START", "System Online")

    mvn_cmd = "mvn.cmd" if os.name == 'nt' else "mvn"
    cmd = f"{mvn_cmd} spring-boot:run -Dmaven.test.skip=true"

    while True:
        log_event("⚙️ [SYSTEM] Booting App...")
        process = subprocess.Popen(cmd, cwd=TARGET_APP_DIR, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        
        stack_trace_regex = re.compile(r"at\s+([a-zA-Z0-9_.]+)\.[a-zA-Z0-9_]+\((.+\.java):(\d+)\)")
        crash_buffer = []

        try:
            for line in iter(process.stdout.readline, ''):
                line = line.strip()
                if not line: continue
                log_event(f"[APP] {line}")
                
                crash_buffer.append(line)
                if len(crash_buffer) > 50: crash_buffer.pop(0)

                # TRIGGER 1: Standard Stack Trace
                if "at " in line and "com.example" in line:
                    full_log = "\n".join(crash_buffer[-10:])
                    if not ai_triage_error(full_log):
                        log_event("🛡️ [AI TRIAGE] Classification: SAFE. Ignoring.")
                        continue

                    match = stack_trace_regex.search(line)
                    if match:
                        crash_start_time = time.time()
                        crashed_class = match.group(1).split(".")[-1] # Just class name
                        
                        log_event(f"\n🔥 [ALARM] RUNTIME CRASH: {crashed_class}")
                        log_metric("CRASH", crashed_class)
                        
                        subprocess.run(f"taskkill /F /T /PID {process.pid}", shell=True)
                        if heal_project("\n".join(crash_buffer), crashed_class, brain, crash_start_time):
                            log_event("🔄 [REBOOT] Restarting...")
                            break

                # TRIGGER 2: Startup Failures (Port in use, etc.)
                if "APPLICATION FAILED TO START" in line:
                    crash_start_time = time.time()
                    log_event("\n🔥 [ALARM] STARTUP FAILURE DETECTED")
                    log_metric("CRASH", "Startup Failure")
                    
                    # Capture the reason (usually lines before this)
                    full_error = "\n".join(crash_buffer)
                    
                    subprocess.run(f"taskkill /F /T /PID {process.pid}", shell=True)
                    
                    # Hint to check properties if no class found
                    if heal_project(full_error, "application.properties", brain, crash_start_time):
                        log_event("🔄 [REBOOT] Restarting...")
                        break

        except KeyboardInterrupt:
            subprocess.run(f"taskkill /F /T /PID {process.pid}", shell=True)
            break

if __name__ == "__main__":
    run_supervisor()
