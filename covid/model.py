"""The core model of a patient and virus"""
# pylint: disable=C0103
from dataclasses import dataclass

import numpy as np

from covid.config import MAX_DIST, MAX_X, MAX_Y, MIN_X, MIN_Y


@dataclass
class Virus:
    infection_severity: float
    infection_length: int = 19
    infection_prob: float = 1.0
    active: bool = False
    immune: bool = False

    def __post_init__(self):
        self.t = int(self.infection_length)
        self.curve = self.infection_severity * Virus.get_severity_curve(self.infection_length)
        if self.active:
            self.infect()

    @property
    def severity(self):
        ind = self.curve.size - int(self.t) - 1
        return self.curve[ind]

    def recover(self):
        """patient recovers and gains immunity"""
        self.active = False
        self.immune = True
        self.infection_severity = 0

    def kill_host(self):
        """
        alias for recover, but to be used when virus can no longer spread because host is dead--
        None
        """
        self.recover()

    def recover_wo_immunity(self):
        """recover, but no immunity gained"""
        self.recover()
        self.immune = False

    def infect(self):
        """infect and get severity"""
        self.active = True

    def step(self, dt=1):
        """
        progress the virus through one more unit of time.

        Parameters
        ----------
        dt : int (default=1)
            unit of time

        Returns
        -------
        None

        """
        if self.active:
            self.t -= dt
            if self.t <= 0:
                self.recover()

    # def get_severity(self):
    #     """get severity of disease"""
    #     return self.curve[-int(self.t)]

    @staticmethod
    def get_severity_curve(t, dt=1):
        """severity of disease as a function of time.  Simplified as one half period of a sinusoid"""
        x = np.arange(0, t + 1, dt)
        curve = x * x * np.sin(np.pi * x / x.max())
        return curve / curve.max()


@dataclass
class Patient:
    x: float
    y: float
    vx: float
    vy: float
    infection: Virus
    mortality_thresh: float = 0.9
    isolate_thresh: float = 0.4
    isolate_behavior: bool = False
    _isolate: bool = False
    _is_dead: bool = False
    _susceptible: bool = True

    def step(self, dt=1):
        """
        progress the patient through one more unit of time

        Parameters
        ----------
        dt : int (default=1)
            unit of time

        Returns
        -------
        None
        """
        if not self.is_dead:
            self.infection.step(dt)
            if not self.isolate:
                self.move_it(dt)

    @property
    def susceptible(self):
        self._susceptible = all(
            [not self.is_dead, not self.infection.immune, not self.infection.active]
        )
        return self._susceptible

    @property
    def is_dead(self):
        """getter for is_dead.  When dead, a person is effectively isolated"""
        if not self._is_dead:
            if self.infection.severity > self.mortality_thresh:
                self.infection.kill_host()
                self._isolate = True
                self._is_dead = True
            else:
                self._is_dead = False
        return self._is_dead

    @property
    def isolate(self):
        """
        isolate a person under certain conditions:
        - severity of infection forces person to isolate
        - person follow self-isolation behavior
        - person is dead
        """
        if self._is_dead:
            self._isolate = True  # the dead can't move...
        elif self.infection.active:  # behavior when sick
            self._isolate = (self.infection.severity > self.isolate_thresh) or self.isolate_behavior
        elif self.infection.immune:
            self._isolate = False
        else:  # behavior when not sick or dead
            self._isolate = self.isolate_behavior
        return self._isolate

    def move_it(self, dt):
        """
        move a person one unit.  When near a wall, reflect the person.

        Parameters
        ----------
        dt : float
            time increment
        """
        if not (MIN_X < self.x < MAX_X):
            self.vx = -self.vx

        if not (MIN_Y < self.y < MAX_Y):
            self.vy = -self.vy

        self.x += self.vx * dt
        self.y += self.vy * dt

    def change_direction(self):
        """
        Randomly change direction on interaction
        """
        # change direction
        self.vx = np.random.normal(loc=0.0, scale=3.0)
        self.vy = np.random.normal(loc=0.0, scale=3.0)

    def __str__(self):
        return "pos=({:0.2f}, {:0.2f}), vel=({:0.2f}, {:0.2f})".format(
            self.x, self.y, self.vx, self.vy
        )

    @staticmethod
    def distance(a, b):
        """
        calc distance

        Parameters
        ----------
        a : Patient
        b : Patient

        Returns
        -------
        float
        """
        dx = a.x - b.x
        dy = a.y - b.y
        return np.sqrt(dx * dx + dy * dy)

    def can_be_infected(self):
        """
        Check whether can be infected.

        Returns
        -------
        bool
            True if person can be infected.
        """
        return all([not self.is_dead, not self.infection.immune, not self.infection.active])

    def interact(self, other, max_dist=MAX_DIST, dist=None):
        """
        Interact two people.  If one is

        Parameters
        ----------
        other : Patient
            other person
        max_dist : float
            max distance for interaction to be possible
        dist : float (optional)
            separation

        Returns
        -------
        None
        """

        self.change_direction()

        if not self.susceptible:
            return

        if not dist:
            # set min separation to be 1 unit.
            dist = max([1.0, Patient.distance(self, other)])

        if other.infection.active and dist < max_dist:
            val = other.infection.infection_prob / (dist ** 2.0)
            val = min([1.0, val])
            if np.random.choice([True, False], p=[val, 1.0 - val]):
                self.infection.infect()

    @staticmethod
    def find_interactions(patients, partial_isolate=True, frac=0.4):
        """
        iterate through patents to interact

        Parameters
        ----------
        patients : list(Patient)
            list of patients
        partial_isolate : bool
            if true, include some fraction of the hermits at random in each step
        frac : float < 1
            fraction of hermits who still have to interact anyway this round

        Returns
        -------
        None
        """
        ind_lst = [
            i for i in range(len(patients)) if not patients[i].is_dead and not patients[i].isolate
        ]
        if partial_isolate:
            _lst = [i for i in range(len(patients)) if patients[i].isolate]
            isolate_ind = list(np.random.choice(_lst, size=int(frac * len(_lst))))
            ind_lst = list(set(isolate_ind + ind_lst))
        for i in ind_lst:
            for j in ind_lst[i:]:
                if i == j:
                    continue
                dist = Patient.distance(patients[i], patients[j])
                if dist < MAX_DIST:
                    dist = max(1.0, dist)  # prob maximizes within 1 unit
                    patients[i].interact(patients[j], dist=dist)
                    patients[j].interact(patients[i], dist=dist)
