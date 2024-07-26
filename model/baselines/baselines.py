from argparse import ArgumentParser
import json
from tqdm import tqdm
import requests
import pickle
from wikimapper import WikiMapper

from refined.inference.processor import Refined
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from trie import Trie, MarisaTrie

models = {
  "refined": lambda: Refined.from_pretrained(model_name='wikipedia_model_with_numbers', entity_set="wikidata"),
  # Requires docker running
  "extend": lambda: lambda t: requests.post('http://127.0.0.1:22002/', json=[{"text": t}]).json(),
  "genre": lambda: (
    AutoTokenizer.from_pretrained("facebook/genre-kilt"),
    AutoModelForSeq2SeqLM.from_pretrained("facebook/genre-kilt").eval(),
    Trie.load_from_dict(pickle.load(open("kilt_titles_trie_dict.pkl", "rb"))),
  ),
  "mgenre": lambda: (
    AutoTokenizer.from_pretrained("facebook/mgenre-wiki"),
    AutoModelForSeq2SeqLM.from_pretrained("facebook/mgenre-wiki").eval(),
    pickle.load(open("titles_lang_all105_marisa_trie_with_redirect.pkl", "rb"))
  )
}

mapper = WikiMapper("index_enwiki-20190420.db")

argparser = ArgumentParser()
argparser.add_argument("-i", "--input", type=str, required=True)
argparser.add_argument("-o", "--output", type=str, required=True)
argparser.add_argument("-m", "--model", type=str, required=True)

if __name__ == "__main__":
  args = argparser.parse_args()

  model = models[args.model]()

  documents = [json.loads(d) for d in open(args.input).readlines()]
  for doc in tqdm(documents):
    if args.model == "refined":
      try:
        entities, scores = list(zip(*[
          (ent.wikidata_entity_id, score) 
          for span in model.process_text(doc["sentence"]) if span.text == doc["mention"] 
          for ent, score in span.top_k_predicted_entities]))
      except:
        entities, scores = ["NIL",], [1.0,]
    elif args.model == "extend":
      try:
        entities = [
          ent["entity"] 
          for ent in model(doc["sentence"])[0]["disambiguated_entities"]
          if ent["mention"] == doc["mention"]
        ]
        
        mapped_entities = [mapper.title_to_id(e.replace(" ", "_")) for e in entities]
        if mapped_entities[0] == None:
          response = requests.get('https://www.wikidata.org/w/api.php', 
            params={
                'action': 'wbsearchentities',
                'search': entities[0],
                'format': 'json',
                'errorformat': 'plaintext',
                'language': 'en',
                'uselang': 'en',
                'type': 'item',
            }, 
            headers={"Accept": "application/json"}
          )
          if len(response.json()["search"]) > 0:
            mapped_entities = [response.json()["search"][0]["id"]]


        entities = mapped_entities
      except:
        entities = []
      scores = []
    elif args.model == "genre":
      tokenizer, genre, trie = model
      
      sentences = [doc["sentence"].replace(doc['mention'], f"[START_ENT] {doc['mention']} [END_ENT]")]
      sentences = tokenizer(sentences, return_tensors="pt")

      outputs = genre.generate(
          **sentences,
          num_beams=10,
          num_return_sequences=10,
          prefix_allowed_tokens_fn=lambda batch_id, sent: trie.get(sent.tolist()),
      )

      entities = tokenizer.batch_decode(outputs, skip_special_tokens=True)
      mapped_entities = [mapper.title_to_id(e.replace(" ", "_")) for e in entities]
      if mapped_entities[0] == None:
        response = requests.get('https://www.wikidata.org/w/api.php', 
          params={
              'action': 'wbsearchentities',
              'search': entities[0],
              'format': 'json',
              'errorformat': 'plaintext',
              'language': 'en',
              'uselang': 'en',
              'type': 'item',
          }, 
          headers={"Accept": "application/json"}
        )
        if len(response.json()["search"]) > 0:
          mapped_entities = [response.json()["search"][0]["id"]]

      entities = mapped_entities
      scores = []
    elif args.model == "mgenre":
      tokenizer, genre, trie = model
      
      sentences = [doc["sentence"].replace(doc['mention'], f"[START] {doc['mention']} [END]")]
      sentences = tokenizer(sentences, return_tensors="pt")

      outputs = genre.generate(
          **sentences,
          num_beams=10,
          num_return_sequences=10,
          prefix_allowed_tokens_fn=lambda batch_id, sent: trie.get(sent.tolist()),
      )

      entities = tokenizer.batch_decode(outputs, skip_special_tokens=True)
      entities = [e.split(" >>")[0].replace(" ", "_") for e in entities]
      mapped_entities = [mapper.title_to_id(e) for e in entities]
      if all([ e is None for e in mapped_entities]):
        response = requests.get('https://www.wikidata.org/w/api.php', 
          params={
              'action': 'wbsearchentities',
              'search': entities[0],
              'format': 'json',
              'errorformat': 'plaintext',
              'language': 'en',
              'uselang': 'en',
              'type': 'item',
          }, 
          headers={"Accept": "application/json"}
        )
        if len(response.json()["search"]) > 0:
          mapped_entities = [response.json()["search"][0]["id"]]

      entities = mapped_entities
      scores = []

    doc["predictions"] = entities
    doc["scores"] = scores
  
  
  with open(args.output, "w") as f:
    for doc in documents:
      f.write(json.dumps(doc) + "\n")