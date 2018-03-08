import wmi

debug = False


class OHM:

    def __init__(self):
        self.hwmon = wmi.WMI(namespace="root\OpenHardwareMonitor")

    def get_core_temps(self):
        data = {}
        sensors_temp = self.hwmon.Sensor(["Name", "Parent", "Value", "Identifier", "SensorType", "Max"],
                                         SensorType="Temperature")
        if debug:
            print(sensors_temp)

        for temperature in sensors_temp:

            if debug:
                print("temperature object")
                print(temperature)

            if (temperature.Identifier.find("ram") == -1) and (temperature.Identifier.find("hdd") == -1) \
                    and (temperature.Name.find("Package") == -1):
                if debug:
                    print("cpu temperature values")
                    print(f"{temperature.value}, {temperature.max}, {temperature.name}")

                data['type'] = "cpu temperature"
                data[temperature.name] = temperature.value

        return data

    def get_core_loads(self):
        data = {}
        sensors_load = self.hwmon.Sensor(SensorType="Load")

        if debug:
            print(sensors_load)

        for load in sensors_load:
            if (load.Identifier.find("ram") == -1) and (load.Identifier.find("hdd") == -1) and (
                    load.Name.find("Total") == -1):

                if debug:
                    print(f"{load.value}, {load.name}")

                data['type'] = "cpu load"
                data[load.name] = load.value

        return data

    def get_clock_speeds(self):
        data = {}
        sensors_speed = self.hwmon.Sensor(SensorType="Clock")

        if debug:
            print(sensors_speed)

        for speed in sensors_speed:
            if (speed.Identifier.find("ram") == -1) and (speed.Identifier.find("hdd") == -1) and (
                    speed.Name.find("Total") == -1):

                if debug:
                    print(f"{speed.value}, {speed.name}")

                data['type'] = "clock speeds"
                data[speed.name] = speed.value

        return data


if __name__ == '__main__':

    my_ohm = OHM()
    core_temps = my_ohm.get_core_temps()
    print(core_temps)
    core_loads = my_ohm.get_core_loads()
    print(core_loads)
    clock_speeds = my_ohm.get_clock_speeds()
    print(clock_speeds)
