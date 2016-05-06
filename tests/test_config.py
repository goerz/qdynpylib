import QDYN
from textwrap import dedent
from QDYN.config import (read_config_str, get_config_value,
        generate_make_config, config_data_to_str)

import pytest

@pytest.fixture()
def config1():
    config = r'''
    ! the following is a config file for 3 pulses and some custom
    ! data
    pulse: type = gauss, t_FWHM = 1.8, E_0 = 1.0, w_L = 0.2, &
    & oct_shape = flattop, ftrt = 0.2, oct_lambda_a = 100, &
    & oct_increase_factor = 10
    * id = 1, t_0 = 0, oct_outfile = pulse1.dat    ! pulse 1
    * id = 2, t_0 = 2.5, oct_outfile = pulse2.dat  ! pulse 2
    * id = 3, t_0 = 5, oct_outfile = pulse3.dat    ! pulse 3

    user_string: &
    A = "x**2", &
    B = 'B_{"avg"}' ! some "arbitrary" strings
    '''
    return read_config_str(config)


def test_get_config_value(config1):
    assert get_config_value(config1, ('pulse', 1, 'id')) == 2
    assert get_config_value(config1, ('pulse', 1, 'w_L')) == 0.2
    with pytest.raises(ValueError) as exc_info:
        get_config_value(config1, ('pulse', '1', 'id'))
    assert 'list indices must be integers' in str(exc_info)
    assert get_config_value(config1, ('user_string', 'B')) == 'B_{"avg"}'
    with pytest.raises(ValueError) as exc_info:
        get_config_value(config1, ('oct', 'method'))
    assert 'oct' in str(exc_info)
    print(str(exc_info))
    with pytest.raises(ValueError) as exc_info:
        get_config_value(config1, ('pulse', 5, 'xxx'))
    assert 'list index out of range' in str(exc_info)


def test_generate_make_config(config1):
    make_config = generate_make_config(config1,
            variables={'E_0': ('pulse', 0, 'E_0'), 'A': ('user_string', 'A')},
            dependencies={('pulse', 1, 'E_0'): lambda kwargs: kwargs['E_0'],
                          ('pulse', 2, 'E_0'): lambda kwargs: kwargs['E_0'],
                         },
            checks={'E_0': lambda val: val > 0.0,
                    'A': lambda val: isinstance(val, str)})
    config = make_config(E_0=0.1)
    assert "\n"+config_data_to_str(config) == dedent(r'''
    pulse: type = gauss, t_FWHM = 1.8, E_0 = 0.1, w_L = 0.2, oct_shape = flattop, &
      ftrt = 0.2, oct_lambda_a = 100, oct_increase_factor = 10
    * id = 1, t_0 = 0, oct_outfile = pulse1.dat
    * id = 2, t_0 = 2.5, oct_outfile = pulse2.dat
    * id = 3, t_0 = 5, oct_outfile = pulse3.dat

    user_string: A = x**2, B = B_{"avg"}
    ''')
    config = make_config(A="bla")
    assert "\n"+config_data_to_str(config) == dedent(r'''
    pulse: type = gauss, t_FWHM = 1.8, E_0 = 1.0, w_L = 0.2, oct_shape = flattop, &
      ftrt = 0.2, oct_lambda_a = 100, oct_increase_factor = 10
    * id = 1, t_0 = 0, oct_outfile = pulse1.dat
    * id = 2, t_0 = 2.5, oct_outfile = pulse2.dat
    * id = 3, t_0 = 5, oct_outfile = pulse3.dat

    user_string: A = bla, B = B_{"avg"}
    ''')
    with pytest.raises(ValueError) as exc_info:
        config = make_config(E_0=-0.1)
    assert "does not pass check" in str(exc_info)
    with pytest.raises(ValueError) as exc_info:
        config = make_config(A=1)
    assert "does not pass check" in str(exc_info)
    with pytest.raises(TypeError) as exc_info:
        config = make_config(B=1)
    assert "unexpected keyword" in str(exc_info)


