"""
MechForge AI Knowledge CLI

Entry point for the knowledge CLI.
"""


def main() -> None:
    """Main entry point for knowledge CLI"""
    from mechforge_knowledge.cli import main as knowledge_main

    knowledge_main()


if __name__ == "__main__":
    main()
