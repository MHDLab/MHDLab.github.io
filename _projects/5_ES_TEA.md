---
layout: page
title: Long Duration Energy Storage Techno-Economic Analysis 
use_math: true
img: /projects/5_ES_TEA/thumbnail.png
display: false
---

This page hosts some preliminary interactive visualizations of the data collected of the material cost floor for the energy capital cost ($USD/kWh$) for different energy types suitable for long duration energy storage. The details of the the methods used for data collection are part of a manuscript in preparation and available on request. The work on this page is particularly inspired by [Albertus 2020](https://www.cell.com/joule/pdf/S2542-4351(19)30539-2.pdf) and [Hunter 2021](https://www.sciencedirect.com/science/article/abs/pii/S2542435121003068).


# Levelized cost of storage (LCOS)

A key metric for energy storage systems is levelized cost of storage (**LCOS**) which can be defined as the extra amount, in addition to the price of charging paid by the system operator, that must be charged to make the energy storage system economically viable. With some simplifying assumptions we can derive an expression of the LCOS:

$$
LCOS = \frac{1}{CF*LT_{eff,h}}\left\lbrack \frac{C_{kWh}}{\eta_{d\ }}*DD\  + C_{kW} \right\rbrack + P_{chg}\left( \frac{1}{\eta_{RT}} - 1 \right)
$$


<div markdown = "0">
<button type="button" class="collapsible">Open for term definitions and  derivation of LCOS equation </button>
  <div class="extended" style="display:none">

    {% include_relative 5_ES_TEA/lcos.md %}

  </div>
</div>

### Duration dependence


Figure 1a below shows how the LCOS depends on the discharge duration (DD) of the system. 

<figure style="display: inline-block">
<img src="lcosfig.png" style="width:70%">

<figcaption style="text-align: center;font-style: italic;">
Figure 1: a) Investigation of discharge duration dependence for a fixed $C_{kW}$ = 1000 USD/kW b) Energy and power capital tradeoff. The lines represent combinations of power and energy capital costs that result in a LCOS of 0.1 USD/kWh. For both graphs the input parameters are $P_{chg} = 0.05  USD/kWh$, $CF = 0.7$, and $LT_{eff}=10 y$. For these figures we make the simplifying assumption that $η_d=√(η_{RT})$, meaning that there are no storage losses, and the charge and discharge efficiencies are equal.
 </figcaption>
</figure>

The critical feature of the LCOS for long durations is that the last term will begin to dominate the expression and the LCOS can be approximated 

$$
LCOS \approx \frac{C_{kWh}}{CF*LT_{eff}*\eta_{d}} * DD
$$

The scaling factor with duration represents the key figure of merit for long duration energy storage systems. In this expression the component that will be able to vary over many orders of magnitude is $C_{kWh}$ and therefore could be considered the most important.  

We can get an idea of the ballpark of what $C_{kWh}$ is required by considering the tradeoffs between different parameters in the LCOS equation to achieve a fixed LCOS of 0.1 USD/kWh. Figure 1b shows economically viable combinations of $C_{kW}$ and  $C_{kWh}$ by solving the LCOS equation for the maximum allowable $C_{kW}$ as a funciton of $C_{kWh}$, defining a tradeoff curve of economic viabaility. We can see that for reasonable efficiency of 0.75, then $ C_{kWh} <\approx 10\ USD/kWh $ is needed for ~100 hours of storage duration, even as $C_{kW}$ approaches zero.

# Materials energy capital cost ($C_{kWh,mat}$) dataset

The cost of the material that the storage medium is built out of sets a lower bound on the achievable $C_{kWh}$. Therefore we meed to find a storage medium with a **material energy capital cost $(C_{kWh, mat})$** than approximately $10\ USD/kWh$.  $C_{kWh, mat}$ is calculated from the energy density, $\rho_E$ [kWh/kg], of the storage media (storing a given form of enegy) and the material price, $C_{mat}$  [USD/kg], of the materials used in the storage media through the equation 


$$
C_{kWh, mat} = \frac{C_{mat} [USD/kg]}{\rho_E [kWh/kg]}
$$


Below is a plot that shows calculated $C_{kWh, mat}$ for a wide range of storage media.  Mouse over to see the name of the material. 

<div>
<center>
  <embed type="text/html" src="Ckwh_bokeh.html" style="width:100%" height=800> 
</center>
</div>

The plot below breaks out each storage medium into the material cost and energy density used to calculate $C_{kWh, mat}$ above. Click on a storage medium type in the legend to hide that class of storage medium. The line indicates  $C_{kWh, mat} = 10\ USD/kWh$

<div>
<center>
  <embed type="text/html" src="Ckwh_line_bokeh.html" style="width:100%" height=800> 
</center>
</div>

<div markdown = "0">
{% include collapsible.html %}
</div>