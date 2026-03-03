from __future__ import annotations

import argparse

from .graph import build_report_graph


def main() -> None:
    parser = argparse.ArgumentParser(description="行业调研报告 Agent")
    parser.add_argument("topic", help="调研主题")
    parser.add_argument("--audience", default="管理层")
    parser.add_argument("--constraints", default="")
    args = parser.parse_args()

    app = build_report_graph()
    result = app.invoke(
        {
            "topic": args.topic,
            "audience": args.audience,
            "constraints": args.constraints,
            "revision_count": 0,
        }
    )
    print(result.get("final_report") or result.get("draft_report") or "")


if __name__ == "__main__":
    main()
