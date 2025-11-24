def calibrate_light_sensor() -> None:
    print('Begin calibraing light sensor!', flush=True)
    print('FR -> Einloggen  || FL -> Alle Bestaetigen ||  BR -> Letzten neu  ||  BL -> Alle neu', flush=True)
    print('===========================================', flush=True)
    points = 0
    last_points = None
    pressed_f = False
    pressed_br = False
    keeper = {'front_start_on': 0, 'front_start_off': 0, 'front_middle_on': 0, 'front_middle_off': 0,
              'front_condiment_on': 0, 'front_condiment_off': 0, 'back_start_on': 0, 'back_start_off': 0,
              'back_middle_on': 0, 'back_middle_off': 0, 'back_condiment_on': 0, 'back_condiment_off': 0}

    def calc_avrg_light():
        global ON_LIGHT_SENSOR_FRONT, OFF_LIGHT_SENSOR_FRONT, ON_LIGHT_SENSOR_BACK, OFF_LIGHT_SENSOR_BACK
        ON_LIGHT_SENSOR_FRONT = min([v for k, v in keeper.items() if 'front' in k and k.endswith('on')])
        OFF_LIGHT_SENSOR_FRONT = max([v for k, v in keeper.items() if 'front' in k and k.endswith('off')])
        ON_LIGHT_SENSOR_BACK = min([v for k, v in keeper.items() if 'back' in k and k.endswith('on')])
        OFF_LIGHT_SENSOR_BACK = max([v for k, v in keeper.items() if 'back' in k and k.endswith('off')])

    while True:
        while k.digital(PORT_DIGITAL_FL) == 1:
            if points == 6:
                points = 7
        while k.digital(PORT_DIGITAL_FR) == 1:
            pressed_f = True
        while k.digital(PORT_DIGITAL_BR) == 1:
            pressed_br = True
        if k.digital(PORT_DIGITAL_BL) == 1:
            points = 0

        if pressed_f:
            pressed_f = False
            if points < 6:  # if points reach 7, then this function will end, so we need to make it stop at 6
                points += 1
            else:
                print('!!! YOU CLICKED ONCE TOO MANY !!!', flush=True)
        if pressed_br:
            pressed_br = False
            if points > 0:
                points -= 1

        if last_points != points:
            last_points = points
            if points == 0:
                print('========== STARTING BOX ==========', flush=True)
                print('Starting Box - Front on BLACK ...', flush=True)
            elif points == 1:
                keeper['front_start_on'] = k.analog(PORT_LIGHT_SENSOR_FRONT)
                keeper['back_start_off'] = k.analog(PORT_LIGHT_SENSOR_BACK)
                print('Starting Box - Front on WHITE ...', flush=True)
            elif points == 2:
                keeper['front_start_off'] = k.analog(PORT_LIGHT_SENSOR_FRONT)
                keeper['back_start_on'] = k.analog(PORT_LIGHT_SENSOR_BACK)
                print('============= MIDDLE =============', flush=True)
                print('Middle - Front on BLACK ...', flush=True)
            elif points == 3:
                keeper['front_middle_on'] = k.analog(PORT_LIGHT_SENSOR_FRONT)
                keeper['back_middle_off'] = k.analog(PORT_LIGHT_SENSOR_BACK)
                print('Middle - Front on WHITE ...', flush=True)
            elif points == 4:
                keeper['front_middle_off'] = k.analog(PORT_LIGHT_SENSOR_FRONT)
                keeper['back_middle_on'] = k.analog(PORT_LIGHT_SENSOR_BACK)
                print('=========== CONDIMENT ===========', flush=True)
                print('Condiment Station - Front on BLACK ...', flush=True)
            elif points == 5:
                keeper['front_condiment_on'] = k.analog(PORT_LIGHT_SENSOR_FRONT)
                keeper['back_condiment_off'] = k.analog(PORT_LIGHT_SENSOR_BACK)
                print('Condiment Station - Front on WHITE ...', flush=True)
            elif points == 6:
                keeper['front_condiment_off'] = k.analog(PORT_LIGHT_SENSOR_FRONT)
                keeper['back_condiment_on'] = k.analog(PORT_LIGHT_SENSOR_BACK)
                print('============= SUBMIT =============', flush=True)
                print('Submit or reset (last) now ...', flush=True)
            else:
                break

    calc_avrg_light()
    print('====== FINISHED, GOOD LUCK! ======', flush=True)


def start_position() -> None:
    """makes the claw begin every time the same on start

    Args:
        None

    Returns:
        None

    """
    claw_position_open(2000)
    shovel_servo_base()
    shovel_motor_position(10000)
    shovel_servo_position(1900)
    shovel_motor_position(15000)
    shovel_servo_position(2047)


stabelized = False  # variable for stabelizing. If a motor gets stabelizing at the moment, this variable will become 'True'

def start_stabelizing_motor(Port: int) -> None:
    global stabelized

    if not stabelized:
        stabelized = True
        k.clear_motor_position_counter(PORT_MOTOR_CLAW)

        def stab():
            avrg = 0
            while stabelized:
                avrg += k.gmpc(PORT_MOTOR_CLAW)
                if avrg > 0:
                    speed = -DC_SPEED
                else:
                    speed = DC_SPEED
                k.mav(PORT_MOTOR_CLAW, -k.gmpc(PORT_MOTOR_CLAW) * 2)

        threading.Thread(target=stab).start()
    else:
        print('start_stabelizing_motor() Exception: motor is already stabelizing', flush=True)
        raise Exception('start_stabelizing_motor() Exception: motor is already stabelizing')

def stop_stabelizing_motor() -> None:
    global stabelized

    if not stabelized:
        print('stop_stabelizing_motor() Exception: there is no stabelizing taking place', flush=True)
        raise Exception('stop_stabelizing_motor() Exception: there is no stabelizing taking place ')
    else:
        stabelized = False


def setup(at_competition: bool) -> None:
    def tryout():
        try:
            global bias_gyro_z, bias_gyro_y, OFF_LIGHT_SENSOR_BACK, ON_LIGHT_SENSOR_BACK, OFF_LIGHT_SENSOR_FRONT, ON_LIGHT_SENSOR_FRONT, ON_LIGHT_SENSOR_SIDE, OFF_LIGHT_SENSOR_SIDE, NINETY_DEGREES_SECS, ONEEIGHTY_DEGREES_SECS
            m = 2
            calibrate_gyro_z(1, m)
            calibrate_gyro_y(2, m)
            ON_LIGHT_SENSOR_FRONT = 3694
            OFF_LIGHT_SENSOR_FRONT = 867
            ON_LIGHT_SENSOR_BACK = 3024
            OFF_LIGHT_SENSOR_BACK = 210
            ON_LIGHT_SENSOR_SIDE = 4000
            OFF_LIGHT_SENSOR_SIDE = 2800
            ONEEIGHTY_DEGREES_SECS = 1.6893332799275715
            NINETY_DEGREES_SECS = 0.8446666399637858
        # bias_accel_x = get_bias_accel_x() -> not in use
        # bias_accel_y = get_bias_accel_y() -> not in use
        except Exception as e:
            print('setup() Error: ', str(e), flush=True)

    def actual():
        try:
            calibrate_light_sensor()
            max = 2
            calibrate_gyro_z(1, max)
            calibrate_gyro_y(2, max)
            calibrate_degrees()
            print('')

        except Exception as e:
            print('setup() Error: ', str(e), flush=True)

    start_position()
    print('////////////////////////////////////////////', flush=True)
    if at_competition:
        print(f'!!! You are currently in the COMPETITION mode !!!', flush=True)
        print('////////////////////////////////////////////\n', flush=True)
        actual()
    else:
        print(f'!!! You are currently in the TRYOUT mode !!!', flush=True)
        print('////////////////////////////////////////////\n', flush=True)
        tryout()
    k.cmpc(PORT_MOTOR_CLAW)

def align_on_black_line(self, crossing: bool, direction: str = 'vertical', leaning_side: str = None) -> None:
    '''
   Align yourself on the black line. If there is a crossing you can choose on which line you want to get onto by switching the direction parameter. You need to be somewhere on top of the black line to let this function work!

   Args:
       crossing (bool): are there two overlapping black lines (True) or not (False)
       direction (str, optional): "vertical" (default) or "horizontal" - depends on where you want to go
       leaning_side (str, optional): "left" or "right" - helps the roboter to turn in the right direction (-> faster)
       precise (bool, optional): if True, then it takes longer, but is slightly better aligned on the black line. If False, it takes less time but the bias is therefor more forgiving

   Returns:
       None
   '''
    self.check_instance_light_sensors_middle()
    motor_id = self._manage_motor_stopper(True)
    try:
        if direction != 'vertical' and direction != 'horizontal':
            log('Only "vertical" or "horizontal" are valid options for the "direction" parameter',
                in_exception=True)
            raise ValueError(
                'align_on_black_line() Exception: Only "vertical" or "horizontal" are valid options for the "direction" parameter')

        if leaning_side != None and leaning_side != 'right' and leaning_side != 'left':
            log('Only "right", "left" or None / nothing are valid options for the "leaning_side" parameter',
                in_exception=True)
            raise ValueError(
                'align_on_black_line() Exception: Only "right", "left" or None / nothing are valid options for the "leaning_side" parameter')

        if not crossing:
            log('no crossing')
            if not leaning_side or leaning_side == 'right':
                ports = self.port_wheel_left, self.port_wheel_right
            else:
                ports = self.port_wheel_right, self.port_wheel_left
            startTime = k.seconds()
            while self.light_sensor_back.sees_white() and self.light_sensor_front.sees_white() and self.is_motor_active(motor_id):
                if k.seconds() - startTime < self.NINETY_DEGREES_SECS:
                    k.mav(ports[0], self.ds_speed)
                    k.mav(ports[1], -self.ds_speed)
                else:
                    k.mav(ports[0], -self.ds_speed)
                    k.mav(ports[1], self.ds_speed // 2)
                    k.msleep(1)

            self.break_all_motors()

            if not self.light_sensor_back.sees_white():  # hinten ist oben
                while not self.light_sensor_front.sees_black() and self.is_motor_active(motor_id):
                    k.mav(ports[0], -self.ds_speed)
                    k.mav(ports[1], -self.ds_speed)
                self.break_all_motors()
                while self.light_sensor_front.sees_black() and self.is_motor_active(motor_id):
                    k.mav(ports[0], 1500)
                self.break_all_motors()
                while not self.light_sensor_front.sees_black() and self.is_motor_active(motor_id):
                    k.mav(ports[1], 1500)
                self.break_all_motors()
                while self.light_sensor_front.sees_black() and self.is_motor_active(motor_id):
                    k.mav(ports[1], 1500)
                self.break_all_motors()
                while not self.light_sensor_front.sees_black() and self.is_motor_active(motor_id):
                    k.mav(ports[1], -1500)
                    k.mav(ports[0], -200)
                self.break_all_motors()

            elif not self.light_sensor_front.sees_white():  # vorne ist oben
                while not self.light_sensor_back.sees_black() and self.is_motor_active(motor_id):
                    k.mav(ports[0], self.ds_speed)
                    k.mav(ports[1], self.ds_speed)
                while not self.light_sensor_front.sees_black() and self.is_motor_active(motor_id):
                    k.mav(ports[0], -1500)
                    k.mav(ports[1], 1500)

            self.break_all_motors()

            if not self.light_sensor_front.sees_black():
                self.break_all_motors()
                while not self.light_sensor_front.sees_white() and self.is_motor_active(motor_id):
                    k.mav(ports[1], 1500)

                while not self.light_sensor_front.sees_black() and self.is_motor_active(motor_id):
                    k.mav(ports[1], 1500)

            if not self.light_sensor_back.sees_black():
                while self.light_sensor_front.sees_black() and self.is_motor_active(motor_id):
                    k.mav(ports[1], 1500)
                while self.light_sensor_back.sees_white() and self.is_motor_active(motor_id):
                    k.mav(ports[1], -1500)
                    k.mav(ports[0], 1500)

            self.break_all_motors()

        else:
            ports = self.port_wheel_left, self.port_wheel_right
            on_line = False
            first_line_hit = None
            line_counter = 0
            line_timer = 0
            line_timer_collector = []

            startTime_front = k.seconds()
            while k.seconds() - startTime_front < self.ONEEIGHTY_DEGREES_SECS * 2 + 0.2  and self.is_motor_active(motor_id):  # +0.2 is a kind of bias
                while self.light_sensor_front.sees_black()  and self.is_motor_active(motor_id):
                    on_line = True
                    line_timer += 1
                    k.mav(ports[0], -self.ds_speed)
                    k.mav(ports[1], self.ds_speed)
                if on_line:
                    if not first_line_hit:
                        first_line_hit = k.seconds() - startTime_front
                    on_line = False
                    line_counter += 1
                    line_timer_collector.append(line_timer)
                    line_timer = 0
                k.mav(ports[0], -self.ds_speed)
                k.mav(ports[1], self.ds_speed)

            if line_counter > 4:
                line_counter = 4

            on_line = False
            direct = 'right', 'left'
            dir_picker = self.NINETY_DEGREES_SECS / 1.4, first_line_hit
            if direction == 'horizontal':
                dir_picker = dir_picker[1], dir_picker[0]

            if line_counter == 1 and line_timer_collector[0] < 400:  # There is no crossing, just the normal line
                self.align_on_black_line(False, direction=direction, leaning_side=leaning_side)
                return

            if line_counter == 2 and line_timer_collector[0] < 400 and line_timer_collector[
                1] < 400:  # There is no crossing, just the normal line
                self.align_on_black_line(False, direction=direction, leaning_side=leaning_side)
                return

            if line_counter == 4:
                if dir_picker[0] < dir_picker[1]:
                    d = direct[0]
                    while not self.light_sensor_front.sees_black() and self.is_motor_active(motor_id):
                        k.mav(ports[0], self.ds_speed)
                        k.mav(ports[1], -self.ds_speed)
                    self.break_all_motors()
                    while not self.light_sensor_back.sees_black() and self.is_motor_active(motor_id):
                        k.mav(ports[0], self.ds_speed)
                        k.mav(ports[1], self.ds_speed)
                    while not self.light_sensor_front.sees_black() and self.is_motor_active(motor_id):
                        k.mav(ports[0], self.ds_speed)
                        k.mav(ports[1], -self.ds_speed)
                    self.break_all_motors()
                else:
                    d = direct[1]
                    while not self.light_sensor_front.sees_black() and self.is_motor_active(motor_id):
                        k.mav(ports[0], -self.ds_speed)
                        k.mav(ports[1], self.ds_speed)
                    self.break_all_motors()
                    while not self.light_sensor_back.sees_black() and self.is_motor_active(motor_id):
                        k.mav(ports[0], self.ds_speed)
                        k.mav(ports[1], self.ds_speed)
                    self.break_all_motors()
                    while not self.light_sensor_front.sees_black() and self.is_motor_active(motor_id):
                        k.mav(ports[0], -self.ds_speed)
                        k.mav(ports[1], self.ds_speed)
                    self.break_all_motors()

            elif line_counter == 3:
                if dir_picker[0] > dir_picker[1]:
                    d = direct[0]
                    while not self.light_sensor_front.sees_black() and self.is_motor_active(motor_id):
                        k.mav(ports[0], self.ds_speed)
                        k.mav(ports[1], -self.ds_speed)
                    self.break_all_motors()
                    while not self.light_sensor_back.sees_black() and self.is_motor_active(motor_id):
                        k.mav(ports[0], self.ds_speed)
                        k.mav(ports[1], self.ds_speed)
                    self.break_all_motors()
                    if not self.light_sensor_front.sees_black():
                        while not self.light_sensor_front.sees_black() and self.is_motor_active(motor_id):
                            k.mav(ports[0], -self.ds_speed)
                            k.mav(ports[1], self.ds_speed)
                        self.break_all_motors()
                else:
                    d = direct[1]
                    while not self.light_sensor_front.sees_black() and self.is_motor_active(motor_id):
                        k.mav(ports[0], -self.ds_speed)
                        k.mav(ports[1], self.ds_speed)
                    self.break_all_motors()
                    while not self.light_sensor_back.sees_black() and self.is_motor_active(motor_id):
                        k.mav(ports[0], self.ds_speed)
                        k.mav(ports[1], self.ds_speed)
                    self.break_all_motors()
                    if not self.light_sensor_front.sees_black():
                        while not self.light_sensor_front.sees_black() and self.is_motor_active(motor_id):
                            k.mav(ports[0], -self.ds_speed)
                            k.mav(ports[1], self.ds_speed)
                        self.break_all_motors()

            else:  # line_counter == 2
                if dir_picker[0] < dir_picker[1]:
                    d = direct[0]
                    while not self.light_sensor_front.sees_black() and self.is_motor_active(motor_id):
                        k.mav(ports[0], self.ds_speed)
                        k.mav(ports[1], -self.ds_speed)
                    self.break_all_motors()
                    while not self.light_sensor_back.sees_black() and self.is_motor_active(motor_id):
                        k.mav(ports[0], self.ds_speed)
                        k.mav(ports[1], self.ds_speed)
                    self.break_all_motors()
                else:
                    d = direct[1]
                    while not self.light_sensor_front.sees_black() and self.is_motor_active(motor_id):
                        k.mav(ports[0], -self.ds_speed)
                        k.mav(ports[1], self.ds_speed)
                    self.break_all_motors()

            #self.next_to_onto_line(d)
        self.break_all_motors()
        self._manage_motor_stopper(False)


    except Exception as e:
        log(str(e), important=True, in_exception=True)