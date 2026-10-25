#!/usr/bin/env bash
# 세 언어 구현(과제1)과 Python 구현(과제2)을 같은 입력으로 돌려 기대 출력과 비교한다.
set -e
cd "$(dirname "$0")/.."
BUILD=$(mktemp -d)

gcc -Wall -Wextra -o "$BUILD/parser" assignment1/parser.c
javac -d "$BUILD" assignment1/Parser.java

check() { diff <("$@") "$EXPECTED" > /dev/null && echo "PASS  $NAME" || { echo "FAIL  $NAME"; diff <("$@") "$EXPECTED"; exit 1; }; }

EXPECTED=tests/assignment1_expected.txt
NAME="assignment1 python"; check python3 assignment1/parser.py < tests/assignment1_input.txt
NAME="assignment1 c";      check "$BUILD/parser"            < tests/assignment1_input.txt
NAME="assignment1 java";   check java -cp "$BUILD" Parser   < tests/assignment1_input.txt

EXPECTED=tests/assignment2_expected.txt
NAME="assignment2 python"; check python3 assignment2/parser.py < tests/assignment2_input.txt

rm -rf "$BUILD"
