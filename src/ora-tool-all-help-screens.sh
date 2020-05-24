#!/bin/bash
#
# This script is a quick and dirty hack to generate an overview of the operations for the README.md file
#

cd $(dirname $0)

echo "### general usage"
echo ""
echo "\`\`\`"
echo "> ./ora-tool.py"
echo ""
./ora-tool.py
echo "\`\`\`"

echo "### apply yaml file"
echo ""
echo "\`\`\`"
echo "> ./ora-tool.py help yaml"
echo ""
./ora-tool.py help yaml
echo "\`\`\`"

echo "### available operations"
echo ""
echo "\`\`\`"
echo "> ./ora-tool.py help ops"
echo ""
./ora-tool.py help ops
echo "\`\`\`"
echo ""

./ora-tool.py help ops | grep -A 10000 'The following operations are supported:' | \
while read LINE ; do
    if [[ "$LINE" == "The following operations are supported:" ]] ; then
        continue
    fi
    if [[ "$LINE" == "You may obtain further information on these operations with" ]] ; then
        break
    fi
    OPNAME="$LINE"
    echo "### $OPNAME"
    echo ""
    echo "\`\`\`"
    echo "> ./ora-tool.py help op $OPNAME"
    ./ora-tool.py help op "$OPNAME"
    ./ora-tool.py help op "$OPNAME" | grep -A 10000 'where \[parameter\] is one of the following:' | \
    while read LINEB ; do
        if [[ "$LINEB" == "where [parameter] is one of the following:" ]] ; then
            continue
        fi 
        PARAMNAME="$LINEB"
        echo ""
        echo "> ./ora-tool.py help parameter $OPNAME $PARAMNAME"
        echo ""
        ./ora-tool.py help parameter "$OPNAME" "$PARAMNAME"
        echo ""
    done
    echo "\`\`\`"
    echo ""
done
