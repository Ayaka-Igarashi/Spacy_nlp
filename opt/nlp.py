import benepar, spacy
from spacy.tokenizer import Tokenizer
# import neuralcoref
import coreferee

f_input = open('opt/htmlParseOut.txt', 'r', encoding='UTF-8')
# f_input = open('a.txt', 'r', encoding='UTF-8')
datalist = f_input.readlines()
f_input.close()

f_out = open('nlpOut.txt', 'w')

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

# ハイフンで区切らないように調整
infixes = []
for infix_ in nlp.Defaults.infixes:
   if '-' not in infix_:
      infixes.append(infix_)
infix_re = spacy.util.compile_infix_regex(infixes)
nlp.tokenizer.infix_finditer = infix_re.finditer

docs = []

for data in datalist:
  if data.startswith("#"):
    f_out.write(data[1:])
  else:
    doc = nlp(data.rstrip('\n').lstrip(" "))
    for sent in list(doc.sents):
      f_out.write(sent._.parse_string)
      f_out.write('\n')

# for doc in docs:
#    # for token in doc:
#    #    f_out.write(token.text)
#    # doc._.coref_chains.print()
   
#    # f_out.write(str(doc._.coref_chains))
#    # f_out.write('\n')
#    for sent in list(doc.sents):
#       f_out.write(sent._.parse_string)
#       f_out.write('\n')
f_out.close()