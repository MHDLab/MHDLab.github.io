  $\mathbf{E}_{\mathbf{SM}}$                Storage medium energy capacity           $kWh$

  <br>

  $\mathbf{E}_{\mathbf{r}}$                 Rated Output energy capacity             $kWh$

  <br>
  $\mathbf{E}_{\mathbf{in}}$                Rated Input energy capacity              $kWh$

  <br>
  $\mathbf{Pow}_{\mathbf{R}}$               Rated Power Capacity                     $kW$

  <br>
  $\mathbf{C}_{\mathbf{kW}}$                Power Capacity Capital Cost              $\$/kW$

  <br>
  $\mathbf{C}_{\mathbf{kWh}}$               Energy Capacity Capital Cost             $\$/kWh$

  <br>
  $\mathbf{P}_{\mathbf{chg}}$               Electricity Price during charge          $\$/kWh$

  <br>
  $\mathbf{P}_{\mathbf{dis}}$               Electricity price during discharge       $\$/kWh$

  <br>
  $\mathbf{r}$                              Discount rate                            

  <br>
  $\mathbf{\eta}_{\mathbf{RT}}$             Round trip efficiency                    

  <br>
  $\mathbf{n}_{\mathbf{c}}$                 Number Cycles per year                   $Cycles/year$

  <br>
  $\mathbf{DD}$                             Discharge Duration                       $hours$

  <br>
  $\mathbf{LT}$                             System Lifetime                          $years$

  <br>
  $\mathbf{L}\mathbf{T}_{\mathbf{eff}}$     Effective System Lifetime from discount  $years$

  <br>
  $\mathbf{L}\mathbf{T}_{\mathbf{eff,h}}$   Effective System Lifetime from discount  $hours$


  <br>
  $\mathbf{CF}$                             Capacity Factor                          

  <br>
  $\mathbf{\eta}_{\mathbf{d}}$              Discharge Efficiency                     

  <br>
  $\mathbf{VOM}$                            Variable Operation and Maintenance       $\$/kWh - cycle$

  <br>
  $\mathbf{FOM}$                            Fixed operation and Maintenance          $\$/kW - year$

  <br>
  $\mathbf{FO}\mathbf{M}_{\mathbf{h}}$      Fixed operation and Maintenance          $\$/kW - hours$


  <br>
  <br>


We begin by constructing
the Total Cost of Ownership (TCO) of the system. Generally following
Albertus we write :

$$TCO = \ C_{kWh}E_{SM} + C_{kW}{Pow}_{R}$$

$$+ \sum_{t}^{LT}{\frac{1}{(1 + r)^{t}}\left\lbrack P_{chg,t}E_{in,t}n_{c,t} + VOM_{t}n_{c,t}E_{r} + {Pow}_{R}FOM \right\rbrack}$$

$$+ E_{SM}C_{R,e}(1 + r)^{L/n_{c}}$$

The first two terms in this equation are the overnight energy and power
capital costs. The next set of terms represent constant payments that
must be made to charge the system and pay variable and fixed operation
and maintenance costs. These payment terms are indexed by the period in
years $t$ during which they are paid and discounted by the discount
factor $\frac{1}{(1 + r)^{t}}$The final term is the cost to replace the
storage medium at some point in the system lifetime. We can see that the
discounted storage medium replacement costs $C_{R,e}(1 + r)^{L/n_{c}}$
can be incorporated as an inflated $C_{kWh}$ and we neglect this term.

The $TCO$ can be equated to the present value of the revenue generated
over the system lifetime, $PVR$. We consider an arbitrage revenue stream
where money is generated upon discharge of the rated energy capacity at
the price $P_{dis}$. Albertus also considers a constant revenue stream
for on-demand power capacity.^6^

$$PVR = \ \sum_{t}^{LT}{\frac{1}{(1 + r)^{t}}P_{dis,t}E_{r,t}n_{c,t}}$$

For the system to be economically viable, $PVR = TCO$

$$\sum_{t}^{LT}{\frac{1}{(1 + r)^{t}}P_{dis,t}E_{r,t}n_{c,t}} = C_{kWh}E_{SM} + C_{kW}{Pow}_{R} + \sum_{t}^{LT}{\frac{1}{(1 + r)^{t}}\left\lbrack P_{chg,t}E_{in,t}n_{c,t} + VOM_{t}n_{c,t}E_{r} + {Pow}_{R}FOM \right\rbrack}$$

We can simplify the discount summations by considering the payments and
income as constant values throughout the lifetime of the system (e.g.
$n_{c,t} = n_{c}$). This is an often made implicit assumption in
levelized cost of storage analyses that calculate the average price
difference that must be charged over the lifetime of the system. In the
case of constant annuities, the terms can be pulled out of the
summations.

$$P_{dis}E_{r}n_{c}\sum_{t}^{LT}\frac{1}{(1 + r)^{t}} = C_{kWh}E_{SM} + C_{kW}{Pow}_{R} + \left\lbrack P_{chg}E_{in}n_{c} + n_{c}E_{r}VOM + {Pow}_{R}FOM \right\rbrack\sum_{t}^{LT}\frac{1}{(1 + r)^{t}}$$

The remaining summations can be simplified with a geometric series into
a term which we call an 'effective lifetime', $LT_{eff}$.

$$\sum_{t}^{LT}\frac{1}{(1 + r)^{t}} = \frac{1 - \frac{1}{(1 + r)^{LT}}}{r} = LT_{eff}$$

$LT_{eff}$ represents the effective (shortened) number of years to one
could collect the constant cash flows to achieve the same result as
collecting the discounted cash flows over the real lifetime of the
system. Figure 1 shows $LT_{eff}$ as a function of both the $LT$ (the
real lifetime) and $r$. Figure 1a shows that for a 10% discount rate,
which is close to what is assumed in many levelized cost studies,
$LT_{eff}$ asymptotically approaches approximately 10 years. Figure 1b
shows that $LT_{eff}\sim 10\ years\ $for most lifetimes and discount
rates around 10%. Therefore, we assume $LT_{eff}$ = 10 years.

The above equation shows that for constant cash flows over the lifetime
of the system, the discount rate effectively acts as a shortening of the
system lifetime as future cash flows are heavily discounted. This means
that technologies with long lifetimes to not be viewed as favorably as
otherwise and this is among the criticisms of discounted cash flow
analysis for selecting energy technologies.


Figure : a) $LT_{eff}$ vs $LT$ for different discount rates and b)
$LT_{eff}$ vs discount rate (r) for different fixed $LT$

With the simplification described above the TCO=PVR equation becomes

$$P_{dis}E_{r}n_{c}LT_{eff} = C_{kWh}E_{SM} + C_{kW}{Pow}_{R} + \left\lbrack P_{chg}E_{in}n_{c} + n_{c}E_{r}VOM + {Pow}_{R}FOM \right\rbrack LT_{eff}$$

We first simplify the number of terms with the relationships
$E_{SM} = E_{r}/\eta_{d}$ and $E_{in} = E_{r}/\eta_{RT}$.

$$P_{dis}E_{r}n_{c}LT_{eff} = \frac{C_{kWh}E_{r}}{\eta_{d\ }}\  + C_{kW}{Pow}_{R} + \left\lbrack \frac{P_{chg}E_{r}n_{c}}{\eta_{RT}}\  + n_{c}E_{r}VOM + {Pow}_{R}FOM \right\rbrack LT_{eff}$$

We can then divide through by the discounted lifetime energy output
$E_{r}n_{c}LT_{eff}$ to determine $P_{dis}$. Because we have assumed an
average constant electricity price and divided by the total electricity
output of the system over its lifetime this can replace $P_{dis}$ with
the LCOE. We also use the relationship $DD = \ E_{r}/{Pow}_{R}$

$$LCOE = \frac{1}{n_{c}LT_{eff}}\lbrack\frac{C_{kWh}}{\eta_{d\ }}\  + \frac{C_{kW}}{DD}\rbrack + \frac{P_{chg}}{\eta_{RT}} + \ VOM + \frac{FOM}{DDn_{c}}$$

We can subtract $P_{chg}$ from both sides to determine the required
average price arbitrage, or the levelized cost of storage,
$LCOS = {LCOE - P}_{chg}$. This metric has also been referred to as the
'required average price spread' and assumes that electricity arbitrage
is the primary source of revenue.^8^

$$LCOS = \frac{1}{n_{c}LT_{eff}}\left\lbrack \frac{C_{kWh}}{\eta_{d\ }}\  + \frac{C_{kW}}{DD} \right\rbrack + P_{chg}\left( \frac{1}{\eta_{RT}} - 1 \right) + \ VOM + \frac{FOM}{DDn_{c}}$$

$n_{c}$ will be determined by DD but also the capacity factor
$CF = n_{c}/n_{c,max}$, where $n_{c,max} = \frac{4380\ h/y}{DD}$. . We
assume maximum accumulated discharge duration throughout a year is 4380
hours, following Albertus. This means that a CF = 1 means the charging
and discharging times are equal and the system is in constant operation
throughout the year.

We can then rewrite $LCOS\ $as

$$LCOS = \frac{1}{CF*4380*LT_{eff}}\left\lbrack \frac{C_{kWh}}{\eta_{d\ }}*DD\  + C_{kW} \right\rbrack + P_{chg}\left( \frac{1}{\eta_{RT}} - 1 \right) + \ VOM + 4380\frac{FOM}{DD*CF}$$

This equation can be rewritten converting the units of $LT_{eff}$ and
$FOM$ to hours

$$LCOS = \frac{1}{CF*LT_{eff,h}}\left\lbrack \frac{C_{kWh}}{\eta_{d\ }}*DD\  + C_{kW} \right\rbrack + P_{chg}\left( \frac{1}{\eta_{RT}} - 1 \right) + \ VOM + \frac{FOM_{h}}{DD*CF}$$

In the text we neglect the OM terms.
