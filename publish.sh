sudo python3 setup.py sdist
twine upload dist/*
sudo rm -rf dist build
