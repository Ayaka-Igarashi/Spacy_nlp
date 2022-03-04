import benepar, spacy
from spacy.tokenizer import Tokenizer
from spacy.pipeline import DependencyParser
import re
import stanza
import spacy_stanza
# import neuralcoref
# import coreferee

f_input = open('htmlParseOut.txt', 'r', encoding='UTF-8')
# f_input = open('a.txt', 'r', encoding='UTF-8')
datalist = f_input.readlines()
f_input.close()

f_out = open('output.txt', 'w')

special_cases = {"end of file": [{"ORTH": "end of file"}],
                  "end-of-file": [{"ORTH": "end-of-file"}],
                  "return state": [{"ORTH": "return state"}],
               }
special_case =  [{"ORTH": "\"script\""}]

def custom_tokenizer(nlp):
   return Tokenizer(nlp.vocab, rules=special_cases)


nlp = spacy.load("en_core_web_md")
# nlp.tokenizer = custom_tokenizer(nlp)
nlp.tokenizer.add_special_case("\"script\"",special_case)
nlp.add_pipe("benepar", config={"model": "benepar_en3"})
# nlp.add_pipe('coreferee')
# nlp.add_pipe("parser")

# ハイフンで区切らないようにinfix調整
infixes = []
for infix_ in nlp.Defaults.infixes:
   if '-' not in infix_:
      infixes.append(infix_)
infix_re = spacy.util.compile_infix_regex(infixes)
nlp.tokenizer.infix_finditer = infix_re.finditer

# 名詞部分のdepparseにstanzaを使う
stanza.download("en")
# 上のやつと同じようにtokenizeするよう設定(空白で分割)
nlp_stanza = spacy_stanza.load_pipeline("en", tokenize_pretokenized=True)

# データ読み込み
docs = []
for data in datalist:
  if data.startswith("#"):
    pass
    # f_out.write(data[1:])
  else:
    docs.append(nlp(data.rstrip('\n').lstrip(" ")))

def extract_np(sent):
    nplist = []
    for child in list(sent._.children):
        if len(child._.labels)!=0 and child._.labels[0] == 'NP':
            nplist.append(child)
        else:
            nplist.extend(extract_np(child))
    return nplist

def replace_in_np(sent):
    # print(list(sent._.children)[0])
    # print(sent._.labels[0] == 'NP')
    for child in list(sent._.children):
        # print(child._.labels)
        if len(child._.labels)!=0 and child._.labels[0] == 'NP':
            d = nlp(str(child))
            dt = construct_dep_tree(d)
            print(dt)
        else:
            replace_in_np(child)

def construct_dep_tree(doc):
    lst = []
    for token in doc:
        lst.append((token.head.i, token.i, token.text, token.dep_,
        ))
    head_l = [s for s in lst if s[3] == 'ROOT']
    if len(head_l) != 0:
        head = head_l[0]
        rst = [s for s in lst if s[3] != 'ROOT']
        return construct_dep_tree_sub(head[1], head[2], rst)[0]
    else:
        return ""

def construct_dep_tree_sub(head,label,lst):
    (found,rst) = find_dep_head(head,lst)
    children = []
    for f in found:
        (tree, r) = construct_dep_tree_sub(f[1], f[2], rst)
        rst = r
        children.append((f[3],tree))
    return ((label, children),rst)

def find_dep_head(idx,lst):
    found = [s for s in lst if s[0] == idx]
    rst = [s for s in lst if s[0] != idx]
    return (found, rst)

def to_tokenized_sent(sent):
    toknized = ""
    for tok in sent:
        toknized += str(tok) + " "
    toknized = toknized[0:-1]
    return toknized

npList = []
for doc in docs:
    for sent in list(doc.sents):
        npList.extend(list(map(to_tokenized_sent, extract_np(sent))))

for np in npList:
    doc = nlp_stanza(np)
    f_out.write(np)
    f_out.write('\n')
    for tok in doc:
      f_out.write(str(tok))
      f_out.write(" , ")
    f_out.write('\n')
    f_out.write('\n')
    for tok in doc:
        f_out.write(str(tok.i))
        # f_out.write(" " + str(tok.dep))
        f_out.write(" " + str(tok.dep_))
        f_out.write(" " + str(tok.head.i))
        
        f_out.write('\n')
    f_out.write('\n')
f_out.close()
