def lookup(func):
    from . import dolly_v2_3b, redpajama_incite_chat_3b_v1

    ret = dolly_v2_3b.lookup(func)
    if ret is not None:
        return ret
    ret = redpajama_incite_chat_3b_v1.lookup(func)
    if ret is not None:
        return ret
    return None
