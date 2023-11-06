import importlib
import os

if __name__ == "__main__":
    pipe = getattr(importlib.import_module("Pipeline"), "PipelineBuild")
    pipe = pipe("config.yaml")
    pipe.pipeline()
    print(len(os.listdir(pipe.data["ENVIRONMENT_VARIABLES"]["IMAGE_DIR"])))
    print("Done")
