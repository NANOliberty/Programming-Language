import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Scanner;

/**
 * 구현과제1 - Recursive-Descent Parser (Java)
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
 */
public class Parser {

    /** 문법 오류 신호. 어디서 발생하든 parse()에서 한 번에 잡는다. */
    static class ParseError extends Exception {
        ParseError() { super(null, null, false, false); }
    }

    /** <expr>의 결과: 정수(<aexpr>) 또는 불리언(<bexpr>). */
    static class Value {
        final boolean isBool;
        final int num;
        final boolean bool;

        Value(int num) { this.isBool = false; this.num = num; this.bool = false; }
        Value(boolean bool) { this.isBool = true; this.num = 0; this.bool = bool; }

        @Override
        public String toString() {
            return isBool ? (bool ? "TRUE" : "FALSE") : Integer.toString(num);
        }
    }

    private static final String[] RELOPS = {"==", "!=", "<", ">", "<=", ">="};
    private static final String[] VARS = {"x", "y", "z"};

    private final Map<String, Value> vars = new HashMap<>();
    private String[] tokens;
    private int pos;
    private List<Value> outputs;

    // ----- 토큰 유틸 -----
    private String peek(int offset) {
        int i = pos + offset;
        return i < tokens.length ? tokens[i] : null;
    }

    private String peek() { return peek(0); }

    private String advance() throws ParseError {
        if (pos >= tokens.length) throw new ParseError();
        return tokens[pos++];
    }

    private void match(String expected) throws ParseError {
        if (!expected.equals(peek())) throw new ParseError();
        pos++;
    }

    private static boolean contains(String[] set, String tok) {
        if (tok == null) return false;
        for (String s : set) if (s.equals(tok)) return true;
        return false;
    }

    private static boolean isNumber(String tok) {
        if (tok == null || tok.isEmpty()) return false;
        for (char c : tok.toCharArray()) if (c < '0' || c > '9') return false;
        return true;
    }

    // ----- 진입점 -----
    void parse(String line) {
        tokens = line.trim().isEmpty() ? new String[0] : line.trim().split("\\s+");
        pos = 0;
        outputs = new ArrayList<>();
        for (String v : VARS) vars.put(v, new Value(0)); // 한 줄 = 하나의 프로그램이므로 매번 초기화
        try {
            program();
            if (!outputs.isEmpty()) {
                StringBuilder sb = new StringBuilder(">>");
                for (Value v : outputs) sb.append(' ').append(v);
                System.out.println(sb);
            }
        } catch (ParseError e) {
            System.out.println(">> syntax error!!");
        }
    }

    // <program> → {<statement>}
    private void program() throws ParseError {
        while (peek() != null) statement();
    }

    // <statement> → <var> = <expr> ; | print <var> ;
    private void statement() throws ParseError {
        if ("print".equals(peek())) {
            advance();
            String name = var();
            match(";");
            outputs.add(vars.get(name));
        } else {
            String name = var();
            match("=");
            Value value = expr();
            match(";");
            vars.put(name, value);
        }
    }

    // <var> → x | y | z
    private String var() throws ParseError {
        String tok = advance();
        if (!contains(VARS, tok)) throw new ParseError();
        return tok;
    }

    // <expr> → <bexpr> | <aexpr>   (두 번째 토큰이 <relop>이면 <bexpr>)
    private Value expr() throws ParseError {
        if (isNumber(peek()) && contains(RELOPS, peek(1))) return new Value(bexpr());
        return new Value(aexpr());
    }

    // <bexpr> → <number> <relop> <number>
    private boolean bexpr() throws ParseError {
        int left = number();
        String op = advance();
        if (!contains(RELOPS, op)) throw new ParseError();
        int right = number();
        switch (op) {
            case "==": return left == right;
            case "!=": return left != right;
            case "<":  return left < right;
            case ">":  return left > right;
            case "<=": return left <= right;
            default:   return left >= right;
        }
    }

    // <aexpr> → <term> {( + | - ) <term>}
    private int aexpr() throws ParseError {
        int result = term();
        while ("+".equals(peek()) || "-".equals(peek())) {
            String op = advance();
            int rhs = term();
            result = op.equals("+") ? result + rhs : result - rhs;
        }
        return result;
    }

    // <term> → <factor> {( * | / ) <factor>}
    private int term() throws ParseError {
        int result = factor();
        while ("*".equals(peek()) || "/".equals(peek())) {
            String op = advance();
            int rhs = factor();
            if (op.equals("*")) {
                result *= rhs;
            } else {
                if (rhs == 0) throw new ParseError();
                result /= rhs;
            }
        }
        return result;
    }

    // <factor> → <number>
    private int factor() throws ParseError {
        return number();
    }

    // <number> → <dec> {<dec>}
    private int number() throws ParseError {
        String tok = advance();
        if (!isNumber(tok)) throw new ParseError();
        return Integer.parseInt(tok);
    }

    public static void main(String[] args) {
        Parser parser = new Parser();
        Scanner in = new Scanner(System.in);
        while (true) {
            System.out.print(">> ");
            if (!in.hasNextLine()) break;
            String line = in.nextLine();
            if (line.trim().equals("terminate")) break;
            parser.parse(line);
        }
    }
}
