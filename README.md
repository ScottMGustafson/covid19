# Simulating the spread of COVID-19

As a side project, I decided to play around with some monte carlo techniques to roughly model the spread of an infection disease. 
There is nothing surprising here in my results: staying home means fewer people get sick and fewer people die.

### Disclaimer
I am not an epidemiologist, nor a public health expert, nor anyone who knows anything about infectious disease.  
I'm just a data scientist who thought that this would make for a good weekend project.
Don't take these calculations as anymore than a toy model to satisfy the creator's curiousity.

### Overview and Assumptions
In these simulations, I treat people as points in a box moving at random existing in one a few states: susceptible, infected, immune (i.e. recovered) or dead.
The people are given an initial position and velocity.
When any two or more people get close enough, they interact may get infected with some probability determined by a randomly generated infection probability score and by distance following an inverse square law.

I assume that there is only one strain of the virus and no possibility for reinfection.

Some fraction of people will practice social distancing, where they stay put and other people will pass right through them *most* of the time rather than interact.
Some fraction of self-isolating people will still randomly interact with people, but the majority of passers-byers will just pass through them without interaction.
The thought here was that people practicing social distancing may not *completely* cut themselves off of everyone else.
They may make exceptions for certain family members and loved ones.

The infection length, initial positions, and velocities are randomized for each individual following a Normal distribution.
The infection severity score, infection probability score were generated from a normal distribution, but I took the absolute value of the score and clipped it to be within the range [0, 1].

### Results
For an individual realization, we can visually see the spread of the disease, while there are a few holdouts who practice social distancing and never get infected.


![Realization Gif](https://github.com/scottmgustafson/covid19/raw/master/assets/realization.gif)


To see the impact of self-isolation, I ran these simulations over a range of isolation fractions: with an initial population of 1000, and 32 realizations each.  

![aggregate10_png](https://github.com/scottmgustafson/covid19/raw/master/assets/10_pct.png)


![aggregate50_png](https://github.com/scottmgustafson/covid19/raw/master/assets/50_pct.png)


![aggregate75_png](https://github.com/scottmgustafson/covid19/raw/master/assets/75_pct.png)

With no people coming into or out of the box (this was turned off for these simulations) we can clearly see the infection curve flattening and elongating as the social distancing percentages increase.

![aggregate75_png](https://github.com/scottmgustafson/covid19/raw/master/assets/max_infect.png)

Eventhough **these input parameters were arbitrary and not validated on real data**, these simulations still clearly point to the general idea that social distancing is an effective way of curbing the spread of infectious disease.

One shortcoming of this model is that the mortality rate is just randomly sampled from a statistical distribution that will be the same regardless of other factors.
In real life, the mortality rate of COVID-19 will obviously depend on many factors, perhaps most important being access to proper medical care.
An overburdened hospital can't properly care for their patients and thus, more people than necessary will die.
We can reduce the burden on our hospitals by staying home when we can and reducing social interactions.


## Getting Started Using the Code
Set your parameters as desired.  For example:

 ```python
params = dict(
    n=1000,
    steps=125,
    initially_infected=4,
    mu_add_at_step=0.0,
    mu_remove_at_step=0.0,
    vel_std=0.1,
    mortality_thresh=0.8,
    isolate_thresh=0.4,
    severity_score_mean=0.1,
    severity_score_std=0.4,
    infection_length_mean=31,
    infection_length_std=3.0,
    infection_prob_mean=0.8,
    infection_prob_std=0.2,
    partial_isolate_frac=0.4,
)
```


To run your simulations and get aggregated views over n simulations: 

```python
import run_sim
run_sim.run_all(params, n_proc=8, n_iter=16)
```

To Generate an animation of an individual realization:

```python
run_sim.run_sim_for_animation(**params)
```

### List of Parameters for `run_sim`

| **Parameter Name** | **meaning**   |  
|--------------------|---|
| `n`                 |  initial population size |
| `steps`         |  number of days  |
| `initially_infected` |  number of initially infected people |
|    `mu_add_at_step` | poisson mean to add new people at each step |
|    `mu_remove_at_step` | poisson mean to remove non-dead people at each step |
|    `vel_std` | stdev of velocity of our people |
|    `mortality_thresh` | severity threshold before death (float: 0->1) |
|    `isolate_thresh` | severity threshold before self isolation (float: 0->1) |
|    `severity_score_mean` | mean of infection severity among population (clipped to 0,1 of absolute value) | 
|    `severity_score_std` | std of infection severity among  population | 
|    `infection_length_mean` | mean of infection length (days) assuming normal distribution|
|    `infection_length_std` | stdev infection length (days) |
|    `infection_prob_mean` | mean of infection probability among population (clipped to 0,1 of absolute value) |
|    `infection_prob_std` |  stdev of infection probability among population | 
|    `proactive_isolate_frac` | fraction of people who proactively self isolate (float: 0->1) . Here this means, the do not move and cannot interact with other people|
|`partial_isolate_frac` | The exception to the above.  (float: 0->1)  Some fraction of the time, they will interact with someone nearby.  These would be exceptions for people who are self isolating, such as, when a family member or close loved one comes to visit someone who is self isolating.|

### Overview of package:
 - `run_sim.py` : top level script to run the simulations.
 - `covid/config.py` : set some global configurations: box size, max distance to infection, output path, etc.
 - `covid/model.py` : the underlying model used for the infection, split into two main classes: `Virus`, for the infection and `Patient` for the people
 - `covid/simulate.py` : some control functions to manage the simulations and initialize the populations.
 - `covid/visuals.py` : plotting functions.
