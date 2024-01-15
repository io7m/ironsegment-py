python -m pip install --upgrade hatch

hatch fmt
hatch run types:check
hatch build
hatch run cov
