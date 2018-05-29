from functools import wraps
import time
def func_time(func) :
    @wraps(func)
    def wrapper(*args, **kargs) :
        start = time.time()
        result = func(*args,**kargs)
        elapsed_time =  time.time() - start
        print(f"[{func.__name__}]::{elapsed_time}:sec")
        return result
    return wrapper