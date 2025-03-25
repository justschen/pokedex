from setuptools import setup

setup(
    name="Pokedex",
    version="1.0",
    packages=["pokedex"],
    install_requires=[
        "requests>=2.31.0",
        "Pillow>=10.2.0"
    ]
)
