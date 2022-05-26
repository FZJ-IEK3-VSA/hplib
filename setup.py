from setuptools import setup
from pathlib import Path 
import versioneer

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()
setup(  name='hplib',
        version=versioneer.get_version(),
        cmdclass=versioneer.get_cmdclass(), 
        description='Database and code to simulate heat pumps',
        install_requires=['numpy >= 1.16.0', 
                        'pandas >= 0.22.0',
                        'scipy'],
        long_description=long_description,
        long_description_content_type='text/markdown',
        url='https://github.com/RE-Lab-Projects/hplib',
        author='RE-Lab HS-Emden-Leer',
        packages=['hplib'],
        package_data={'hplib': ['hplib/*.csv', 'hplib/*.pkl']},
        include_package_data=True
        )
