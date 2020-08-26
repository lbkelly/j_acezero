import json
import math
import os
import shutil

import ace_zero
import charts


class BatchRun():
    """ Test ACE Zero initialisation including argument handling. """

    def setUp(self):
        # Change working directory to the directory of this test so paths work
        abspath = os.path.abspath(__file__)
        dname = os.path.dirname(abspath)
        os.chdir(dname)

    def batch_run(self):
        """ Tests running ACE Zero multiple times with changing blue starting
        positions. """

        # Clear the runs directory
        shutil.rmtree("runs", ignore_errors=True)

        # Set up batch parameters
        blue_path = "blue.json"
        xmin = -4
        xmax = 0
        ymin = -4
        ymax = 5
        step = 2
        results = []
        total = math.ceil((xmax - xmin) / float(step)) * \
                math.ceil((ymax - ymin) / float(step))

        # Incrementally modify the blue starting position
        count = 0
        for x in range(xmin, xmax, step):
            for y in range(ymin, ymax, step):
                # Modify blue starting position
                with open(blue_path, 'r+') as f:
                    # Read the current file and modify the starting position
                    data = json.load(f)
                    data['x'] = x
                    data['y'] = y

                    # Write over the file with the modified json
                    f.seek(0)
                    json.dump(data, f, indent=4)
                    f.truncate()  # remove remaining part

                # Run ACE Zero with updated blue parameters and save the results
                traces = ace_zero.run_ace_zero(scenario="scenario.json",
                                               noxcombat=True)
                results.append(traces)

                # Update progress indicator
                count += 1
                print "{0:.1f}%".format(count / float(total) * 100.0)

        charts.multiple_run_chart(results)


if __name__ == '__main__':
    batch_run = BatchRun()
    batch_run.batch_run()
