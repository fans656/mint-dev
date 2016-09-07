import os
import subprocess

def test(name):
    if not name:
        return lambda f: f
    def deco(cases):
        fpath = os.path.join(name + '.py')
        if not os.path.exists(fpath):
            raise Exception('{} does not exist'.format(name))
        for i_case, case in enumerate(cases()):
            p = subprocess.Popen(['python', fpath],
                                 stdin=subprocess.PIPE,
                                 stdout=subprocess.PIPE)
            case = case[1:-1]
            print 'Test: #{}'.format(i_case + 1)
            out, err = p.communicate(case)
            print out,
        return cases
    return deco
