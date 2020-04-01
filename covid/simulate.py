"""Functions used for the simulations"""

import numpy as np

from covid.config import MAX_X
from covid.model import Patient, Virus


def new_patients(
    n,
    mortality_thresh=0.95,
    isolate_thresh=0.5,
    vel_std=0.1,
    severity_score_mean=0.1,
    severity_score_std=0.4,
    infection_length_mean=19,
    infection_length_std=3.0,
    infection_prob_mean=1.0,
    infection_prob_std=1.0,
    proactive_isolate_frac=0.0,
    **kwargs
):
    """
    returns a list of new Patients.  Parameters are determined by statistical distributions:
    - velocity and infection length, are normal distributions
    - severity and infection prob are the absolute value of a normal distributions clipped to the range [0, 1]
    - x, y coordinates of initial position are normal clipped to the dimensions of the box

    Parameters
    ----------
    n : int
        num people
    mortality_thresh : float (0->1)
        threshold for death
    isolate_thresh : float (0->1)
        threshold before a person self-isolates
    vel_std : float
        standard deviation of persons velocity
    severity_score_mean : float (0->1)
        determines the magnitude of how severe the average case is
    severity_score_std : float
        standard deviation of the above
    infection_length_mean : float
        determines how long an average case is
    infection_length_std : float
         standard deviation of the above
    infection_prob_mean : float (0->1)
        determines the average infection probability on contact between
        a suceptible and an infected person is.
    infection_prob_std : float
        standard deviation of the above
    proactive_isolate_frac : float (0->1)
        fraction of people who proactively self-isolate by staying in place.
        a fraction of these people can interact with people who approach them
        but the rest do not interact at all.

    Returns
    -------
    List[Patient]

    """
    pos = 2 * MAX_X * np.random.random_sample(size=(n, 2)) - MAX_X
    vel = np.random.normal(loc=0, scale=vel_std, size=(n, 2))
    infect_len = np.fabs(
        np.random.normal(loc=infection_length_mean, scale=infection_length_std, size=n)
    )

    proactive_isolate = np.random.choice(
        [True, False], p=[proactive_isolate_frac, 1.0 - proactive_isolate_frac], size=n
    )

    _severity = np.fabs(
        np.random.normal(loc=severity_score_mean, scale=severity_score_std, size=n)
    )
    severity = np.clip(_severity, 0.0, 1.0)

    _infect = np.fabs(
        np.random.normal(loc=infection_prob_mean, scale=infection_prob_std, size=n)
    )
    infection_prob = np.clip(_infect, 0.0, 1.0)
    infections = [
        Virus(
            infection_severity=severity[i],
            infection_length=infect_len[i],
            infection_prob=infection_prob[i],
            active=False,
            immune=False,
        )
        for i in range(n)
    ]
    return [
        Patient(
            x=pos[i][0],
            y=pos[i][1],
            vx=vel[i][0],
            vy=vel[i][1],
            infection=infections[i],
            mortality_thresh=mortality_thresh,
            isolate_thresh=isolate_thresh,
            isolate_behavior=proactive_isolate[i],
        )
        for i in range(n)
    ]


def add_remove_patients(num_new, num_remove, patients, **kwargs):
    """
    Add and remove patients

    Parameters
    ----------
    num_new : int
    num_remove : int
    patients : List[Patient]

    Other Parameters
    ----------------
    outside_infections: int (default nun_new // 100)
        new infections coming from newly added people

    Returns
    -------
    List[Patient]
    """
    # extend the list with new patients
    if num_new > 0:
        new_people = new_patients(num_new, **kwargs)
        n_infect = kwargs.get("outside_infections", num_new // 100)
        randomly_infect(new_people, n_infect)
        patients.extend(new_people)
    # remove some patients
    if num_remove > 0:
        np.random.shuffle(patients)
        patients = [x for i, x in enumerate(patients) if i > num_remove or x.is_dead]
    return patients


def randomly_infect(patient_lst, n_infect):
    """
    randomly infect elements of a list

    Parameters
    ----------
    patient_lst : List[Patient]
    n_infect : int

    Returns
    -------
    None
    """
    for i in range(n_infect):
        patient_lst[i].infection.infect()
