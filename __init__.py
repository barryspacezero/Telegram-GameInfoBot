from modules.bot import LOGGER


def list_all_modules():
    import glob
    from os.path import basename, dirname, isfile

    # This generates a list of modules in this folder for the * in __main__ to work.
    mod_paths = glob.glob(dirname(__file__) + "/*.py")
    all_modules = [
        basename(f)[:-3]
        for f in mod_paths
        if isfile(f) and f.endswith(".py") and not f.endswith("__init__.py")
    ]

    return all_modules


ALL_MODULES = list_all_modules()
LOGGER.info("Modules Loaded: %s", str(ALL_MODULES))

__all__ = ALL_MODULES + ["ALL_MODULES"]
