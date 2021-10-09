import pygame
import threading

should_exit = False
draw_queue = []
frame_event = threading.Event()

def wait_frame():
    frame_event.wait()
    frame_event.clear()



def stop():
    global should_exit
    should_exit = True


def submit_draw(draw_fn):
    draw_queue.append(draw_fn)


def draw_thread():
    global should_exit
    global draw_queue
    pygame.init()
    screen = pygame.display.set_mode((300, 300))
    clock = pygame.time.Clock()

    while not should_exit:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                should_exit = True

        try:
            for draw_fn in draw_queue:
                draw_fn(screen)
        except Exception as e:
            print(e)

        draw_queue = []

        pygame.display.flip()
        clock.tick(200)
        frame_event.set()


def start():
    threading.Thread(target=draw_thread).start()
