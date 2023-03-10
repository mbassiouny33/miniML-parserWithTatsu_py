#!/usr/bin/env python
# coding: utf-8

# #EITQ TP4: Languages

# In[60]:


get_ipython().system('pip install tatsu')


# Let us import the library so we can use it. We also take this opportunity to give a short nickname to some of the trees generated by `tatsu`. 

# In[61]:


import tatsu
from tatsu.ast import AST


# These two will come as handy in order to visualize some of trees:

# ## Mini-project

# 
# 
# 1.   By incremental modifications of the last version of the above-given grammars, provide a grammar for `Mini-ML` language we saw in class.
# 2.   Implement the big steps semantics of `Mini-ML` we saw in class. 
# 
# *Advanced.*
# 
# 3.   In your grammar and semantics, modify the type of constants to be booleans instead of integers or floats, and let the primitives be Not, Or, And, Nand gates, so as to eventually obtain a custom language: `Circuit-ML`. 
# 4.    Implement a type-checker for `Circuit-ML`.
# 
# 
# ###### add exponentiaion **

# ## Mini-proj answers 

# 1. grammar for mini-ml

# In[1]:


# grammar 2, overwrite 1 because the question was modified in miniprojet.pdf and now it requests to implement MiniML with a prefix notation! 
import tatsu
grammar = """
@@grammar::CALC


start
    =
    expression $
    ;

expression
    =
    | application
    | int
    | addition
    | subtraction
    | multiplication
    | division
    | exp
    | parentheses
    | pair
    | fst
    | snd
    | comp
    | assignmentlet
    | assignment
    | variable
    | lambda_function
    
    ;

  
comp 
    = 
    | gt
    | lt
    | geq
    | leq
  ;  
gt::gt = left:'>' right:pair;
lt::lt = left:'<' right:pair;
geq::geq = left:'>=' right:pair;
leq::leq = left:'<=' right:pair;
# we don't want to define booleans here, so these operators don't make much sense,specially without branching
    
parentheses::par  = '(' expr:expression ')' ;  

int::int
    =
    /\d+/
    ;



addition::add
    =
    left:'+' right:pair
    ;

subtraction::sub
    =
    left:'-' right:pair
    ;
    
multiplication::mul
    =
    left:'*' right:pair
    ;

division::div
    =
    left:'/' right:pair
    ;
exp::exp =left:'^' right:pair;

pair::pair = '(' left:expression ',' right:expression ')' ;
fst::fst = 'fst' pair ;
snd::snd = 'snd' pair ;




variable = /[a-z]+/!'=' ;

@@keyword :: let
assignmentlet::assignlet =  'let' /[a-z]+/ '=' expression 'in' expression ;

assignment::assign =  vname: /[a-z]+/ '=' left: expression ';' right: expression ;



lambda_function::lfct
    =
    'Lambda'  left:variable ':' right:expression
    ;



application::apply =/ /<{expression}+ ;

#application::apply =ex:/ /<{expression}+ ;




"""


parser = tatsu.compile(grammar)

def parse_expr(code):
    return parser.parse(code)

# Parse an expression
ast = parse_expr("+(1,42)")
ast2 = parse_expr("*(1,42)")
ast3 = parse_expr("fst(13,42)")    
# ast3 = parse_expression("let x=3 in (fst(x,24))")
ast4 = parse_expr("Lambda fct: 3")     # lambda
ast5=parse_expr("1 2 (x=1;47) *(42,7)")  #application
ast6=parse_expr("x=10;+(x,42)")  #assign
ast7=parse_expr("x=10;>(x,42)")  # gt
ast7=parse_expr("(40)") 
ast7=parse_expr("^(40,3)") # gt
# parser.parse("let x=1 in +(x,1)") #won't work, 'if' is defined similarly in doc, tatsu is just being a ****.
sep=40
ast2,ast3,ast4,"--"*sep,ast5,"--"*sep,ast6,ast7


# In[2]:


from pprint import pprint
import json
parser = tatsu.compile(grammar, asmodel=True)
ast = parser.parse("* ( 10, 20 )")
print(type(ast).__name__)
print(type(ast))
print(json.dumps(ast.asjson(), indent=4))


# In[3]:


#Question 2

from tatsu.walkers import NodeWalker

# @param takes a tree a string and a value, find the given string in the tree 
# @returns a modified tree with [find<-replace]
def find_and_replace(tree,find,replace):
    if type(tree).__name__ in ["add","sub","mul","div"]:
        #right is op, nothing to do there, 
        find_and_replace(tree.right,find,replace)
    if type(tree).__name__ == "pair":
        if tree.right==find:
#             print("FOUND IT1")
            tree.right=replace
        if tree.left==find:
#             print("FOUND IT2")
            tree.left=replace
        find_and_replace(tree.right,find,replace)
        find_and_replace(tree.left,find,replace)


class miniMLWalker(NodeWalker):
    def walk_object(self, node):
#        print (node)
        raise Exception('Unexpected tyle %s walked', type(node).__name__,node)
#         return node
#     def walk_str(self, s):
#         print("ooops, found an str",s)
#         return
        
    def walk_int(self, ast):
#         print("number",ast)
        return int(ast)
    
    def walk_add(self, node):
        return self.walk_fst(node.right) + self.walk_snd(node.right)

    def walk_sub(self, node):
        return self.walk_fst(node.right) - self.walk_snd(node.right)

    def walk_mul(self, node):
        return self.walk_fst(node.right) * self.walk_snd(node.right)

    def walk_div(self, node):
        #warning, python division (in particular) is not closed in the sense that it result in a float, not a type in our language,
        # which is different than ML behavior for simplicity we just cast it to int, we don't deal with /. and /, etc
        return int(self.walk_fst(node.right) / self.walk_snd(node.right))
    def walk_exp(self,node):
        return self.walk_fst(node.right) ** self.walk_snd(node.right)
##############################
    def walk_gt(self,node):
        return self.walk_fst(node.right) > self.walk_snd(node.right)
    def walk_lt(self,node):
        return self.walk_fst(node.right) < self.walk_snd(node.right)
    def walk_geq(self,node):
        return self.walk_fst(node.right) >= self.walk_snd(node.right)
    def walk_leq(self,node):
        return self.walk_fst(node.right) <= self.walk_snd(node.right)
##############################
    def walk_fst(self, node):
        return self.walk(node.left)

    def walk_snd(self, node):
        return self.walk(node.right)

    def walk_pair(self, node):
        return (self.walk(node.left), self.walk(node.right))

    def walk_lfct(self, node):
#         print(f"called lfct {node}")
#         print(node)
        #'Lambda'  left:variable ':' right:expression
        x = node.left
#         e2 = node.right
        
#         exp = self.walk(node.expression)
        return lambda x: self.walk(node.right)

# not needed because there are no applications unless they are under a lambda
    def walk_apply(self, node):
        # Walk the left operand and bind it to a variable
#         print(f"called apply {node}")
   
#         return f(x)
        return node
    
    def walk_assign(self, node):
        x = node.vname # this becomes the bound variable in the expression node.right
        e1 = self.walk(node.left)
        e2 = node.right
        find_and_replace(e2,x,e1) #this functions avoids any "cheating" with eval or manipulation of global variable to force a cast back and forth
        return self.walk(e2)
    def walk_par(self, node):
        return self.walk(node.expr)

    
parser = tatsu.compile(grammar, asmodel=True)
def comp_expr(code):
    var=parse_expr(code)
    return miniMLWalker().walk(var)
    
# Create a MiniML walker

test = "/(21,3)"
ast = parser.parse(test)
ast2 = parse_expr("*(1,42)") #42
ast4 = parse_expr("Lambda fct: 3") #a constant function
ll = miniMLWalker().walk(ast4)
# ast5=parse_expr("1 2 (x=1;47) *(42,7)")
ast5=("1 2 48 14")  #
asgn=("x=10;(+(x,3),42)")  #here the x in the nested expressions is replaced with 10 [see below]
comp7=(">=(40,42)")  #False
par8="(40)"  #40
exp="^(5,2)"  #exp 5^2 = 25
result = miniMLWalker().walk(ast)

# Print the result
print(">>> lambda:",ll(0)) #the lambda function
msg_arr=["assign","comp","par8","exp" , "result"]
tst_arr=[ asgn   , comp7,par8,exp , result]
for i in range(len(tst_arr)):
    print(f"{msg_arr[i]}>>>",comp_expr(tst_arr[i]))

Example of what `find_and_replace` does:

called from assign(), before find_and_replace {
  "__class__": "pair",
  "right": 42,
  "left": {
    "__class__": "add",
    "right": {
      "__class__": "pair",
      "right": 3,
      **"left": "x"**
    },
    "left": "+"
  }
}

called from assign(), before find_and_replace {
  "__class__": "pair",
  "right": 42,
  "left": {
    "__class__": "add",
    "right": {
      "__class__": "pair",
      "right": 3,
      **"left": 10**
    },
    "left": "+"
  }
}
Notice how the part between "**"  has been modified from "left": "x" to "left": 10
# Note that the implementation of the >,<,<= and >=  operators is not perfect just like division that returns a float, because we return type boolean which is not exactly part of the source language

# In[4]:


# question 3 grammar for CircuitML 
import tatsu
grammarCML = """
@@grammar::CALC


start
    =
    expression $
    ;

expression
    =
    | application
    
    | True
    | False
    | negation
    | b_and
    | b_or
    | nand
    | parentheses
    | pair
    | fst
    | snd
    | assignmentlet
    | assignment
    | variable
    | lambda_function
    | if_statement
    
    ;

if_statement:: opif = 'If' cond:expression 'Then' left: expression  'Else' right: expression 'Endif';
False = 'False';
True = 'True';

parentheses::par  = '(' expr:expression ')' ;  

negation::neg
    =
    left:'!' right:expression 
    ;

b_and::and
    =
    left:'&' right:pair
    ;
    
b_or::or
    =
    left:'|' right:pair
    ;

nand::nand
    =
    left:'Nand'~ right:pair
    ;



pair::pair = '(' left:expression ',' right:expression ')' ;
fst::fst = 'fst' pair ;
snd::snd = 'snd' pair ;




variable = /[a-z]+/!'=' ;

@@keyword :: let
assignmentlet::assignlet =  'let' /[a-z]+/ '=' expression 'in' expression ;

assignment::assign =  vname: /[a-z]+/ '=' left: expression ';' right: expression ;



lambda_function::lfct
    =
    'Lambda'  left:variable ':' right:expression
    ;



application::apply =/ /<{expression}+ ;




"""




def parse_expr(code):
    parser = tatsu.compile(grammarCML)
    return parser.parse(code)

# Parse an expression
ast = parse_expr("&(False,True)")
ast2 = parse_expr("|(False,True)")
ast3 = parse_expr("fst(False,True)")
# # ast3 = parse_expression("let x=3 in (fst(x,24))")
ast4 = parse_expr("Lambda fct: True")
# ast5=parse_expr("1 2 (x=1;47) *(42,7)")
ast6=parse_expr("x=True;fst(False,True)")
ast7=parse_expr("Nand(False,True)")
astTrue=parse_expr("If True Then |(False,True) Else |(False,True) Endif")
result4 = parse_expr("Lambda fct: (Lambda fctt: True)")

#parser.parse("let x=1 in +(x,1)") #won't work, 'if' is defined similarly in doc, tatsu is just being a ****.

ast,ast2,ast3,ast4, ast6,ast7
#result4


# In[6]:


#question 3 contin'd
from tatsu.walkers import NodeWalker
def find_and_replace_b(tree,find,replace):
#     print("gonna find", find, "and repalce it with", replace)
#     print ('got a type: ', type(tree).__name__,">>",tree)
        
    if type(tree).__name__ in ["and","or","nand"]:
        #right is op, nothing to do there, 
        find_and_replace_b(tree.right,find,replace)
    if type(tree).__name__ in ["pair","neg"]:
        if tree.right==find:
#             print("FOUND IT1")
            tree.right=replace
        if tree.left==find:
#             print("FOUND IT2")
            tree.left=replace
        find_and_replace_b(tree.right,find,replace)
        find_and_replace_b(tree.left,find,replace)

class circMLWalker(NodeWalker):
    def walk_object(self, node):
        if node=="True": return True
        elif node=="False": return False
        
        raise Exception('Unexpected tyle %s walked', type(node).__name__,node)
#         return node
    def walk_bool(self, b):
#         print("str",s)
        return bool(b)

    
    def walk_neg(self, node):
#         print ("not",node)
        return not(self.walk(node.right))

    def walk_and(self, node):
        return self.walk_fst(node.right) and self.walk_snd(node.right)

    def walk_or(self, node):
        return self.walk_fst(node.right) or self.walk_snd(node.right)

    def walk_nand(self, node):
        return not(self.walk_fst(node.right) and self.walk_snd(node.right))

    def walk_fst(self, node):
        return self.walk(node.left)

    def walk_snd(self, node):
        return self.walk(node.right)

    def walk_pair(self, node):
        return (self.walk(node.left), self.walk(node.right))
    def walk_opif(self,node):
        cond = self.walk(node.cond)
        if cond :
            return self.walk(node.left)
        return self.walk(node.right)
        

    def walk_lfct(self, node):
#         print(f"called lfct {node}")
#         print(node)
        #'Lambda'  left:variable ':' right:expression
        x = node.left
#         e2 = node.right
        
#         exp = self.walk(node.expression)
        return lambda x: self.walk(node.right)

    def walk_apply(self, node):
        return node
#         # Walk the left operand and bind it to a variable
#         print(f"called apply {node}")
#         return
#         f = self.walk(node.left)
#         # Walk the right operand and bind it to a variable
#         x = self.walk(node.right)
#         # Return the result of applying the function to the argument
#         return f(x)

    def walk_assign(self, node):
        x = node.vname # this becomes the bound variable in the expression node.right
        e1 = self.walk(node.left)
        e2 = node.right
#         print(f"called from assign, before {e2}")
        find_and_replace_b(e2,x,e1) #this functions avoids any "cheating" with eval or manipulation of global variable to force a cast back and forth
#         print(f"called from assign, after {e2}") 
        return self.walk(e2)
    def walk_par(self, node):
        return self.walk(node.expr)

def parse_expr2(code):
    parser = tatsu.compile(grammarCML,asmodel=True)
    ast2cml= parser.parse(code)
    return circMLWalker().walk(ast2cml)

# parse_expr("If True Then |(False,True) Else |(False,True) Endif")
result1 = parse_expr2("If True Then (True,True) Else False Endif")  #(true,true)

result2 = parse_expr2("If False Then (True,True) Else &(False,False) Endif") #false


result3 = parse_expr2("x=True;!&(False,True)")  #not then and || #false

result4 = parse_expr2("x=True;Nand(False,True)") #same as above but using nand ||  #false


# parser = tatsu.compile(grammarCML)
# ast=parser.parse("& (False,True)", semantics=circMLWalker())


# Print the result
result1, result2,result3,result4, f"test nand is ok:{(result4==result3)}"


# ## Question 4 : 
# for simplicity we will keep the grammar as is, the type checking will only be external/cosmetic.
# 
# This approach makes more sense because we don't always have access to the language itself and usually we implement verification tools, typecheckers, with decorators/externally without messing up with the language itself.

# In[7]:


# Question 4  

from tatsu.walkers import NodeWalker


class circMLCheckWalker(NodeWalker):
    def walk_object(self, node):
        if node=="True": return (True, "B")
        elif node=="False": return (False, "B")
        raise Exception('Unexpected tyle %s walked', type(node).__name__,node)
#         return node
    def walk_bool(self, b):
#         print("str",s)
        return (bool(b), "B")

    
    def walk_neg(self, node):
#         print ("not",node)
        e,t = self.walk(node.right)
        return (not(e),t)

    def walk_and(self, node):
        r,rt = self.walk_fst(node.right)
        l,lt = self.walk_snd(node.right)
        if not (lt ==rt):
            raise Exception('Type error in and fct', type(node).__name__,node)
        return  ((r and l) ,lt)

    def walk_or(self, node):
        r,rt = self.walk_fst(node.right)
        l,lt = self.walk_snd(node.right)
        if not (lt ==rt):
            raise Exception('Type error in or fct', type(node).__name__,node)
        return  ((r or l) ,lt)

    def walk_nand(self, node):
        r,rt = self.walk_fst(node.right)
        l,lt = self.walk_snd(node.right)
        if not (lt ==rt):
            raise Exception('Type error in nand fct', type(node).__name__,node)
        return  (not(r and l) ,lt)

    def walk_fst(self, node):
        #by design will return the type of the first element when it reaches the end of the parsing with walk_bool
        return self.walk(node.left)

    def walk_snd(self, node):
        return self.walk(node.right)

    def walk_pair(self, node):
        
        r,rt = self.walk(node.left)
        l,lt = self.walk(node.right)
        return ((r,l), f"{rt} * {lt}")
    def walk_opif(self,node):
        cond,c_type = self.walk(node.cond)
        if c_type != "B": raise Exception("type error tried do an if with non boolean condition")
        if cond  :
            return self.walk(node.left)
        return self.walk(node.right)
    
        

    def walk_lfct(self, node):
        #'Lambda'  left:variable ':' right:expression
        x = node.left
        y, t= self.walk(node.right)
        return ( lambda x: y, f"(%REP% ->{t})")

    def walk_apply(self, node):
        return node


    def walk_assign(self, node):
        x = node.vname # this becomes the bound variable in the expression node.right
        e1,t1 = self.walk(node.left)
        e2 = node.right
        find_and_replace_b(e2,x,e1) #this functions avoids any "cheating" with eval or manipulation of global variable to force a cast back and forth
        return self.walk(e2)
    def walk_par(self, node):
        return self.walk(node.expr)

def parse_expr2(code):
    parser = tatsu.compile(grammarCML,asmodel=True)
    return parser.parse(code)
def check_lambda(parsed, args_list):
    fct,typ =parsed
    
    tt=type(args_list[0]).__name__
    applied_type=typ.replace('%REP%',tt)
    applied_fct=fct
    for arg in args_list:
        applied_fct= applied_fct(arg)
        if tt !=type(arg).__name__ :
            raise Exception("type error: you are chaining lambda expressions of different types!")
        
    
    return (applied_fct, applied_type)

def typecheck(expr,*apps):
    ast2cml = parse_expr2(expr)
    result = circMLCheckWalker().walk(ast2cml) 
    if '%REP%' in str(result) and len(apps)>0:
        arg_list = [item for item in apps]
        return check_lambda(result,arg_list)
    return result
    
# parse_expr("If True Then |(False,True) Else |(False,True) Endif")
# ast2cml = parse_expr2("!False")
# result1 = circMLCheckWalker().walk(ast2cml) 
result1 = typecheck("!False")
result2 = typecheck("&(True,False)")
result3 = typecheck("(True,False)")
# result3FAIL = typecheck("&(True,1)") # this should fail
result4 = typecheck("x=True;(x,False)") 
result4 = typecheck("x=True;Nand(x,False)") 
try:
    expr="If (True,False) Then True Else False Endif"
    typecheck(expr)   # this should fail bcz non bool condition
except Exception as TypeErr:
    print(TypeErr,f"in <{expr}>")
    

result4 = typecheck("If (x=True;&(x,False)) Then (True,True) Else False Endif")   ##test parentheses  + opif
#lambda fct typechecking
result5 = typecheck("Lambda fct: True") #the absract type unapplied
result5 = typecheck("Lambda fct: True",3)   #the type after application

#Nested lambda fct typechecking
try:
    #this should fail type error: you are chaining lambda expressions of different types!
    typecheck("Lambda fct: (Lambda fctt: True)",3,"False")
except Exception as TypeErr:
    print(TypeErr,f"in <{expr}>")
#this howerver should work fine
result7 = typecheck("Lambda fct: (Lambda fctt: True)",3,3)    
# ast=parser.parse("& (False,True)", semantics=circMLWalker())


# Print the result
print(result1,"\n",result2,"\n",result3,"\n ",result4,"\n\n",result5, "\n\n",result7)

