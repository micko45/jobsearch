import pickle
p_file = "./pikle.pk"
df = pickle.load(open(p_file, 'rb'))

print(df.to_html(escape=False))

