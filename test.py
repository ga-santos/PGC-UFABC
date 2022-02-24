from nltk.corpus import wordnet as wn
import sem


from multiprocessing import Pool
import multiprocessing as mp
import time

# Parallelizing using Pool.apply()

#import multiprocessing as mp

# Step 1: Init multiprocessing.Pool()
#pool = mp.Pool(mp.cpu_count())

# Step 2: `pool.apply` the `howmany_within_range()`
#results = [pool.apply(howmany_within_range, args=(row, 4, 8)) for row in data]

def f(x):
    return x*x

if __name__ == '__main__':


    
    start_para = time.time()
    with Pool(6) as p:
        p.map(f, range(0, 100000))

    end_para = time.time()


    start = time.time()
    tmp = []
    for i in range(0,100000):
        f(i)
    end = time.time()

    print("Time paralel : " + "{:.3f}".format(end_para - start_para)+ " seconds.")
    print("Time single : " + "{:.3f}".format(end - start) + " seconds.")
    


def adaptedLesk(word1, context_list):
    syn = wn.synsets(word1)
    maxoverlap = 0
    overlap = 0
    syndef_maxoverlap = 0
    if(syn == None): return None
    else:
        syndefs = []
        for i in syn:
            h = i.definition()
            h = h.replace("(", "")
            h = h.replace(")", "")
            h = h.replace(":", "")
            syndefs.append(h.split())

        for i, x in enumerate(syndefs):
            for synword in x:
                overlap = 0
                for y in context_list:
                    if(synword == y): 
                        overlap += 1
                if(overlap > maxoverlap): 
                    maxoverlap = overlap
                    syndef_maxoverlap = i

    return (syndefs[syndef_maxoverlap], maxoverlap)

#bank = wn.synset('bank.n.01')
#coinbank = wn.synset('bank.n.03')
#print("bank" , wn.path_similarity(bank, coinbank), coinbank)

#for i in bank:
#    print("===============")
#    x = i.lemmas()
#    print(i.name())
#    for k in x:
#        print(k.name())


#love = wn.synset('love.n.01')

#hate = wn.synset('hate.n.01')

#romance = wn.synset('romance.n.01')

#print(sem.compSense('bank', 'money', None, None))

#print(("Teste teste teste teste teste a a a adf df df ").split())
#print((wn.synsets('bank'))[0].lemmas()[0].name())
#a = wn.synsets('bank')[0].definition()
#print(a)
#print(a.split())

#print(love, hate, romance)
#print("path ", wn.path_similarity(love, hate), wn.path_similarity(love, romance))
#print("lch ", wn.lch_similarity(love, hate), wn.lch_similarity(love, romance))
#print("wup ", wn.wup_similarity(love, hate), wn.wup_similarity(love, romance))


#avocado = wn.synset('avocado.n.01')
#bus = wn.synset('bus.n.01')
#papaya = wn.synset('papaya.n.01')
#banana = wn.synset('banana.n.01')

#print(papaya.definition())
#print('---------------------------------')

#print("Path : Avocado x Bus = ", wn.path_similarity(avocado, bus) , " | Avocado x Papaya = ", wn.path_similarity(avocado, papaya) , " | Avocado x Banana = ", wn.path_similarity(avocado, banana) ," | Avocado x Avocado = ", wn.path_similarity(avocado, avocado), "\n")
#print("Leacock-Chodorow : Avocado x Bus = ", wn.lch_similarity(avocado, bus) , " | Avocado x Papaya = ", wn.lch_similarity(avocado, papaya) , " | Avocado x Banana = ", wn.lch_similarity(avocado, banana) ," | Avocado x Avocado = ", wn.lch_similarity(avocado, avocado), "\n")
#print("Wu-Palmer : Avocado x Bus = ", wn.wup_similarity(avocado, bus) , " | Avocado x Papaya = ",  wn.wup_similarity(avocado, papaya) , " | Avocado x Banana = ", wn.wup_similarity(avocado, banana) ," | Avocado x Avocado = ", wn.wup_similarity(avocado, avocado), "\n")

#print("\n\n")


#x = ['river', 'beach', 'water', 'stream']
#y = ['financial', 'institution', 'money']
#print(x, adaptedLesk('bank', x))
#print(y, adaptedLesk('bank', y))

