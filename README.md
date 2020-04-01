#covid19 infections

Simulates the spread of covid19 infections utilising Monte Marlo methods

![Realization Gif](https://github.com/scottmgustafson/covid19/raw/master/assets/realization.gif)

![aggregate_png](https://github.com/scottmgustafson/covid19/raw/master/assets/covid19_sim.png)

## Getting Started
Set your parameters as desired:

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
The parameters were used for the realization seen in the above views.

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
|    infection_prob_mean | *mean of infection probability among population (clipped to 0,1 of absolute value) |
|    infection_prob_std |  stdev of infection probability among population | 
|    proactive_isolate_frac | **fraction of people who proactively self isolate (0->1)|

 > *Note: this is the max infection probability when one person is directly on top of another at interaction. 
>This probability goes down following an inverse square law with distance.

 > **Note: some fraction of self-isolating people sill still randomly interact with people, but the majority of passers-byers will just pass through them without interaction.
