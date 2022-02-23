import benepar, spacy
from spacy.tokenizer import Tokenizer
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
nlp.add_pipe('coreferee')
# print(nlp.Defaults.infixes)

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

for doc in docs:
   # for token in doc:
   #    f_out.write(token.text)
   # doc._.coref_chains.print()
   
   # f_out.write(str(doc._.coref_chains))
   # f_out.write('\n')
   for sent in list(doc.sents):
      f_out.write(sent._.parse_string)
      f_out.write('\n')
f_out.close()