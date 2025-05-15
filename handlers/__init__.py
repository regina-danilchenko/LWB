from .add import add_router
from .delete import delete_router
from .help import help_router
from .learn import learn_router
from .open_dict import open_dict_router
from .start import start_router
from .test import test_router
from .statistics import statistics_router


__all__ = [
    'add_router',
    'delete_router',
    'help_router',
    'learn_router',
    'open_dict_router',
    'start_router',
    'test_router',
    'statistics_router',
    'routers'
]

routers = [
    add_router,
    delete_router,
    help_router,
    learn_router,
    open_dict_router,
    start_router,
    test_router,
    statistics_router
]
