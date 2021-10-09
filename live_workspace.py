#!/usr/bin/python3

import importlib.util
import os
import signal
import time
import watchdog.events
import watchdog.observers
import traceback

from absl import app
from absl import flags

FLAGS = flags.FLAGS

should_exit = False


def handle_signal(signal, frame):
    global should_exit
    print(signal, frame)
    should_exit = True


def curry(function, *args):
    return lambda *additional_args: (function(*args, *additional_args))


class Watcher(watchdog.events.FileSystemEventHandler):
    def __init__(self, filename, handler):
        self.filename = filename
        self.handler = handler

        print("Watcher initialized for", self.filename)

        super(Watcher, self).__init__()

    def on_modified(self, event):
        if (event.event_type == "modified" and self.filename == event.src_path
                and event.is_directory == False):
            try:
                self.handler()
            except Exception as e:
                print(
                    f"Encountered exception during file handler execution: {e}"
                )
                traceback.print_exc()

    @property
    def dirname(self):
        return os.path.dirname(self.filename)


def observe(watcher):
    observer = watchdog.observers.Observer()
    observer.schedule(watcher, watcher.dirname, recursive=True)
    observer.start()


def load_module(module_file):
    module_spec = importlib.util.spec_from_file_location("module", module_file)
    module = importlib.util.module_from_spec(module_spec)
    return module_spec, module


def reload_module_handler(module_file, module_handler):
    print(f"Reloading module from {module_file:s}")
    module_spec, module = load_module(module_file)
    # Provide the module to the handler, along with its spec.
    module_handler(module, module_spec)

current_module = [None]

def module_executor(workspace, module, module_spec):
    if current_module[0] is not None:
        current_module[0].stop()
    module.workspace = workspace
    module_spec.loader.exec_module(module)
    current_module[0] = module
    module.start()


def main(argv):
    spec, workspace = load_module(FLAGS.workspace_file)
    spec.loader.exec_module(workspace)
    workspace.start()

    watcher = Watcher(
        FLAGS.generate_file,
        curry(reload_module_handler, FLAGS.generate_file,
              curry(module_executor, workspace)))
    observe(watcher)
    signal.signal(signal.SIGINT, handle_signal)

    while not should_exit:
        time.sleep(0.1)

    workspace.stop()


if __name__ == "__main__":
    flags.DEFINE_string("workspace_file", None, "")
    flags.mark_flag_as_required("workspace_file")
    flags.DEFINE_string("generate_file", None, "")
    flags.mark_flag_as_required("generate_file")
    app.run(main)
