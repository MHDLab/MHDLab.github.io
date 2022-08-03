---
layout: page
title: Symposium on the Engineering Aspects of Magnetohydrodynamics
description: Preserving decades of research into magnetohydrodynamic power generation
img: /projects/3_mhdseams/seamsbooks.jpg
importance: 1
display: true
---

The SEAMS were a series of conference proceedings on the topic of magnetohydrodynamic power generation, called the Symposium on the Engineering Aspects of Magnetohydrodynamics (SEAM). The SEAM conferences took place nearly yearly from 1961 to 1997. 

We have recently digitized this collection of works and released them on DOE's [Energy Data Exchange](https://edx.netl.doe.gov/group/symposia-on-the-engineering-aspects-of-magnetohydrodynamics)


# Per-paper Topic Distribution Visualization with t-SNE
Below is an interactive plot showing natural language processing results grouping the papers from the SEAMs into topics. To use the plot, mouse over each item to get information about the paper. Papers can be clicked to open up the articles web page (you will have to allow popups). Use the tools on the right to move around, and note the 'refresh' button to reset the graph. Topics can be hidden by clicking on the topic color in the legend.

See below the plot for more explanation. **The code used to generate this plot can be found on github [here](https://github.com/MHDLab/SciLitNLP)**

<div class="row" style="width:100%">
  <embed type="text/html" src="wedgeplot.html" style="width:100%" height=950> 
</div>



In this plot each paper in the SEAMs corpus is represented as a marker that shows two pieces of information.

*  The positions of the papers are detrmined using t-Distributed Stochastic Neighbor Embedding (t-SNE) algorithm to project the representation of the papers in N-dimensional word vector space into two dimensions.

* The colors represent different topics as determined by the Latent Dirichlet Allocation topic modeling algorithm. The top words for each topic are indicated in the legend (see next visualization to explore the topic words in more detail). The topics in the legend are sorted by the number of papers that have that topic as their most probable topic.


Because the position and color of the markers are determined by the two separate algorithms, regions of a similar color indicate that both algorithms are independently indicating the papers of that region are related. 


The topic distribution for each paper is visualized by representing each paper as a pie chart. Each slice represents a topic, and the fractional size (angle) of each slice represents the probability of that topic. Only the top 3 topics for each paper are inclused (resulting in an incomplete pie chart) for the sake of graphics processing. The figure below shows some example papers (Figure is from the energy storage literature dataset)


![](wedge_example.png)  








