# coding: UTF-8

import pymodbus  # To not delete this module reference!!
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.client.sync import ModbusTcpClient
from pymodbus.exceptions import ConnectionException


##!!!!##################################################################################################
#### Own written code can be placed above this commentblock . Do not change or delete commentblock! ####
########################################################################################################
##** Code created by generator - DO NOT CHANGE! **##

class KostalKSEM_ModbusTCP14181(hsl20_3.BaseModule):

    def __init__(self, homeserver_context):
        hsl20_3.BaseModule.__init__(self, homeserver_context, "kostalKsemModbusTCP14181")
        self.FRAMEWORK = self._get_framework()
        self.LOGGER = self._get_logger(hsl20_3.LOGGING_NONE,())
        self.PIN_I_SWITCH=1
        self.PIN_I_FETCH_INTERVAL=2
        self.PIN_I_KSEM_IP=3
        self.PIN_O_ACTIVE_POWER=1
        self.PIN_O_REACTIVE_POWER=2
        self.PIN_O_APPARENT_POWER=3
        self.PIN_O_POWER_FACTOR=4
        self.PIN_O_SUPPLY_FREQUENCY=5
        self.PIN_O_ACTIVE_POWER_L1=6
        self.PIN_O_REACTIVE_POWER_L1=7
        self.PIN_O_APPARENT_POWER_L1=8
        self.PIN_O_CURRENT_L1=9
        self.PIN_O_VOLTAGE_L1=10
        self.PIN_O_POWER_FACTOR_L1=11
        self.PIN_O_ACTIVE_POWER_L2=12
        self.PIN_O_REACTIVE_POWER_L2=13
        self.PIN_O_APPARENT_POWER_L2=14
        self.PIN_O_CURRENT_L2=15
        self.PIN_O_VOLTAGE_L2=16
        self.PIN_O_POWER_FACTOR_L2=17
        self.PIN_O_ACTIVE_POWER_L3=18
        self.PIN_O_REACTIVE_POWER_L3=19
        self.PIN_O_APPARENT_POWER_L3=20
        self.PIN_O_CURRENT_L3=21
        self.PIN_O_VOLTAGE_L3=22
        self.PIN_O_POWER_FACTOR_L3=23
        self.PIN_O_COUNTER_ACTIVE_POWER_PLUS=24
        self.PIN_O_COUNTER_ACTIVE_POWER_MINUS=25
        self.PIN_O_COUNTER_REACTIVE_POWER_PLUS=26
        self.PIN_O_COUNTER_REACTIVE_POWER_MINUS=27
        self.PIN_O_COUNTER_APPARENT_POWER_PLUS=28
        self.PIN_O_COUNTER_APPARENT_POWER_MINUS=29
        self.FRAMEWORK._run_in_context_thread(self.on_init)

########################################################################################################
#### Own written code can be placed after this commentblock . Do not change or delete commentblock! ####
###################################################################################################!!!##

        self.ksem_port = 502
        self.ksem_unitid = 71

        self.interval = None
        self.DEBUG = self.FRAMEWORK.create_debug_section()

        self.skip_interval_counter = 0

        self.client = None

    #############

    def on_interval(self):
        self.DEBUG.set_value("Due error skipping N intervals: ", self.skip_interval_counter)

        if self.skip_interval_counter > 0:
            self.skip_interval_counter -= 1
            return

        ip_address = str(self._get_input_value(self.PIN_I_KSEM_IP))

        try:
            self.DEBUG.set_value("Connection IP:Port (UnitID)",
                                 ip_address + ":" + str(self.ksem_port) + " (" + str(self.ksem_unitid) + ")")
            if self.client is None:
                self.client = ModbusTcpClient(ip_address, self.ksem_port)
            if self.client.is_socket_open() is False:
                self.client.connect()

            result = self.client.read_holding_registers(0, 66, unit=self.ksem_unitid)
            if not result.isError():
                payload_dec = BinaryPayloadDecoder.fromRegisters(result.registers, byteorder=Endian.Big)
                self.read_sum_values(payload_dec)  # Read Register 0-27
                self.read_l1_values(payload_dec)  # Skip till register 40 and read until 65

            result = self.client.read_holding_registers(80, 66, unit=self.ksem_unitid)
            if not result.isError():
                payload_dec = BinaryPayloadDecoder.fromRegisters(result.registers, byteorder=Endian.Big)
                self.read_l2_values(payload_dec)  # Read Register 0-27
                self.read_l3_values(payload_dec)  # Skip till register 40 and read until 65

            result = self.client.read_holding_registers(512, 40, unit=self.ksem_unitid)
            if not result.isError():
                payload_dec = BinaryPayloadDecoder.fromRegisters(result.registers, byteorder=Endian.Big)
                self.read_counter_values(payload_dec)  # Read Register 512-551

        except ConnectionException as con_err:
            # Error during comm. Maybe temp. network error.
            # Lets try it again in a 5 Minutes (when used with 5 seconds interval)
            self.skip_interval_counter = 60
            self.DEBUG.set_value("Last exception msg logged", "retrying after 60 intervals: " + con_err.message)
        except Exception as err:
            # Error during comm. Maybe temp. network error.
            # Lets try it again in a 30 Minutes (when used with 5 seconds interval)
            self.skip_interval_counter = 360
            self.DEBUG.set_value("Last exception msg logged", "retrying after 360 intervals: " + err.message)

    def read_sum_values(self, payload_dec):
        # Active Power Plus 0,1 / Minus 2,3 combined and transformed (uint)
        current_active_power = (payload_dec.decode_32bit_uint() - payload_dec.decode_32bit_uint()) / 10.0
        self._set_output_value(self.PIN_O_ACTIVE_POWER, current_active_power)

        # Reactive Power Plus 4,5 / Minus 6,7 combined and transformed (uint)
        current_reactive_power = (payload_dec.decode_32bit_uint() - payload_dec.decode_32bit_uint()) / 10.0
        self._set_output_value(self.PIN_O_REACTIVE_POWER, current_reactive_power)
        payload_dec.skip_bytes(16)  # skip 8 registers

        # Apparent Power Plus 16,17 / Minus 18,19 combined and transformed (uint)
        current_apparent_power = (payload_dec.decode_32bit_uint() - payload_dec.decode_32bit_uint()) / 10.0
        self._set_output_value(self.PIN_O_APPARENT_POWER, current_apparent_power)
        payload_dec.skip_bytes(8)  # skip 4 registers

        # Power Factor 24,25 transformed (int!)
        self._set_output_value(self.PIN_O_POWER_FACTOR, (payload_dec.decode_32bit_int() / 1000.0))
        # Frequency 26,27 transformed (uint)
        self._set_output_value(self.PIN_O_SUPPLY_FREQUENCY, (payload_dec.decode_32bit_uint() / 1000.0))

    def read_l1_values(self, payload_dec):
        payload_dec.skip_bytes(24)  # Skip over 12 registers

        # Active Power L1 40,41 / Minus 42,43 combined and transformed (uint)
        active_power_l1 = (payload_dec.decode_32bit_uint() - payload_dec.decode_32bit_uint()) / 10.0
        self._set_output_value(self.PIN_O_ACTIVE_POWER_L1, active_power_l1)

        # Reactive Power L1 44,45 / Minus 46,47 combined and transformed (uint)
        reactive_power_l1 = (payload_dec.decode_32bit_uint() - payload_dec.decode_32bit_uint()) / 10.0
        self._set_output_value(self.PIN_O_REACTIVE_POWER_L1, reactive_power_l1)
        payload_dec.skip_bytes(16)  # skip 8 registers

        # Apparent Power L1 56,57 / Minus 58,59 combined and transformed (uint)
        apparent_power_l1 = (payload_dec.decode_32bit_uint() - payload_dec.decode_32bit_uint()) / 10.0
        self._set_output_value(self.PIN_O_APPARENT_POWER_L1, apparent_power_l1)

        # Current L1 60/61 transformed (uint) / Voltage L1 62/63 transformed (uint)
        self._set_output_value(self.PIN_O_CURRENT_L1, (payload_dec.decode_32bit_uint() / 1000.0))
        self._set_output_value(self.PIN_O_VOLTAGE_L1, (payload_dec.decode_32bit_uint() / 1000.0))
        # Power Factor L1 64/65 transformed (int!)
        self._set_output_value(self.PIN_O_POWER_FACTOR_L1, (payload_dec.decode_32bit_int() / 1000.0))

    def read_l2_values(self, payload_dec):
        # Active Power L2 80,81 / Minus 82,83 combined and transformed (uint)
        active_power_l2 = (payload_dec.decode_32bit_uint() - payload_dec.decode_32bit_uint()) / 10.0
        self._set_output_value(self.PIN_O_ACTIVE_POWER_L2, active_power_l2)

        # Reactive Power L2 84,85 / Minus 86,87 combined and transformed (uint)
        reactive_power_l2 = (payload_dec.decode_32bit_uint() - payload_dec.decode_32bit_uint()) / 10.0
        self._set_output_value(self.PIN_O_REACTIVE_POWER_L2, reactive_power_l2)
        payload_dec.skip_bytes(16)  # skip 8 registers

        # Apparent Power L2 96,97 / Minus 98,99 combined and transformed (uint)
        apparent_power_l2 = (payload_dec.decode_32bit_uint() - payload_dec.decode_32bit_uint()) / 10.0
        self._set_output_value(self.PIN_O_APPARENT_POWER_L2, apparent_power_l2)

        # Current L2 100/101 transformed (uint) / Voltage L2 102/103 transformed (uint)
        self._set_output_value(self.PIN_O_CURRENT_L2, (payload_dec.decode_32bit_uint() / 1000.0))
        self._set_output_value(self.PIN_O_VOLTAGE_L2, (payload_dec.decode_32bit_uint() / 1000.0))
        # Power Factor L2 104/105 transformed (int!)
        self._set_output_value(self.PIN_O_POWER_FACTOR_L2, (payload_dec.decode_32bit_int() / 1000.0))

    def read_l3_values(self, payload_dec):
        payload_dec.skip_bytes(28)  # Skip over 14 registers

        # Active Power L3 120,121 / Minus 122,123 combined and transformed (uint)
        active_power_l3 = (payload_dec.decode_32bit_uint() - payload_dec.decode_32bit_uint()) / 10.0
        self._set_output_value(self.PIN_O_ACTIVE_POWER_L3, active_power_l3)

        # Reactive Power L3 124,125 / Minus 126,127 combined and transformed (uint)
        reactive_power_l3 = (payload_dec.decode_32bit_uint() - payload_dec.decode_32bit_uint()) / 10.0
        self._set_output_value(self.PIN_O_REACTIVE_POWER_L3, reactive_power_l3)
        payload_dec.skip_bytes(16)  # skip 8 registers

        # Apparent Power L3 136,137 / Minus 138,139 combined and transformed (uint)
        apparent_power_l3 = (payload_dec.decode_32bit_uint() - payload_dec.decode_32bit_uint()) / 10.0
        self._set_output_value(self.PIN_O_APPARENT_POWER_L3, apparent_power_l3)

        # Current L3 140/141 transformed (uint) / Voltage L3 142/143 transformed (uint)
        self._set_output_value(self.PIN_O_CURRENT_L3, (payload_dec.decode_32bit_uint() / 1000.0))
        self._set_output_value(self.PIN_O_VOLTAGE_L3, (payload_dec.decode_32bit_uint() / 1000.0))
        # Power Factor L3 144/145 transformed (int!)
        self._set_output_value(self.PIN_O_POWER_FACTOR_L3, (payload_dec.decode_32bit_int() / 1000.0))

    def read_counter_values(self, payload_dec):

        # Active Power from grid 512-515 - transformed to kWh
        self._set_output_value(self.PIN_O_COUNTER_ACTIVE_POWER_PLUS, (payload_dec.decode_64bit_uint() / 10000.0))
        # Active Power feed-in 516-519 - transformed to kWh
        self._set_output_value(self.PIN_O_COUNTER_ACTIVE_POWER_MINUS, (payload_dec.decode_64bit_uint() / 10000.0))

        # Reactive Power from grid 520-523 - transformed to kvarh
        self._set_output_value(self.PIN_O_COUNTER_REACTIVE_POWER_PLUS, (payload_dec.decode_64bit_uint() / 10000.0))
        # Reactive Power feed-in 524-527 - transformed to kvarh
        self._set_output_value(self.PIN_O_COUNTER_REACTIVE_POWER_MINUS, (payload_dec.decode_64bit_uint() / 10000.0))

        # Reactive Power from grid 544-547 - transformed to kVAh
        self._set_output_value(self.PIN_O_COUNTER_APPARENT_POWER_PLUS, (payload_dec.decode_64bit_uint() / 10000.0))
        # Reactive Power feed-in 548-551 - transformed to kVAh
        self._set_output_value(self.PIN_O_COUNTER_APPARENT_POWER_MINUS, (payload_dec.decode_64bit_uint() / 10000.0))

    #############

    def on_init(self):
        self.interval = self.FRAMEWORK.create_interval()
        if self._get_input_value(self.PIN_I_SWITCH) == 1:
            self.interval.set_interval(self._get_input_value(self.PIN_I_FETCH_INTERVAL) * 1000, self.on_interval)
            self.interval.start()

    def on_input_value(self, index, value):
        if index == self.PIN_I_SWITCH:
            self.interval.stop()
            if value == 1:
                self.interval.set_interval(self._get_input_value(self.PIN_I_FETCH_INTERVAL) * 1000, self.on_interval)
                self.interval.start()
