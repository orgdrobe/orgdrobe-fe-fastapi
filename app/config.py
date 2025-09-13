import os
from dotenv import dotenv_values

config = {
    **dotenv_values(".env.shared"),
    **dotenv_values(".env.secret"),
    # **os.environ,
}