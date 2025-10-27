from setuptools import setup
import os
from glob import glob

package_name = 'sparky_hardware'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        # Ajouter les fichiers statiques
        (os.path.join('share', package_name, 'static'), 
            glob('sparky_hardware/static/*')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Admin',
    maintainer_email='Admin@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'sparky_node = sparky_hardware.sparky_node:main',
            'web_server = sparky_hardware.web_server:main',
        ],
    },
)
