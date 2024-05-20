# 예시: 사용자로부터 입력받은 숫자를 더하는 do-while 루프
'''
<program> → {<declaration>} {<statement>}
<declaration> → <type> <var> ;
<statement> → <var> = <aexpr> ; | print <bexpr> ; | print <aexpr> ; |
do ‘ { ’ {<statement>} ‘ } ’ while ( <bexpr> ) ; 
<bexpr> → <relop> <aexpr> <aexpr>
<relop> → == | != | < | > | <= | >=
<aexpr> → <term> {( + | - | * | / ) <term>}
<term> → <number> | <var> | ( <aexpr> )

do { 0개이상의statement } while ( bexpr ) ;

int k ; int j ; k = 3 ; j = 20 ;
do { print k + ( j - 1 ) * 10 ; k = k - 1 ; } 
while ( > k + 10 10 ) ; print == k 0 ;
'''


def state_start():
    print("Start")
    return "label"

def state_label():
    print("Jumped to label")
    return "end"

states = {
    "start": state_start,
    "label": state_label,
    "end": lambda: None
}

current_state = "start"
while current_state != "end":
    current_state = states[current_state]()
