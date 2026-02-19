class JavaStackTraceCollector:
    def __init__(self):
        self.lines = []
        self.active = False
        self.seen_stack_frame = False
        self.last_trace = None

    def process(self, line: str):
        stripped = line.strip()

        # START condition
        if not self.active:
            if (
                "Exception" in line
                or "Error" in line
                or "APPLICATION FAILED TO START" in line
            ):
                self.lines = [line]
                self.active = True
                self.seen_stack_frame = False
                return None

        # CONTINUATION
        if self.active:
            if stripped.startswith("at ") or stripped.startswith("Caused by"):
                self.lines.append(line)
                self.seen_stack_frame = True
                return None

            # Exception header line
            if "Exception" in stripped and not self.seen_stack_frame:
                self.lines.append(line)
                return None

            # END condition
            if self.seen_stack_frame:
                self.last_trace = self.lines[:]
                self.lines = []
                self.active = False
                self.seen_stack_frame = False
                return None

            self.lines.append(line)

        return None

    def flush_if_any(self):
        """
        Returns the last completed stack trace once, then clears it.
        """
        trace = self.last_trace
        self.last_trace = None
        return trace
