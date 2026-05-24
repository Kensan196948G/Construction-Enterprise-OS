from setuptools import setup, find_packages

setup(
    name="construction-enterprise-os-event-core",
    version="0.1.0",
    description="Construction-Enterprise-OS Event Bus Core - Kafka event infrastructure",
    author="Construction-Enterprise-OS Team",
    packages=find_packages(),
    install_requires=[
        "pydantic>=2.9.0",
        "aiokafka>=0.11.0",
        "python-dotenv>=1.0.0",
    ],
    python_requires=">=3.12",
)
