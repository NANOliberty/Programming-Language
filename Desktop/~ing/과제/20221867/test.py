'''
-do-while문만 구현하지 않은 과제
'''

# Parser 클래스 정의
class Parser :
    def __init__(self) :
        # 선언된 변수(var)와 그에 해당하는 값(value)을 딕셔너리 형태로 저장
        self.vars_and_values = {} 
        
        # <relop> → == | != | < | > | <= | >=
        self.relops = ['==', '!=', '<', '>', '<=', '>=']
        
        # 최종 결과를 출력하기 위한 answer 리스트
        self.answers = []

    # 문자열 길이가 10자 이하이며, 소문자 알파벳으로만 구성되어 있는지 확인
    def is_var_true(self, string) :
        return len(string) <= 10 and all(char.islower() for char in string)

    # 문자열 길이가 10자 이하이며, 숫자로만 구성되어 있는지 확인
    def is_num_true(self, string) :
        return len(string) <= 10 and string.isdigit()

    # 다음에 올 token과 기대하는 토큰이 일치하는지 확인하고 맞으면 인덱스+1하는 함수
    def match(self, expected) :
        if self.code[self.index] == expected :
            self.index += 1
        else :
            self.answers.clear()
            self.index = len(self.code)
            print('1Syntax Error!!')
        
    # match 함수에서 현재 인덱스가 마지막 인덱스일 예정일 경우 사용할 함수
    def last_match(self, expected) :
        try :
            if self.code[self.index] != expected :
                self.answers.clear()
                self.index = len(self.code)
                print('2Syntax Error!!')
        # 맨 마지막에 ;이 존재하지 않을 경우, 그 전의 계산 결과를 다 지우고 에러 메시지 출력
        except IndexError :
            self.answers.clear()
            self.index = len(self.code)
            print('3Syntax Error!!')
            
    # 공백 단위로 토큰을 리스트에 넣음, 필드에 들어갈 내용 초기화
    def parse(self, code) :
        # parse를 하기 전에 이전 기록 지우기
        self.answers.clear() 
        self.vars_and_values.clear() 
        self.code = code.split() 
        self.index = 0  
        self.code_len = len(self.code)-1
        #
        print(self.code)
        try : # try1: program을 시작
            self.program()
            try : # try2: 최종 계산 결과 출력
                if self.answers:
                    result = ['TRUE' if item is True else 'FALSE' if item is False else int(item) for item in self.answers]
                print(*result)
            except :
                pass
        except :
            print('4Syntax Error!!')

    # <program> -> {<declaration>} {<stratement>}
    def program(self) :
        #
        print('program')
        while self.index < len(self.code) : 
            if self.code[self.index] == 'int' : 
                self.index += 1
                self.declaration()
            elif self.code[self.index] == 'print' or self.code[self.index] == 'do' or self.is_var_true(self.code[self.index]) == True :
                self.statement()
                
    # <declaration> → <type> <var> ;
    # <type> → int
    def declaration(self) :
        #
        print('deflaration')
        var_name = self.code[self.index]   
        if self.is_var_true(var_name) == False :
            self.answers.clear()
            self.index = len(self.code)
            print('5Syntax Error!!')
        self.vars_and_values[var_name] = 0
        #
        print(self.vars_and_values)
        self.index += 1
        if self.index < self.code_len :    
            self.match(";")
        else : 
            self.last_match(";")
            self.index += 1
             
    '''
    <statement> → <var> = <aexpr> ; | 
                  print <bexpr> ; | 
                  print <aexpr> ; |
                  do ' { ' {<statement>} ' } ' while ( <bexpr> ) ;
    '''
    def statement(self) :
        #
        print('statement')
        token = self.code[self.index]
        if token == 'print' :
            self.index += 1
            self.expected = self.code[self.index]
            if self.expected in self.relops :
                self.answers.append(self.bexpr())
            elif self.is_num_true(self.expected) or self.is_var_true(self.expected) or self.expected == '(' :
                self.answers.append(self.aexpr())
            else :
                self.answers.clear()
                self.index = len(self.code)
                print('6Syntax Error!!')
            if self.index < self.code_len :
                self.match(';')
                if self.code[self.index] == 'print' or self.code[self.index] == 'do' or (self.code[self.index] != 'int' and self.is_var_true(self.code[self.index])) == True :
                    pass
                else :
                    self.answers.clear()
                    self.index = len(self.code)
                    print('7Syntax Error!!')  
            else :
                self.last_match(';')
                self.index += 1
        # 여기서부터 짜야함
        elif token == 'do' :
            self.index += 1
            self.match('{')
            self.index += 1
            while self.code[self.index] != '}' :
                self.statement()
            self.index += 1
            self.match('while')
            self.match('(')
            in_while = self.bexpr()
            self.match(')')
            if self.index < self.code_len :
                    self.match(';')
                    if self.code[self.index] == 'print' or self.code[self.index] == 'do' or (self.code[self.index] != 'int' and self.is_var_true(self.code[self.index])) == True :
                        pass
                    else :
                        self.answers.clear()
                        self.index = len(self.code)
                        print('8Syntax Error!!')                   
            else :
                self.last_match(';')
                self.index += 1
        # 여기까지    
        # var일 경우
        elif token in self.vars_and_values and self.is_var_true(token) == True :
            self.index += 1
            self.match('=')
            value = self.aexpr()
            self.vars_and_values[token] = value
            if self.index < self.code_len :
                self.match(';')
                if self.code[self.index] == 'print' or self.code[self.index] == 'do' or (self.code[self.index] != 'int' and self.is_var_true(self.code[self.index])) == True :
                    pass
                else :
                    self.answers.clear()
                    self.index = len(self.code)
                    print('9Syntax Error!!')              
            else :
                self.last_match(';')
                self.index += 1
        else : 
            self.answers.clear()
            self.index = len(self.code)
            print('10Syntax Error!!')
            
    # <bexpr> → <relop> <aexpr> <aexpr>        
    def bexpr(self) :
        #
        print('bexpr')
        op = self.code[self.index]
        self.index += 1
        left = self.aexpr()
        right = self.aexpr()
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
        else :
            self.answers.clear()
            self.index = len(self.code)
            print('11Syntax Error!!')
    
    # <aexpr> → <term> {( + | - | * | / ) <term>}    
    def aexpr(self) :
        #
        print('aexpr')
        result = self.term()
        while self.index < len(self.code) and self.code[self.index] in ('+', '-', '*', '/') :
            op = self.code[self.index]
            self.index += 1
            term = self.term()
            if op == '+' :
                result += term
            elif op == '-' :
                result -= term
            elif op == '*' :
                result *= term
            elif op == '/' :
                result /= term
        return result
    
    # <term> → <number> | <var> | ( <aexpr> )    
    def term(self) :
        #
        print('term')
        token = self.code[self.index]
        #
        # print(token)
        self.index += 1
        if token.isdigit() :
            return int(token)
        elif token in self.vars_and_values :
            return int(self.vars_and_values[token])
        elif token == '(' :
            result = self.aexpr()
            self.match(')')
            return result
        else :
            self.answers.clear()
            self.index = len(self.code)
            print('12Syntax Error!!')
         
# Main 함수
if __name__ == "__main__" :
    parser = Parser()
    while True:
        code = input() # 공백 Enter는 에러가 아님
        if code == 'terminate' : # terminate 입력하면 프로그램 종료
            break
        parser.parse(code) # Parser 작동 시작