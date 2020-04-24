import asyncio

import click
import uvloop  # type: ignore
from aiohttp_micro.management.server import server  # type: ignore

from apollo.app import AppConfig, init


@click.group()
@click.option("--debug", default=False, is_flag=True)
@click.option("--conf-dir", default=None)
@click.pass_context
def cli(ctx, conf_dir: str = None, debug):
    uvloop.install()
    loop = asyncio.get_event_loop()

    consul_config = ConsulConfig()
    load(consul_config, providers=[EnvValueProvider()])

    config = AppConfig(
        defaults={
            "consul": consul_config,
            "debug": debug,
        }
    )

    if conf_dir:
        conf_path = Path(conf_dir)
    else:
        conf_path = Path.cwd()

    load_from_file(config, path=conf_path / "config.json")
    load(config, providers=[FileValueProvider(conf_path), EnvValueProvider()])

    app = loop.run_until_complete(init("apollo", config))

    ctx.obj["app"] = app
    ctx.obj["config"] = config
    ctx.obj["loop"] = loop


cli.add_command(server, name="server")


if __name__ == "__main__":
    cli(obj={})
