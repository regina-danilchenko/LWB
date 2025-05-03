from .add import add_router
from .help import help_router
from .learn import learn_router
from .open_dict import open_dict_router
from .start import start_router
from .test import test_router


__all__ = ['add_router', 'help_router', 'learn_router', 'open_dict_router', 'start_router', 'test_router', 'routers']

routers = [
    add_router,
    help_router,
    learn_router,
    open_dict_router,
    start_router,
    test_router
]
