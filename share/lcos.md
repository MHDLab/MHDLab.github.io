The Levelized Cost of Electricity (LCOE) is the price that the energy
storage system operator must charge for electricity to break even over
the lifetime of the system.

$$LCOE\ \left\lbrack \frac{\$}{kWh} \right\rbrack = \frac{\sum_{n}^{}{\frac{C_{charge}}{(1 + r)^{n}} +}C_{invest} + \sum_{n}^{}{\frac{C_{O\& M}}{(1 + r)^{n}} +}\text{~}\sum_{n}^{}\frac{C_{EOL}}{(1 + r)^{n}}}{\sum_{n}^{}\frac{E_{out}}{(1 + r)^{n}}}$$

$r$ -- discount rate

$n$ -- number of years (costs and output are accumulated over a year)

$C_{charge}$ -- Charging Cost (\$/year)

$C_{invest}$- Investment costs (\$)

$C_{O\& M}$- Operation and Maintenance costs (\$/year)

$C_{EOL}$ -- End of life costs (\$/year)

$E_{out}$ -- Electricity out (kWh)

LT -- System Lifetime in years

DD -- Discharge Duration

$\eta_{RT}$ -- Round trip efficiency

$\eta_{d}$- Discharge Efficiency

To simplify this equation let's neglect $O\& M$ and $EOL$ costs. Further
we will neglect the discount rate ($r = 1$). By neglecting the discount
rate we are assuming the charging cost does not change and those terms
can be pulled out of the sums (revisit). Note that neglecting the
discount rate overemphasizes the benefit of technologies with long
lifetimes, as in reality cash flows in the future will be less valuable
than today.

Considering the **Lifetime (LT)** of the system to be $\Sigma_{n}$ we
arrive at

$$LCOE\ \left\lbrack \frac{\$}{kWh} \right\rbrack = \frac{LT*C_{charge} + \ C_{invest}}{LT*E_{out}}$$

$$LCOE\ \left\lbrack \frac{\$}{kWh} \right\rbrack = \frac{C_{charge}}{E_{out}} + \frac{C_{invest}}{LT*E_{out}}$$

We can write the charging cost in terms of the price of electricity paid
by the system operator $C_{E,in}$ (\$/kWh) and the electricity input
$(E_{in})$.

$$C_{charge} = C_{E,in}*E_{in}$$

The electricity input and output are related by the round trip
efficiency $\eta_{RT}$:

$$E_{out} = E_{in}\eta_{RT}$$

Therefore the first term of the LCOE can be rewritten

$$LCOE\ \left\lbrack \frac{\$}{kWh} \right\rbrack = \frac{C_{E,in}}{\eta_{RT}} + \frac{C_{invest}}{LT*E_{out}}$$

The first term, which originated from the charging cost, means that
round trip energy losses require the system operator to overpurchased
electricity by a factor of $\frac{1}{\eta_{RT}}$. It is helpful to
define the Levelized cost of storage (LCOS) which subtracts off the cost
of electricity to only look at the extra cost due to inefficiencies.

$$LCOS = LCOE - C_{E,in}$$

$$LCOS = C_{E,in}(\frac{1}{\eta_{RT}} - 1) + \frac{C_{invest}}{LT*E_{out}}$$

Therefore for $\eta_{RT} = 1,$ the only extra cost that must be charged
beyond the base electricity cost is what is needed to pay back the
initial investment.

The investment cost can be written in terms of an energy capital cost
($C_{kWh}$) that scales with the storage medium energy capacity
($Cap_{kWh}$) and a power capital cost ($C_{kW}$) that scales with the
rated power discharge capacity ($Cap_{kW}$).

$$C_{invest} = \ C_{kWh}Cap_{kWh} + \ C_{kW}Cap_{kW}$$

Let's consider a storage device with an unrealistic but simplifying duty
cycle where it charges instantly and then discharges constantly
according to its power rating. In this case the discharge duration is

$$Duration = \frac{Cap_{kWh}}{Cap_{kW}}$$

$$C_{invest} = Cap_{kW}(C_{kW} + C_{kWh}*DD)$$

The LCOS then becomes

$$LCOS = C_{E,in}(\frac{1}{\eta_{RT}} - 1) + \frac{Cap_{kW}(C_{kW} + C_{kWh}*DD)}{LT*E_{out}}$$

We can write

$$Lifetime*E_{out} = \ Cap_{kWh}*\# cycles*\eta_{discharge}$$

Where $\eta_{discharge}$ is the discharge efficiency.
$\eta_{discharge} = \eta_{store}*\eta_{out}$.

$$LCOS = C_{E,in}(\frac{1}{\eta_{RT}} - 1) + \frac{Cap_{kW}(C_{kW} + C_{kWh}*DD)}{Cap_{kWh}*\# cycles*\eta_{d}}$$

Again we can use the definition of the duration above, along with
$DD*\# cycles = LT*CF$ where CF is the capacity factor.

$$LCOS = C_{E,in}(\frac{1}{\eta_{RT}} - 1) + \frac{(C_{kW} + C_{kWh}*DD)}{CF*LT*\eta_{d}}$$

For now, we just assume CF= 1, but this should be revisited.
