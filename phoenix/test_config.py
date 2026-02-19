from phoenix.config import PhoenixConfig
from phoenix.paths import CONFIG_DIR

cfg = PhoenixConfig(CONFIG_DIR / "phoenix.yaml")

print(cfg.get("runtime", "language"))
print(cfg.get("execution", "start_command"))
print(cfg.get("ai", "max_tokens_per_request"))
