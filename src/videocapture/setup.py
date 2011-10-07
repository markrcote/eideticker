from setuptools import setup, find_packages
setup(
    name = "videocapture",
    version = "0.1.0",
    packages = find_packages(),
    scripts = [ "videocapture/decklink/decklink-capture",
                "videocapture/decklink/decklink-convert.sh" ],
    entry_points = {
      "console_scripts": ["eideticker-server = eideticker.server:main"]
    }
)

# FIXME: Compile decklink-capture script automatically
