#!/bin/bash -eu
cd "${0%/*}"
find ../ -name "rules*.yaml" -exec sed -i 's/cause: \([a-z]*\)/causes: [\1]/g' {} \;
echo -e "---\n- ['RegexFilenameMatcher', {'type': 'default', 'path_pattern': 'node_1.log'}]" > log_locations.yaml
for i in $(find ../whylog/ -type d -name "[0-9]*" -type d); do
    cp log_locations.yaml "$i"
done
rm log_locations.yaml