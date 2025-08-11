NUMBER = "NUMBER"
PLUS = "PLUS"
MINUS = "MINUS"
TIMES = "TIMES"
DIVIDE = "DIVIDE"
LPAREN = "LPAREN"
RPAREN = "RPAREN"
op_map = {TIMES : '*', DIVIDE : '/', PLUS : '+', MINUS : '-'}

NAME = "NAME"
ASSIGN = "ASSIGN"

SEMICOLON = 'SEMICOLON'


LT = "LT"    # <
GT = "GT"    # >
LE = "LE"    # <= 
GE = "GE"    # >= 
EQ = "EQ"    # ==
NE = "NE"    # !=

class Token:
    def __init__(self, _type, value=None):
        self.type = _type
        self.value = value
    def __repr__(self):
        if self.value:
            return f"{self.type}({self.value})"
        else:
            return f"{self.type}"



def tokenize(expr):
    tokens = []

    i = 0
    while i < len(expr):
        current = expr[i]

        # handling the whitespace
        if current.isspace():
            i += 1
            continue

        # handling the digit case
        if current.isdigit():
            num = current
            i += 1
            while i < len(expr) and expr[i].isdigit():
                num += expr[i]
                i += 1
            tokens.append(Token(NUMBER, int(num)))
            continue
        
        # handle comparisons (and assignment)
        elif current == '<':
            if i + 1 < len(expr) and expr[i+1] == '=':
                tokens.append(Token(LE))
                i += 2
                continue
            else:
                tokens.append(Token(LT))
        
        elif current == '>':
            if i + 1 < len(expr) and expr[i] == '=':
                tokens.append(Token(GE))
                i += 2
                continue
            else:
                tokens.append(Token(GT))
        
        elif current == '=':
            if i + 1 < len(expr) and expr[i+1] == '=':
                tokens.append(Token(EQ))
                i += 2
                continue
            else:
                tokens.append(Token(ASSIGN))
        
        elif current == '!':
            if i + 1 < len(expr) and expr[i+1] == '=':
                tokens.append(Token(NE))
                i += 2


        # handling operations (+, -, *, /)
        elif current == '+':
            tokens.append(Token(PLUS))
        elif current == '-':
            tokens.append(Token(MINUS))
        elif current == '*':
            tokens.append(Token(TIMES))
        elif current == '/':
            tokens.append(Token(DIVIDE))
        elif current == '(':
            tokens.append(Token(LPAREN))
        elif current == ')':
            tokens.append(Token(RPAREN))
        
        elif current.isalpha() or current == '_':
            name = current
            i += 1
            while i < len(expr) and (expr[i].isalnum() or expr[i] == '_'):
                name += expr[i]
                i += 1
            tokens.append(Token(NAME, name))
            continue

        elif current == ';':
            tokens.append(Token(SEMICOLON))
        
        else:
            raise ValueError(f"Unexpected character : {current}")
        
        i += 1
    return tokens



class NumberNode:
    def __init__(self, number):
        self.number = number
    def __repr__(self):
        return str(self.number)

class UnaryOpNode:
    def __init__(self, oper, operand):
        self.oper = oper
        self.operand = operand
    def __repr__(self):
        return f"({self.oper}{self.operand})"

class NameNode:
    def __init__(self, name):
        self.name = name
    def __repr__(self):
        return self.name


class BinOpNode:
    def __init__(self, left, oper, right):
        self.left = left
        self.oper = oper
        self.right = right
    def __repr__(self):
        return f"({self.left} {self.oper} {self.right})"

class AssignNode:
    def __init__(self, name, value):
        self.name = name
        self.value = value
    def __repr__(self):
        return f"{self.name} = {self.value}"

class CompareNode:
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right
    def __repr__(self):
        return f"{self.left} {self.op} {self.right}"
        

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
    
    def peek(self): 
        # return the current token
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None
    
    def prev(self):
        # get back to the previous token
        self.pos -= 1
    
    def eat(self):
        # return current token and get to the next token
        token = self.peek()
        self.pos += 1
        return token
    
    def parse(self):
        return self.parse_statements()
    
    def parse_statements(self):
        statements = []
        while self.peek() is not None:
            stmt = self.statement()
            statements.append(stmt)
            current = self.peek()

            if current is not None and current.type == SEMICOLON:
                self.eat()   # consume semicolon
            else:
                break
        return statements

            
    
    def statement(self):
        current = self.peek()

        # handle assignment
        if current and current.type == NAME:
            name_token = self.eat()
            if self.peek() and self.peek().type == ASSIGN:
                self.eat()   # eat '='
                expr_node = self.expression()
                return AssignNode(name_token.value, expr_node)
            else:
                self.prev()


        return self.comparison()
    
    def comparison(self):
        node = self.expression()
        current = self.peek()
        if current and current.type in (LT, GT, LE, GE, EQ, NE):
            op = self.eat()
            right = self.expression()
            node = CompareNode(node, op.type, right)
        return node

    
    def expression(self):
        node = self.term()

        while True:
            current = self.peek()
            
            if current is None:
                break
            
            if current.type in (PLUS, MINUS):
                op = self.eat()
                right = self.term()
                node = BinOpNode(node, op_map[op.type], right)
            else:
                break
        
        return node
    
    def term(self):
        node = self.factor()

        while True:
            current = self.peek()
            if current is None:
                break
            
            if current.type in (TIMES, DIVIDE):
                op = self.eat()
                right = self.factor()
                node = BinOpNode(node, op_map[op.type], right)
            else:
                break
        
        return node
    
    def factor(self):
        current = self.peek()

        # handle unary operators
        if current.type in (PLUS, MINUS):
            op = self.eat()
            operand = self.factor()   # recursively parse the operand
            return UnaryOpNode(op_map[op.type], operand)

        # handle numbers
        if current.type == NUMBER:
            self.eat()
            return NumberNode(current.value)
        
        # handle variable names
        elif current.type == NAME:
            self.eat()
            return NameNode(current.value)
        
        # handle parentheses
        elif current.type == LPAREN:
            self.eat()  # eat '('
            node = self.expression()
            if self.peek() is None or self.peek().type != RPAREN:
                raise SyntaxError("Expected ')'")
            self.eat()

            return node
        
        # handle errors
        else:
            raise SyntaxError(f"Unexpected token : {current}")


# dictionary to keep track of variables
variables = {}

# evaluator function
def evaluate(node):
    if isinstance(node, NumberNode):
        return node.number
    elif isinstance(node, BinOpNode):
        left = evaluate(node.left)
        right = evaluate(node.right)

        if node.oper == '+':
            return left + right
        elif node.oper == '-':
            return left - right
        elif node.oper == '*':
            return left * right
        elif node.oper == '/':
            if right == 0:
                raise ZeroDivisionError("Error! Cannot divide by zero")
            return left // right    
    
    elif isinstance(node, AssignNode):
        value = evaluate(node.value)
        variables[node.name] = value
        return value
    
    elif isinstance(node, NameNode):
        if node.name not in variables:
            raise NameError(f"Undefined variable : {node.name}")
        return variables[node.name]

    elif isinstance(node, UnaryOpNode):
        operand = evaluate(node.operand)
        if node.oper == '+':
            return +operand
        elif node.oper == '-':
            return -operand
    
    elif isinstance(node, list):
        result = None
        for stmt in node:
            result = evaluate(stmt)
        return result
    
    elif isinstance(node, CompareNode):
        left = evaluate(node.left)
        right = evaluate(node.right)
        if node.op == LT:
            return left < right
        elif node.op == GT:
            return left > right
        elif node.op == LE:
            return left <= right
        elif node.op == GE:
            return left >= right
        elif node.op == EQ:
            return left == right
        elif node.op == NE:
            return left != right
            



if __name__ == "__main__":
    expr = "2 < 3; x = 2;x > 4"

    tokens = tokenize(expr)
    parser = Parser(tokens)
    ast = parser.parse()
    result = evaluate(ast)
    print(result)
    print(type(result))



