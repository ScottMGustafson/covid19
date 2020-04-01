# Simulating the spread of COVID-19

As a side project, I decided to play around with some monte carlo techniques to roughly model the spread of an infection disease.  

### Disclaimer
I am not an epidemiologist, nor a public health expert, nor anyone who knows anything about infectious disease.  
I'm just a data scientist who thought that this would make for a fun weekend project.
As such, do not take any of my calculations seriously--I have no idea as to how realistic any of my model assumptions are or what the parameter choices actually should be and I have not validated this model with data.

### Overview and Assumptions
In these simulations, I treat people as points in a box moving at random existing in one a a few states: susceptible, infected, immune (i.e. recovered) or dead.
The people are given an initial position and velocity.
When any two or more people get close enough, they interact may get infected with some probability determined by a randomly generated infection probability score and by distance following an inverse square law.
Some fraction of people will practice social distancing, where they stay put and other people will pass right through them *most* of the time rather than interact.
Some fraction of self-isolating people will still randomly interact with people, but the majority of passers-byers will just pass through them without interaction.
The thought here was that people practicing social distancing may not *completely* cut themselves off of everyone else.
They may make exceptions for certain family members and loved ones.

The infection length, initial positions, and velocities are randomized for each individual following a Normal distribution.
The infection severity score, infection probability score were generated from a normal distribution, but I took the absolute value of the score and clipped it to be within the range [0, 1].

For an individual realization, we can visually see the spread of the disease, while there are a few holdouts who practice social distancing and never get infected.

![Realization Gif](https://github.com/scottmgustafson/covid19/raw/master/assets/realization.gif)

We also see in aggregate over 400 realizations the infection/recovery/dead curves along with one-sigma confidence intervals.

![aggregate_png](https://github.com/scottmgustafson/covid19/raw/master/assets/covid19_sim.png)
Keep in mind, however, that **the parameters used to generate these views were arbitrarily chosen to produce pretty views** so please, don't trust this to have any bearing on reality!

## Getting Started
Set your parameters as desired. These parameters were used to generate the above views.

 ```python
params = dict(
    n=400,
    steps=125,
    initially_infected=2,
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
    proactive_isolate_frac=0.01,
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

## Parameters

| **Parameter Name** | **meaning**   |  
|--------------------|---|
| n                  |  initial population size |
| steps              |  number of days  |
| initially_infected |  number of initially infected people |
|    mu_add_at_step | poisson mean to add new people at each step |
|    mu_remove_at_step | poisson mean to remove non-dead people at each step |
|    vel_std | stdev of velocity of our people |
|    mortality_thresh | severity threshold before death (0->1)|
|    isolate_thresh | severity threshold before self isolation (0->1)|
|    severity_score_mean | mean of infection severity among population (clipped to 0,1 of absolute value) | 
|    severity_score_std | std of infection severity among  population | 
|    infection_length_mean | mean of infection length (days) assuming normal distribution|
|    infection_length_std | stdev infection length (days) |
|    infection_prob_mean | mean of infection probability among population (clipped to 0,1 of absolute value) |
|    infection_prob_std |  stdev of infection probability among population | 
|    proactive_isolate_frac | fraction of people who proactively self isolate (0->1)|

 > *Note: this is the max infection probability when one person is directly on top of another at interaction. 
>This probability goes down following an inverse square law with distance.

 
