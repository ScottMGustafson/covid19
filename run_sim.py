"""run simulations and visualize results"""
import multiprocessing as mp
import os

import numpy as np
import pandas as pd

from covid.config import MAX_X, data_path
from covid.model import Patient
from covid.simulate import add_remove_patients, new_patients, randomly_infect
from covid.visuals import create_animation, plot_curve  # , plot_points


def count_cases(patients, step=0, dct=None):
    """

    Parameters
    ----------
    patients : list
    step : int
    dct : dict (optional)

    Returns
    -------
    dict
    """
    if not dct:
        dct = {
            k: []
            for k in ["infected", "dead", "immune", "total", "susceptible", "step"]
        }
    dct["infected"].append(len([x for x in patients if x.infection.active]))
    dct["dead"].append(len([x for x in patients if x._is_dead]))
    dct["immune"].append(
        len([x for x in patients if x.infection.immune and not x._is_dead])
    )
    dct["total"].append(len([x for x in patients if not x._is_dead]))
    dct["susceptible"].append(len([x for x in patients if x.susceptible]))
    dct["step"].append(step)
    return dct


def run_sim(n, steps, mu_add_at_step, mu_remove_at_step, initially_infected, **kwargs):
    """
    run simulation.  adding or removing people at each step is a poisson process.

    Parameters
    ----------
    n : int
    steps : int
    mu_add_at_step : float
        mean to add people at each step
    mu_remove_at_step : float
        mean to randomly remove non-dead people at each step
    initially_infected : int
        number of initially infected poeple

    Returns
    -------
    pd.DataFrame

    """
    add_at_step = np.random.poisson(mu_add_at_step, steps)
    remove_at_step = np.random.poisson(mu_remove_at_step, steps)
    patients = new_patients(n, **kwargs)

    randomly_infect(patients, initially_infected)

    count_dct = count_cases(patients)
    for step in range(steps):
        Patient.find_interactions(patients)
        patients = add_remove_patients(
            num_new=add_at_step[step],
            num_remove=min(remove_at_step[step], len(patients)),
            patients=patients,
            **kwargs
        )

        for p in patients:
            p.step()
        count_dct = count_cases(patients, step=step + 1, dct=count_dct)

    df = pd.DataFrame(count_dct)
    return df


def run_all(kwds, n_proc=8, n_iter=5):
    """
    run `run_sim` `n_iter` times

    Parameters
    ----------
    kwds : dict
        kwargs for `run_sim`
    n_proc : int
        num processes
    n_iter : int
        num iterations to run in parallel

    Returns
    -------
    None
    """
    pool = mp.Pool(processes=min(mp.cpu_count(), n_proc))
    results = [pool.apply(run_sim, args=(), kwds=kwds) for x in range(n_iter)]
    df = (
        pd.concat(results, axis=0)
        .groupby("step")
        .agg(["mean", "median", "std", "count"])
    )
    df.columns = [" ".join(col).strip() for col in df.columns.values]
    df.to_csv(os.path.join(data_path, "results.csv"), header=True)
    plot_curve(df)


def get_points(lst):
    """
    get list of people in each category

    Parameters
    ----------
    lst : List[Patient]

    Returns
    -------
    dict
    """
    dct = {
        "dead": [(x.x, x.y) for x in lst if x._is_dead],
        "infected": [(x.x, x.y) for x in lst if x.infection.active],
        "immune": [(x.x, x.y) for x in lst if x.infection.immune and not x._is_dead],
        "susceptible": [(x.x, x.y) for x in lst if x.susceptible],
    }
    return {k: np.array(v).T for k, v in dct.items()}


def run_sim_for_animation(**kwargs):
    """Run sims and generate animation of people."""
    patients = new_patients(**kwargs)
    ret_lst = [get_points(patients)]

    randomly_infect(patients, kwargs.get("initially_infected", 1))
    steps = kwargs.get("steps", 100)
    for step in range(steps):
        Patient.find_interactions(patients)
        for p in patients:
            p.step()
        ret_lst.append(get_points(patients))
    create_animation(ret_lst, total_frames=steps, fps=kwargs.get('fps', 15))
    return ret_lst


if __name__ == "__main__":
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
    #run_all(params, n_proc=8, n_iter=16)
    run_sim_for_animation(fps=15, **params)
