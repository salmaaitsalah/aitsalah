from util.FilesLoader import FilesLoader


def data_store():
    classes = "./data/classes.txt"

    f_arms = FilesLoader(classes)
    store_arms = f_arms.loadFile()
    res_arms = f_arms.processFileArms(store_arms)
    arms = res_arms[2]
    nb_arms = res_arms[1]
    d_arms = res_arms[0]

    # print(arms[0].getArmId())
    # print(arms[0].getArmName())
    # print(arms[0].getArmFeat())


    # print(contexts[0].getContextId())
    # print(contexts[0].getContextFeat())

    # print(ratings)

    f_arms.close(store_arms)

    return nb_arms, arms, d_arms
