""" Stage of a heavy lift vehicle
	attach_engine(engine)
	attached_engine_report
	jettison
"""

from util import func


class Stage(object):
    """actions and info regarding a stage of a heavy lift vehicle"""

    def __init__(self, stage_specs):
        self.fuel_used = 0.0
        self.fuel = 0.0
        self.lift_off_weight = 0.0
        self.name = "Not set"
        self.fueling_engines = []
        self.attached_engines = []
        self.attached = True
        self.jettison_time = None
        for key, value in stage_specs.items():
            setattr(self, key, value)

        if self.jettison_time:
            self.jettison_time = round(self.jettison_time, 1)

    def __str__(self):
        return "Stage Name = {} Fuel Remaining = {} Burn Rate = {}".format(
            self.name, self.get_fuel_remaining(), self.get_fuel_burn_rate()
        )

    def attach_engine(self, engine):
        """add an engine object to the list of engines"""
        self.attached_engines.append(engine)

    def attached_engine_report(self):
        """view attached engines"""
        print(" \n {}".format(self.name))
        for engine in self.attached_engines:
            print(engine)

    @staticmethod
    def check_fuel(fuel, fuel_used, attached):
        """Check if FuelValueError should be raised"""
        fuel_remaining = fuel - fuel_used
        if attached and fuel_remaining < 0:
            print("ERROR: Fuel used is {:.2f} of {:.2f}".format(fuel_used, fuel))
            # raise exceptions.FuelValueError("More fuel was used than available")

    def check_state(self):
        """check if the stage is in a valid state:
        a) check fuel level
        """
        self.check_fuel(self.fuel, self.fuel_used, self.attached)

    def fueling(self, engine):
        """add an engine to the list of engines that this stage provides fuel for"""
        self.fueling_engines.append(engine)

    def get_fuel_used(self):
        """get the fuel used"""
        return self.fuel_used

    def get_fuel_remaining(self):
        """get the fuel remaining"""
        fuel_remaining = self.fuel - self.fuel_used
        self.check_state()
        return fuel_remaining

    def get_fuel_burn_rate(self):
        """get the sum of the fueling engines burn rate"""
        burn = 0.0
        for engine in self.fueling_engines:
            burn += engine.get_eff_fuel_burn_rate()
        return burn

    def jettison(self):
        """jettisons the stage and checks that attached engines are off"""
        print("\nEVENT: Jettisoned {}".format(self.name))
        self.attached = False
        for engine in self.attached_engines:
            # set the average throttle of attached engines to zero
            engine.throt_cur = 0.0
            engine.throt_prev = 0.0
        # if rocket total weight is calculated on total values change to be fueled_weight:
        # if rocket total weight is calculated on lift-off values use this:
        self.fuel_used = self.lift_off_weight

    def events(self, time, time_inc):
        # check for jettison time and then jettison
        if self.jettison_time and func.almost_equal(self.jettison_time, time, 0.01):
            self.jettison()
