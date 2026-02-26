from setuptools import find_packages, setup


setup(
    name="adaptive-nav",
    version="0.1.0",
    description="Adaptive Navigation Strategy Benchmark",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "PyYAML>=6.0",
        "matplotlib>=3.8",
    ],
    entry_points={
        "console_scripts": [
            "adaptive-nav-benchmark=adaptive_nav.benchmark:run",
            "adaptive-nav-visual=adaptive_nav.visual:run",
        ]
    },
)
