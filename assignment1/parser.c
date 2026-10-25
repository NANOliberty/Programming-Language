/*
 * 구현과제1 - Recursive-Descent Parser (C)
 *
 * <program>   → {<statement>}
 * <statement> → <var> = <expr> ; | print <var> ;
 * <expr>      → <bexpr> | <aexpr>
 * <bexpr>     → <number> <relop> <number>
 * <relop>     → == | != | < | > | <= | >=
 * <aexpr>     → <term> {( + | - ) <term>}
 * <term>      → <factor> {( * | / ) <factor>}
 * <factor>    → <number>
 * <number>    → <dec> {<dec>}
 * <var>       → x | y | z
 *
 * 문법 오류는 setjmp/longjmp로 parse()까지 한 번에 되돌아간다.
 */
#include <ctype.h>
#include <setjmp.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_LINE   4096
#define MAX_TOKENS 1024
#define MAX_OUTPUT 1024

typedef struct {
    int is_bool;  /* 1이면 <bexpr> 결과, 0이면 <aexpr> 결과 */
    int num;
    int bool_val;
} Value;

static const char *RELOPS[] = {"==", "!=", "<", ">", "<=", ">="};
static const char *VARS[] = {"x", "y", "z"};

static char  *tokens[MAX_TOKENS];
static int    ntokens;
static int    pos;
static Value  vars[3];            /* x, y, z */
static Value  outputs[MAX_OUTPUT];
static int    noutputs;
static jmp_buf error_jmp;

/* ----- 토큰 유틸 ----- */
static void error(void) { longjmp(error_jmp, 1); }

static const char *peek_at(int offset) {
    int i = pos + offset;
    return i < ntokens ? tokens[i] : NULL;
}
static const char *peek(void) { return peek_at(0); }

static const char *advance(void) {
    if (pos >= ntokens) error();
    return tokens[pos++];
}

static void match(const char *expected) {
    const char *t = peek();
    if (t == NULL || strcmp(t, expected) != 0) error();
    pos++;
}

static int in_set(const char **set, int n, const char *tok) {
    if (tok == NULL) return -1;
    for (int i = 0; i < n; i++)
        if (strcmp(set[i], tok) == 0) return i;
    return -1;
}

static int is_number(const char *tok) {
    if (tok == NULL || *tok == '\0') return 0;
    for (const char *p = tok; *p; p++)
        if (!isdigit((unsigned char)*p)) return 0;
    return 1;
}

static int is_token(const char *tok, const char *s) {
    return tok != NULL && strcmp(tok, s) == 0;
}

/* ----- 문법 규칙 ----- */
static Value expr(void);
static int   aexpr(void);

/* <number> → <dec> {<dec>} */
static int number(void) {
    const char *tok = advance();
    if (!is_number(tok)) error();
    return atoi(tok);
}

/* <factor> → <number> */
static int factor(void) { return number(); }

/* <term> → <factor> {( * | / ) <factor>} */
static int term(void) {
    int result = factor();
    while (is_token(peek(), "*") || is_token(peek(), "/")) {
        const char *op = advance();
        int rhs = factor();
        if (op[0] == '*') {
            result *= rhs;
        } else {
            if (rhs == 0) error();
            result /= rhs;
        }
    }
    return result;
}

/* <aexpr> → <term> {( + | - ) <term>} */
static int aexpr(void) {
    int result = term();
    while (is_token(peek(), "+") || is_token(peek(), "-")) {
        const char *op = advance();
        int rhs = term();
        result = (op[0] == '+') ? result + rhs : result - rhs;
    }
    return result;
}

/* <bexpr> → <number> <relop> <number> */
static int bexpr(void) {
    int left = number();
    int op = in_set(RELOPS, 6, advance());
    if (op < 0) error();
    int right = number();
    switch (op) {
        case 0:  return left == right;
        case 1:  return left != right;
        case 2:  return left <  right;
        case 3:  return left >  right;
        case 4:  return left <= right;
        default: return left >= right;
    }
}

/* <expr> → <bexpr> | <aexpr>   (두 번째 토큰이 <relop>이면 <bexpr>) */
static Value expr(void) {
    Value v;
    if (is_number(peek()) && in_set(RELOPS, 6, peek_at(1)) >= 0) {
        v.is_bool = 1; v.bool_val = bexpr(); v.num = 0;
    } else {
        v.is_bool = 0; v.num = aexpr(); v.bool_val = 0;
    }
    return v;
}

/* <var> → x | y | z  (변수 인덱스 반환) */
static int var(void) {
    int i = in_set(VARS, 3, advance());
    if (i < 0) error();
    return i;
}

/* <statement> → <var> = <expr> ; | print <var> ; */
static void statement(void) {
    if (is_token(peek(), "print")) {
        advance();
        int i = var();
        match(";");
        if (noutputs >= MAX_OUTPUT) error();
        outputs[noutputs++] = vars[i];
    } else {
        int i = var();
        match("=");
        Value v = expr();
        match(";");
        vars[i] = v;
    }
}

/* <program> → {<statement>} */
static void program(void) {
    while (peek() != NULL) statement();
}

/* ----- 진입점 ----- */
static void tokenize(char *line) {
    ntokens = 0;
    for (char *t = strtok(line, " \t\r\n"); t != NULL; t = strtok(NULL, " \t\r\n")) {
        if (ntokens >= MAX_TOKENS) break;
        tokens[ntokens++] = t;
    }
}

static void print_value(const Value *v) {
    if (v->is_bool) printf(" %s", v->bool_val ? "TRUE" : "FALSE");
    else            printf(" %d", v->num);
}

static void parse(char *line) {
    tokenize(line);
    pos = 0;
    noutputs = 0;
    memset(vars, 0, sizeof(vars));  /* 한 줄 = 하나의 프로그램이므로 매번 초기화 */

    if (setjmp(error_jmp) == 0) {
        program();
        if (noutputs > 0) {
            printf(">>");
            for (int i = 0; i < noutputs; i++) print_value(&outputs[i]);
            printf("\n");
        }
    } else {
        printf(">> syntax error!!\n");
    }
}

int main(void) {
    char line[MAX_LINE];

    while (1) {
        printf(">> ");
        fflush(stdout);
        if (fgets(line, sizeof(line), stdin) == NULL) break;

        /* terminate 판정: 앞뒤 공백 제거 후 비교 */
        char *s = line;
        while (isspace((unsigned char)*s)) s++;
        char *e = s + strlen(s);
        while (e > s && isspace((unsigned char)e[-1])) e--;
        if ((size_t)(e - s) == 9 && strncmp(s, "terminate", 9) == 0) break;

        parse(line);
    }
    return 0;
}
