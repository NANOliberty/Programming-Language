# Programming Language — Recursive-Descent Parser 과제

숭실대학교 컴퓨터학부 「프로그래밍 언어」 수업의 구현 과제. EBNF로 정의된 소형 언어를 읽어 실행 결과를 출력하는 파서를 Recursive-Descent 방식으로 만들었다. 파싱과 실행을 분리하지 않고 한 번에 처리한다.

- 구현과제1 — 같은 문법을 **Python · Java · C** 세 언어로 각각 구현
- 구현과제2 — 변수 선언, 괄호, 전위 비교식, do-while이 추가된 문법을 Python으로 구현
- Chapter 3·4 연습문제(파스 트리, 모호성 증명, pairwise disjointness test, LR 파싱 추적) 풀이는 [`docs/problem-sets/`](docs/problem-sets/)

> 제출 당시 과제1은 C 구현을 완성하지 못했고 Python·Java도 오류 처리가 허술해 감점을 받았다. 이 저장소의 코드는 제출 이후 세 언어 모두 다시 작성한 것이고, 제출본은 [`docs/assignment1/submitted_parser.py`](docs/assignment1/submitted_parser.py)·[`docs/assignment2/submitted_parser.py`](docs/assignment2/submitted_parser.py)에 그대로 두었다.

## 구성

```
assignment1/   parser.py · Parser.java · parser.c   (구현과제1, 동일 동작)
assignment2/   parser.py                            (구현과제2)
tests/         입력·기대 출력 · run.sh              (네 구현 모두 같은 입력으로 비교)
docs/          명세서 · 제출 보고서 · 제출본 코드 · 연습문제 풀이
```

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

## 실행

한 줄이 하나의 프로그램이다. 엔터까지 읽어 파싱·실행하고, 출력할 것이 있으면 한 줄에 모아 찍는다. `terminate`로 종료.

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

## 구현에서 결정한 것들

**비터미널 하나 = 함수 하나.** `program() → statement() → expr() → aexpr() → term() → factor() → number()` 순으로 EBNF 규칙을 그대로 함수로 옮겼다. `{ ... }` 반복은 while, `|` 선택은 다음 토큰을 보고 분기. 세 언어 모두 같은 함수 구조라 한 언어에서 고친 것을 나머지에 그대로 옮길 수 있다.

**오류는 한 곳에서 잡는다.** 토큰이 기대와 다르면 어느 깊이에서든 예외(Python/Java) 또는 `longjmp`(C)로 `parse()`까지 바로 빠져나온다. 제출본은 분기마다 `answers.clear(); index = len(code); raise`를 반복해 놓았는데, 이걸 `match()`/`advance()` 두 함수로 모았다.

**토큰이 모자라도 죽지 않게.** `print x` 처럼 `;`가 없는 입력에서 제출본은 `IndexError`로 터지는 걸 바깥 `except:`로 뭉개고 있었다. 지금은 `peek()`가 범위 밖이면 `None`을 돌려주고 `advance()`가 그걸 오류로 바꾼다. 입력 끝이 어디든 같은 경로로 처리된다.

**`<expr> → <bexpr> | <aexpr>` 는 두 토큰을 미리 본다.** 과제1에서 `12 == 3`과 `12 + 3`은 첫 토큰이 같아서 구별이 안 된다. 두 번째 토큰이 `<relop>`이면 `bexpr()`, 아니면 `aexpr()`. 과제2는 비교식이 전위 표기라 첫 토큰만으로 결정된다.

**do-while은 위치를 되감아 다시 파싱한다.** 파싱과 실행이 한 몸이라 본문을 AST로 저장해 두지 않는다. `{` 다음 위치를 기억해 두고, `while ( <bexpr> )`가 참이면 그 위치로 `pos`를 되돌려 본문을 다시 읽는다. 제출본은 `code.index('{')`로 첫 `{`를 찾아 돌아갔기 때문에 do-while이 두 개 이상이거나 중첩되면 틀렸는데, 되감을 위치를 호출 스택에 두니 중첩도 그냥 된다 (`tests/assignment2_input.txt` 15행).

**출력은 줄이 끝까지 통과한 뒤에.** `x = 12 == 3 print x ;`처럼 뒤에서 오류가 나면 앞의 `print` 결과도 버려야 한다. `print`는 바로 찍지 않고 리스트에 모아 두었다가 `program()`이 끝나야 출력한다.

**변수는 줄마다 초기화.** 명세가 "엔터키 입력까지를 하나의 프로그램으로 인식"이라 이전 줄의 대입이 다음 줄에 남지 않게 했다. 과제2는 선언이 있으니 당연하고, 과제1도 맞췄다.

**나눗셈.** 과제1은 결과가 `<number>`(음이 아닌 정수) 범위라 정수 나눗셈. 과제2는 음수가 허용되므로 C와 같은 0 방향 절삭(`int(a / b)`)으로 통일했다. 0으로 나누면 syntax error.

## 알고 있는 한계

| 항목 | 현재 | 이유 | 다음에 한다면 |
|---|---|---|---|
| 토큰 분리 | 공백 `split()` | 명세에 "토큰 사이에 공백이 들어감"이 보장됨 | 문자 단위 렉서를 두고 `x=1;`도 받기 |
| `<number>` 범위 | 10자리까지 통과, 오버플로 검사 없음 | 명세가 결과값을 `<number>` 범위로 한정 | C/Java에서 `long` 또는 범위 검사 |
| do-while 종료 | 조건이 영원히 참이면 무한 루프 | 명세에 상한 없음 | 반복 횟수 상한 |
| 오류 위치 | `Syntax Error!!`만 출력 | 명세 출력 형식 | 몇 번째 토큰인지 함께 출력 |

## 테스트

`tests/run.sh`가 과제1의 세 구현과 과제2 구현을 같은 입력 파일로 실행해 기대 출력과 `diff`한다. 입력에는 명세의 실행예 전부와 `;` 누락, 미선언 변수, 11자 변수명·숫자, 중첩 do-while, 0 나눗셈이 들어 있다.
