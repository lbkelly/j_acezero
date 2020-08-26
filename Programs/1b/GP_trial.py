def main():

    scores = []
    for i in xrange(10):
        scores.append(i)

    for x in xrange(100):
        scores.append(scores[9]+1)
        scores.pop(0)
        print scores

    # scores.append(10)
    #
    # for x in scores:
    #     print x
    #
    # scores.pop(0)
    #
    # for x in scores:
    #     print x
    #
    # print scores


if __name__ == "__main__":
    main()
