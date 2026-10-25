"""
구현과제2 - Parser (Python)

<program>     → {<declaration>} {<statement>}
<declaration> → <type> <var> ;
<statement>   → <var> = <aexpr> ; | print <bexpr> ; | print <aexpr> ;
              | do '{' {<statement>} '}' while ( <bexpr> ) ;
<bexpr>       → <relop> <aexpr> <aexpr>
<relop>       → == | != | < | > | <= | >=
<aexpr>       → <term> {( + | - | * | / ) <term>}
<term>        → <number> | <var> | ( <aexpr> )
<type>        → int
<number>      → <dec>{<dec>}
<var>         → <alphabet>{<alphabet>}

Static semantics
- 토큰 사이에는 공백이 1개 이상 들어간다.
- 선언하지 않은 변수를 쓰면 syntax error. 선언된 변수는 0으로 초기화된다.
- <aexpr>의 결과는 정수(음수 포함). 산술 연산은 우선순위 없이 왼쪽 결합이다.
- <var>, <number>의 최대 길이는 10이다.

do-while은 파싱과 실행을 한 번에 하므로, 본문 시작 위치를 기억해 두었다가
조건이 참이면 그 위치로 돌아가 본문을 다시 파싱(=실행)한다.
"""

RELOPS = ("==", "!=", "<", ">", "<=", ">=")
ARITH_OPS = ("+", "-", "*", "/")
KEYWORDS = ("int", "print", "do", "while")
MAX_LEN = 10


class ParseError(Exception):
    pass


class Parser:
    # ----- 토큰 유틸 -----
    def peek(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def advance(self):
        tok = self.peek()
        if tok is None:
            raise ParseError()
        self.pos += 1
        return tok

    def match(self, expected):
        if self.peek() != expected:
            raise ParseError()
        self.pos += 1

    @staticmethod
    def is_var(tok):
        return (
            tok is not None
            and 0 < len(tok) <= MAX_LEN
            and all("a" <= c <= "z" for c in tok)
            and tok not in KEYWORDS
        )

    @staticmethod
    def is_number(tok):
        return tok is not None and 0 < len(tok) <= MAX_LEN and tok.isdigit()

    # ----- 진입점 -----
    def parse(self, line):
        self.tokens = line.split()
        self.pos = 0
        self.vars = {}      # 한 줄 = 하나의 프로그램이므로 매번 초기화
        self.outputs = []
        try:
            self.program()
            if self.outputs:
                print(">>", *(format_value(v) for v in self.outputs))
        except ParseError:
            print(">> Syntax Error!!")

    # <program> → {<declaration>} {<statement>}
    def program(self):
        while self.peek() == "int":
            self.declaration()
        while self.peek() is not None:
            self.statement()   # 여기서 'int'를 만나면 <var>가 아니므로 오류

    # <declaration> → <type> <var> ;
    def declaration(self):
        self.match("int")
        name = self.advance()
        if not self.is_var(name):
            raise ParseError()
        self.match(";")
        self.vars[name] = 0

    # <statement> → <var> = <aexpr> ; | print <bexpr> ; | print <aexpr> ;
    #             | do '{' {<statement>} '}' while ( <bexpr> ) ;
    def statement(self):
        tok = self.peek()
        if tok == "print":
            self.advance()
            if self.peek() in RELOPS:
                self.outputs.append(self.bexpr())
            else:
                self.outputs.append(self.aexpr())
            self.match(";")
        elif tok == "do":
            self.do_while()
        else:
            name = self.var()
            self.match("=")
            value = self.aexpr()
            self.match(";")
            self.vars[name] = value

    # do '{' {<statement>} '}' while ( <bexpr> ) ;
    def do_while(self):
        self.match("do")
        self.match("{")
        body_start = self.pos
        while True:
            self.pos = body_start
            while self.peek() != "}":
                self.statement()
            self.match("}")
            self.match("while")
            self.match("(")
            cond = self.bexpr()
            self.match(")")
            if not cond:
                break
        self.match(";")

    # <var> → <alphabet>{<alphabet>}  (선언된 변수만 허용)
    def var(self):
        tok = self.advance()
        if not self.is_var(tok) or tok not in self.vars:
            raise ParseError()
        return tok

    # <bexpr> → <relop> <aexpr> <aexpr>
    def bexpr(self):
        op = self.advance()
        if op not in RELOPS:
            raise ParseError()
        left = self.aexpr()
        right = self.aexpr()
        return {
            "==": left == right,
            "!=": left != right,
            "<": left < right,
            ">": left > right,
            "<=": left <= right,
            ">=": left >= right,
        }[op]

    # <aexpr> → <term> {( + | - | * | / ) <term>}   (우선순위 없음, 왼쪽 결합)
    def aexpr(self):
        result = self.term()
        while self.peek() in ARITH_OPS:
            op = self.advance()
            rhs = self.term()
            if op == "+":
                result += rhs
            elif op == "-":
                result -= rhs
            elif op == "*":
                result *= rhs
            else:
                if rhs == 0:
                    raise ParseError()
                result = int(result / rhs)   # 0 방향 절삭 (C 정수 나눗셈과 동일)
        return result

    # <term> → <number> | <var> | ( <aexpr> )
    def term(self):
        tok = self.peek()
        if self.is_number(tok):
            self.advance()
            return int(tok)
        if tok == "(":
            self.advance()
            value = self.aexpr()
            self.match(")")
            return value
        return self.vars[self.var()]


def format_value(v):
    if isinstance(v, bool):
        return "TRUE" if v else "FALSE"
    return str(v)


if __name__ == "__main__":
    parser = Parser()
    while True:
        try:
            line = input(">> ")
        except EOFError:
            break
        if line.strip() == "terminate":
            break
        parser.parse(line)
