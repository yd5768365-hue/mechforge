"""
MechForge Work CLI Wrapper

Entry point for the work CLI.
"""


def main() -> None:
    """Main entry point for work CLI"""
    from mechforge_work.work_cli import main as work_main

    work_main()


if __name__ == "__main__":
    main()
