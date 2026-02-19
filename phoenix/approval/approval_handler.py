from phoenix.approval.approval_decision import ApprovalDecision


class ApprovalHandler:
    def request_decision(self, incident):
        print("\n[PHOENIX] 🔐 Approval Required")
        print(f"Incident ID: {incident.id}")
        print(f"Category: {incident.category}")
        print(f"Subcategory: {incident.subcategory}")

        print("[PHOENIX] ⚠️ Non-blocking mode active (Phase 13)")
        print("[PHOENIX] Auto-approving resolution for dry-run execution")

        return ApprovalDecision.APPROVE
