from setuptools import setup

setup(
    name="line2pub",
    version="2.1",
    py_modules=["line2pub"],
    include_package_data=True,
    install_requires=["click", "tqdm", "pandas", "line_protocol_parser", "paho-mqtt", "fpstimer"],
    entry_points="""
        [console_scripts]
        line2pub=line2pub:cli
    """,
)
