---
layout: page
title: Building citation networks to obtain literature datasets
description: Using the semantic scholar research corpus citation data to generate citation network graphs
img: /projects/4_citationmaps/citation-map.PNG
importance: 1
---

<!-- [test](/projects/1_nlp) -->

<!-- https://gist.github.com/pierrejoubert73/902cc94d79424356a8d20be2b382e1ab -->


<details>
<summary> This page outlines <b>building citation networks from a seed corpus</b> to obtain a full corpus for topic modeling.</summary>
<p>
<br>
<code>
One of the main challenes I've encountered in natural language processing of scientific literature is how to get a representative collection of articles. Searching for articles that have a given term (e.g. carbon nanotube) might miss relevant articles that just don't happen to use that word. To solve this problem I've been experimenting with building citation networks from the semantic scholar open research corpus. 
</code>
</p>
</details>

* Use the [Semantic Scholar Open Research Corpus](https://api.semanticscholar.org/corpus/) as a MySQL database, allowing for **quick local access to metadata for ~25 million papers**
* Able to quickly get a set of paper abstracts from a simple search term, then building a citation network
* Perform topic modeling on the dataset with a [CorEx topic model](https://github.com/gregversteeg/corex_topic)


[See the repository here](https://github.com/aspitarl/NLP-Semantic) for the codes used to generate the plots below and more information about the dataset used. 


# Building a Citation network for "Geographic imaging system"

The semantic scholar dataset includes information about **references and citations** for a paper, allowing us to build graphs of citations. The 2D layouts are determined by the [Force Atlas Algorithm](https://github.com/bhargavchippada/forceatlas2)

### Citation network algorithm

1. Obtain 3000 papers for the phrase "geographic imaging system"
2. Keep the largest connected graph
3. Trim to 300 most connected papers, based on number of connected edges
4. Grow the graph by adding references and citations, then trimming to a larger amount. 

<figure>
<img src="cit_tree_rounds.png" style="max-width: 100%; height:auto;">
<figcaption style="text-align: center;font-style: italic;">This shows the citation network building through one algorithm. </figcaption>
</figure>

### Resulting final literature dataset (~10000 abstracts)

Below is the final dataset of papers with the growth round indicated by the color. 

<div style="text-align:center;">
  <embed type="text/html" src="cit_tree_bokeh.html" style="width:100%; height:700px;" > 
</div>

## Topic modeling on resulting literature dataset

Then on this final collection of papers, a topic modeling pipeline is performed 

1. **The starting text is the title and abstract concatenated**
2. Check for the top 130 words in the overall semantic dataset and remove those (e.g. 'science', 'research', 'et al', etc.) and remove along with general stopwords
3. Apply the **[Mat2Vec](https://github.com/materialsintelligence/mat2vec) text processing** to intellgently handle chemical formulas
4. Pefrom Porter Stemming (testing -> test)
5. Form bigrams (natural language -> natural_language)
6. Perform **topic modeling with a [Correlation Explanation (CorEx)](https://github.com/gregversteeg/corex_topic) topic model** with 50 topics.  CorEx generally forms better topics to me than LDA and also allows for anchoring of topics, though I don't utilize anchoring here. 

### Hot topics

By looking at the trend in the probability for each topic over each year, we can **find which topics are 'hot' and which topics are 'cold'**. 

<figure>
<img src="top_slopes_plot.png"/>
<figcaption style="text-align: center;font-style: italic;">This show the top 10 topics as determined by the CorEx topic model, ranked by the slope of the topic probability over the past 5 years</figcaption>
</figure>

### Interactive topic visualization

Below is an interactive visualization of the topic model. **This visualization was developed as part of the MLEF 2021 program and is described further [here](https://mlef-energy-storage.github.io/).**

<div class="row" style="width:100%">
  <embed type="text/html" src="topic_network.html" style="width:100%; height:2000px"> 
</div>

