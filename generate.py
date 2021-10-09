import pygame
import threading
import time
import numpy


def Vec(*args):
    return numpy.array([float(x) for x in args])


def Project(x, y):
    return y * numpy.dot(x, y) / numpy.dot(y, y)


class Ball:
    def __init__(self,
                 position=Vec(0, 0),
                 velocity=Vec(0, 0),
                 mass=1,
                 frozen=False):
        self.position = position
        self.velocity = velocity
        self.accel = Vec(0, 0)
        self.color = (255, ) * 3
        self.mass = mass
        self.frozen = frozen

    def apply_force(self, force):
        self.accel += force / self.mass

    def apply_impulse(self, impulse):
        self.velocity += impulse / self.mass

    def tick(self, dt):
        if self.frozen:
            self.velocity = Vec(0, 0)
        else:
            self.velocity += self.accel * dt
            self.position += self.velocity * dt
        self.accel = Vec(0, 0)

    def draw(self, screen):
        pygame.draw.circle(screen, self.color,
                           Vec(self.position[0], 300 - self.position[1]), 10,
                           1)


class Spring:
    def __init__(self, obj_a, obj_b, length, k):
        self.obj_a = obj_a
        self.obj_b = obj_b
        self.length = length
        self.k = k
        self.linear_damping_factor = 0.5
        self.tangential_damping_factor = 0.2

    def tick(self, dt):
        axis = (self.obj_a.position - self.obj_b.position)
        length = numpy.linalg.norm(axis)
        normalized_axis = axis / length
        force = normalized_axis * (length - self.length) * self.k
        a_component = Project(self.obj_a.velocity, normalized_axis)
        damping_a = -a_component * self.linear_damping_factor + (
            a_component - self.obj_a.velocity) * self.tangential_damping_factor
        b_component = Project(self.obj_b.velocity, normalized_axis)
        damping_b = -b_component * self.linear_damping_factor + (
            b_component - self.obj_b.velocity) * self.tangential_damping_factor
        self.obj_a.apply_force(-force / 2 + damping_a)
        self.obj_b.apply_force(force / 2 + damping_b)

    def draw(self, screen):
        pygame.draw.line(screen, (255, 0, 0),
                         Vec(0, 300) + Vec(1, -1) * self.obj_a.position,
                         Vec(0, 300) + Vec(1, -1) * self.obj_b.position, 1)


class World:
    def __init__(self):
        self.objects = []

        balls = []
        springs = []
        for i in range(20):
            balls.append(
                Ball(Vec(150, 280),
                     Vec(i / 10, i / 10),
                     mass=1,
                     frozen=(i == 0)))
            if i > 0:
                springs.append(Spring(balls[-1], balls[-2], 10, 100))
        self.objects.extend(balls)
        self.objects.extend(springs)
        self.last_time = time.time()

    def draw(self, screen):
        current_time = time.time()
        dt = current_time - self.last_time

        self.objects[0].position[0] = pygame.mouse.get_pos()[0]
        self.objects[0].position[1] = 300 - pygame.mouse.get_pos()[1]

        for o in self.objects:
            if hasattr(o, 'mass'):
                o.apply_force(Vec(0, -50))

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
