---
layout: page
title: Energy Storage Materials Cost Floor Analysis 
use_math: true
---

This page is an ongoing attempt to consolidate data from the literature on the material cost floor for the energy capital cost ($\\$/kWh$) for different energy types suitable for long duration storage. 


# Levelized cost of storage (LCOS)

A key metric for energy storage systems is levelized cost of storage (**LCOS**) which can be defined as the extra cost, in addition to the **Price of Electricty** paid by the system operator, that must be charged to make the energy storage system economically viable. 

<center>
<figure style="display: inline-block">
<img src="mat_cost/lcos_arpae.png" style="width:50%">
<figcaption style="text-align: center;font-style: italic;">A schematic of the levelized cost of storage from the <a href="https://www.semanticscholar.org/paper/Duration-Addition-to-electricitY-Storage-(DAYS)/e9951a5c294cf96dd9840cc6d2d44a66b61e1d32">Source: Duration Addition to electricitY Storage (DAYS) Overview</a></figcaption>
</figure>
</center>



With some simplifying assumptions (no discount rate, no O&M, no end of life, capacity factor = 1) we can form a simplified version of the LCOS:

$$
LCOS[$/kWh] = (1 - \frac{1}{\eta_{RT}}) * Price Electricity + \frac{1}{Lifetime*\eta_{out}}(C_{kW} + C_{kWh} * Duration)
$$

The first term represents the "Inefficiency electricity premium", which arises as we must purchase extra electricity to compensate for round trip efficiences ($\eta_{RT}$) less than 1. The second term represents money required to repay the capital investement of the plant. The capital is split in to an energy capital cost ($C_{kWh}$) that scales with the storage medium energy capacity and a power capital cost ($C_{kW}$) that scales with the rated power discharge capacity. The ratio of the energy capaicty to the power capacity defines the discharge **Duraiton** of the system (assuming instant charging or duty cycle=1). The system is paid off over it's **Lifetime** and we have to overbuild the capacities by the output efficiency $\eta_{out} = \eta_{discharge}*\eta_{store}$ to compensate for losses. 


# LCOS for Long Duration Storage 

For long durations the last term will begin to dominate the expression and the LCOS can be approximated 

$$
LCOS \approx \frac{C_{kWh}}{Lifetime*\eta_{out}} * Duration
$$

The scaling factor with duration represents the key figure of merit for long duration energy storage systems. In this expression the component that will be able to vary over many orders of magnitude is $C_{kWh}$ and therefore could be considered the most important. We can get a handle on the ballpark of what $C_{kWh}$ is required by considering a long-duraiton energy storage system with the following characteristics

* LCOS of of 10¢/kWh
* Duration of 100 hours
* Lifetime of 10 years (~$10^6$ hours) and  
* $ \eta_{out} = 1$

We calculate $ C_{kWh} <\approx \\$10/kWh $ meaning a energy storage medium cannot have a capital cost significantly above this to be viable for durations on the order of 100 hours. Recent work by [Albertus](https://doi.org/10.1016/j.joule.2019.11.009) is consistent with this message but provides a more quantitative analysis presented in the figure below that includes the tradeoffs between $C_{kWh} (C_{E,th})$, $\eta_{RTE} \propto \eta_{out}$, and $ C_{kW} (C_p)$. The region to the left of the lines indicates combinations of $C_{kWh}$ and $C_{kW}$ that are economically viable. The key message is that the maximum $C_{kWh}$ is the most densitive to increases in duration and around 50-100 hours we require a storage medium with  $C_{kWh} <\approx \\$10/kWh$


<center>
<figure style="display: inline-block">
<img src="mat_cost/albertus.png" style="width:70%">

<figcaption style="text-align: center;font-style: italic;">Recent modeling by <a href="https://doi.org/10.1016/j.joule.2019.11.009">Albertus</a> that indicates regions (left of lines) of economic viability for different combinations of storage medium fiugres of merit </figcaption>
</figure>
</center>

# Materials Cost Floor

The cost of the material that the storage medium is built out of sets a lower bound on the achievable $C_{kWh}$. Therefore we meed to find a material that costs of less than $ 10\\$/kWh$. Below is a plot that shows data on the energy capital cost of energy stored in different materials for different forms of energy. Viral refers to forms of energy limited by materials strength of a container (flywheel, pressure vessel, SMES). Mouse over to see the name of the material. This plot is an ongoing work in progress with more data to be added. 

<div>
<center>
  <embed type="text/html" src="mat_cost/mat_cost_compare.html" style="width:100%" height=800> 
</center>
</div>

Sources: 

[Alva et al. 2018](https://doi.org/10.1016/j.energy.2017.12.037)

[Li et al. 2017](https://doi.org/10.1016/j.joule.2017.08.007)

[Kale 2018](https://doi.org/10.1016/j.egyr.2018.09.003)

