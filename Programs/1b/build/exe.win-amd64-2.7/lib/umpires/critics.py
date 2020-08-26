
__author__ = 'miquelramirez'

import matplotlib.pyplot as plt

import utils


class GunScore :

    def __init__( self, name, subject, object, min_range, max_range, max_altitude, max_speed, max_angle ) :
        self.name = name
        self.subject = subject
        self.object = object
        self.min_range = min_range
        self.max_range = max_range
        self.max_altitude = max_altitude
        self.max_speed = max_speed
        self.max_angle = max_angle
        self.measures = { 't' : [], 'score' : [] }
        self.score = 0

    def print_score(self):
        print 'Total run score: ', self.score

    def get_score(self):
        return getattr(self, 'score')

    def increase_fitness(self, weight):
        self.score += weight

    def check_range(self, sub_fighter, obj_fighter):
        if self.max_range > utils.get_range(sub_fighter.fcs.platform,
                                            obj_fighter.fcs.platform) > self.min_range:
            self.increase_fitness(1)

    def check_attack_angle(self, sub_fighter, obj_fighter):
        if utils.is_in_attack_angle(sub_fighter.fcs.platform, obj_fighter.fcs.platform, self.max_angle):
            self.increase_fitness(1)

    def check_reverse_attack_angle(self, sub_fighter, obj_fighter):
        if utils.is_in_reverse_attack_angle(obj_fighter.fcs.platform, sub_fighter.fcs.platform, self.max_angle):
            self.increase_fitness(1)

    def check_altitude(self, sub_fighter, obj_fighter):
        if utils.altitude_difference(sub_fighter.fcs.platform.get_altitude(),
                                     obj_fighter.fcs.platform.get_altitude()) < self.max_altitude:
            self.increase_fitness(1)

    def check_speed(self, sub_fighter, obj_fighter):
        if utils.speed_difference(sub_fighter.fcs.platform.get_speed(),
                                  obj_fighter.fcs.platform.get_speed()) < self.max_speed:
            self.increase_fitness(1)

    def check_is_behind(self, sub_fighter, obj_fighter):
        if utils.is_behind(sub_fighter.fcs.platform, obj_fighter.fcs.platform):
            self.increase_fitness(1)
            if utils.is_behind(obj_fighter.fcs.platform, sub_fighter.fcs.platform):
                self.increase_fitness(-1)

    def evaluate( self, obj) :
        sub_fighter = getattr( obj, self.subject)
        obj_fighter = getattr( obj, self.object)

        # # Measure 3D Range
        # range = utils.get_range( sub_fighter.fcs.platform, obj_fighter.fcs.platform )
        # if range > self.max_range :
        #     self.measures['t'].append( obj.current_time)
        #     self.measures['score'].append( 0.0 )
        #     return
        #
        # # Measure 3D Target Aspect Angle
        # taa = utils.get_aspect_angle( sub_fighter.fcs.platform, obj_fighter.fcs.platform )
        # if (taa < 180.0 - self.max_angle) and (taa > 180.0 + self.max_angle) :
        #     self.measures['t'].append( obj.current_time)
        #     self.measures['score'].append( 0.0 )
        #     return

        if self.subject == 'viper' and utils.is_close(obj.current_time % 1, 1):
            self.check_is_behind(sub_fighter, obj_fighter)
            self.check_range(sub_fighter, obj_fighter)
            self.check_attack_angle(sub_fighter, obj_fighter)
            self.check_reverse_attack_angle(sub_fighter, obj_fighter)
            self.check_altitude(sub_fighter, obj_fighter)
            self.check_speed(sub_fighter, obj_fighter)
            sub_fighter.set_score(self.get_score())

        if self.subject == 'cobra' and utils.is_close(obj.current_time % 1, 1):
            self.check_is_behind(sub_fighter, obj_fighter)
            self.check_range(sub_fighter, obj_fighter)
            self.check_attack_angle(sub_fighter, obj_fighter)
            self.check_reverse_attack_angle(sub_fighter, obj_fighter)
            self.check_altitude(sub_fighter, obj_fighter)
            self.check_speed(sub_fighter, obj_fighter)
            sub_fighter.set_score(self.get_score())

        # Compute gun scores
        # Gun score mimics a cumulative distribution function for the log PK of
        # achieving a gun kill.

        # self.measures['t'].append( obj.current_time )
        # if len(self.measures['score']) == 0 : # first datum
        #     self.measures['score'].append( 1.0 )
        #     return
        # self.measures['score'].append( self.measures['score'][-1] + self.score )

    def draw_chart( self ) :
        fig = plt.figure()
        ax = fig.gca()
        plt.grid(True)
        plt.title(self.name, loc='left')
        plt.axis('equal')

        ax.set_xlabel( 't (seconds)')
        ax.set_ylabel( 'score')

        xmin = min(self.measures['t'])
        xmax = max(self.measures['t'])
        ymin = min(self.measures['score'])
        ymax = max(self.measures['score'])

        ax.set_xlim(xmin,xmax)
        ax.set_ylim(ymin,ymax)

        # Plot Trajectories
        plt.plot(self.measures['t'], self.measures['score'], color='b')
        plt.show()
