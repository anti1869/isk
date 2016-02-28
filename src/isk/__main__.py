"""
Isk entry point with CLI
"""

from sunhead.cli.commands.runserver import Runserver
from sunhead.cli.entrypoint import main as sunhead_main


commands = (
    Runserver("isk.web.server.IskHTTPServer"),
)


DEFAULT_ENVIRONMENT_VARIABLE = "ISK_SETTINGS_MODULE"
GLOBAL_CONFIG_MODULE = "isk.global_settings"


def main():
    sunhead_main(
        commands=commands,
        settings_ennvar=DEFAULT_ENVIRONMENT_VARIABLE,
        fallback_settings_module=GLOBAL_CONFIG_MODULE
    )


if __name__ == '__main__':
    main()
