from setuptools import setup, find_packages

setup(
    name="lexip",
    version="1.0.0",
    packages=find_packages(include=["layer*", "lexip*"]),
    install_requires=[
        "numpy",
        "scipy",
        "opencv-python",
        "scikit-learn",
        "PySide6",
        "PyOpenGL"
    ],
    entry_points={
        "console_scripts": [
            "lexip=layer7_extensions.lexip_cli:main",
        ],
    },
    python_requires=">=3.9",
)
