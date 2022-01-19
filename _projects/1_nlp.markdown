---
layout: page
title: Topic Modeling of Energy Storage Literature 
description: Utilizing machine learning to facilitate scientific literature review
img: /projects/1_nlp/lit-clustering.png
importance: 1
---


<!-- Storing energy from intermittent renewables, such as wind and solar, is one of the most pressing challenges we face for enabling a sustainable civilization. [The scale of the problem is immense](https://ieeexplore.ieee.org/document/7229426). A wide array of energy storage technologies are under development, each with their own advantages and disadvantages for various use cases.  -->


Scientific research into energy storage technologies has exploded in recent years, as shown in the figure below. Sorting through this large body of knowledge to understand the state-of-the-art is a challenge. This project aims to **use artificial intelligence, specifically natural language processing, to extract insights from paper metadata found in the [Semantic Scholar Academic Graph](https://api.semanticscholar.org/corpus).** The goal is to be able to gain a big-picture view of the field to better direct research efforts and investments toward promising technologies. 


<figure>
<img src="lit-trends.png" style="width:1000px;"/>
<figcaption style="text-align: center;font-style: italic;">Left: The number of all annual publications in the left) full Semantic Scholar Open Research Corpus database, excluding papers categorized as solely 'Medicine' by Microsoft Academic and right) The percentage of papers containing term "Energy Storage" in the title or abstract.</figcaption>
</figure>


## Interactive Topic Model Plot
Below is an interactive plot that explores a topic model of an energy storage literature dataset. The literature dataset was obtained from the semantic scholar open research corpus by finding **papers that contained the term 'energy storage' in the title or abstract resulting in approximately 70,000 papers**. Topic modeling was performed using Latent Dirichlet Allocation (LDA) with [Gensim](https://radimrehurek.com/gensim/). LDA is an unsupervised machine learning technique to determine a set of topics that can represnt the modeled collection of texts (corpus).  To understand the high level structure of the corpus the probability that a given pair of topics are present together in the same paper was calculated. This co-occurrence matrix defines the edges of a graph where the nodes are each topic. Research communities are then determined through the Louvian community detection algorithm, as described in [Bickel (2019)](https://energsustainsoc.biomedcentral.com/articles/10.1186/s13705-019-0226-z).


<div class="row" style="width:100%">
  <embed type="text/html" src="topic_network.html" style="width:100%" height=2000> 
</div>







