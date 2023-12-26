import re
import spacy, coreferee
import pickle
from pathlib import Path
from os.path import join, exists


class OntoLoader:

    def __init__(self):
        self.nlp = spacy.load("en_core_web_lg")
        self.nlp.add_pipe('coreferee')


    def ner(self, filename):
        print("\n>> Applying NER to book corpus located in ",filename)

        with open(filename,'r') as f:
            txt = f.read().rstrip()
            doc = self.nlp(txt)
            entity_ids = {}
            print("\n",txt)


            for ent in doc.ents:
                print("\t>>> ENT:",ent.text, ent.start_char, ent.end_char, ent.label_)
        return doc


    def is_person(self, chain, ents):
        person = False
        for e in chain:
            e = e.pretty_representation
            m = re.search('(.*)\([0-9]*\)',e)
            if m.group(1) in ents['PERSON']:
                person = True
                break
        return person


    def get_entities(self, doc):
        ents = {'PERSON':[],'LOC':[], 'ORG':[]}
        for ent in doc.ents:
            #print(ent.text,ent.label_,ent.start)
            if ent.text not in ents and ent.label_ in ['PERSON','LOC','ORG']:
                if ent.text not in ents[ent.label_]:
                    ents[ent.label_].append(ent.text)
        return ents


    def eidx_to_name(self,doc):
        '''Map each entity id to a name'''
        ent_idx = {}
        ents = self.get_entities(doc)
        for chain in doc._.coref_chains:
            if not self.is_person(chain,ents):
                continue
            name=None
            for e in chain:
                name = doc._.coref_chains.resolve(doc[e[0]])
                if name is not None:
                    name = name[0].text
                    break

            for group in chain:
                for e in group:
                    ent_idx[e] = name
        #print(ent_idx)
        return ent_idx


    def coref(self, filename):
        '''Return the original document with corefs resolved.'''
        with open(filename,'r') as f:
            txt = f.read().rstrip()
            doc = self.nlp(txt)
            ent_idx = self.eidx_to_name(doc)

            doc_resolved = ""
            for token in doc:
                poss = False
                space = True
                if token.pos_ == 'PRON' and (token.dep_ == 'poss' or token.dep_ == 'appos'):
                    poss = True
                if token.pos_ =='PUNCT' and token.text in [',','.','!','?','-',':',';']:
                    space = False
                if token.pos_ =='PART' and token.dep_ == 'case':
                    space = False
                if token.i in ent_idx.keys() and not poss:
                    doc_resolved+=ent_idx[token.i]+' '
                #elif token.i in ent_idx.keys() and poss:
                #    doc_resolved+=ent_idx[token.i]+"'s "
                elif not space:
                    if token.text != '-':
                        doc_resolved = doc_resolved[:-1]+token.text+' '
                    else:
                        doc_resolved = doc_resolved[:-1]+token.text
                else:
                    doc_resolved+=token.text+' '
        return doc_resolved, ent_idx


    def bounding_box_people(self, doc_resolved_str, ent_idx):
        '''Take a string with corefs resolved and turn it into people bounding boxes.'''
        doc = self.nlp(doc_resolved_str)
        i = 0
        ents = []
        for token in doc:
            if token.pos_ == 'PUNCT' and token.text in ['.','!','?']:
                sent = doc_resolved_str[i:token.idx+1]
                for ent in ents:
                    bounding_box = "\t<person name='"+ent+"'>"+sent+"</person>\n"
                    print(bounding_box)
                sent = ''
                ents = []
                i = token.idx+1
            if token.i in ent_idx:
                ents.append(ent_idx[token.i])
