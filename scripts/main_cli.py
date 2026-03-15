"""
MechForge AI CLI

Entry point for the CLI.
"""

import sys


def main() -> None:
    """Main entry point"""
    if "-k" in sys.argv or "--k" in sys.argv or "k" in sys.argv:
        # Knowledge mode
        from mechforge_knowledge.cli import main as knowledge_main

        knowledge_main()
    else:
        # Chat mode
        from mechforge_ai.terminal import MechForgeTerminal

        terminal = MechForgeTerminal()
        terminal.start()


if __name__ == "__main__":
    main()
