# MHERCL v1.0 - Benchmark

We aim to mitigate the need for gold-standard resources containing NERC- and EL-annotated historical documents by releasing a new model for historical entity linking and a new benchmark for the task. We release the Musical Heritage Historical named Entities Recognition, Classification and Linking benchmark (MHERCL v1.0) to enrich the landscape of gold-standard resources containing NERC- and EL-annotated historical documents.

## Statistics

#### MHERCL v1.0 - Dataset Stats

| Dataset                     | Lang. | #docs | #sents | #tokens |
|-----------------------------|-------|--------|---------|----------|
| MHERCL v1.0 | EN    | 76   | 875   | 27,549 |


#### MHERCL v1.0 - Named Entities Superficial Mentions Stats


|        | #mentions | #types | noisy    | NIL      |
|--------|-----------|---------|----------|----------|
| all    | 2,370   | N/A      | 0.14  | 0.30|
| unique | 1,805     | 58   | N/A | 0.38 |

As the tables above summarise, MHERCL v1.0 comprises 875 sentences extrapolated from 76 documents (historical periodicals). MHERCL v1.0 includes 1,805 unique named entities belonging to 58 different types. Of the annotated named entity mentions, 30% could not be linked to a QID. In those cases, the annotators could not identify a Wikidata entry corresponding to the named entity. Those cases are annotated with the label NIL. On the total of annotated named entity mentions, 14% are _noisy_, namely impacted by errors due to OCR.

## Exploratory Study

As the PKE framework automatically recognises named entities in its text-to-AMR parsing step, we ran a preliminary experiment to evaluate the off-the-shelf performance of the PKE text-to-AMR parser and its embedded entity linker, BLINK. We focused on a sample of 2205 sentences taken from the _Periodicals_ module of the PTC and on named entities of type person (pNE). The results are reported in the Table below and shared in a [TSV file](benchmark/preliminary_study/ptc_sample_pne_preliminary_study.tsv) in this repository.

#### Table reporting statistics about the off-the-shelf quality of [PKE](https://github.com/polifonia-project/Polifonia-Knowledge-Extractor) framework on EL of _person named entities_ in a [PTC](https://github.com/polifonia-project/Polifonia-Corpus) sample.

| #sents      | pNE mentions (#recognised) |   pNE mentions (#linked)    | pNE QID (#found)  |        pNE QID (#not found)   | pNE DoB  (#plausible)  | pNE DoB  (#implausible)|pNE DoB  (#not found)|
|-------|--------------|-------|----------|-----------|------------|--------------|-----------|
| 2205 | 2262         | 2108 | 2006    | 102   | 1199       | 203         | 604     |

## Sampling

The annotated sentences of MHERCL v1.0 were extrapolated from the [Polifonia Textual Corpus (PTC)](https://github.com/polifonia-project/Polifonia-Corpus). They originate from a sample of the English [_Periodicals_](https://doi.org/10.5281/zenodo.6671912) module of the corpus, whose documents' publication dates range from 1823 to 1900. They were processed through the [Polifonia Knowledge Extractor (PKE)](https://github.com/polifonia-project/Polifonia-Knowledge-Extractor) and are part of the [Filtered AMR Graphs Bank](https://zenodo.org/record/7025779\#.ZDls8OxBy3I).

## Annotation Guidelines

MHERCL v1.0 sentences are manually annotated. The annotations focus on Named Entities Recognition, Classification and Linking. Thanks to the work of two interns (Foreign Languages and Literature undergraduate students, both Italian native speakers, one graduating in English and Spanish Language and Literature, the other graduating in Russian and Spanish) who have received training on the NERC and EL annotation task. 

Generally, the annotation work was performed under the criteria that a named entity is a real-world thing indicating a unique individual through a proper noun. The interns' annotation work involved inspecting the sentences and identifying the named entities, eventually linking them to their corresponding Wikidata ID (QID).

| named entity type   | #occurrences |
|------------------------------|------------------------|
| person                       | 1253                   |
| city                         | 262                    |
| music                        | 187                    |
| organization                 | 93                     |
| work-of-art                  | 85                     |
| country                      | 80                     |
| building                     | 52                     |
| opera                        | 52                     |
| theatre                      | 42                     |
| worship-place                | 41                     |


Named entities were recognised, classified and linked following the [AMR named entity annotations guidelines](https://amr.isi.edu/doc/amr-dict.html\#named\%20entity).
The types were assigned according to the [AMR annotation guidance instructions](https://www.isi.edu/~ulf/amr/lib/popup/ne-type-selection.html) and extrapolated from the [AMR named entity types list](https://www.isi.edu/~ulf/amr/lib/ne-types.html). 

A full list of the types used for Named Entities classification is in the table above.

## Inter-annotator Agreement

| #sents | #tokens (Tot.) | # matching tokens (Annotated) | # unmatching tokens (Annotated) | Krippendorf's alpha |
|--------------------------|----------------------------------|------------------------------------------|------------------|--------------------|
| 101 | 6,589        | 656                 | 124              | 0.82 |


Inter-annotator agreement (IAA) measures the reliability of human annotations by estimating consistency among annotators. To measure IAA, we made two annotators independently annotate 101 sentences. We calculated Krippendorff's alpha for nominal metric on the resulting annotations using [Fast Krippendorf](https://github.com/pln-fing-udelar/fast-krippendorff). We opted for Krippendorff's alpha for its flexibility and resilience in handling missing values. We obtained the following result: 0.82. 

## Format
### CoNLL-U

```#document_date:1873
#sent_text:A native of Parma, ateighteen years of age ‘Jong was received into the Conservatory of Music of that town, where ‘Jong soon made himself.a name as the most promising pupil of the institution.
A	O	_	a	DET
native	O	_	native	NOUN
of	O	_	of	ADP
Parma	B-city	Q2683	Parma	PROPN
,	O	_	,	PUNCT
ateighteen	O	_	ateighteen	NUM
years	O	_	year	NOUN
of	O	_	of	ADP
age	O	_	age	NOUN
‘	O	_	'	PUNCT
Jong	B-person	NIL	Jong	PROPN
was	O	_	be	AUX
received	O	_	receive	VERB
into	O	_	into	ADP
the	O	_	the	DET
Conservatory	B-school	Q1439627	Conservatory	PROPN
of	I-school	Q1439627	of	ADP
Music	I-school	Q1439627	Music	PROPN
of	O	_	of	ADP
that	O	_	that	DET
town	O	_	town	NOUN
,	O	_	,	PUNCT
where	O	_	where	SCONJ
‘	O	_	'	PUNCT
Jong	B-person	NIL	Jong	PROPN
soon	O	_	soon	ADV
made	O	_	make	VERB
himself.a	O	_	himself.a	PRON
name	O	_	name	NOUN
as	O	_	as	ADP
the	O	_	the	DET
most	O	_	most	ADV
promising	O	_	promising	ADJ
pupil	O	_	pupil	NOUN
of	O	_	of	ADP
the	O	_	the	DET
institution	O	_	institution	NOUN
.	O	_	.	PUNCT
```

### JSONL

MHERCL is available on [HuggingFace](https://huggingface.co/datasets/n28div/MHERCL) in JSONL format.
