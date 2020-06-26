import click

from .time import Time


@click.group()
def main():
    pass


@main.command()
def test():
    now = Time.now()
    print(now)
    print(now.utc)
    print(now.tai)
    print(now.jdtai)
    print(now.mjdtai)
    print(now.tt)
    print(now.jdtt)
    print(now.mjdtt)
    print(now.tcg)
    print(now.jdtcg)
    print(now.mjdtcg)
    print(now.tdb)
    print(now.jdtdb)
    print(now.mjdtdb)
