# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Electrical component types."""

from ._battery import (
    Battery,
    BatteryType,
    LiIonBattery,
    NaIonBattery,
    UnrecognizedBattery,
    UnspecifiedBattery,
)
from ._breaker import Breaker
from ._capacitor_bank import CapacitorBank
from ._category import ElectricalComponentCategory
from ._chp import Chp
from ._connection import ComponentConnection
from ._converter import Converter
from ._crypto_miner import CryptoMiner
from ._electrical_component import ElectricalComponent
from ._electrolyzer import Electrolyzer
from ._ev_charger import (
    AcEvCharger,
    DcEvCharger,
    EvCharger,
    EvChargerType,
    HybridEvCharger,
    UnrecognizedEvCharger,
    UnspecifiedEvCharger,
)
from ._grid_connection_point import GridConnectionPoint
from ._hvac import Hvac
from ._inverter import (
    BatteryInverter,
    HybridInverter,
    Inverter,
    InverterType,
    SolarInverter,
    UnrecognizedInverter,
    UnspecifiedInverter,
)
from ._meter import Meter
from ._plc import Plc
from ._power_transformer import PowerTransformer
from ._precharger import Precharger
from ._problematic import (
    MismatchedCategoryComponent,
    UnrecognizedComponent,
    UnspecifiedComponent,
)
from ._static_transfer_switch import StaticTransferSwitch
from ._steam_boiler import SteamBoiler
from ._uninterruptible_power_supply import UninterruptiblePowerSupply
from ._wind_turbine import WindTurbine

__all__ = [
    "Chp",
    "CryptoMiner",
    "Battery",
    "BatteryType",
    "LiIonBattery",
    "NaIonBattery",
    "UnrecognizedBattery",
    "UnspecifiedBattery",
    "Breaker",
    "Converter",
    "CapacitorBank",
    "ElectricalComponentCategory",
    "ElectricalComponent",
    "Electrolyzer",
    "AcEvCharger",
    "DcEvCharger",
    "EvCharger",
    "EvChargerType",
    "HybridEvCharger",
    "UnrecognizedEvCharger",
    "UnspecifiedEvCharger",
    "GridConnectionPoint",
    "Hvac",
    "BatteryInverter",
    "HybridInverter",
    "Inverter",
    "InverterType",
    "SolarInverter",
    "UnrecognizedInverter",
    "UnspecifiedInverter",
    "Meter",
    "Plc",
    "PowerTransformer",
    "Precharger",
    "MismatchedCategoryComponent",
    "UnrecognizedComponent",
    "UnspecifiedComponent",
    "SteamBoiler",
    "StaticTransferSwitch",
    "UninterruptiblePowerSupply",
    "WindTurbine",
    "ComponentConnection",
]
