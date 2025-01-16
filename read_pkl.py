import pickle

def read_pkl(fp):
    with open(fp, "rb") as f:
        data = []
        try:
            while True:
                data.append(pickle.load(f))
        except EOFError as e:
            pass
    return data
