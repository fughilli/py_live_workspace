import pygame
import threading
import time
import numpy


def Vec(*args):
    return numpy.array([float(x) for x in args])


class Ball:
    def __init__(self, position=Vec(0, 0), velocity=Vec(0, 0)):
        self.position = position
        self.velocity = velocity
        self.accel = Vec(0, 0)
        self.color = (255, ) * 3
        self.mass = 1

    def apply_force(self, force):
        self.accel += force / self.mass

    def apply_impulse(self, impulse):
        self.velocity += impulse / self.mass

    def tick(self, dt):
        self.velocity += self.accel * dt
        self.position += self.velocity * dt
        self.accel = Vec(0, 0)

    def draw(self, screen):
        pygame.draw.circle(screen, self.color,
                           Vec(self.position[0], 300 - self.position[1]), 10,
                           1)


class World:
    def __init__(self):
        self.objects = []
        for i in range(1000):
            self.objects.append(Ball(Vec(150, 200), Vec(i/10, i/10)))
        self.last_time = time.time()

    def draw(self, screen):
        current_time = time.time()
        dt = current_time - self.last_time

        for o in self.objects:
            o.apply_force(Vec(0, -500))
            if o.position[1] <= 0 and o.velocity[1] < 0:
                o.apply_impulse(2 * o.mass * -Vec(0, o.velocity[1]))
            if ((o.position[0] <= 0 and o.velocity[0] < 0)
                    or (o.position[0] >= 300 and o.velocity[0] > 0)):
                o.apply_impulse(2 * o.mass * -Vec(o.velocity[0], 0))
            o.apply_force(-o.velocity/10)

        for o in self.objects:
            o.tick(dt)

        for o in self.objects:
            o.draw(screen)

        self.last_time = current_time


world = World()


def draw_fn(screen):
    screen.fill((0, 0, 0))
    world.draw(screen)


class Runner:
    def start(self):
        self.should_exit = False
        self.thread = threading.Thread(target=self.run)
        self.thread.start()

    def stop(self):
        self.should_exit = True
        self.thread.join()

    def run(self):
        while not self.should_exit:
            workspace.submit_draw(draw_fn)
            workspace.wait_frame()


runner = Runner()


def start():
    runner.start()


def stop():
    runner.stop()
