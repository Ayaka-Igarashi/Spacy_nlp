import benepar, spacy
from spacy.tokenizer import Tokenizer
from spacy.pipeline import DependencyParser
import re
# import neuralcoref
import coreferee

# f_input = open('opt/parsetest_state_p.txt', 'r', encoding='UTF-8')
f_input = open('a.txt', 'r', encoding='UTF-8')
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

# ハイフンで区切らないように調整
infixes = []
for infix_ in nlp.Defaults.infixes:
   if '-' not in infix_:
      infixes.append(infix_)
infix_re = spacy.util.compile_infix_regex(infixes)
nlp.tokenizer.infix_finditer = infix_re.finditer

docs = []

for data in datalist:
   docs.append(nlp(data.rstrip('\n').lstrip(" ")))
   
# docs.append(nlp('Although he was very busy with his work, Peter had had enough of it. He and his wife decided they needed a holiday. They travelled to Spain because they loved the country very much.'))

# docs.append(nlp("This is an end-of-file. Switch to the state."))
# docs.append(nlp("This is an U+39c7"))
# # docs.append(nlp("This is an endof file"))
# docs.append(nlp("Emit a start tag."))
# docs.append(nlp("Emit a start tag (this is true. )."))

# for doc in nlp.pipe("This is an end-of-file. Switch to the state.", batch_size=50):
#     print(doc)

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
    
for doc in docs:
    for sent in list(doc.sents):
        print(sent._.parse_string)
        # print(list(sent._.children)[0])
        replace_in_np(sent)
        print(construct_dep_tree(sent))
        # for token in sent:
        #     print(token.text, token.dep_, token.head.text,
        #         #   token.head.pos_,
        #         #   [child for child in token.children]
        #         )
        print("")

# for doc in docs:
#    for sent in list(doc.sents):
#       f_out.write(sent._.parse_string)
#       f_out.write('\n')
# f_out.close()