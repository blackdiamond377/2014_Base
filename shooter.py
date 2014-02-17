import common

try:
    import wpilib
except ImportError:
    from pyfrc import wpilib


__all__ = ['Shooter']


class Shooter(common.ComponentBase):

    SHOOTING = 'shooting'
    RESET = 'reset'
    RESETTING = 'resetting'
    AUTO_SHOOT_DONE = 'auto_shoot_done'

    def __init__(self, config):
        self.motors = config.motors

        self.shoot_button = config.shoot_button

        self.stop_buttons = config.stop_buttons
        
        self.stop_counters = config.stop_counters


        self.reset_stop = config.reset_stop
    
        self.op_state = self.RESETTING

        self.stop_pos = -1

        self.auto_state = self.RESET

        self.RESETTING_SPEED = -.1

        self.SHOOTING_SPEED = 1


    def op_init(self):
        for counter in self.stop_counters:
            counter.Reset()

        self.op_state = self.RESETTING 

    def op_tick(self, time):

        if self.op_state == self.RESET:
            speed = 0
            if self.shoot_button.get():
                self.op_state = self.SHOOTING
                self.stop_pos = self.get_current_stop()
                for counter in self.stop_counters:
                    counter.Reset()

        if self.op_state == self.SHOOTING:
            speed = self.SHOOTING_SPEED
            if self.should_stop(self.stop_pos):
                speed = 0
                self.op_state = self.RESETTING
                self.stop_pos = -1

        if self.op_state == self.RESETTING:
            speed = self.RESETTING_SPEED
            if self.should_stop(self.stop_pos):
                speed = 0
                self.op_state = self.RESET

    def auto_shoot_tick(self, time):

        speed = 0
        if self.auto_state == self.RESET:
            self.auto_state = self.SHOOTING

        elif self.auto_state == self.SHOOTING:
            speed = self.SHOOTING_SPEED
            if self.stop_counters[-1].Get():
                self.auto_state = self.RESETTING

        elif self.auto_state == self.RESETTING:
            speed = self.RESETTING_SPEED
            if self.reset_stop.Get():
                self.auto_state = self.AUTO_SHOOT_DONE

        elif self.auto_state == self.AUTO_SHOOT_DONE:
            speed = 0

        self.motors.Set(speed)
        
        wpilib.SmartDashboard.PutString('auto shooter state', self.auto_state)

    def is_auto_shoot_done(self):
        return self.auto_state == self.AUTO_SHOOT_DONE

    def get_current_stop(self):
        for idx, button in enumerate(self.stop_buttons):
            if button.get():
                return idx

        # If we don't detect any buttons go for the most restrictive.
        # That way if the switch malfunctions or we don't read it, we just
        # stop.
        return 0


    def should_stop(self, stop_pos):
        if stop_pos == -1 and self.reset_stop.Get():
            return True

        for idx, counter in enumerate(self.stop_counters):
            # 0 is False and positve is True
            if idx >= stop_pos and counter.Get(): 
                return True

        return False
