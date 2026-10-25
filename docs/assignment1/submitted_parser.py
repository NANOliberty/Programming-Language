# 예외 처리를 꼼꼼하게 하지 않음
import re

class Parser:
    def __init__(self):
        self.vars = {'x': 0, 'y': 0, 'z': 0} 
        self.relops = ['==', '!=', '<', '>', '<=', '>=']
        self.answers = []

    def match(self, expected):
        if self.code[self.index] == expected:
            self.index += 1
        else:
            raise SyntaxError
        
    def last_match(self, expected):
        if self.code[self.index] != expected:
            raise SyntaxError

    def parse(self, code):
        self.code = code.split() 
        self.index = 0  
        self.code_len = len(self.code)-1
        try:
            self.program()
        except:
            print(">> syntax error!!")

    # <program> → {<statement>}
    def program(self):
        self.answers.clear()
        while self.index < len(self.code):
            self.statement()
        if self.answers:
            result = ['TRUE' if item is True else 'FALSE' if item is False else item for item in self.answers]
            print('>>', *result)

    # <statement> → <var> = <expr> ; | print <var> ;
    def statement(self):
        token = self.code[self.index]
        if token == 'print':
            self.index += 1
            var = self.code[self.index]
            self.index += 1
            if var not in self.vars:
                raise Exception
            self.answers.append(self.vars[var])
            if self.index < self.code_len:    
                self.match(";")
            else: 
                self.last_match(";")
        
        elif token == ';' :
            self.index += 1

        else:
            var = token
            if var not in self.vars:
                raise Exception
            self.index += 1
            self.match('=')
            value = self.expr()
            self.vars[var] = value   
            if self.index < self.code_len:    
                self.match(";")
            else: 
                self.last_match(";")
            
    # <expr> → <bexpr> | <aexpr>
    def expr(self):
        token = self.code[self.index]
        next_token = self.code[self.index+1]
        if token.isdigit() and next_token in self.relops:
            return self.bexpr()
        else:
            return self.aexpr()
        
    # <bexpr> → <number> <relop> <number>
    def bexpr(self):
        left = int(self.code[self.index])
        self.index += 1
        op = self.code[self.index]
        self.index += 1
        right = int(self.code[self.index])
        self.index += 1
        if op == '==':
            return left == right
        elif op == '!=':
            return left != right
        elif op == '<':
            return left < right
        elif op == '>':
            return left > right
        elif op == '<=':
            return left <= right
        elif op == '>=':
            return left >= right
        
    # <aexpr> → <term> {( + | - ) <term>}
    def aexpr(self):
        result = self.term()
        while self.index < len(self.code) and self.code[self.index] in ('+', '-'):
            op = self.code[self.index]
            self.index += 1
            term = self.term()
            if op == '+':
                result += term
            elif op == '-':
                result -= term
        return result
     
    # <term> → <factor> {( * | / ) <factor>}
    def term(self):
        result = self.factor()
        while self.index < len(self.code) and self.code[self.index] in ('*', '/'):
            op = self.code[self.index]
            self.index += 1
            factor = self.factor()
            if op == '*':
                result *= factor
            elif op == '/':
                result /= factor
        return int(result)

    # <factor> → <number>
    def factor(self):
        token = self.code[self.index]
        self.index += 1
        if token.isdigit():
            return int(token)
        else:
            return self.vars[token]

# Main 함수
if __name__ == "__main__":
    parser = Parser()
    while True:
        code = input('>> ')
        if code == "terminate":
            break
        parser.parse(code)
