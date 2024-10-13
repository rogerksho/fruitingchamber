import sys

class PID:
    curr_e = 0
    prev_e = 0
    accumulated_e = 0

    set_point = None

    def __init__(self, Kp, Ki, Kd):
        self.Kp = Kp
        self.Kd = Kd
        self.Ki = Ki

    def set_operating_point(self, set_point):
        self.set_point = set_point

    def set_command_limit(self, c_min, c_max):
        self.command_min = c_min
        self.command_max = c_max

    def _p_control(self, measured_state):
        self.curr_e = self.set_point - measured_state

        return self.Kp*self.curr_e

    def _d_control(self):
        deriv = self.curr_e - self.prev_e
        self.prev_e = self.curr_e
        return self.Kd*deriv
    
    def _i_control(self):
        # read from file
        f = open('accumulated_error.txt', 'r')
        self.accumulated_e = int(f.read())
        f.close()
        
        # add current error
        self.accumulated_e += self.curr_e
        
        # write error back in
        f_out = open('accumulated_error.txt', 'w')
        f_out.write(str(int(self.accumulated_e)))
        f_out.flush()
        f_out.close()
        
        print('accumulated error:', self.accumulated_e)
        return self.Ki*self.accumulated_e

    def get_control(self, measured_state):
        if self.set_point is None:
            print('no setpoint defined. exiting.')
            sys.exit(1)

        p_command = self._p_control(measured_state)
        i_command = self._i_control()
        d_command = self._d_control()

        command = p_command + d_command + i_command
        return command

    def get_control_saturated(self, measured_state):
        unsat_command = self.get_control(measured_state)

        if unsat_command > self.command_max:
            return self.command_max

        if unsat_command < self.command_min:
            return self.command_min

        return unsat_command
