# Programming Language — Recursive-Descent Parser 과제

숭실대학교 컴퓨터학부 「프로그래밍 언어」 수업의 구현 과제. EBNF로 정의된 소형 언어를 읽어 실행 결과를 출력하는 파서를 Recursive-Descent 방식으로 만들었다. 파싱과 실행을 분리하지 않고 한 번에 처리한다.

- 구현과제1 — 같은 문법을 **Python · Java · C** 세 언어로 각각 구현
- 구현과제2 — 변수 선언, 괄호, 전위 비교식, do-while이 추가된 문법을 Python으로 구현
- Chapter 3·4 연습문제(파스 트리, 모호성 증명, pairwise disjointness test, LR 파싱 추적) 풀이는 [`docs/problem-sets/`](docs/problem-sets/)

> 제출 당시 과제1은 C 구현을 완성하지 못했고 Python·Java도 오류 처리가 허술해 감점을 받았다. 이 저장소의 코드는 제출 이후 세 언어 모두 다시 작성한 것이고, 제출본은 [`docs/assignment1/submitted_parser.py`](docs/assignment1/submitted_parser.py)·[`docs/assignment2/submitted_parser.py`](docs/assignment2/submitted_parser.py)에 그대로 두었다.

<br>

## 구성

```
assignment1/   parser.py · Parser.java · parser.c   (구현과제1, 동일 동작)
assignment2/   parser.py                            (구현과제2)
tests/         입력·기대 출력 · run.sh              (네 구현 모두 같은 입력으로 비교)
docs/          명세서 · 제출 보고서 · 제출본 코드 · 연습문제 풀이
```

<br>

## 문법

**구현과제1**

```
<program>   → {<statement>}
<statement> → <var> = <expr> ; | print <var> ;
<expr>      → <bexpr> | <aexpr>
<bexpr>     → <number> <relop> <number>
<aexpr>     → <term> {( + | - ) <term>}
<term>      → <factor> {( * | / ) <factor>}
<factor>    → <number>
<var>       → x | y | z
```

**구현과제2** — 선언이 생기고, 비교식이 전위 표기(`> k 10`)로 바뀌고, 사칙연산이 우선순위 없이 왼쪽 결합이 된다.

```
<program>     → {<declaration>} {<statement>}
<declaration> → int <var> ;
<statement>   → <var> = <aexpr> ; | print <bexpr> ; | print <aexpr> ;
              | do { {<statement>} } while ( <bexpr> ) ;
<bexpr>       → <relop> <aexpr> <aexpr>
<aexpr>       → <term> {( + | - | * | / ) <term>}
<term>        → <number> | <var> | ( <aexpr> )
```

<br>

## 실행

한 줄이 하나의 프로그램이다. 엔터까지 읽어 파싱·실행하고, 출력할 것이 있으면 한 줄에 모아 출력한다. (`terminate`로 종료)

```
$ python3 assignment1/parser.py
>> x = 12 == 3 ; y = 10 + 5 * 3 ; print y ; print x ;
>> 25 FALSE
>> x = ( 12 + 3 ;
>> syntax error!!

$ python3 assignment2/parser.py
>> int k ; int j ; k = 3 ; j = 20 ; do { print k + ( j - 1 ) * 10 ; k = k - 1 ; } while ( > k + 10 10 ) ; print == k 0 ;
>> 220 210 200 TRUE
```

```
gcc -o parser assignment1/parser.c && ./parser
javac assignment1/Parser.java && java -cp assignment1 Parser
bash tests/run.sh        # 네 구현 전부 기대 출력과 diff
```

<br>

## 테스트

`tests/run.sh`가 과제1의 세 구현과 과제2 구현을 같은 입력 파일로 실행해 기대 출력과 `diff`한다. 입력에는 명세의 실행예 전부와 `;` 누락, 미선언 변수, 11자 변수명·숫자, 중첩 do-while, 0 나눗셈이 들어 있다.
