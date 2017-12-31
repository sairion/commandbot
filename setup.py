from distutils.core import setup


setup(
    name="commandbot",
    version="0.1",
    author="Jaeho Lee",
    author_email="me@jaeholee.org",
    description="partial fork of pse1202/coinbot",
    long_description="partial fork of pse1202/coinbot",
    license="MIT",
    url="http://github.com/sairion/commandbot",
    packages=[
        "commandbot",
        "commandbot.market",
    ],
)
