"""
구현과제1 - Recursive-Descent Parser (Python)

<program>   → {<statement>}
<statement> → <var> = <expr> ; | print <var> ;
<expr>      → <bexpr> | <aexpr>
<bexpr>     → <number> <relop> <number>
<relop>     → == | != | < | > | <= | >=
<aexpr>     → <term> {( + | - ) <term>}
<term>      → <factor> {( * | / ) <factor>}
<factor>    → <number>
<number>    → <dec> {<dec>}
<var>       → x | y | z

- 토큰은 공백으로 구분된다.
- 문법 오류가 있으면 "syntax error!!"만 출력하고, 그 줄의 print 결과는 버린다.
- <aexpr>의 결과는 <number> 범위(음이 아닌 정수)로 한정되므로 / 는 정수 나눗셈으로 처리한다.
- 엔터까지가 하나의 프로그램이므로 변수(x, y, z)는 줄마다 0으로 초기화한다.
"""

RELOPS = ("==", "!=", "<", ">", "<=", ">=")
VARS = ("x", "y", "z")


class ParseError(Exception):
    pass


class Parser:
    def __init__(self):
        self.vars = {v: 0 for v in VARS}

    # ----- 토큰 유틸 -----
    def peek(self, offset=0):
        i = self.pos + offset
        return self.tokens[i] if i < len(self.tokens) else None

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
    def is_number(tok):
        return tok is not None and tok.isdigit()

    # ----- 진입점 -----
    def parse(self, line):
        self.tokens = line.split()
        self.pos = 0
        self.outputs = []
        self.vars = {v: 0 for v in VARS}  # 한 줄 = 하나의 프로그램이므로 매번 초기화
        try:
            self.program()
            if self.outputs:
                print(">>", *(format_value(v) for v in self.outputs))
        except ParseError:
            print(">> syntax error!!")

    # <program> → {<statement>}
    def program(self):
        while self.peek() is not None:
            self.statement()

    # <statement> → <var> = <expr> ; | print <var> ;
    def statement(self):
        tok = self.peek()
        if tok == "print":
            self.advance()
            name = self.var()
            self.match(";")
            self.outputs.append(self.vars[name])
        else:
            name = self.var()
            self.match("=")
            value = self.expr()
            self.match(";")
            self.vars[name] = value

    # <var> → x | y | z
    def var(self):
        tok = self.advance()
        if tok not in VARS:
            raise ParseError()
        return tok

    # <expr> → <bexpr> | <aexpr>
    # 두 번째 토큰이 <relop>이면 <bexpr>, 아니면 <aexpr>
    def expr(self):
        if self.is_number(self.peek()) and self.peek(1) in RELOPS:
            return self.bexpr()
        return self.aexpr()

    # <bexpr> → <number> <relop> <number>
    def bexpr(self):
        left = self.number()
        op = self.advance()
        if op not in RELOPS:
            raise ParseError()
        right = self.number()
        return {
            "==": left == right,
            "!=": left != right,
            "<": left < right,
            ">": left > right,
            "<=": left <= right,
            ">=": left >= right,
        }[op]

    # <aexpr> → <term> {( + | - ) <term>}
    def aexpr(self):
        result = self.term()
        while self.peek() in ("+", "-"):
            op = self.advance()
            rhs = self.term()
            result = result + rhs if op == "+" else result - rhs
        return result

    # <term> → <factor> {( * | / ) <factor>}
    def term(self):
        result = self.factor()
        while self.peek() in ("*", "/"):
            op = self.advance()
            rhs = self.factor()
            if op == "*":
                result *= rhs
            else:
                if rhs == 0:
                    raise ParseError()
                result //= rhs
        return result

    # <factor> → <number>
    def factor(self):
        return self.number()

    # <number> → <dec> {<dec>}
    def number(self):
        tok = self.advance()
        if not self.is_number(tok):
            raise ParseError()
        return int(tok)


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
