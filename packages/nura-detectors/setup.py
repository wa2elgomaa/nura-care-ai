from setuptools import setup, find_packages

setup(
    name="nura-detectors",
    version="0.1.0",
    description="Shared fast-path detectors for Nura childcare AI",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.11",
    install_requires=[
        "opencv-python-headless>=4.9.0",
        "numpy>=1.24.0",
        "ultralytics>=8.0.0",  # YOLOv8 for pose detection (Phase 2)
        "tensorflow>=2.13.0",  # RNN temporal analysis (Phase 3)
        "scikit-learn>=1.3.0",  # For train/test split
    ],
)
