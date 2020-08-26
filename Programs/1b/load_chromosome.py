import write_chromosome as wc
import write_initial_values as initial_values

"""
A script that contains methods that will help save the chromosome values back to file, so we can specify and
individually inspect any chromosome in Ace0. It's much easier to copy and paste the values from the hall of fame into
this script, rather than manually altering the JSON file.
"""

__author__ = 'lbkelly'

chromosome_parameters = wc.WriteChromosome()
chromosome_initial_values = initial_values.WriteInitial()


def main():
    # the parameter values of the chromosome we want to load

    # use for 1a experiments
    chromosome_parameters.update_chromosome(12.663348019681429, -70.58181163952935, 0.0, 0.0, 971.3098931925933)


    # use for 1b experiments
    # temp = [-33817.9353344, 10136.0034014, -41843.5788796, 37713.6518802, -42509.5428107, 6943.04684127, -153.952653988, 253.41335001, -3.30346320329, 1000, 140.174326605, 123.671155524, -53.336882426, 49.7866113398, -96.2365999231, 44.6429746619, -100, 23.9247996558, -48152, 41054.3481601, -18993.0672394, 28784.3878141, -31140.1589974, 21385.2449969, -306.872151279, 427.133537019, -304.0111742, 1000, -943.865811657, 5.86735131193, -100, 63.8712328527, -54.479322587, 36.6851797356, -56.0991011879, 88.3135070819, -8704.06441125, 28831.7601923, -4153.23577522, 28677.8629044, -34094.6969044, 20734.5584834, -182.42490493, 69.2870936543, -1000, 357.513121517, -317.555354426, 1000, -43.1281384657, 100, -100, 100, -99.2959179701, 89.4632578405, -8738.89710911, 35780.7852565, -36699.1486281, 26734.2195737, -28168.4664422, -48152, -337.123900164, 643.244389011, -919.336643532, 84.0888535746, -1000, 434.614245757, -38.860308673, 33.8610613404, -13.4418294259, -81.0183348104, -7.89859170188, 93.9763926731, -20901.2569574, 16720.02805, -40856.8786214, 38806.5220472, -7171.7618145, 4210.70672537, -311.010266118, 610.372271272, -296.732836426, 750.899339195, -251.239742315, -655.284113008, -34.414014709, 99.9795783277, -78.9984244004, 5.21667570974, -99.7043335982, -100, -33677.0961038, 7464.43408205, -13001.6696241, 47999.7692201, 48152, 48152, -373.399286897, 904.757104867, -904.315138869, 295.028215908, -1000, -838.066474972, -41.6640440402, 100, -100, 82.6681889552, -25.2471810463, 37.6033834997, -14024.9162854, 48152, -47799.1325363, 396.737245739, -2970.15832975, 14803.1573726, -899.924248839, 547.7400336, -139.708435669, 34.5825602121, 352.891259375, -667.827736829, 100, 12.0051443546, -21.8159270826, 87.9709651269, -27.4128042564, -100, -31795.5715667, 41848.4252665, -16213.3013175, 41899.029872, -23838.070412, 37178.5508379, -954.421122401, 928.530245005, -948.459439186, 341.270250127, -1000, 703.33486741, -3.2569929881, 68.3590316539, -39.3981422974, 10.8578062978, -35.7561369579, 96.8176546241, -45669.4147456, 29890.0512135, 48152, 5978.4706099, 48152, 28625.0332002, -728.934656675, 6.91524341942, -678.466777125, 71.2595683592, -372.182535999, 678.259806836, -75.2308821393, 1.90709488124, -35.7097957644, 73.1852859503, -100, 57.4185042251, -6012.66700113, 46621.0801324, -32753.4556824, 2182.15146255, -29464.4882983, 1703.36417466, -684.915426391, 800.762757996, -1000, 618.043304204, -217.159936328, 612.722293235, -65.4728799225, -100, -15.0180360053, 92.2067760159, -23.0735338989, 33.1948513012, -20495.6092116, 8844.10513527, -13230.7866435, 3808.11506693, -16284.1487775, 29859.3390638, -923.287748107, 302.354924856, -867.211223742, -1000, -86.9401381529, 273.653028861, -45.2746549583, 100, -75.8077461909, 90.5630155279, -68.8589729866, 85.1325231886, -16955.6867535, 11919.7314299, -16840.6425402, -37931.5317571, -6042.08539317, 3524.7606678, -292.649757629, 1000, -190.481907957, 847.646569658, -789.81088996, 1000, -4.26613908429, 52.959891209, 100, 72.4501201843, -20.0736187292, 14.6587035378]

    # # ecu stern agent
    # chromosome_parameters.load_ecu_chromosome(temp)

    # park ecu agent
    # chromosome_parameters.load_basic_ecu_chromosome(temp)

    # change the initial starting positions x, y, altitude, speed, heading
    chromosome_initial_values.update_initial_values(0, 0, 15000, 0, 400)


if __name__ == "__main__":
    main()