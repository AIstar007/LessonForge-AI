import argparse
from service import run_agent


def main():
    parser = argparse.ArgumentParser(description="Self-Evaluating Lesson Content Generator")
    parser.add_argument("--topic", required=True)
    parser.add_argument("--inject-error", action="store_true")
    args = parser.parse_args()

    result = run_agent(args.topic, args.inject_error)

    print("\n" + "=" * 70)
    print("RUN ID:", result["run_id"])
    print("STATUS:", result["status"])
    print("ATTEMPTS USED:", result["attempts_used"])
    print("=" * 70)

    print("\nFINAL LESSON\n")
    print(result["lesson"])

    print("\nREJECTION LOG\n")
    if not result["rejection_log"]:
        print("No rejection. First attempt passed all hard gates.")
    else:
        for item in result["rejection_log"]:
            print(f"Attempt {item['attempt']}")
            for check, reason, fix in zip(
                item["failed_checks"], item["reasons"], item["changes_requested"]
            ):
                print(f"- {check}: {reason}")
                print(f"  Fix: {fix}")


if __name__ == "__main__":
    main()
