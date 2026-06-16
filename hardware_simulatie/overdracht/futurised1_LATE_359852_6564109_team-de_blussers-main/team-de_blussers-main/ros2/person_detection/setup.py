from setuptools import find_packages, setup
from glob import glob

package_name = 'person_detection'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', ['launch/detection.launch.py']),
        ('share/' + package_name + '/rviz', ['rviz/person_detection.rviz']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='root',
    maintainer_email='jansen.tess29@gmail.com',
    description='Persoons-detectie met YOLO + thermische temperatuur-overlay',
    license='TODO',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'person_detector = person_detection.detector:main',
            'make_screenshot = person_detection.make_screenshot:main',
            'thermal_relay = person_detection.thermal_relay:main',
        ],
    },
)
