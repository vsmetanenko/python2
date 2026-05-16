import asyncio
import argparse
import logging
from aiopath import AsyncPath
from aioshutil import copyfile


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Сортування файлів"
    )
    parser.add_argument(
        "source",
        type=str,
        help="Шлях до початкової папки",
    )
    parser.add_argument(
        "output",
        type=str,
        help="Шлях до папки призначення",
    )
    return parser.parse_args()


async def main() -> None:
    args = parse_args()

    source = AsyncPath(args.source)
    output = AsyncPath(args.output)

    if not await source.exists() or not await source.is_dir():
        logger.error("Source folder '%s' does not exist or is not a directory.", source)
        return

    await output.mkdir(parents=True, exist_ok=True)

    await read_folder(source, output)
    logger.info("Done.")



async def read_folder(source: AsyncPath, output: AsyncPath) -> None:
    files = []
    async for item in source.rglob("*"):
        if await item.is_file():
            files.append(item)

    async with asyncio.TaskGroup() as tg:
        for file in files:
            tg.create_task(copy_file(file, output))


async def copy_file(file: AsyncPath, output: AsyncPath) -> None:
    try:
        suf = "".join(AsyncPath(file).suffix).lower()
        folder_name = suf.lstrip(".") if suf else "NO_EXTENSION"
        dest = output / folder_name
        await dest.mkdir(parents=True, exist_ok=True)
        dest_file = dest / file.name

        counter = 1
        while await dest_file.exists():
            base_name = file.stem if suf else file.name
            dest_file = dest / f"{base_name}_{counter}{suf}"
            counter += 1

        await copyfile(file, dest_file)
        logger.info("Copied: %s → %s", file, dest_file)

    except Exception as error:
        logger.error("Failed to copy %s: %s", file, error)


if __name__ == "__main__":
    asyncio.run(main())