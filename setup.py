import setuptools

if __name__ == "__main__":
    setuptools.setup(
        name='ppi',
        version='0.0.1',
        packages=setuptools.find_packages(),
        install_requres=["python-Levenshtein"],
        entry_points={
            'console_scripts': [
                'ppi = ppi.main:main',
            ],
        },
    )
