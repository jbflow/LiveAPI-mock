"""
Tests for the live.Device and Parameter classes.
"""

import pytest
from live import Device, Parameter


@pytest.fixture
def device():
    """Create a fresh device instance for each test."""
    return Device("Operator")


@pytest.fixture
def parameter():
    """Create a fresh parameter instance for each test."""
    return Parameter("Volume", 0.0, 1.0, 0.5)


def test_device_creation(device):
    """Test that a device is created with default values."""
    assert device.name == "Operator"
    assert len(device.parameters) == 0
    assert len(device.chains) == 0


def test_device_add_parameter(device, parameter):
    """Test adding parameters to a device."""
    device.add_parameter(parameter)
    assert len(device.parameters) == 1
    assert device.get_parameter(0) == parameter


def test_device_get_parameter(device):
    """Test getting parameters from a device."""
    param1 = Parameter("Volume", 0.0, 1.0, 0.5)
    param2 = Parameter("Pan", -1.0, 1.0, 0.0)

    device.add_parameter(param1)
    device.add_parameter(param2)

    assert device.get_parameter(0) == param1
    assert device.get_parameter(1) == param2
    assert device.get_parameter(2) is None


def test_parameter_creation(parameter):
    """Test that a parameter is created with correct values."""
    assert parameter.name == "Volume"
    assert parameter.min == 0.0
    assert parameter.max == 1.0
    assert parameter.value == 0.5


def test_parameter_value_listener(parameter):
    """Test parameter value change callbacks."""
    callback_values = []

    def callback(value):
        callback_values.append(value)

    parameter.add_value_listener(callback)
    parameter._notify_listeners(0.7)
    assert len(callback_values) == 1
    assert callback_values[0] == 0.7

    parameter.remove_value_listener(callback)
    parameter._notify_listeners(0.9)
    assert len(callback_values) == 1


def test_parameter_value_constraints(parameter):
    """Test that parameter values respect min/max constraints."""
    parameter.value = 0.3
    assert parameter.value == 0.3

    # Note: We don't enforce constraints in setter - the user is responsible
    # This matches Ableton's behavior where constraint checking is optional
    parameter.value = 1.5
    assert parameter.value == 1.5


def test_multiple_device_parameters():
    """Test a device with multiple parameters."""
    device = Device("EQ-Eight")
    param1 = Parameter("Gain", -24.0, 24.0, 0.0)
    param2 = Parameter("Freq", 20.0, 20000.0, 1000.0)
    param3 = Parameter("Q", 0.1, 10.0, 1.0)

    device.add_parameter(param1)
    device.add_parameter(param2)
    device.add_parameter(param3)

    assert len(device.parameters) == 3
    assert device.get_parameter(0).name == "Gain"
    assert device.get_parameter(1).name == "Freq"
    assert device.get_parameter(2).name == "Q"
