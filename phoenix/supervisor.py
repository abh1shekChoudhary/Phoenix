import subprocess
import time
from datetime import datetime, timedelta
from pathlib import Path
import hashlib

from phoenix.config import PhoenixConfig
from phoenix.log_buffer import LogBuffer
from phoenix.detectors import FailureDetector

from phoenix.incident_manager import IncidentManager
from phoenix.incident_reasoner import IncidentReasoner
from phoenix.decision_policy import DecisionPolicy

from phoenix.execution.executor import Executor
from phoenix.execution.execution_plan_builder import ExecutionPlanBuilder
from phoenix.patching.patch_generator import PatchGenerator

from phoenix.approval.approval_handler import ApprovalHandler
from phoenix.approval.approval_decision import ApprovalDecision

from phoenix.persistence.incident_repository import IncidentRepository
from phoenix.persistence.incident_state import IncidentState

from phoenix.context_resolver import JavaContextResolver
from phoenix.stacktrace_collector import JavaStackTraceCollector
from phoenix.context_expander import ContextExpander

from phoenix.resolution.resolution_builder import ResolutionBuilder
from phoenix.ai_diagnoser import AIDiagnoser

from phoenix.escalation.fix_failure_evaluator import FixFailureEvaluator
from phoenix.strategy.strategy_manager import StrategyManager

from phoenix.learning.strategy_performance_repository import (
    StrategyPerformanceRepository,
)
from phoenix.learning.strategy_optimizer import StrategyOptimizer

from phoenix.classifier import FailureClassifier


COOLDOWN_MINUTES = 5


class Supervisor:
    def __init__(self, config: PhoenixConfig):
        self.config = config
        self.process = None

        # Core
        self.buffer = LogBuffer()
        self.detector = FailureDetector()

        # Lifecycle
        self.incident_manager = IncidentManager()
        self.reasoner = IncidentReasoner()
        self.policy = DecisionPolicy()

        # AI
        self.ai_diagnoser = AIDiagnoser()

        # Resolution
        self.resolution_builder = ResolutionBuilder()
        self.patch_generator = PatchGenerator()
        self.executor = Executor()
        self.execution_plan_builder = ExecutionPlanBuilder()

        # Escalation & Strategy
        self.fix_failure_evaluator = FixFailureEvaluator()
        self.strategy_manager = StrategyManager()

        # Approval
        self.approval_handler = ApprovalHandler()

        # Persistence
        self.repository = IncidentRepository(
            Path("phoenix_data/incidents.json")
        )

        self.strategy_repo = StrategyPerformanceRepository(
            Path("phoenix_data/strategy_performance.json")
        )

        self.strategy_optimizer = StrategyOptimizer(self.strategy_repo)

        # Diagnostics
        self.classifier = FailureClassifier()

        # Stack trace
        self.stacktrace_collector = JavaStackTraceCollector()

        # Context
        self.context_resolver = JavaContextResolver(
            project_root=Path(
                self.config.get("execution", "working_directory")
            ),
            token_budget=self.config.get(
                "ai", "max_tokens_per_request", default=4000
            ),
        )

    # ---------------------------------------------------------

    def start(self):
        cmd = self.config.get("execution", "start_command")
        cwd = self.config.get("execution", "working_directory")

        if not cmd:
            raise ValueError("No start_command defined in config")

        if not cwd or not Path(cwd).exists():
            raise ValueError(f"Invalid working_directory: {cwd}")

        print(f"[Phoenix] Starting process: {cmd}")

        self.process = subprocess.Popen(
            cmd,
            cwd=cwd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )

    # ---------------------------------------------------------

    def stream_logs(self):
        if not self.process:
            raise RuntimeError("Process not started")

        for line in self.process.stdout:
            line = line.rstrip()

            self.buffer.add(line)
            self.stacktrace_collector.process(line)

            signal = self.detector.detect(line, self.buffer)
            if not signal:
                yield line
                continue

            print("\n[PHOENIX] ⚠️ Failure Signal Detected")

            incident, is_new = self.incident_manager.ingest(signal)
            incident = self.reasoner.reason(incident)
            incident.decision = self.policy.decide(incident)

            now = datetime.utcnow()
            signal_ts = time.time()
            # --------------------------------------------------
            # STRATEGY AUTO-SELECTION (Phase 14.3A)
            # --------------------------------------------------

            if incident.state == IncidentState.DETECTED and incident.failure_fingerprint:

                best_version = self.strategy_optimizer.get_best_strategy(
                    incident.failure_fingerprint
                )

                if incident.strategy_version != best_version:
                    incident.strategy_version = best_version

                    print(
                        f"[PHOENIX] 🧠 Selected Strategy V{best_version} "
                        f"based on historical performance"
                    )


            # ==================================================
            # FIX FAILURE + STRATEGY EVOLUTION
            # ==================================================

            current_fp = incident.failure_fingerprint

            if current_fp:
                if self.fix_failure_evaluator.evaluate(
                    incident,
                    signal_ts,
                    current_fp,
                ):
                    print(
                        f"[PHOENIX] 🔁 Fix failure detected "
                        f"(count={incident.post_fix_reoccurrence_count})"
                    )

                    # 🔴 RECORD FAILURE FOR LEARNING
                    self.strategy_repo.record(
                        fingerprint=current_fp,
                        strategy_version=incident.strategy_version,
                        success=False,
                    )

                    action = self.strategy_manager.evaluate(incident)

                    if action == "UPGRADE":
                        print(
                            f"[PHOENIX] 🚀 Strategy upgraded to V{incident.strategy_version}"
                        )

                    elif action == "LOCK":
                        print(
                            "[PHOENIX] ⛔ Strategy LOCKED — manual intervention required"
                        )
                        incident.strategy_locked = True
                        incident.decision = "ESCALATE_TO_HUMAN"

            # ==================================================
            # MONITORING / COOLDOWN
            # ==================================================

            if incident.state == IncidentState.MONITORING:
                if incident.cooldown_until and now < incident.cooldown_until:
                    print(
                        f"[PHOENIX] 🛡 Incident stabilized "
                        f"(ID: {incident.id}), monitoring only"
                    )
                    self.repository.persist(incident)
                    yield line
                    continue
                else:
                    print("[PHOENIX] ✅ Cooldown complete — resetting strategy state")

                    incident.post_fix_reoccurrence_count = 0
                    incident.strategy_version = 1
                    incident.strategy_locked = False
                    incident.state = IncidentState.DETECTED

            # ==================================================
            # ENRICHMENT
            # ==================================================

            if is_new:
                incident.state = IncidentState.ENRICHING
                incident.enrichment_started_at = time.time()

                print("\n[PHOENIX] 🚨 New Incident Detected")
                print(f"  ID: {incident.id}")
                print(f"  Category: {incident.category}")
                print(f"  Subcategory: {incident.subcategory}")

            trace = self.stacktrace_collector.flush_if_any()
            if trace:
                incident.has_stacktrace = True
                incident.last_enriched_at = time.time()
                print("[PHOENIX] 🧵 Stack trace completed")

                if not incident.context_expanded:
                    context = self.context_resolver.resolve_from_stacktrace(trace)
                    expander = ContextExpander(incident.token_budget)

                    for f in context.files:
                        expanded = expander.expand(f)
                        incident.context_summary = expanded.summary
                        incident.has_context = True

                        print("[PHOENIX] 🧠 Context Summary")
                        print(expanded.summary)

                    incident.context_expanded = True

            if (
                incident.has_stacktrace
                and incident.has_context
                and incident.confidence >= 0.6
                and incident.state == IncidentState.ENRICHING
            ):
                incident.state = IncidentState.READY
                print("[PHOENIX] ✅ Incident READY for resolution")

            if incident.state != IncidentState.READY:
                self.repository.persist(incident)
                yield line
                continue

            # ==================================================
            # ANALYSIS
            # ==================================================

            diagnosis = self.ai_diagnoser.diagnose(incident)
            print("[PHOENIX] 🧠 AI Diagnosis")
            print(f"  Root cause: {diagnosis.likely_root_cause}")

            # ==================================================
            # RESOLUTION
            # ==================================================

            incident.state = IncidentState.ANALYZED
            resolution = self.resolution_builder.build(incident)
            incident.resolution_plan = resolution
            incident.state = IncidentState.PLANNED

            print("[PHOENIX] 📦 Resolution Plan")
            print(
                f"  Problem: {resolution.problem_summary} "
                f"(Strategy V{incident.strategy_version})"
            )

            # ==================================================
            # APPROVAL
            # ==================================================

            incident.state = IncidentState.AWAITING_APPROVAL
            decision = self.approval_handler.request_decision(incident)

            if decision == ApprovalDecision.APPROVE:
                incident.state = IncidentState.RESOLVED

                incident.fix_attempted = True
                incident.last_fix_attempt_at = time.time()
                incident.post_fix_reoccurrence_count = 0

                # 🟢 RECORD SUCCESS
                self.strategy_repo.record(
                    fingerprint=current_fp,
                    strategy_version=incident.strategy_version,
                    success=True,
                )

                fp_source = (
                    resolution.problem_summary
                    + str([a.description for a in resolution.actions])
                )

                incident.fix_fingerprint = hashlib.sha256(
                    fp_source.encode()
                ).hexdigest()

                patches = self.patch_generator.generate(incident)
                if patches:
                    print("[PHOENIX] 🧩 Generated Patches")
                    for p in patches:
                        print(p.diff)

                execution_plan = self.execution_plan_builder.build(
                    incident_id=incident.id,
                    resolution=resolution,
                )

                self.executor.execute(execution_plan)

                incident.executed_at = now
                incident.cooldown_until = now + timedelta(minutes=COOLDOWN_MINUTES)
                incident.state = IncidentState.MONITORING

            elif decision == ApprovalDecision.REJECT:
                incident.state = IncidentState.CLOSED

                # 🔴 RECORD REJECTION AS FAILURE
                self.strategy_repo.record(
                    fingerprint=current_fp,
                    strategy_version=incident.strategy_version,
                    success=False,
                )

            self.repository.persist(incident)

            classification = self.classifier.classify(signal)
            print("[PHOENIX] 📊 Diagnostic Classification")
            print(classification)
            print()

            yield line
