#!/bin/bash -eux
yapf --in-place --recursive .
isort --order-by-type --recursive --line-width 100 --diff --verbose -y
pyflakes .
echo 'SUCCESS!'
