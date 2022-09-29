# Batteries Swap

This repository consists of a discrete event simulation showing that electric vehicles cannot exist without ***batteries sharing*** (also known as ***batteries swapping***). Batteries sharing is not just a more environmental and social friendly solution, it is also more efficient and more beneficial for traffic mitigation.

<p align="center"><img src="/images/share.jpg" width="30%" height="30%"></p>

## Table of contents

- [Overview](#overview)
- [Roads Network](#roads-network)



## Overview

In my view, it's not possible to talk about electric vehicles without ***batteries sharing*** (or ***batteries swapping***). Waiting for almost an hour for the vehicle to charge is not handy, realistic, and not compliant with modern car sharing or ride sharing methods. 
A situation where electric vehicles drivers, once arrived to a charging station, remove exhausted batteries and replace them with the charged batteries previously left by somebody else is ***much more convenient***, and it gives rise to a ***much more appreciated scenario***.


Batteries sharing is also a more ***environmental and social friendly*** scenario for several reasons. 
- the service life of batteries is decoupled from the service life of vehicles, in this way batteries are used as much as possible; 
- batteries would be managed by few easy-to-control companies by reducing the risk of illegal disposals;
- batteries must be redistributed, since, according to the period of the year, there might be more vehicles travelling in a direction rather than the other, and this generate many job places.


This future scenario requires a standardization of batteries and their clusterization in few categories, but, unfortunately, cars producers are going in a different direction, each producing their own batteries. Fortunately, this scenario boasts the support of major companies, like the American startup [Ample](https://ample.com/) (which is supported by a leading group in the energy sector like [Shell](https://www.shell.com/)).

<p align="right">(<a href="#table-of-contents">back to top</a>)</p>


## Roads Network

The download of roads networks is made by interrogating [Open Street Map](https://www.openstreetmap.org/#map=6/42.088/12.564) through [OSMnx](https://osmnx.readthedocs.io/en/stable/). This process might be time consuming, hence some sample extractions are saved in [graphs](/graphs/) directory as [GraphML](http://graphml.graphdrawing.org/) and can be read by using [NetworkX](https://networkx.org/).

![graph1](/images/graph1.png)  ![graph2](/images/graph2.png) 