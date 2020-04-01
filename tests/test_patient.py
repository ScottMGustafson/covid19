from unittest import mock

import numpy as np
import pytest

from covid.model import Patient, Virus


def test_isolates():
    x0, y0, vx0, vy0 = 1, 1, 1, 1
    p = Patient(
        x0,
        y0,
        vx0,
        vy0,
        infection=Virus(1),
        _is_dead=False,
        mortality_thresh=1.0,
        isolate_thresh=0.01,
        isolate_behavior=False,
    )

    p.infection.infection_severity = 0.5
    p.infection.curve = p.infection.infection_severity * np.ones(10)
    p.infection.t = 10

    p.infection.active = True

    assert p.infection.severity > p.isolate_thresh
    assert not p.is_dead
    assert p.infection.t == 10
    p.step()
    assert p.infection.t == 9
    assert not p.infection.immune
    assert not p._is_dead
    assert p.infection.active
    assert p.infection.severity > p.isolate_thresh
    assert not p.is_dead
    assert p.isolate
    assert p.x == x0 and p.y == y0


def test_dies():
    p = Patient(
        1,
        1,
        1,
        1,
        infection=Virus(
            infection_severity=1.0, infection_length=10, active=True, immune=False
        ),
        _is_dead=False,
        mortality_thresh=0.1,
        isolate_thresh=0.1,
    )
    p.infection.infect()
    p.infection.curve = np.ones(10)
    p.mortality_thresh = 0.9
    p.step()
    val = p.is_dead
    assert val
    assert not p.infection.active


def test_moves():
    x0, y0, vx0, vy0 = 1, 1, 1, 1
    p = Patient(
        x0,
        y0,
        vx0,
        vy0,
        infection=Virus(0.01, active=True, immune=False),
        _is_dead=False,
        mortality_thresh=10,
        isolate_thresh=0.1,
        isolate_behavior=False,
    )
    p.infection.infection_severity = 0.1
    p.infection.curve *= p.infection.infection_severity
    p.mortality_thresh = 9
    p.step()
    assert p.x == 2 and p.y == 2


@pytest.mark.parametrize(
    "act,imm,ded,exp",
    [
        (False, False, False, True),
        (True, False, False, False),
        (False, True, False, False),
        (True, True, True, False),
    ],
)
def test_susceptible(act, imm, ded, exp):
    p = Patient(
        1,
        1,
        1,
        1,
        infection=Virus(10, active=True, immune=False),
        _is_dead=False,
        mortality_thresh=0.1,
        isolate_thresh=0.1,
    )

    p._is_dead = ded
    p.infection.immune = imm
    p.infection.active = act
    val = p.susceptible
    assert val == exp, "act, imm, ded = {}, {}, {}".format(act, imm, ded)


def fake_fn(x, p=None):
    return bool(x)


@mock.patch("covid.model.np.random.choice", fake_fn)
def init_patient_pair():
    p1 = Patient(1, 1, 1, 1, infection=Virus(10, active=False, immune=False),)

    p2 = Patient(1, 1, 1, 1, infection=Virus(10, active=False, immune=False),)
    return p1, p2


@mock.patch("covid.model.np.random.choice", fake_fn)
def test_interact():
    p1, p2 = init_patient_pair()
    # cant be infected
    p2.infection.recover()
    p1.infection.infect()
    p2.interact(p1, max_dist=10, dist=1.0)
    assert not p2.infection.active

    # can be infected
    p2.infection.infect()
    p1.infection.recover_wo_immunity()
    p1.interact(p2, max_dist=10, dist=1.0)
    assert p1.infection.active


@mock.patch("covid.model.np.random.choice", fake_fn)
def test_interact_dist():
    p1, p2 = init_patient_pair()
    # can be infected, but too far away
    p1.infection.infect()
    p2.interact(p1, max_dist=10, dist=100.0)
    assert not p2.infection.active


@mock.patch("covid.model.np.random.choice", fake_fn)
def test_interact_thresh():
    p1, p2 = init_patient_pair()
    # can be infected, but thresh too high
    p1.infection.infect()
    p1.infection.infection_prob = 0
    p2.interact(p1, max_dist=10, dist=100.0)
    assert not p2.infection.active
