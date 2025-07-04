def yazim_hatasi_var_mi(text):
    return any(word for word in text.split() if len(word) > 15 or word.count("ttt") > 0)