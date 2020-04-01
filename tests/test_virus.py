from covid.model import Virus


def test_step():
    length = 10
    virus = Virus(
        infection_severity=1, infection_length=length, infection_prob=1.0, active=False
    )
    virus.t = 3
    virus.active = True
    virus.immune = False
    virus.step()
    assert virus.active
    assert virus.t == 2
    assert virus.severity == virus.curve[length - 2]


def test_step_finish():
    virus = Virus(
        infection_severity=1, infection_length=10, infection_prob=1.0, active=False
    )
    virus.t = 1
    virus.active = True
    virus.immune = False
    virus.step()

    assert not virus.active
    assert virus.immune
    assert virus.infection_severity == 0


def test_step_inactive():
    virus = Virus(
        infection_severity=1, infection_length=10, infection_prob=1.0, active=False
    )
    virus.t = 100
    virus.active = False
    virus.step()

    assert virus.t == 100
    assert not virus.active
