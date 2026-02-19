from phoenix.config import PhoenixConfig
from phoenix.paths import CONFIG_DIR
from phoenix.supervisor import Supervisor

def main():
    config = PhoenixConfig(CONFIG_DIR / "phoenix.yaml")
    supervisor = Supervisor(config)

    supervisor.start()

    for log in supervisor.stream_logs():
        print("[APP]", log)

if __name__ == "__main__":
    main()
