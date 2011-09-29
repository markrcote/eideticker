from setuptools import setup, find_packages
setup(
    name = "eideticker",
    version = "0.1.0",
    packages = find_packages(),
    scripts = [ "eideticker/decklink/decklink-capture",
                "eideticker/decklink/decklink-convert.sh" ],
    entry_points = {
      "console_scripts": ["eideticker-server = eideticker.server:main"]
    }
)

# FIXME: Compile decklink-capture script automatically
